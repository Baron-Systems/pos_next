# Copyright (c) 2026, POS Next and contributors
# For license information, please see license.txt

"""
Currency Exchange API for POS
Handles currency exchange operations including:
- Getting currency setup for a POS Profile
- Creating currency exchange transactions
- Validating exchange parameters
- Creating Journal Entries for GL posting
"""

import frappe
from frappe import _
from frappe.utils import cint, flt, now, nowdate, today


@frappe.whitelist()
def get_currency_setup(pos_profile):
	"""
	Get currency setup for a specific POS Profile.

	Args:
		pos_profile: POS Profile name

	Returns:
		list: Currency setup entries with currency, cash_account, company, buy_rate, sell_rate
	"""
	if not pos_profile:
		return []

	# Check if user has access to this POS Profile
	has_access = frappe.db.exists(
		"POS Profile User",
		{"parent": pos_profile, "user": frappe.session.user}
	)

	if not has_access and not frappe.has_permission("POS Settings", "read"):
		frappe.throw(_("You don't have access to this POS Profile"))

	# Get POS Settings
	settings_name = frappe.db.get_value(
		"POS Settings",
		{"pos_profile": pos_profile},
		"name"
	)

	if not settings_name:
		return []

	settings_doc = frappe.get_doc("POS Settings", settings_name)

	if not cint(settings_doc.enable_currency_exchange):
		return []

	return [
		{
			"currency": row.currency,
			"cash_account": row.cash_account,
			"company": row.company,
			"buy_rate": flt(row.buy_rate),
			"sell_rate": flt(row.sell_rate),
		}
		for row in settings_doc.currency_setup
	]


@frappe.whitelist()
def get_exchange_rates(pos_profile):
	"""
	Get exchange rates table for the currency exchange dialog.
	Returns currency setup with buy/sell rates, and company default currency.
	"""
	if not pos_profile:
		return {"rates": [], "company_currency": None}

	setup = get_currency_setup(pos_profile)
	if not setup:
		return {"rates": [], "company_currency": None}

	company = setup[0].get("company") if setup else None
	company_currency = None
	if company:
		company_currency = frappe.db.get_value("Company", company, "default_currency")

	# Exclude the company default currency from the rates table
	rates = [
		{
			"currency": row["currency"],
			"buy_rate": row["buy_rate"],
			"sell_rate": row["sell_rate"],
		}
		for row in setup
		if row["currency"] != company_currency
	]

	return {"rates": rates, "company_currency": company_currency}


@frappe.whitelist()
def validate_exchange(source_currency, target_currency, amount, exchange_rate, transaction_type=None):
	"""
	Validate a currency exchange request.

	Args:
		source_currency: Source currency code
		target_currency: Target currency code
		amount: Source amount
		exchange_rate: Exchange rate
		transaction_type: 'Buy' or 'Sell'

	Returns:
		dict: Validation result with success/failure and message
	"""
	errors = []

	if not source_currency:
		errors.append(_("Source currency is required"))
	if not target_currency:
		errors.append(_("Target currency is required"))
	if source_currency == target_currency:
		errors.append(_("Source and target currency cannot be the same"))
	if not transaction_type:
		errors.append(_("Transaction type is required"))
	elif transaction_type not in ("Buy", "Sell"):
		errors.append(_("Transaction type must be Buy or Sell"))

	amount_val = flt(amount)
	if amount_val <= 0:
		errors.append(_("Amount must be greater than zero"))

	rate_val = flt(exchange_rate)
	if rate_val <= 0:
		errors.append(_("Exchange rate must be greater than zero"))

	if errors:
		return {"valid": False, "errors": errors}

	# Calculate target amount
	target_amount = flt(amount_val * rate_val)

	return {
		"valid": True,
		"target_amount": target_amount,
		"errors": []
	}


@frappe.whitelist()
def create_exchange(source_currency, target_currency, amount, exchange_rate, transaction_type, pos_opening_shift=None, pos_profile=None):
	"""
	Create a POS Currency Exchange transaction and Journal Entry.

	Args:
		source_currency: Source currency code
		target_currency: Target currency code
		amount: Source amount
		exchange_rate: Exchange rate
		transaction_type: 'Buy' or 'Sell'
		pos_opening_shift: POS Opening Shift name (optional)
		pos_profile: POS Profile name (for validation)

	Returns:
		dict: Created exchange document name and journal entry name
	"""
	# Validate inputs
	validation = validate_exchange(source_currency, target_currency, amount, exchange_rate, transaction_type)
	if not validation["valid"]:
		frappe.throw("<br>".join(validation["errors"]))

	# Get currency setup
	if pos_profile:
		setup = get_currency_setup(pos_profile)
	elif pos_opening_shift:
		# Infer pos_profile from shift
		pos_profile = frappe.db.get_value("POS Opening Shift", pos_opening_shift, "pos_profile")
		setup = get_currency_setup(pos_profile)
	else:
		frappe.throw(_("POS Profile or POS Opening Shift is required"))

	if not setup or len(setup) < 2:
		frappe.throw(_("Currency exchange requires at least 2 currencies configured in POS Settings"))

	# Find accounts for both currencies
	source_setup = None
	target_setup = None
	for row in setup:
		if row["currency"] == source_currency:
			source_setup = row
		if row["currency"] == target_currency:
			target_setup = row

	if not source_setup:
		frappe.throw(_("No cash account configured for source currency {0}").format(source_currency))
	if not target_setup:
		frappe.throw(_("No cash account configured for target currency {0}").format(target_currency))

	# Determine company (use first setup's company, they should be same)
	company = source_setup["company"] or frappe.defaults.get_user_default("Company")
	if not company:
		frappe.throw(_("Company is required"))

	# Create POS Currency Exchange document
	exchange_doc = frappe.get_doc({
		"doctype": "POS Currency Exchange",
		"posting_date": today(),
		"posting_time": now().split()[1],
		"user": frappe.session.user,
		"company": company,
		"pos_opening_shift": pos_opening_shift,
		"status": "Submitted",
		"transaction_type": transaction_type,
		"source_currency": source_currency,
		"source_amount": flt(amount),
		"target_currency": target_currency,
		"target_amount": validation["target_amount"],
		"exchange_rate": flt(exchange_rate),
		"source_account": source_setup["cash_account"],
		"target_account": target_setup["cash_account"],
	})

	exchange_doc.insert()
	exchange_doc.submit()

	return {
		"exchange_name": exchange_doc.name,
		"journal_entry": exchange_doc.journal_entry,
		"source_amount": flt(amount),
		"target_amount": validation["target_amount"],
		"exchange_rate": flt(exchange_rate),
		"transaction_type": transaction_type,
	}


@frappe.whitelist()
def get_exchange_history(pos_profile, limit=50):
	"""
	Get currency exchange history for a POS Profile.

	Args:
		pos_profile: POS Profile name
		limit: Maximum number of records to return

	Returns:
		list: Exchange records
	"""
	if not pos_profile:
		return []

	# Get opening shifts for this profile to find related exchanges
	shifts = frappe.get_all(
		"POS Opening Shift",
		filters={"pos_profile": pos_profile},
		pluck="name"
	)

	if not shifts:
		return []

	exchanges = frappe.get_all(
		"POS Currency Exchange",
		filters={
			"pos_opening_shift": ["in", shifts],
			"docstatus": 1,
		},
		fields=[
			"name", "posting_date", "posting_time", "user",
			"company", "source_currency", "source_amount",
			"target_currency", "target_amount", "exchange_rate",
			"journal_entry", "status"
		],
		order_by="posting_date desc, posting_time desc",
		limit=limit
	)

	return exchanges


@frappe.whitelist()
def update_exchange_rates(pos_profile, rates):
	"""
	Update buy/sell rates in POS Currency Setup for a POS Profile.

	Args:
		pos_profile: POS Profile name
		rates: List of dicts with {currency, buy_rate, sell_rate}

	Returns:
		dict: Success status
	"""
	if not pos_profile:
		frappe.throw(_("POS Profile is required"))

	# Check access
	has_access = frappe.db.exists(
		"POS Profile User",
		{"parent": pos_profile, "user": frappe.session.user}
	)
	if not has_access and not frappe.has_permission("POS Settings", "write"):
		frappe.throw(_("You don't have permission to update exchange rates"))

	# Find POS Settings
	settings_name = frappe.db.get_value(
		"POS Settings",
		{"pos_profile": pos_profile},
		"name"
	)
	if not settings_name:
		frappe.throw(_("POS Settings not found for this profile"))

	settings_doc = frappe.get_doc("POS Settings", settings_name)

	# Update rates
	updated = 0
	for rate_update in rates:
		currency = rate_update.get("currency")
		buy_rate = flt(rate_update.get("buy_rate"))
		sell_rate = flt(rate_update.get("sell_rate"))
		for row in settings_doc.currency_setup:
			if row.currency == currency:
				row.buy_rate = buy_rate
				row.sell_rate = sell_rate
				updated += 1
				break

	if updated > 0:
		settings_doc.save()
		frappe.db.commit()

	return {"success": True, "updated": updated}
