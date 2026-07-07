# -*- coding: utf-8 -*-
# Copyright (c) 2020, Youssef Restom and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import cint
from frappe.model.document import Document


class POSOpeningShift(Document):
    def validate(self):
        self.validate_pos_profile_and_cashier()
        self.set_status()
        self.set_currency_opening_balances()

    def set_currency_opening_balances(self):
        """Auto-populate currency opening balances from POS Settings if enabled."""
        if not self.pos_profile:
            return

        from frappe.utils import cint, flt

        pos_settings = frappe.db.get_value(
            "POS Settings",
            {"pos_profile": self.pos_profile},
            ["name", "enable_currency_exchange"],
            as_dict=True,
        )

        if not pos_settings or not cint(pos_settings.enable_currency_exchange):
            return

        # Fetch currency setup from POS Settings
        currency_setup = frappe.get_all(
            "POS Currency Setup",
            filters={"parent": pos_settings.name},
            fields=["currency", "cash_account"],
            order_by="idx",
        )

        if not currency_setup:
            return

        # Build a map of existing balances (from frontend or previous save)
        existing = {}
        for row in self.get("currency_opening_balances", []):
            existing[row.currency] = row

        # Clear and rebuild to ensure ALL currencies are present
        self.set("currency_opening_balances", [])
        for row in currency_setup:
            opening_amount = flt(existing.get(row.currency, {}).get("opening_amount", 0))
            self.append("currency_opening_balances", {
                "currency": row.currency,
                "account": row.cash_account,
                "opening_amount": opening_amount,
            })

    def validate_pos_profile_and_cashier(self):
        if self.company != frappe.db.get_value("POS Profile", self.pos_profile, "company"):
            frappe.throw(
                _("POS Profile {} does not belongs to company {}".format(self.pos_profile, self.company))
            )

        if not cint(frappe.db.get_value("User", self.user, "enabled")):
            frappe.throw(_("User {} has been disabled. Please select valid user/cashier".format(self.user)))

    def on_submit(self):
        self.set_status(update=True)

    def set_status(self, update=False):
        """Set the status of the opening shift"""
        if self.docstatus == 0:
            status = "Draft"
        elif self.docstatus == 1:
            if self.pos_closing_shift:
                status = "Closed"
            else:
                status = "Open"
        else:
            status = "Cancelled"

        if update:
            frappe.db.set_value("POS Opening Shift", self.name, "status", status)
        else:
            self.status = status
