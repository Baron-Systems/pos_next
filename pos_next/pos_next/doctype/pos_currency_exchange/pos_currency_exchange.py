# Copyright (c) 2026, POS Next and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt, now


class POSCurrencyExchange(Document):
	def before_submit(self):
		"""Create Journal Entry on submit"""
		if not self.journal_entry:
			self.journal_entry = self.create_journal_entry()

	def create_journal_entry(self):
		"""Create Journal Entry for currency exchange based on transaction type (Buy/Sell)."""
		from frappe.utils import today

		je = frappe.get_doc({
			"doctype": "Journal Entry",
			"voucher_type": "Journal Entry",
			"posting_date": self.posting_date,
			"company": self.company,
			"user_remark": self._get_remark(),
			"pos_opening_shift": self.pos_opening_shift,
			"multi_currency": 1,
		})

		company_currency = frappe.get_value("Company", self.company, "default_currency")

		# Determine exchange rates so both sides balance in company currency
		if self.source_currency == company_currency:
			source_exchange_rate = 1.0
			company_amount = flt(self.source_amount)
			target_exchange_rate = company_amount / flt(self.target_amount)
		elif self.target_currency == company_currency:
			target_exchange_rate = 1.0
			company_amount = flt(self.target_amount)
			source_exchange_rate = company_amount / flt(self.source_amount)
		else:
			try:
				from erpnext.setup.utils import get_exchange_rate
				source_exchange_rate = get_exchange_rate(self.source_currency, company_currency, self.posting_date) or 1.0
			except Exception:
				source_exchange_rate = 1.0
			company_amount = flt(self.source_amount) * flt(source_exchange_rate)
			target_exchange_rate = company_amount / flt(self.target_amount)

		if self.transaction_type == "Buy":
			# Buy: We receive source currency, we pay target currency
			# Debit: Source Account (we receive source)
			# Credit: Target Account (we pay target)
			debit_row = je.append("accounts", {})
			debit_row.update({
				"account": self.source_account,
				"debit_in_account_currency": flt(self.source_amount),
				"credit_in_account_currency": 0,
				"exchange_rate": flt(source_exchange_rate),
			})

			credit_row = je.append("accounts", {})
			credit_row.update({
				"account": self.target_account,
				"debit_in_account_currency": 0,
				"credit_in_account_currency": flt(self.target_amount),
				"exchange_rate": flt(target_exchange_rate),
			})
		else:
			# Sell: We pay source currency, we receive target currency
			# Debit: Target Account (we receive target)
			# Credit: Source Account (we pay source)
			debit_row = je.append("accounts", {})
			debit_row.update({
				"account": self.target_account,
				"debit_in_account_currency": flt(self.target_amount),
				"credit_in_account_currency": 0,
				"exchange_rate": flt(target_exchange_rate),
			})

			credit_row = je.append("accounts", {})
			credit_row.update({
				"account": self.source_account,
				"debit_in_account_currency": 0,
				"credit_in_account_currency": flt(self.source_amount),
				"exchange_rate": flt(source_exchange_rate),
			})

		je.flags.ignore_permissions = True
		je.save()
		je.submit()

		return je.name

	def _get_remark(self):
		return (
			f"POS Currency Exchange - {self.transaction_type} {self.source_currency}\n"
			f"Source: {flt(self.source_amount)} {self.source_currency}\n"
			f"Target: {flt(self.target_amount)} {self.target_currency}\n"
			f"Rate: {flt(self.exchange_rate)}\n"
			f"Created from POS Currency Exchange"
		)

	def before_cancel(self):
		"""Cancel linked Journal Entry"""
		if self.journal_entry:
			try:
				je = frappe.get_doc("Journal Entry", self.journal_entry)
				if je.docstatus == 1:
					je.flags.ignore_permissions = True
					je.cancel()
			except Exception:
				pass
