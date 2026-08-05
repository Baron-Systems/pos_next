# -*- coding: utf-8 -*-
# Copyright (c) 2024, POS-ABS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import json
import frappe
from frappe import _
from frappe.utils import nowdate, nowtime, get_datetime, flt
from pos_next.api.utilities import get_wallet_payment_modes


@frappe.whitelist()
def get_opening_dialog_data():
	"""Get data required for opening shift dialog"""
	data = {}

	# Get POS Profiles where current user is defined in POS Profile User table
	pos_profiles_data = frappe.db.sql(
		"""
		SELECT DISTINCT p.name, p.company, p.currency, p.warehouse, p.selling_price_list
		FROM `tabPOS Profile` p
		INNER JOIN `tabPOS Profile User` u ON u.parent = p.name
		WHERE p.disabled = 0 AND u.user = %s
		ORDER BY p.name
		""",
		frappe.session.user,
		as_dict=1,
	)

	data["pos_profiles_data"] = pos_profiles_data

	# Derive companies from accessible POS Profiles
	company_names = []
	for profile in pos_profiles_data:
		if profile.company and profile.company not in company_names:
			company_names.append(profile.company)
	data["companies"] = [{"name": c} for c in company_names]

	# Get payment methods for POS profiles (exclude wallet payment methods)
	pos_profiles_list = [p.name for p in pos_profiles_data]

	if pos_profiles_list:
		# Exclude wallet payment modes from opening balance
		wallet_modes = get_wallet_payment_modes()

		payment_filters = {"parent": ["in", pos_profiles_list]}
		if wallet_modes:
			payment_filters["mode_of_payment"] = ["not in", wallet_modes]

		payment_filters["parenttype"] = "POS Profile"
		payment_filters["parentfield"] = "payments"
		data["payments_method"] = frappe.get_all(
			"POS Payment Method",
			filters=payment_filters,
			fields=["*"],
			limit_page_length=0,
			order_by="parent"
		)

		# Set currency from pos profile
		for mode in data["payments_method"]:
			mode["currency"] = frappe.get_cached_value("POS Profile", mode["parent"], "currency")
	else:
		data["payments_method"] = []

	# Include currency setup for profiles with enabled currency exchange
	profile_currency_setups = {}
	if pos_profiles_list:
		for profile_name in pos_profiles_list:
			profile = next((p for p in pos_profiles_data if p.name == profile_name), None)
			company = profile.company if profile else None

			pos_settings = frappe.db.get_value(
				"POS Settings",
				{"pos_profile": profile_name},
				["name", "enable_currency_exchange"],
				as_dict=True,
			)
			if pos_settings and pos_settings.enable_currency_exchange:
				currency_setup = frappe.get_all(
					"POS Currency Setup",
					filters={"parent": pos_settings.name},
					fields=["currency", "cash_account", "buy_rate", "sell_rate"],
					order_by="idx",
				)

				# Exclude the currency whose cash_account matches the Cash mode's default account
				# to avoid duplicate opening balance inputs (Cash payment already covers it)
				cash_mode = (
					frappe.db.get_value("POS Profile", profile_name, "posa_cash_mode_of_payment")
					or "Cash"
				)
				cash_account = None
				if company and cash_mode:
					cash_account = frappe.db.get_value(
						"Mode of Payment Account",
						{"parent": cash_mode, "parenttype": "Mode of Payment", "company": company},
						"default_account",
					)

				if cash_account:
					currency_setup = [
						cs for cs in currency_setup
						if cs.cash_account != cash_account
					]

				profile_currency_setups[profile_name] = currency_setup

	data["profile_currency_setups"] = profile_currency_setups

	return data


@frappe.whitelist()
def check_opening_shift(user=None):
	"""Check if user has an open shift"""
	if not user:
		user = frappe.session.user

	open_shifts = frappe.db.get_all(
		"POS Opening Shift",
		filters={
			"user": user,
			"pos_closing_shift": ["is", "not set"],
			"docstatus": 1,
			"status": "Open",
		},
		fields=["name", "pos_profile", "period_start_date"],
		order_by="period_start_date desc",
	)

	if not open_shifts:
		return None

	# Get the latest open shift
	shift_data = open_shifts[0]
	data = {}
	data["pos_opening_shift"] = frappe.get_doc("POS Opening Shift", shift_data["name"])
	data["pos_profile"] = frappe.get_doc("POS Profile", shift_data["pos_profile"])
	data["company"] = frappe.get_doc("Company", data["pos_profile"].company)

	return data


@frappe.whitelist()
def create_opening_shift(pos_profile, company, balance_details, currency_opening_balances=None):
	"""Create a new POS Opening Shift"""
	balance_details = json.loads(balance_details) if isinstance(balance_details, str) else balance_details
	if currency_opening_balances and isinstance(currency_opening_balances, str):
		currency_opening_balances = json.loads(currency_opening_balances)

	# Check if user already has an open shift
	existing_shift = check_opening_shift(frappe.session.user)
	if existing_shift:
		frappe.throw(_("You already have an open shift: {0}").format(existing_shift["pos_opening_shift"].name))

	new_pos_opening = frappe.get_doc(
		{
			"doctype": "POS Opening Shift",
			"period_start_date": get_datetime(),
			"posting_date": nowdate(),
			"posting_time": nowtime(),
			"user": frappe.session.user,
			"pos_profile": pos_profile,
			"company": company,
			"status": "Open",
		}
	)

	# Add balance details - map opening_amount to amount
	formatted_balance_details = []
	for detail in balance_details:
		formatted_balance_details.append({
			"mode_of_payment": detail.get("mode_of_payment"),
			"amount": detail.get("opening_amount", 0)
		})

	new_pos_opening.set("balance_details", formatted_balance_details)

	# Add currency opening balances if provided
	if currency_opening_balances:
		formatted_currency_balances = []
		for detail in currency_opening_balances:
			formatted_currency_balances.append({
				"currency": detail.get("currency"),
				"account": detail.get("account"),
				"opening_amount": flt(detail.get("opening_amount", 0)),
			})
		new_pos_opening.set("currency_opening_balances", formatted_currency_balances)

	new_pos_opening.insert(ignore_permissions=True)
	new_pos_opening.submit()

	data = {}
	data["pos_opening_shift"] = new_pos_opening.as_dict()
	data["pos_profile"] = frappe.get_doc("POS Profile", pos_profile)
	data["company"] = frappe.get_doc("Company", company)

	return data


@frappe.whitelist()
def get_closing_shift_data(opening_shift):
	"""Get data for closing shift"""
	from pos_next.pos_next.doctype.pos_closing_shift.pos_closing_shift import make_closing_shift_from_opening

	try:
		# Get the opening shift document
		opening_shift_doc = frappe.get_doc("POS Opening Shift", opening_shift)

		# Convert to dict with proper datetime serialization
		opening_shift_dict = opening_shift_doc.as_dict()
		opening_shift_json = json.dumps(opening_shift_dict, default=str)

		# Create closing shift from opening shift (returns a dict)
		closing_data = make_closing_shift_from_opening(opening_shift_json)

		# Ensure datetime values are JSON serializable
		return json.loads(json.dumps(closing_data, default=str))
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Get Closing Shift Data Error")
		frappe.throw(_("Error getting closing shift data: {0}").format(str(e)))


@frappe.whitelist()
def submit_closing_shift(closing_shift):
	"""Submit closing shift"""
	from pos_next.pos_next.doctype.pos_closing_shift.pos_closing_shift import submit_closing_shift as submit_shift

	try:
		# closing_shift is already a JSON string from frontend
		# If it's a dict, convert to JSON string
		if isinstance(closing_shift, dict):
			closing_shift = json.dumps(closing_shift)

		result = submit_shift(closing_shift)
		return {"name": result, "status": "success"}
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Submit Closing Shift Error")
		frappe.throw(_("Error submitting closing shift: {0}").format(str(e)))


@frappe.whitelist()
def get_shift_notes(opening_shift):
	"""Get shift notes for an opening shift"""
	if not opening_shift or not frappe.db.exists("POS Opening Shift", opening_shift):
		return []

	opening = frappe.get_doc("POS Opening Shift", opening_shift)
	return [
		{
			"name": note.name,
			"title": note.title,
			"description": note.description,
			"idx": note.idx,
		}
		for note in opening.get("shift_notes", [])
	]


@frappe.whitelist()
def add_shift_note(opening_shift, title, description=None):
	"""Add a new note to an opening shift"""
	if not opening_shift or not frappe.db.exists("POS Opening Shift", opening_shift):
		frappe.throw(_("لم يتم العثور على الوردية المفتوحة"))

	if not title:
		frappe.throw(_("العنوان مطلوب"))

	opening = frappe.get_doc("POS Opening Shift", opening_shift)
	if opening.status != "Open" or opening.docstatus != 1:
		frappe.throw(_("لا يمكن إضافة ملاحظات إلى وردية مغلقة أو غير مؤكدة"))

	opening.append("shift_notes", {
		"title": title,
		"description": description or "",
	})
	opening.save(ignore_permissions=True)

	return {"status": "success", "name": opening.shift_notes[-1].name}


@frappe.whitelist()
def update_shift_note(note_id, title, description=None):
	"""Update an existing shift note"""
	if not note_id:
		frappe.throw(_("معرف الملاحظة مطلوب"))

	parent = frappe.db.get_value("POS Shift Note", note_id, "parent")
	if not parent or not frappe.db.exists("POS Opening Shift", parent):
		frappe.throw(_("لم يتم العثور على الملاحظة"))

	opening_doc = frappe.get_doc("POS Opening Shift", parent)
	if opening_doc.status != "Open" or opening_doc.docstatus != 1:
		frappe.throw(_("لا يمكن تعديل ملاحظات وردية مغلقة أو غير مؤكدة"))

	for note in opening_doc.get("shift_notes", []):
		if note.name == note_id:
			title = (title or "").strip()
			if not title:
				frappe.throw(_("العنوان مطلوب"))
			note.title = title
			note.description = description or ""
			opening_doc.save(ignore_permissions=True)
			return {"status": "success", "name": note_id}

	frappe.throw(_("لم يتم العثور على الملاحظة"))


@frappe.whitelist()
def delete_shift_note(note_id):
	"""Delete a shift note"""
	if not note_id:
		frappe.throw(_("معرف الملاحظة مطلوب"))

	parent = frappe.db.get_value("POS Shift Note", note_id, "parent")
	if not parent or not frappe.db.exists("POS Opening Shift", parent):
		frappe.throw(_("لم يتم العثور على الملاحظة"))

	opening_doc = frappe.get_doc("POS Opening Shift", parent)
	for note in opening_doc.get("shift_notes", []):
		if note.name == note_id:
			opening_doc.get("shift_notes").remove(note)
			opening_doc.save(ignore_permissions=True)
			return {"status": "success"}

	frappe.throw(_("لم يتم العثور على الملاحظة"))


@frappe.whitelist()
def verify_shift_password(pos_profile, password):
	"""Verify the shift password for a POS Profile"""
	if not pos_profile:
		frappe.throw(_("POS Profile is required"))

	stored_password = frappe.db.get_value(
		"POS Profile", pos_profile, "posa_shift_password"
	)

	if stored_password is None:
		stored_password = 123456

	try:
		entered = int(password)
	except (TypeError, ValueError):
		return {"verified": False, "message": _("Invalid password format")}

	if entered == int(stored_password):
		return {"verified": True}
	return {"verified": False, "message": _("Incorrect shift password")}
