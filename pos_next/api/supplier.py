# Copyright (c) 2025, BrainWise and contributors
# For license information, please see license.txt

"""Supplier API - Create supplier and payment from POS."""

import frappe
from frappe import _
from frappe.utils import flt, nowdate


@frappe.whitelist()
def create_supplier(supplier_name, mobile_no=None, email_id=None, supplier_group=None, supplier_type="Company"):
    """Create a new Supplier."""
    if not supplier_name:
        frappe.throw(_("Supplier Name is required"))

    # Check if supplier already exists
    existing = frappe.db.get_value("Supplier", {"supplier_name": supplier_name}, "name")
    if existing:
        frappe.throw(_("Supplier '{0}' already exists").format(supplier_name))

    # Resolve supplier_group: use provided, or fallback to first valid leaf group
    if not supplier_group or not frappe.db.exists("Supplier Group", supplier_group):
        supplier_group = frappe.db.get_value(
            "Supplier Group", {"is_group": 0}, "name", order_by="name asc"
        ) or "All Supplier Groups"

    supplier = frappe.get_doc({
        "doctype": "Supplier",
        "supplier_name": supplier_name,
        "supplier_group": supplier_group,
        "supplier_type": supplier_type,
        "mobile_no": mobile_no,
        "email_id": email_id,
    })
    supplier.insert(ignore_permissions=True)
    supplier.reload()

    return {
        "name": supplier.name,
        "supplier_name": supplier.supplier_name,
        "mobile_no": supplier.mobile_no,
    }


@frappe.whitelist()
def get_supplier_financial_summary(supplier, company=None):
    """Get supplier financial summary."""
    if not supplier:
        frappe.throw(_("Supplier is required"))

    params = {"supplier": supplier, "docstatus": 1}
    cc = "AND company = %(company)s" if company else ""
    if company:
        params["company"] = company

    total_purchases = flt(frappe.db.sql("""
        SELECT COALESCE(SUM(grand_total), 0) FROM `tabPurchase Invoice`
        WHERE supplier=%(supplier)s AND docstatus=%(docstatus)s {cc}
    """.format(cc=cc), params)[0][0])

    total_payments = flt(frappe.db.sql("""
        SELECT COALESCE(SUM(paid_amount), 0) FROM `tabPayment Entry`
        WHERE party=%(supplier)s AND party_type='Supplier'
        AND docstatus=1 AND payment_type='Pay' {cc}
    """.format(cc=cc), params)[0][0])

    # Outstanding balance from GL
    outstanding_balance = get_supplier_gl_balance(supplier, company)

    currency = frappe.db.get_value("Company", company, "default_currency") if company else \
        frappe.db.get_single_value("Global Defaults", "default_currency")

    return {
        "total_purchases": total_purchases,
        "total_payments": total_payments,
        "outstanding_balance": outstanding_balance,
        "currency": currency,
    }


def get_supplier_gl_balance(supplier, company=None):
    """Get supplier balance from General Ledger."""
    payable_account = None
    if company:
        payable_account = frappe.db.get_value("Company", company, "default_payable_account")

    gl_filters = {
        "party_type": "Supplier",
        "party": supplier,
        "is_cancelled": 0
    }
    if company:
        gl_filters["company"] = company
    if payable_account:
        gl_filters["account"] = payable_account

    result = frappe.db.sql("""
        SELECT COALESCE(SUM(credit), 0) - COALESCE(SUM(debit), 0) as balance
        FROM `tabGL Entry`
        WHERE party_type = %(party_type)s
        AND party = %(party)s
        AND is_cancelled = %(is_cancelled)s
        {company_filter}
        {account_filter}
    """.format(
        company_filter="AND company = %(company)s" if company else "",
        account_filter="AND account = %(account)s" if payable_account else ""
    ), gl_filters)

    return flt(result[0][0]) if result else 0


@frappe.whitelist()
def create_supplier_payment(supplier, company, amount, mode_of_payment="Cash", payment_type="Pay", pos_opening_shift=None):
    """Create a Payment Entry for a supplier."""
    if not supplier:
        frappe.throw(_("Supplier is required"))
    if not company:
        frappe.throw(_("Company is required"))

    amount = flt(amount)
    if amount <= 0:
        frappe.throw(_("Amount must be greater than zero"))

    # Get payable account
    payable_account = frappe.db.get_value("Company", company, "default_payable_account")
    if not payable_account:
        frappe.throw(_("Default Payable Account not set for Company {0}").format(company))

    # Get mode of payment account
    mode_account = frappe.db.get_value("Mode of Payment Account", {"parent": mode_of_payment, "company": company}, "default_account")
    if not mode_account:
        # Fallback: try to get from mode of payment itself or use cash account
        mode_account = frappe.db.get_value("Company", company, "default_cash_account")
    if not mode_account:
        frappe.throw(_("Payment account not found for mode of payment {0}").format(mode_of_payment))

    pe = frappe.get_doc({
        "doctype": "Payment Entry",
        "payment_type": payment_type,
        "party_type": "Supplier",
        "party": supplier,
        "company": company,
        "paid_amount": amount,
        "received_amount": amount,
        "paid_from": mode_account if payment_type == "Pay" else payable_account,
        "paid_to": payable_account if payment_type == "Pay" else mode_account,
        "mode_of_payment": mode_of_payment,
        "posting_date": nowdate(),
        "reference_no": pos_opening_shift or f"POS-SUP-{frappe.generate_hash(length=8)}",
        "reference_date": nowdate(),
        "pos_opening_shift": pos_opening_shift,
    })

    pe.insert(ignore_permissions=True)
    pe.submit()

    return {
        "payment_entry": pe.name,
        "amount": amount,
        "supplier": supplier,
    }
