# Copyright (c) 2025, Youssef Restom and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import cint, flt


class POSSettings(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		allow_change_posting_date: DF.Check
		allow_credit_sale: DF.Check
		allow_customer_payment: DF.Check
		allow_customer_purchase_order: DF.Check
		allow_supplier_payment: DF.Check
		allow_delete_offline_invoice: DF.Check
		allow_duplicate_customer_names: DF.Check
		allow_free_batch_return: DF.Check
		allow_negative_stock: DF.Check
		allow_partial_payment: DF.Check
		allow_print_draft_invoices: DF.Check
		allow_print_last_invoice: DF.Check
		allow_return: DF.Check
		allow_return_without_invoice: DF.Check
		allow_sales_order: DF.Check
		allow_select_sales_order: DF.Check
		allow_submissions_in_background_job: DF.Check
		allow_user_to_edit_additional_discount: DF.Check
		allow_user_to_edit_item_discount: DF.Check
		allow_write_off_change: DF.Check
		auto_create_wallet: DF.Check
		auto_set_delivery_charges: DF.Check
		create_only_sales_order: DF.Check
		decimal_precision: DF.Literal["2", "3", "4", "5", "6"]
		default_card_view: DF.Check
		default_loyalty_program: DF.Link | None
		disable_rounded_total: DF.Check
		display_discount_amount: DF.Check
		display_discount_percentage: DF.Check
		display_item_code: DF.Check
		enable_loyalty_program: DF.Check
		enable_sales_persons: DF.Literal["Disabled", "Single", "Multiple"]
		enabled: DF.Check
		fetch_coupon: DF.Check
		hide_expected_amount: DF.Check
		input_qty: DF.Check
		loyalty_to_wallet: DF.Check
		max_discount_allowed: DF.Float
		pos_profile: DF.Link
		post_change_gl_entries: DF.Check
		return_validity_days: DF.Int
		search_limit: DF.Int
		show_customer_balance: DF.Check
		silent_print: DF.Check
		tax_inclusive: DF.Check
		use_delivery_charges: DF.Check
		use_limit_search: DF.Check
		use_percentage_discount: DF.Check
		wallet_account: DF.Link | None
		enable_currency_exchange: DF.Check
		currency_setup: DF.Table
	# end: auto-generated types

	def validate(self):
		"""Validate POS Settings"""
		# Guard against None values and validate discount percentage
		max_discount = flt(self.max_discount_allowed)
		if max_discount < 0 or max_discount > 100:
			frappe.throw("Max Discount Allowed must be between 0 and 100")

		# Guard against None values and validate search limit
		if self.use_limit_search:
			search_limit = cint(self.search_limit)
			if search_limit <= 0:
				frappe.throw("Search Limit must be greater than 0")

		# Validate currency exchange settings
		self.validate_currency_setup()

	def validate_currency_setup(self):
		"""Validate currency setup table"""
		if not self.enable_currency_exchange:
			return

		currencies = []
		for row in self.currency_setup or []:
			# Check currency is selected
			if not row.currency:
				frappe.throw(f"Row #{row.idx}: Currency is required")
			if not row.cash_account:
				frappe.throw(f"Row #{row.idx}: Cash Account is required")
			if not row.company:
				frappe.throw(f"Row #{row.idx}: Company is required")

			# Check for duplicate currency per company
			key = f"{row.currency}-{row.company}"
			if key in currencies:
				frappe.throw(
					f"Row #{row.idx}: Duplicate currency {row.currency} for company {row.company}"
				)
			currencies.append(key)

			# Validate account company matches
			account_company = frappe.db.get_value("Account", row.cash_account, "company")
			if account_company != row.company:
				frappe.throw(
					f"Row #{row.idx}: Account {row.cash_account} does not belong to company {row.company}"
				)

			# Validate account currency matches
			account_currency = frappe.db.get_value("Account", row.cash_account, "account_currency")
			if account_currency and account_currency != row.currency:
				frappe.throw(
					f"Row #{row.idx}: Account currency ({account_currency}) does not match selected currency ({row.currency})"
				)

		# Require at least 2 currencies
		if len(currencies) < 2:
			frappe.throw("At least 2 currencies must be configured for currency exchange")

	def on_update(self):
		"""Sync allow_negative_stock with Stock Settings"""
		self.sync_negative_stock_setting()

	def sync_negative_stock_setting(self):
		"""
		Synchronize allow_negative_stock with Stock Settings.

		When enabled in POS Settings, it enables the global Stock Settings.
		When disabled, it only disables global Stock Settings if no other
		POS Settings have it enabled.

		Note: Runs in the same transaction as the save, no manual commits.
		"""
		current_stock_setting = cint(
			frappe.db.get_single_value("Stock Settings", "allow_negative_stock") or 0
		)

		if cint(self.allow_negative_stock):
			# Enable Stock Settings if not already enabled
			if not current_stock_setting:
				frappe.db.set_single_value("Stock Settings", "allow_negative_stock", 1, update_modified=False)
				frappe.msgprint(
					"Stock Settings 'Allow Negative Stock' has been automatically enabled.",
					indicator="green",
					alert=True
				)
		else:
			# Only disable if no other enabled POS Settings have it enabled
			if current_stock_setting:
				# Use count for better performance and clarity
				other_enabled_count = frappe.db.count(
					"POS Settings",
					{
						"allow_negative_stock": 1,
						"enabled": 1,  # Only check enabled POS Settings
						"name": ["!=", self.name]
					}
				)

				if other_enabled_count == 0:
					frappe.db.set_single_value("Stock Settings", "allow_negative_stock", 0, update_modified=False)
					frappe.msgprint(
						"Stock Settings 'Allow Negative Stock' has been automatically disabled.",
						indicator="orange",
						alert=True
					)


@frappe.whitelist()
def get_pos_settings(pos_profile=None):
	"""
	Get POS Settings for a specific POS Profile.

	Also injects the current global Stock Settings value to show the actual
	source of truth, preventing confusion when the checkbox appears enabled
	but the global setting was changed elsewhere.
	"""
	from frappe import _

	if not pos_profile:
		return None

	# Check if user has access to this POS Profile
	has_access = frappe.db.exists(
		"POS Profile User",
		{"parent": pos_profile, "user": frappe.session.user}
	)

	if not has_access and not frappe.has_permission("POS Settings", "read"):
		frappe.throw(_("You don't have access to this POS Profile"))

	settings = frappe.db.get_value(
		"POS Settings",
		{"pos_profile": pos_profile},
		"*",
		as_dict=True
	)

	# If no settings exist, create default settings
	if not settings:
		settings = create_default_settings(pos_profile)

	# Inject the current global Stock Settings value for transparency
	# This helps UI reflect the actual state even if multiple POS Settings exist
	settings["_global_allow_negative_stock"] = cint(
		frappe.db.get_single_value("Stock Settings", "allow_negative_stock") or 0
	)

	# Inject allow_customer_payment and allow_supplier_payment from POS Profile (per-profile settings)
	# These control the visibility of the customer/supplier payment buttons in the POS UI
	try:
		pos_profile_doc = frappe.get_doc("POS Profile", pos_profile)
		settings["allow_customer_payment"] = cint(pos_profile_doc.allow_customer_payment or 0)
		settings["allow_supplier_payment"] = cint(pos_profile_doc.allow_supplier_payment or 0)
		settings["allow_stock_lookup"] = cint(pos_profile_doc.posa_allow_stock_lookup or 0)
	except Exception:
		# If POS Profile doesn't exist or field doesn't exist, default to 0
		settings["allow_customer_payment"] = 0
		settings["allow_supplier_payment"] = 0
		settings["allow_stock_lookup"] = 0

	# Inject currency_setup for enabled currency exchange
	if cint(settings.get("enable_currency_exchange")):
		settings_doc = frappe.get_doc("POS Settings", settings["name"])
		settings["currency_setup"] = [
			{
				"currency": row.currency,
				"cash_account": row.cash_account,
				"company": row.company,
			}
			for row in settings_doc.currency_setup
		]

	return settings


def create_default_settings(pos_profile):
	"""Create default POS Settings for a POS Profile"""
	doc = frappe.new_doc("POS Settings")
	doc.pos_profile = pos_profile
	doc.enabled = 1
	doc.insert()

	return doc.as_dict()


@frappe.whitelist()
def update_pos_settings(pos_profile, settings):
	"""Update POS Settings for a POS Profile"""
	import json
	from frappe import _

	if isinstance(settings, str):
		settings = json.loads(settings)

	# Check if user has access to this POS Profile
	has_access = frappe.db.exists(
		"POS Profile User",
		{"parent": pos_profile, "user": frappe.session.user}
	)

	if not has_access and not frappe.has_permission("POS Settings", "write"):
		frappe.throw(_("You don't have permission to update this POS Profile"))

	# Check if settings exist
	existing = frappe.db.exists("POS Settings", {"pos_profile": pos_profile})

	if existing:
		doc = frappe.get_doc("POS Settings", existing)
		doc.update(settings)
		doc.save()
	else:
		doc = frappe.new_doc("POS Settings")
		doc.pos_profile = pos_profile
		doc.update(settings)
		doc.insert()

	return doc.as_dict()
