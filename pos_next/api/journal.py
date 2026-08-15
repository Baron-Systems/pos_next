import frappe
from frappe import _
from frappe.utils import flt, nowdate, now, get_time, getdate
from pos_next.api.invoices import get_payment_account


@frappe.whitelist()
def create_cash_to_card_transfer(company, from_mode_of_payment, to_mode_of_payment, amount, posting_date=None, reference_no=None, remarks=None, pos_opening_shift=None):
    """Create a Journal Entry to transfer funds from one payment method account to another.

    Accounting entry:
        - Debit the target account (mode_of_payment)
        - Credit the source account (mode_of_payment)
    """
    if not company:
        frappe.throw(_("Company is required"))
    if not from_mode_of_payment:
        frappe.throw(_("Source payment method is required"))
    if not to_mode_of_payment:
        frappe.throw(_("Target payment method is required"))
    if from_mode_of_payment == to_mode_of_payment:
        frappe.throw(_("Source and target payment methods must be different"))

    amount = flt(amount)
    if amount <= 0:
        frappe.throw(_("Amount must be greater than zero"))

    from_account_info = get_payment_account(from_mode_of_payment, company)
    to_account_info = get_payment_account(to_mode_of_payment, company)

    from_account = from_account_info.get("account") if from_account_info else None
    to_account = to_account_info.get("account") if to_account_info else None

    if not from_account:
        frappe.throw(_("Could not resolve account for payment method {0}").format(from_mode_of_payment))
    if not to_account:
        frappe.throw(_("Could not resolve account for payment method {0}").format(to_mode_of_payment))

    if from_account == to_account:
        frappe.throw(_("Source and target accounts resolve to the same ledger account"))

    # Validate accounts are not group accounts
    for account in (from_account, to_account):
        acc_doc = frappe.get_doc("Account", account)
        if acc_doc.is_group:
            frappe.throw(_("Account {0} is a group account. Please configure a ledger account.").format(account))
        if acc_doc.company != company:
            frappe.throw(_("Account {0} does not belong to company {1}").format(account, company))

    je = frappe.get_doc({
        "doctype": "Journal Entry",
        "company": company,
        "posting_date": posting_date or nowdate(),
        "reference_no": reference_no,
        "remark": remarks or _("POS Payment Method Transfer"),
        "accounts": [
            {
                "account": from_account,
                "credit_in_account_currency": amount,
            },
            {
                "account": to_account,
                "debit_in_account_currency": amount,
            },
        ],
    })

    je.save(ignore_permissions=True)
    je.submit()

    # Track transfer against the opening shift so it affects closing
    if pos_opening_shift:
        posting_dt = getdate(posting_date or nowdate())
        transfer = frappe.get_doc({
            "doctype": "POS Payment Method Transfer",
            "posting_date": posting_dt,
            "posting_time": get_time(now()),
            "user": frappe.session.user,
            "company": company,
            "pos_opening_shift": pos_opening_shift,
            "status": "Submitted",
            "from_mode_of_payment": from_mode_of_payment,
            "from_account": from_account,
            "to_mode_of_payment": to_mode_of_payment,
            "to_account": to_account,
            "amount": amount,
            "journal_entry": je.name,
        })
        transfer.save(ignore_permissions=True)
        transfer.submit()

    return {
        "journal_entry": je.name,
        "from_mode_of_payment": from_mode_of_payment,
        "to_mode_of_payment": to_mode_of_payment,
        "from_account": from_account,
        "to_account": to_account,
        "amount": amount,
        "posting_date": je.posting_date,
    }


@frappe.whitelist()
def get_name_expenses(company):
    """Return list of predefined expenses (Name expense) for the selected company."""
    if not company:
        frappe.throw(_("Company is required"))

    return frappe.db.sql(
        """
        SELECT ne.name, ne.name_of_the_expense, ne.account
        FROM `tabName expense` ne
        INNER JOIN `tabAccount` acc ON acc.name = ne.account
        WHERE acc.company = %s AND acc.is_group = 0
        ORDER BY ne.name_of_the_expense
        """,
        (company,),
        as_dict=1,
    )


@frappe.whitelist()
def create_shift_expense(company, mode_of_payment, expense_account, amount, expense_name=None, name_expense=None, posting_date=None, remarks=None, pos_opening_shift=None):
    """Create a Journal Entry to record a shift expense and an 'expenses' document.

    Accounting entry:
        - Debit the expense account
        - Credit the payment method account
    """
    if not company:
        frappe.throw(_("Company is required"))
    if not mode_of_payment:
        frappe.throw(_("Payment method is required"))
    if not expense_account:
        frappe.throw(_("Expense account is required"))

    amount = flt(amount)
    if amount <= 0:
        frappe.throw(_("Amount must be greater than zero"))

    payment_account_info = get_payment_account(mode_of_payment, company)
    payment_account = payment_account_info.get("account") if payment_account_info else None
    if not payment_account:
        frappe.throw(_("Could not resolve account for payment method {0}").format(mode_of_payment))

    expense_doc = frappe.get_doc("Account", expense_account)
    if expense_doc.is_group:
        frappe.throw(_("Expense account {0} is a group account.").format(expense_account))
    if expense_doc.company != company:
        frappe.throw(_("Expense account {0} does not belong to company {1}").format(expense_account, company))

    # Resolve Name expense ID if not supplied (e.g. stale frontend builds)
    if not name_expense:
        name_expense = frappe.db.get_value(
            "Name expense",
            {"account": expense_account, "name_of_the_expense": expense_name or ""},
            "name",
        ) or frappe.db.get_value("Name expense", {"account": expense_account}, "name")
    if not name_expense:
        frappe.throw(_("Expense name is required"))

    # Create and submit erpnext 'expenses' doc (it creates the GL entries on submit)
    posting_dt = getdate(posting_date or nowdate())
    erp_expense = frappe.get_doc({
        "doctype": "expenses",
        "company": company,
        "name_expense": name_expense,
        "amount": amount,
        "mode_of_payment": mode_of_payment,
        "date_expenditure": posting_dt,
        "description": remarks,
        "naming_series": "ACC-EXP-.YYYY.-",
    })
    erp_expense.save(ignore_permissions=True)
    erp_expense.flags.ignore_permissions = True
    erp_expense.submit()

    # Track expense against the opening shift so it affects closing
    expense = frappe.get_doc({
        "doctype": "POS Shift Expense",
        "posting_date": posting_dt,
        "posting_time": get_time(now()),
        "user": frappe.session.user,
        "company": company,
        "pos_opening_shift": pos_opening_shift,
        "status": "Submitted",
        "expense_name": expense_name or expense_account,
        "expense_account": expense_account,
        "amount": amount,
        "mode_of_payment": mode_of_payment,
        "payment_account": payment_account,
        "remarks": remarks,
    })
    expense.save(ignore_permissions=True)
    expense.submit()

    return {
        "journal_entry": erp_expense.name,
        "expense_name": expense_name or expense_account,
        "expense_account": expense_account,
        "mode_of_payment": mode_of_payment,
        "payment_account": payment_account,
        "amount": amount,
        "posting_date": posting_dt,
    }
