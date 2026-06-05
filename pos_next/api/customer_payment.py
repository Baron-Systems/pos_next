# Copyright (c) 2025, BrainWise and contributors
# For license information, please see license.txt

"""Customer Payment API - Financial summary, outstanding invoices, and payment creation from POS."""

import frappe
from frappe import _
from frappe.utils import flt, nowdate


@frappe.whitelist()
def get_customer_financial_summary(customer, company=None):
    if not customer:
        frappe.throw(_("Customer is required"))

    params = {"customer": customer, "docstatus": 1}
    cc = "AND company = %(company)s" if company else ""
    if company:
        params["company"] = company

    total_sales = flt(frappe.db.sql("""
        SELECT COALESCE(SUM(grand_total), 0) FROM `tabSales Invoice`
        WHERE customer=%(customer)s AND docstatus=%(docstatus)s {cc}
    """.format(cc=cc), params)[0][0])

    total_payments = flt(frappe.db.sql("""
        SELECT COALESCE(SUM(paid_amount), 0) FROM `tabPayment Entry`
        WHERE party=%(customer)s AND party_type='Customer'
        AND docstatus=1 AND payment_type='Receive' {cc}
    """.format(cc=cc), params)[0][0])

    # Get Outstanding Balance from General Ledger (دفتر الأستاذ العام)
    # This matches the balance shown in Financial Reports > General Ledger
    outstanding_balance = get_general_ledger_balance(customer, company)

    unpaid_count = frappe.db.sql("""
        SELECT COUNT(*) FROM `tabSales Invoice`
        WHERE customer=%(customer)s AND docstatus=%(docstatus)s
        AND outstanding_amount > 0 {cc}
    """.format(cc=cc), params)[0][0]

    currency = frappe.db.get_value("Company", company, "default_currency") if company else \
        frappe.db.get_single_value("Global Defaults", "default_currency")

    return {
        "total_sales": total_sales,
        "total_payments": total_payments,
        "outstanding_balance": outstanding_balance,
        "unpaid_invoice_count": unpaid_count,
        "currency": currency,
    }


def get_general_ledger_balance(customer, company=None):
    """Get customer balance from General Ledger (GL Entry).
    
    This calculates the actual party balance from GL Entries which matches
    the balance shown in Financial Reports > General Ledger (دفتر الأستاذ العام).
    """
    # Get the receivable account for the customer
    receivable_account = None
    if company:
        receivable_account = frappe.db.get_value(
            "Company", company, "default_receivable_account"
        )
    
    # Build GL Entry query
    gl_filters = {
        "party_type": "Customer",
        "party": customer,
        "is_cancelled": 0
    }
    if company:
        gl_filters["company"] = company
    if receivable_account:
        gl_filters["account"] = receivable_account
    
    # Calculate balance: SUM(debit) - SUM(credit)
    result = frappe.db.sql("""
        SELECT 
            COALESCE(SUM(debit), 0) - COALESCE(SUM(credit), 0) as balance
        FROM `tabGL Entry`
        WHERE party_type = %(party_type)s 
        AND party = %(party)s 
        AND is_cancelled = %(is_cancelled)s
        {company_filter}
        {account_filter}
    """.format(
        company_filter="AND company = %(company)s" if company else "",
        account_filter="AND account = %(account)s" if receivable_account else ""
    ), gl_filters)
    
    balance = flt(result[0][0]) if result else 0
    
    # Return actual balance from General Ledger
    # Positive = customer owes (debit balance)
    # Negative = customer overpaid (credit balance - we owe them)
    return balance


@frappe.whitelist()
def get_all_invoices(customer, company=None, limit=300):
    """Get all invoices for customer (paid and unpaid)."""
    if not customer:
        frappe.throw(_("Customer is required"))
    filters = {"customer": customer, "docstatus": 1}
    if company:
        filters["company"] = company
    invoices = frappe.get_all("Sales Invoice", filters=filters,
        fields=["name", "posting_date", "due_date", "grand_total", "outstanding_amount", "status", "currency", "customer_name"],
        order_by="posting_date desc", limit=limit)
    return invoices


@frappe.whitelist()
def get_outstanding_invoices(customer, company=None, limit=300):
    if not customer:
        frappe.throw(_("Customer is required"))
    filters = {"customer": customer, "docstatus": 1, "outstanding_amount": [">", 0]}
    if company:
        filters["company"] = company
    return frappe.get_all("Sales Invoice", filters=filters,
        fields=["name", "posting_date", "due_date", "grand_total", "outstanding_amount", "status", "currency", "customer_name"],
        order_by="posting_date desc", limit=limit)


@frappe.whitelist()
def get_recent_payments(customer, company=None, limit=10):
    if not customer:
        frappe.throw(_("Customer is required"))

    filters = {"party": customer, "party_type": "Customer", "docstatus": 1, "payment_type": "Receive"}
    if company:
        filters["company"] = company

    payments = frappe.get_all("Payment Entry", filters=filters,
        fields=["name", "posting_date", "paid_amount", "mode_of_payment", "reference_no", "remarks"],
        order_by="posting_date desc", limit=limit)

    return payments


@frappe.whitelist()
def create_customer_payment(customer, company, amount, mode_of_payment="Cash", payment_type="Receive", pos_opening_shift=None):
    if not customer:
        frappe.throw(_("Customer is required"))
    if not company:
        frappe.throw(_("Company is required"))

    amount = flt(amount)
    if amount <= 0:
        frappe.throw(_("Payment amount must be greater than zero"))

    # Try to find mode of payment - support both English and Arabic names
    if not frappe.db.exists("Mode of Payment", mode_of_payment):
        # Try common alternatives
        alternatives = []
        if mode_of_payment == "Cash":
            alternatives = ["نقدي", "كاش", "نقداً"]
        elif mode_of_payment == "نقدي":
            alternatives = ["Cash", "كاش", "نقداً"]

        found = False
        for alt in alternatives:
            if frappe.db.exists("Mode of Payment", alt):
                mode_of_payment = alt
                found = True
                break

        if not found:
            frappe.throw(_("Mode of Payment {0} does not exist").format(mode_of_payment))
    if payment_type not in ("Receive", "Pay"):
        frappe.throw(_("Payment type must be either 'Receive' or 'Pay'"))

    from erpnext.accounts.doctype.sales_invoice.sales_invoice import get_bank_cash_account
    account_info = get_bank_cash_account(mode_of_payment, company)
    if not account_info or not account_info.get("account"):
        frappe.throw(_("Could not determine payment account for {0}").format(mode_of_payment))

    company_doc = frappe.get_cached_doc("Company", company)
    if not company_doc.default_receivable_account:
        frappe.throw(_("Default receivable account not set for company {0}").format(company))

    pe = frappe.new_doc("Payment Entry")
    pe.payment_type = payment_type
    pe.posting_date = nowdate()
    pe.party_type = "Customer"
    pe.party = customer
    pe.company = company
    pe.mode_of_payment = mode_of_payment
    pe.reference_no = pos_opening_shift or f"POS-PAY-{frappe.generate_hash(length=8)}"
    pe.reference_date = nowdate()
    pe.posa_pos_opening_shift = pos_opening_shift

    if payment_type == "Receive":
        # Receiving from customer - allocate against outstanding invoices
        pe.paid_from = company_doc.default_receivable_account
        pe.paid_to = account_info.get("account")
        pe.paid_amount = amount
        pe.received_amount = amount
        pe.remarks = _("Payment from POS - {0}").format(mode_of_payment)

        outstanding_invoices = frappe.get_all("Sales Invoice",
            filters={"customer": customer, "company": company, "docstatus": 1, "outstanding_amount": [">", 0]},
            fields=["name", "outstanding_amount", "grand_total", "posting_date"],
            order_by="posting_date asc")

        allocated = []
        if outstanding_invoices:
            remaining = amount
            for inv in outstanding_invoices:
                if remaining <= 0.005:
                    break
                alloc = min(remaining, flt(inv.outstanding_amount))
                if alloc <= 0:
                    continue
                pe.append("references", {
                    "reference_doctype": "Sales Invoice",
                    "reference_name": inv.name,
                    "total_amount": inv.grand_total,
                    "outstanding_amount": inv.outstanding_amount,
                    "allocated_amount": alloc,
                })
                allocated.append({"invoice": inv.name, "amount": alloc})
                remaining -= alloc
    else:
        # Paying to customer - no invoice allocation
        pe.paid_from = account_info.get("account")
        pe.paid_to = company_doc.default_receivable_account
        pe.paid_amount = amount
        pe.received_amount = amount
        pe.remarks = _("Payment to Customer from POS - {0}").format(mode_of_payment)
        allocated = []

    # Validate outstanding amounts are still current before inserting
    # to prevent "allocated amount > outstanding amount" errors
    if outstanding_invoices and payment_type == "Receive":
        refs_to_remove = []
        for ref in pe.get("references", []):
            if ref.reference_doctype == "Sales Invoice":
                current_outstanding = frappe.db.get_value(
                    "Sales Invoice", ref.reference_name, "outstanding_amount"
                )
                if flt(ref.allocated_amount) > flt(current_outstanding) + 0.01:
                    # Adjust to current outstanding amount
                    ref.allocated_amount = flt(current_outstanding)
                    ref.outstanding_amount = flt(current_outstanding)
                # Mark for removal if fully paid already
                if flt(ref.allocated_amount) <= 0.01:
                    refs_to_remove.append(ref)
        # Remove references that are no longer needed
        for ref in refs_to_remove:
            pe.references.remove(ref)

    pe.flags.ignore_permissions = True
    pe.insert()
    pe.submit()
    frappe.db.commit()

    summary = get_customer_financial_summary(customer, company)
    return {
        "payment_entry": pe.name,
        "allocated_invoices": allocated,
        "updated_summary": summary,
    }


@frappe.whitelist()
def get_invoice_items(invoice_name):
    """Get items for a specific Sales Invoice."""
    if not invoice_name:
        frappe.throw(_("Invoice name is required"))
    if not frappe.db.exists("Sales Invoice", invoice_name):
        frappe.throw(_("Invoice {0} not found").format(invoice_name))
    return frappe.get_all("Sales Invoice Item",
        filters={"parent": invoice_name},
        fields=["item_code", "item_name", "qty", "rate", "amount", "uom", "description"],
        order_by="idx asc")
