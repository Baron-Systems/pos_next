# -*- coding: utf-8 -*-
# Copyright (c) 2024, POS-ABS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _


def validate_item(doc, method):
	"""
	Validate Item doctype
	- Allow items with or without company
	- Items without company are treated as global items (available to all companies)
	- Explicitly set custom_company to empty string for new global items
	"""
	# Only set custom_company for new items, don't modify existing items
	if doc.is_new():
		if not doc.get("custom_company"):
			doc.custom_company = ""


def validate_pos_profile(doc, method):
	"""
	Validate the Allowed Price Lists table on POS Profile.
	- At least one price list must be configured.
	- Only one row may be marked as default.
	- If no default is selected, the first row becomes the default.
	- All price lists must be enabled and marked as selling.
	- Price list currency must match the POS Profile currency.
	- The legacy ``selling_price_list`` field is synced to the default row.
	"""
	allowed_price_lists = doc.get("posa_allowed_price_lists") or []

	# Migrate from legacy single price list field for existing POS Profiles
	if not allowed_price_lists and doc.selling_price_list:
		doc.append(
			"posa_allowed_price_lists",
			{"price_list": doc.selling_price_list, "is_default": 1},
		)
		allowed_price_lists = doc.get("posa_allowed_price_lists")

	if not allowed_price_lists:
		frappe.throw(_("At least one price list must be configured in Allowed Price Lists."))

	# Count and resolve defaults
	default_rows = [row for row in allowed_price_lists if row.get("is_default")]

	if len(default_rows) > 1:
		frappe.throw(_("Only one price list can be marked as default."))

	if not default_rows:
		allowed_price_lists[0].is_default = 1

	default_price_list = None

	for row in allowed_price_lists:
		price_list = row.get("price_list")
		if not price_list:
			frappe.throw(_("Price List is required in Allowed Price Lists."))

		if not frappe.db.exists("Price List", price_list):
			frappe.throw(_("Price List {0} does not exist.").format(price_list))

		price_list_doc = frappe.get_cached_doc("Price List", price_list)

		if not price_list_doc.enabled:
			frappe.throw(_("Price List {0} is disabled.").format(price_list))

		if not price_list_doc.selling:
			frappe.throw(_("Price List {0} must be marked as Selling.").format(price_list))

		if doc.get("currency") and price_list_doc.currency != doc.currency:
			frappe.throw(
				_(
					"Price List {0} uses currency {1} which does not match the POS Profile currency {2}."
				).format(price_list, price_list_doc.currency, doc.currency)
			)

		if row.get("is_default"):
			default_price_list = price_list

	# Sync legacy single price list field to the default
	if default_price_list:
		doc.selling_price_list = default_price_list


@frappe.whitelist()
def item_query(doctype, txt, searchfield, start, page_len, filters):
	"""
	Custom query to filter items by company
	- If company is specified in filters, show:
	  1. Items belonging to that company
	  2. Global items (where custom_company is empty)
	- If no company specified, show all items
	"""
	import json

	# Parse filters if it's a string (when called from frontend)
	if isinstance(filters, str):
		filters = json.loads(filters)

	conditions = ["disabled = 0"]
	values = []

	if txt:
		conditions.append(f"({searchfield} LIKE %s OR item_name LIKE %s)")
		values.extend([f"%{txt}%", f"%{txt}%"])

	company = filters.get("company") if filters else None

	if company:
		# Show items for specific company + global items
		conditions.append("(custom_company = %s OR custom_company IS NULL OR custom_company = '')")
		values.append(company)

	query = f"""
		SELECT name, item_name, item_group
		FROM `tabItem`
		WHERE {' AND '.join(conditions)}
		ORDER BY
			CASE WHEN name LIKE %s THEN 0 ELSE 1 END,
			item_name
		LIMIT %s, %s
	"""

	values.extend([f"{txt}%", start, page_len])

	return frappe.db.sql(query, values)
