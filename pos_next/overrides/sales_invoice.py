# Copyright (c) 2025, BrainWise and contributors
# For license information, please see license.txt

"""
Sales Invoice Override
Handles wallet payments that require party information for Receivable accounts.

"""

import math

import frappe
from frappe.utils import cint, flt
from erpnext.accounts.doctype.sales_invoice.sales_invoice import SalesInvoice
from erpnext.accounts.utils import get_account_currency


def _round_pos_amount(amount, precision=2):
	"""
	Standard rounding to the nearest 0.5 (round half up).
	Examples: 18.24 -> 18.0, 18.25 -> 18.5, 18.74 -> 18.5, 18.75 -> 19.0
	"""
	amount = flt(amount)
	if not amount:
		return flt(0.0, precision)

	sign = 1 if amount >= 0 else -1
	rounded = math.floor(abs(amount) * 2 + 0.5) / 2

	return flt(sign * rounded, precision)


class CustomSalesInvoice(SalesInvoice):
	"""
	Custom Sales Invoice class that handles wallet payments correctly.

	When a wallet payment is made using a Receivable account, ERPNext requires
	party information in the GL entry. This override adds party_type and party
	for wallet payment methods marked with is_wallet_payment.
	"""

	def calculate_taxes_and_totals(self):
		"""
		Override rounding for POS invoices to use 0.5-step rounding.
		"""
		super().calculate_taxes_and_totals()

		if not cint(self.is_pos) or self.is_rounded_total_disabled():
			return

		rounded_total = _round_pos_amount(self.grand_total)
		rounding_adjustment = flt(
			rounded_total - self.grand_total, self.precision("rounding_adjustment")
		)

		self.rounded_total = rounded_total
		self.rounding_adjustment = rounding_adjustment
		self.base_rounded_total = flt(
			rounded_total * self.conversion_rate, self.precision("base_rounded_total")
		)
		self.base_rounding_adjustment = flt(
			rounding_adjustment * self.conversion_rate, self.precision("base_rounding_adjustment")
		)

		# Recalculate change against the POS-rounded total.
		# ERPNext computed change_amount inside super() using its own rounded_total
		# (which may differ, e.g. currency fraction rounding), so it must be fixed here.
		if (
			self.get("paid_amount")
			and not self.get("is_return")
			and any(d.type == "Cash" for d in self.get("payments", []))
		):
			self.change_amount = flt(
				max(0, flt(self.paid_amount) - rounded_total),
				self.precision("change_amount"),
			)
			self.base_change_amount = flt(
				self.change_amount * self.conversion_rate,
				self.precision("base_change_amount"),
			)
		else:
			self.change_amount = 0.0
			self.base_change_amount = 0.0

		# Outstanding should be calculated against the rounded total,
		# adding back the change returned to the customer
		if self.get("paid_amount"):
			self.outstanding_amount = flt(
				rounded_total - self.paid_amount + flt(self.change_amount),
				self.precision("outstanding_amount"),
			)
		else:
			self.outstanding_amount = rounded_total

	def make_pos_gl_entries(self, gl_entries):
		"""
		Override to add party information for wallet payment accounts.

		The standard ERPNext implementation doesn't set party_type/party for
		payment mode accounts, which causes validation errors for Receivable
		accounts (like wallet accounts).
		"""
		if cint(self.is_pos):
			skip_change_gl_entries = not cint(
				frappe.db.get_single_value("POS Settings", "post_change_gl_entries")
			)

			for payment_mode in self.payments:
				if skip_change_gl_entries and payment_mode.account == self.account_for_change_amount:
					payment_mode.base_amount -= flt(self.change_amount)

				if payment_mode.amount:
					# POS, make payment entries
					# Credit entry to debit_to (customer receivable)
					gl_entries.append(
						self.get_gl_dict(
							{
								"account": self.debit_to,
								"party_type": "Customer",
								"party": self.customer,
								"against": payment_mode.account,
								"credit": payment_mode.base_amount,
								"credit_in_account_currency": payment_mode.base_amount
								if self.party_account_currency == self.company_currency
								else payment_mode.amount,
								"against_voucher": self.return_against
								if cint(self.is_return) and self.return_against
								else self.name,
								"against_voucher_type": self.doctype,
								"cost_center": self.cost_center,
							},
							self.party_account_currency,
							item=self,
						)
					)

					# Debit entry to payment mode account
					payment_mode_account_currency = get_account_currency(payment_mode.account)

					# Get party info for wallet payments
					party_type, party = self.get_party_and_party_type_for_pos_gl_entry(
						payment_mode.mode_of_payment, payment_mode.account
					)

					gl_entries.append(
						self.get_gl_dict(
							{
								"account": payment_mode.account,
								"party_type": party_type,
								"party": party,
								"against": self.customer,
								"debit": payment_mode.base_amount,
								"debit_in_account_currency": payment_mode.base_amount
								if payment_mode_account_currency == self.company_currency
								else payment_mode.amount,
								"cost_center": self.cost_center,
							},
							payment_mode_account_currency,
							item=self,
						)
					)

			if not skip_change_gl_entries:
				gl_entries.extend(self.get_gle_for_change_amount())

	def validate_selling_price(self):
		"""
		Skip ERPNext's selling-price vs purchase/valuation-rate validation
		for POS invoices only when a discount has been applied.

		A discount can be:
		- A line-level fixed or percentage discount on any item.
		- An invoice-level additional discount (fixed or percentage).

		In those cases the cashier may push the net rate below the last
		purchase rate or valuation rate, so we allow the sale.
		"""
		if not cint(self.is_pos):
			return super().validate_selling_price()

		has_discount = bool(
			flt(self.additional_discount_percentage)
			or flt(self.discount_amount)
			or any(
				flt(item.discount_percentage) or flt(item.discount_amount)
				for item in self.get("items", [])
			)
		)

		if has_discount:
			# POS invoice has a discount: bypass selling-price vs cost validation.
			return

		return super().validate_selling_price()

	def get_party_and_party_type_for_pos_gl_entry(self, mode_of_payment, account):
		"""
		Get party type and party for wallet payment GL entries.

		For wallet payments (Mode of Payment with is_wallet_payment=1),
		returns Customer as party_type and the invoice customer as party.
		For regular payments, returns empty strings.
		"""
		is_wallet_mode_of_payment = frappe.db.get_value(
			"Mode of Payment", mode_of_payment, "is_wallet_payment"
		)

		party_type, party = "", ""
		if is_wallet_mode_of_payment:
			party_type, party = "Customer", self.customer

		return party_type, party
