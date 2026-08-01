# Copyright (c) 2020, Youssef Restom and contributors
# For license information, please see license.txt

import json
from collections import defaultdict

import frappe
from erpnext.accounts.doctype.pos_invoice_merge_log.pos_invoice_merge_log import (
    consolidate_pos_invoices,
)
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


def get_base_value(doc, fieldname, base_fieldname=None, conversion_rate=None):
    """Return the value for a field in company currency."""

    base_fieldname = base_fieldname or f"base_{fieldname}"
    base_value = doc.get(base_fieldname)

    if base_value not in (None, ""):
        return flt(base_value)

    value = doc.get(fieldname)
    if value in (None, ""):
        return 0

    if conversion_rate is None:
        conversion_rate = (
            doc.get("conversion_rate")
            or doc.get("exchange_rate")
            or doc.get("target_exchange_rate")
            or doc.get("plc_conversion_rate")
            or 1
        )

    return flt(value) * flt(conversion_rate or 1)


class POSClosingShift(Document):
    def validate(self):
        user = frappe.get_all(
            "POS Closing Shift",
            filters={
                "user": self.user,
                "docstatus": 1,
                "pos_opening_shift": self.pos_opening_shift,
                "name": ["!=", self.name],
            },
        )

        if user:
            frappe.throw(
                _(
                    "POS Closing Shift <strong>already exists</strong> against {0} between selected period".format(
                        frappe.bold(self.user)
                    )
                ),
                title=_("Invalid Period"),
            )

        if frappe.db.get_value("POS Opening Shift", self.pos_opening_shift, "status") != "Open":
            frappe.throw(
                _("Selected POS Opening Shift should be open."),
                title=_("Invalid Opening Entry"),
            )
        self.update_payment_reconciliation()
        self.update_currency_closing_balances()

    def update_currency_closing_balances(self):
        """Update difference values in Currency Closing Balances child table."""
        precision = frappe.get_cached_value("System Settings", None, "currency_precision") or 3
        for d in self.get("currency_closing_balances", []):
            d.difference = flt(d.closing_amount or 0, precision) - flt(d.expected_amount or 0, precision)
            d.net_exchange = flt(d.receipts or 0, precision) - flt(d.payments or 0, precision)

    def update_payment_reconciliation(self):
        # update the difference values in Payment Reconciliation child table
        # get default precision for site
        precision = frappe.get_cached_value("System Settings", None, "currency_precision") or 3
        for d in self.payment_reconciliation:
            d.difference = +flt(d.closing_amount, precision) - flt(d.expected_amount, precision)

    def on_submit(self):
        opening_entry = frappe.get_doc("POS Opening Shift", self.pos_opening_shift)
        opening_entry.pos_closing_shift = self.name
        opening_entry.set_status()
        self.delete_draft_invoices()
        opening_entry.save()
        # link invoices with this closing shift so ERPNext can block edits
        self._set_closing_entry_invoices()

    def on_cancel(self):
        if frappe.db.exists("POS Opening Shift", self.pos_opening_shift):
            opening_entry = frappe.get_doc("POS Opening Shift", self.pos_opening_shift)
            if opening_entry.pos_closing_shift == self.name:
                opening_entry.pos_closing_shift = ""
                opening_entry.set_status()
                opening_entry.save()
        # remove links from invoices so they can be cancelled
        self._clear_closing_entry_invoices()

    def _set_closing_entry_invoices(self):
        """Set `pos_closing_entry` on linked invoices."""
        for d in self.pos_transactions:
            invoice = d.get("sales_invoice") or d.get("pos_invoice")
            if not invoice:
                continue
            doctype = "Sales Invoice" if d.get("sales_invoice") else "POS Invoice"
            if frappe.db.has_column(doctype, "pos_closing_entry"):
                frappe.db.set_value(doctype, invoice, "pos_closing_entry", self.name)

    def _clear_closing_entry_invoices(self):
        """Clear closing shift links, cancel merge logs and cancel consolidated sales invoices."""
        consolidated_sales_invoices = set()
        for d in self.pos_transactions:
            pos_invoice = d.get("pos_invoice")
            sales_invoice = d.get("sales_invoice")
            if pos_invoice:
                if frappe.db.has_column("POS Invoice", "pos_closing_entry"):
                    frappe.db.set_value("POS Invoice", pos_invoice, "pos_closing_entry", None)

                merge_logs = frappe.get_all(
                    "POS Invoice Merge Log",
                    filters={"pos_invoice": pos_invoice},
                    pluck="name",
                )
                for log in merge_logs:
                    log_doc = frappe.get_doc("POS Invoice Merge Log", log)
                    for field in (
                        "consolidated_invoice",
                        "consolidated_credit_note",
                    ):
                        si = log_doc.get(field)
                        if si:
                            consolidated_sales_invoices.add(si)
                    if log_doc.docstatus == 1:
                        log_doc.cancel()
                    frappe.delete_doc("POS Invoice Merge Log", log_doc.name, force=1)

                if frappe.db.has_column("POS Invoice", "consolidated_invoice"):
                    frappe.db.set_value("POS Invoice", pos_invoice, "consolidated_invoice", None)

                if frappe.db.has_column("POS Invoice", "status"):
                    pos_doc = frappe.get_doc("POS Invoice", pos_invoice)
                    pos_doc.set_status(update=True)

            if sales_invoice:
                if frappe.db.has_column("Sales Invoice", "pos_closing_entry"):
                    frappe.db.set_value("Sales Invoice", sales_invoice, "pos_closing_entry", None)
                if self._is_consolidated_sales_invoice(sales_invoice):
                    consolidated_sales_invoices.add(sales_invoice)

        for si in consolidated_sales_invoices:
            if frappe.db.exists("Sales Invoice", si):
                si_doc = frappe.get_doc("Sales Invoice", si)
                if si_doc.docstatus == 1:
                    si_doc.cancel()

    def _is_consolidated_sales_invoice(self, sales_invoice):
        """Return True if the Sales Invoice was generated by consolidating POS Invoices."""

        if not sales_invoice:
            return False

        if frappe.db.exists(
            "POS Invoice Merge Log", {"consolidated_invoice": sales_invoice}
        ):
            return True

        return bool(
            frappe.db.exists(
                "POS Invoice Merge Log", {"consolidated_credit_note": sales_invoice}
            )
        )

    def delete_draft_invoices(self):
        if frappe.get_value("POS Profile", self.pos_profile, "posa_allow_delete"):
            doctype = "Sales Invoice"
            data = frappe.db.sql(
                f"""
		select
		    name
		from
		    `tab{doctype}`
		where
		    docstatus = 0 and posa_is_printed = 0 and posa_pos_opening_shift = %s
		""",
                (self.pos_opening_shift),
                as_dict=1,
            )

            for invoice in data:
                frappe.delete_doc(doctype, invoice.name, force=1)

    @frappe.whitelist()
    def get_payment_reconciliation_details(self):
        company_currency = frappe.get_cached_value(
            "Company", self.company, "default_currency"
        )

        sales_breakdown = defaultdict(float)
        net_breakdown = defaultdict(float)
        payment_breakdown = {}

        def update_payment_breakdown(mode_of_payment, base_amount=0, currency=None, amount=0):
            if not mode_of_payment:
                return

            row = payment_breakdown.setdefault(
                mode_of_payment,
                {"base": 0.0, "currencies": defaultdict(float)},
            )
            row["base"] += flt(base_amount)
            if currency:
                row["currencies"][currency] += flt(amount)

        cash_mode_of_payment = (
            frappe.db.get_value(
                "POS Profile", self.pos_profile, "posa_cash_mode_of_payment"
            )
            or "Cash"
        )

        for row in self.get("pos_transactions", []):
            invoice = row.get("sales_invoice") or row.get("pos_invoice")
            if not invoice:
                continue

            doctype = "Sales Invoice" if row.get("sales_invoice") else "POS Invoice"
            if not frappe.db.exists(doctype, invoice):
                continue

            invoice_doc = frappe.get_cached_doc(doctype, invoice)
            currency = invoice_doc.get("currency") or company_currency
            conversion_rate = (
                invoice_doc.get("conversion_rate")
                or invoice_doc.get("exchange_rate")
                or invoice_doc.get("target_exchange_rate")
                or invoice_doc.get("plc_conversion_rate")
                or 1
            )

            sales_breakdown[currency] += flt(invoice_doc.get("grand_total") or 0)
            net_breakdown[currency] += flt(invoice_doc.get("net_total") or 0)

            for payment in invoice_doc.get("payments", []):
                update_payment_breakdown(
                    payment.mode_of_payment,
                    get_base_value(payment, "amount", "base_amount", conversion_rate),
                    currency,
                    payment.amount,
                )

            change_amount = invoice_doc.get("change_amount") or 0
            if change_amount:
                update_payment_breakdown(
                    cash_mode_of_payment,
                    -get_base_value(
                        invoice_doc,
                        "change_amount",
                        "base_change_amount",
                        conversion_rate,
                    ),
                    currency,
                    -change_amount,
                )

        for row in self.get("pos_payments", []):
            payment_entry = row.get("payment_entry")
            if not payment_entry or not frappe.db.exists("Payment Entry", payment_entry):
                continue

            payment_doc = frappe.get_cached_doc("Payment Entry", payment_entry)
            currency = (
                payment_doc.get("paid_from_account_currency")
                or payment_doc.get("paid_to_account_currency")
                or payment_doc.get("party_account_currency")
                or payment_doc.get("currency")
                or company_currency
            )
            base_amount = flt(payment_doc.get("base_paid_amount") or 0)
            paid_amount = flt(payment_doc.get("paid_amount") or 0)
            # Pay (outflow) should reduce cash; Receive (inflow) should increase cash
            if payment_doc.payment_type == "Pay":
                base_amount = -base_amount
                paid_amount = -paid_amount
            mode_of_payment = row.get("mode_of_payment") or payment_doc.get("mode_of_payment")

            update_payment_breakdown(mode_of_payment, base_amount, currency, paid_amount)

        mode_summaries = []
        payment_breakdown_copy = payment_breakdown.copy()
        for detail in self.get("payment_reconciliation", []):
            mop = detail.mode_of_payment
            breakdown = payment_breakdown_copy.pop(mop, None)
            currencies = []
            if breakdown:
                currencies = [
                    frappe._dict({"currency": currency, "amount": amount})
                    for currency, amount in sorted(breakdown["currencies"].items())
                    if amount
                ]

            base_total = flt(detail.expected_amount) - flt(detail.opening_amount)

            mode_summaries.append(
                frappe._dict(
                    {
                        "mode_of_payment": mop,
                        "base_amount": base_total,
                        "opening_amount": flt(detail.opening_amount),
                        "expected_amount": flt(detail.expected_amount),
                        "difference": flt(detail.difference),
                        "currency_breakdown": currencies,
                    }
                )
            )

        for mop, breakdown in payment_breakdown_copy.items():
            mode_summaries.append(
                frappe._dict(
                    {
                        "mode_of_payment": mop,
                        "base_amount": breakdown["base"],
                        "opening_amount": 0,
                        "expected_amount": breakdown["base"],
                        "difference": 0,
                        "currency_breakdown": [
                            frappe._dict({"currency": currency, "amount": amount})
                            for currency, amount in sorted(breakdown["currencies"].items())
                            if amount
                        ],
                    }
                )
            )

        sales_currency_breakdown = [
            frappe._dict({"currency": currency, "amount": amount})
            for currency, amount in sorted(sales_breakdown.items())
            if amount
        ]
        net_currency_breakdown = [
            frappe._dict({"currency": currency, "amount": amount})
            for currency, amount in sorted(net_breakdown.items())
            if amount
        ]

        return frappe.render_template(
            "pos_next/pos_next/doctype/pos_closing_shift/closing_shift_details.html",
            {
                "data": self,
                "currency": company_currency,
                "company_currency": company_currency,
                "mode_summaries": mode_summaries,
                "sales_currency_breakdown": sales_currency_breakdown,
                "net_currency_breakdown": net_currency_breakdown,
            },
        )


@frappe.whitelist()
def get_cashiers(doctype, txt, searchfield, start, page_len, filters):
    cashiers_list = frappe.get_all("POS Profile User", filters=filters, fields=["user"])
    result = []
    for cashier in cashiers_list:
        user_email = frappe.get_value("User", cashier.user, "email")
        if user_email:
            # Return list of tuples in format (value, label) where value is user ID and label shows both ID and email
            result.append([cashier.user, f"{cashier.user} ({user_email})"])
    return result


@frappe.whitelist()
def get_pos_invoices(pos_opening_shift, doctype=None):
    if not doctype:
        pos_profile = frappe.db.get_value("POS Opening Shift", pos_opening_shift, "pos_profile")
        use_pos_invoice = False
        doctype = "POS Invoice" if use_pos_invoice else "Sales Invoice"
    submit_printed_invoices(pos_opening_shift, doctype)
    cond = " and ifnull(consolidated_invoice,'') = ''" if doctype == "POS Invoice" else ""
    data = frappe.db.sql(
        f"""
	select
		name
	from
		`tab{doctype}`
	where
		docstatus = 1 and posa_pos_opening_shift = %s{cond}
	""",
        (pos_opening_shift),
        as_dict=1,
    )

    data = [frappe.get_doc(doctype, d.name).as_dict() for d in data]

    return data


@frappe.whitelist()
def get_payments_entries(pos_opening_shift):
    # Search by reference_no (legacy) OR posa_pos_opening_shift field
    # Include both Receive (customer) and Pay (supplier) payment types
    filters = {
        "docstatus": 1,
    }
    
    # Build OR condition for reference_no or posa_pos_opening_shift
    or_filters = [
        ["reference_no", "=", pos_opening_shift],
    ]
    
    # Check if posa_pos_opening_shift field exists
    if frappe.db.has_column("Payment Entry", "posa_pos_opening_shift"):
        or_filters.append(["posa_pos_opening_shift", "=", pos_opening_shift])
    
    return frappe.get_all(
        "Payment Entry",
        filters=filters,
        or_filters=or_filters,
        fields=[
            "name",
            "mode_of_payment",
            "paid_amount",
            "base_paid_amount",
            "target_exchange_rate",
            "reference_no",
            "posting_date",
            "party",
            "party_type",
            "payment_type",
        ],
    )


def _get_cash_mode_of_payment(pos_profile):
    """Get the cash mode of payment for a POS profile."""
    cash_mode = frappe.get_value("POS Profile", pos_profile, "posa_cash_mode_of_payment")
    return cash_mode or "Cash"


def _aggregate_payment(payments, mode_of_payment, amount, opening_amount=0):
    """Add or update payment amount for a mode of payment."""
    for pay in payments:
        if pay.mode_of_payment == mode_of_payment:
            pay.expected_amount += flt(amount)
            return
    payments.append(frappe._dict({
        "mode_of_payment": mode_of_payment,
        "opening_amount": opening_amount,
        "expected_amount": flt(amount) + opening_amount,
    }))


def _aggregate_tax(taxes, account_head, rate, amount):
    """Add or update tax amount for an account."""
    for tax in taxes:
        if tax.account_head == account_head and tax.rate == rate:
            tax.amount += amount
            return
    taxes.append(frappe._dict({
        "account_head": account_head,
        "rate": rate,
        "amount": amount,
    }))


def _get_invoice_payment_status(invoice, tolerance=0.01):
    """Classify invoice settlement status based on paid/outstanding amounts.

    Returns:
        str: 'Cash' (fully paid/settled), 'Debt' (unpaid), or 'Partial Payment'.
    """
    paid = abs(flt(invoice.get("paid_amount", 0)))
    outstanding = abs(flt(invoice.get("outstanding_amount", 0)))

    if outstanding <= tolerance:
        return "Cash"
    if paid <= tolerance:
        return "Debt"
    return "Partial Payment"


def _process_invoice(invoice, invoice_field, company_currency, cash_mode, payments, taxes, summary):
    """Process a single invoice and update aggregates."""
    conversion_rate = invoice.get("conversion_rate")
    is_return = invoice.get("is_return", 0)

    base_grand_total = get_base_value(invoice, "grand_total", "base_grand_total", conversion_rate)
    base_net_total = get_base_value(invoice, "net_total", "base_net_total", conversion_rate)

    # Build transaction record
    transaction = frappe._dict({
        invoice_field: invoice.name,
        "posting_date": invoice.posting_date,
        "grand_total": base_grand_total,
        "transaction_currency": invoice.get("currency") or company_currency,
        "transaction_amount": flt(invoice.get("grand_total")),
        "customer": invoice.customer,
        "is_return": is_return,
        "return_against": invoice.get("return_against") if is_return else None,
        "payment_status": _get_invoice_payment_status(invoice),
    })

    # Update summary totals
    summary["grand_total"] += base_grand_total
    summary["net_total"] += base_net_total
    summary["total_quantity"] += flt(invoice.total_qty)

    if is_return:
        summary["returns_total"] += abs(base_grand_total)
        summary["returns_count"] += 1
    else:
        summary["sales_total"] += base_grand_total
        summary["sales_count"] += 1

    # Process taxes
    for t in invoice.taxes:
        tax_amount = get_base_value(t, "tax_amount", "base_tax_amount", conversion_rate)
        _aggregate_tax(taxes, t.account_head, t.rate, tax_amount)

    # Process payments
    for p in invoice.payments:
        amount = get_base_value(p, "amount", "base_amount", conversion_rate)
        if p.mode_of_payment == cash_mode:
            amount -= get_base_value(invoice, "change_amount", "base_change_amount", conversion_rate)
        _aggregate_payment(payments, p.mode_of_payment, amount)

    return transaction


def _get_currency_exchange_operations(opening_shift_name):
    """Get POS Currency Exchange transactions for the opening shift."""
    if not opening_shift_name:
        return []

    exchanges = frappe.get_all(
        "POS Currency Exchange",
        filters={
            "pos_opening_shift": opening_shift_name,
            "docstatus": 1,
        },
        fields=[
            "name",
            "posting_date",
            "posting_time",
            "source_currency",
            "source_amount",
            "target_currency",
            "target_amount",
            "exchange_rate",
            "status",
            "transaction_type",
        ],
        order_by="posting_date desc, posting_time desc",
    )
    return exchanges


def _build_currency_closing_balances(opening_shift, company_currency=None):
    """Build currency closing balances from opening shift currency balances and exchange transactions."""
    currency_balances = {}

    # 1. Seed from opening shift currency balances
    for detail in opening_shift.get("currency_opening_balances", []):
        currency = detail.get("currency")
        account = detail.get("account")
        opening_amount = flt(detail.get("opening_amount"))
        currency_balances[currency] = {
            "currency": currency,
            "account": account,
            "opening_amount": opening_amount,
            "receipts": 0,
            "payments": 0,
            "net_exchange": 0,
            "expected_amount": opening_amount,
            "closing_amount": None,
            "difference": 0,
        }

    # 1b. Ensure company currency is always tracked (even if not in currency_opening_balances)
    # so that exchange transactions affecting it are properly recorded
    if company_currency and company_currency not in currency_balances:
        currency_balances[company_currency] = {
            "currency": company_currency,
            "account": "",
            "opening_amount": 0,
            "receipts": 0,
            "payments": 0,
            "net_exchange": 0,
            "expected_amount": 0,
            "closing_amount": None,
            "difference": 0,
        }

    # 2. Aggregate POS Currency Exchange transactions for this shift
    opening_shift_name = opening_shift.get("name")
    if opening_shift_name:
        exchanges = frappe.get_all(
            "POS Currency Exchange",
            filters={
                "pos_opening_shift": opening_shift_name,
                "docstatus": 1,
            },
            fields=["source_currency", "source_amount", "target_currency", "target_amount", "transaction_type"],
        )
        for ex in exchanges:
            transaction_type = ex.get("transaction_type") or "Buy"
            src = ex.get("source_currency")
            tgt = ex.get("target_currency")
            src_amt = flt(ex.get("source_amount"))
            tgt_amt = flt(ex.get("target_amount"))

            if transaction_type == "Sell":
                # Sell: we give away source currency, receive target currency
                if src in currency_balances:
                    currency_balances[src]["payments"] += src_amt
                if tgt in currency_balances:
                    currency_balances[tgt]["receipts"] += tgt_amt
            else:
                # Buy: we receive source currency, give away target currency
                if src in currency_balances:
                    currency_balances[src]["receipts"] += src_amt
                if tgt in currency_balances:
                    currency_balances[tgt]["payments"] += tgt_amt

    # 3. Calculate net_exchange and expected_amount for each currency
    for cb in currency_balances.values():
        cb["net_exchange"] = cb["receipts"] - cb["payments"]
        cb["expected_amount"] = cb["opening_amount"] + cb["net_exchange"]

    return list(currency_balances.values())


@frappe.whitelist()
def make_closing_shift_from_opening(opening_shift):
    opening_shift = json.loads(opening_shift)
    doctype = "Sales Invoice"
    invoice_field = "sales_invoice"

    submit_printed_invoices(opening_shift.get("name"), doctype)

    # Initialize closing shift document
    closing_shift = frappe.new_doc("POS Closing Shift")
    closing_shift.update({
        "pos_opening_shift": opening_shift.get("name"),
        "period_start_date": opening_shift.get("period_start_date"),
        "period_end_date": frappe.utils.get_datetime(),
        "pos_profile": opening_shift.get("pos_profile"),
        "user": opening_shift.get("user"),
        "company": opening_shift.get("company"),
    })

    company_currency = frappe.get_cached_value("Company", closing_shift.company, "default_currency")
    cash_mode = _get_cash_mode_of_payment(opening_shift.get("pos_profile"))

    # Initialize collections
    payments = []
    taxes = []
    pos_transactions = []

    # Summary for tracking totals
    summary = {
        "grand_total": 0, "net_total": 0, "total_quantity": 0,
        "returns_total": 0, "returns_count": 0,
        "sales_total": 0, "sales_count": 0,
    }

    # Add opening balances to payments
    for detail in opening_shift.get("balance_details", []):
        opening_amount = flt(detail.get("amount"))
        payments.append(frappe._dict({
            "mode_of_payment": detail.get("mode_of_payment"),
            "opening_amount": opening_amount,
            "expected_amount": opening_amount,
        }))

    # Process invoices
    invoices = get_pos_invoices(opening_shift.get("name"), doctype)
    for invoice in invoices:
        txn = _process_invoice(invoice, invoice_field, company_currency, cash_mode, payments, taxes, summary)
        pos_transactions.append(txn)

    # Process payment entries
    pos_payments_table = []
    for py in get_payments_entries(opening_shift.get("name")):
        # Pay (outflow) should be negative; Receive (inflow) should be positive
        signed_amount = flt(py.paid_amount) * (1 if py.payment_type == "Receive" else -1)
        pos_payments_table.append(frappe._dict({
            "payment_entry": py.name,
            "mode_of_payment": py.mode_of_payment,
            "paid_amount": signed_amount,
            "posting_date": py.posting_date,
            "customer": py.party,
            "payment_type": py.payment_type,
            "party_type": py.party_type,
        }))
        amount = get_base_value(py, "paid_amount", "base_paid_amount")
        if py.payment_type == "Pay":
            amount = -amount
        _aggregate_payment(payments, py.mode_of_payment, amount)

    # Update closing shift with totals
    closing_shift.grand_total = summary["grand_total"]
    closing_shift.net_total = summary["net_total"]
    closing_shift.total_quantity = summary["total_quantity"]

    # Build currency closing balances (before setting child tables so we can adjust payments)
    currency_closing_balances = _build_currency_closing_balances(opening_shift, company_currency)

    # Company currency cash is the same as the main cash box
    # Merge company currency net exchange into cash payment reconciliation
    # and remove company currency from currency reconciliation
    if company_currency:
        company_cb = next((cb for cb in currency_closing_balances if cb["currency"] == company_currency), None)
        if company_cb:
            company_net_exchange = flt(company_cb.get("net_exchange", 0))
            if company_net_exchange != 0:
                for pay in payments:
                    if pay.mode_of_payment == cash_mode:
                        pay.expected_amount = flt(pay.expected_amount) + company_net_exchange
                        break
        # Remove company currency from currency reconciliation
        currency_closing_balances = [cb for cb in currency_closing_balances if cb["currency"] != company_currency]

    # Set child tables (must be AFTER payment adjustments so modified values are captured)
    closing_shift.set("pos_transactions", [
        {k: v for k, v in txn.items() if k not in ("is_return", "return_against")}
        for txn in pos_transactions
    ])
    closing_shift.set("payment_reconciliation", payments)
    closing_shift.set("taxes", taxes)
    closing_shift.set("pos_payments", pos_payments_table)
    closing_shift.set("currency_closing_balances", currency_closing_balances)

    # Copy shift notes from opening shift to closing shift
    opening_notes = opening_shift.get("shift_notes", []) or []
    closing_shift.set("shift_notes", [
        {"title": note.get("title"), "description": note.get("description", "")}
        for note in opening_notes
    ])

    # Build response with display-only fields
    result = closing_shift.as_dict()
    # Enrich pos_payments with payment_type for display separation
    for p in result.get("pos_payments", []):
        entry = next((py for py in get_payments_entries(opening_shift.get("name")) if py.name == p.get("payment_entry")), None)
        if entry:
            p["payment_type"] = entry.payment_type
            # party_type already correctly set in pos_payments_table above

    # Get currency exchange operations for display
    currency_exchange_operations = _get_currency_exchange_operations(opening_shift.get("name"))

    result.update({
        "returns_total": summary["returns_total"],
        "returns_count": summary["returns_count"],
        "sales_total": summary["sales_total"],
        "sales_count": summary["sales_count"],
        "pos_transactions": pos_transactions,  # Include return info for display
        "currency_exchange_operations": currency_exchange_operations,
    })

    return result


@frappe.whitelist()
def submit_closing_shift(closing_shift):
    closing_shift = json.loads(closing_shift)
    closing_shift_doc = frappe.get_doc(closing_shift)
    for row in closing_shift_doc.get("pos_payments", []):
        if not row.payment_entry:
            continue
        payment_data = frappe.db.get_value(
            "Payment Entry",
            row.payment_entry,
            ["payment_type", "party_type", "party"],
            as_dict=True,
        )
        if not payment_data:
            frappe.throw(_("Payment Entry {0} was not found").format(row.payment_entry))
        row.payment_type = payment_data.payment_type
        row.party_type = payment_data.party_type
        row.customer = payment_data.party
    closing_shift_doc.flags.ignore_permissions = True
    closing_shift_doc.save()
    closing_shift_doc.submit()
    return closing_shift_doc.name


def submit_printed_invoices(pos_opening_shift, doctype):
    invoices_list = frappe.get_all(
        doctype,
        filters={
            "posa_pos_opening_shift": pos_opening_shift,
            "docstatus": 0,
            "posa_is_printed": 1,
        },
    )
    for invoice in invoices_list:
        invoice_doc = frappe.get_doc(doctype, invoice.name)
        invoice_doc.submit()
