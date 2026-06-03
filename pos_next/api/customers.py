"""
POS-ABS Customer API
Handles customer search, creation, and management for POS operations
"""

import frappe
from frappe import _

# Import Contact integration functions
from pos_next.api.customer_contact import (
    create_customer_with_contact,
    update_customer_with_contact,
    get_customer_with_contact,
)


@frappe.whitelist()
def get_customers(search_term="", pos_profile=None, limit=None):

    """
    Search customers for inline customer selection in POS.

    Args:
        search_term (str): Search query (name, mobile, or customer ID)
        pos_profile (str): POS Profile to filter by customer group
        limit (int): Maximum number of results to return (default: all customers)

    Returns:
        list: List of customer dictionaries with name, customer_name, mobile_no, email_id, id_no
    """
    try:
        frappe.logger().debug(
            f"get_customers called with search_term={search_term}, pos_profile={pos_profile}, limit={limit}"
        )

        filters = {}

        # Filter by POS Profile customer group if specified
        if pos_profile:
            frappe.logger().debug(f"Loading POS Profile: {pos_profile}")
            profile_doc = frappe.get_cached_doc("POS Profile", pos_profile)
            # Check if customer_group field exists (it may not exist in all versions)
            if hasattr(profile_doc, "customer_group") and profile_doc.customer_group:
                filters["customer_group"] = profile_doc.customer_group
                frappe.logger().debug(f"Filtering by customer_group: {profile_doc.customer_group}")

        # Return all customers (for client-side filtering)
        filters["disabled"] = 0
        
        # If no limit specified, fetch all customers
        if limit:
            customer_limit = limit
        else:
            # No limit = fetch all customers
            customer_limit = 0  # 0 means no limit in frappe.get_all
        
        result = frappe.get_all(
            "Customer",
            filters=filters,
            fields=["name", "customer_name", "mobile_no", "email_id", "id_no"],
            limit=customer_limit or None,  # None means no limit
            order_by="customer_name asc",
        )
        frappe.logger().debug(f"get_customers returned {len(result)} customers")
        return result
    except Exception as e:
        frappe.logger().error(f"Error in get_customers: {str(e)}")
        frappe.logger().error(frappe.get_traceback())
        frappe.throw(_("Error fetching customers: {0}").format(str(e)))


@frappe.whitelist()
def create_customer(customer_name, mobile_no=None, email_id=None, customer_group="Individual", territory="All Territories", company=None):
    """
    Create a new customer from POS.

    Args:
        customer_name (str): Customer name (required)
        mobile_no (str): Mobile number (optional)
        email_id (str): Email address (optional)
        customer_group (str): Customer group (default: Individual)
        territory (str): Territory (default: All Territories)
        company (str): Company (optional, used to auto-assign loyalty program)

    Returns:
        dict: Created customer document
    """
    # Check if user has permission to create customers
    if not frappe.has_permission("Customer", "create"):
        frappe.throw(_("You don't have permission to create customers"), frappe.PermissionError)

    if not customer_name:
        frappe.throw(_("Customer name is required"))

    # Auto-assign loyalty program based on company
    loyalty_program = None
    if company:
        loyalty_program = get_default_loyalty_program(company)

    customer = frappe.get_doc(
        {
            "doctype": "Customer",
            "customer_name": customer_name,
            "customer_type": "Individual",
            "customer_group": customer_group or "Individual",
            "territory": territory or "All Territories",
            "mobile_no": mobile_no or "",
            "email_id": email_id or "",
            "loyalty_program": loyalty_program,
        }
    )

    customer.insert()

    return customer.as_dict()


def get_default_loyalty_program(company):
    """
    Get the default loyalty program for a company.
    Prefers programs with auto_opt_in enabled.

    Args:
        company (str): Company name

    Returns:
        str: Loyalty program name or None
    """
    # First try to find a loyalty program with auto_opt_in for the company
    loyalty_program = frappe.db.get_value(
        "Loyalty Program",
        {"company": company, "auto_opt_in": 1},
        "name"
    )

    if loyalty_program:
        return loyalty_program

    # Fallback: any loyalty program for the company
    loyalty_program = frappe.db.get_value(
        "Loyalty Program",
        {"company": company},
        "name"
    )

    return loyalty_program


def auto_assign_loyalty_program(doc, method=None):
    """
    Auto-assign loyalty program to newly created customers.
    Called as after_insert hook on Customer doctype.

    Uses the default_loyalty_program from POS Settings.
    If no loyalty program is configured in POS Settings, no auto-assignment occurs.

    Args:
        doc: Customer document
        method: Hook method name (not used)
    """
    # Skip if customer already has a loyalty program
    if doc.loyalty_program:
        return

    # Get loyalty program from POS Settings
    loyalty_program = get_default_loyalty_program_from_settings()

    if loyalty_program:
        # Use db_set to avoid triggering validate hooks again
        doc.db_set("loyalty_program", loyalty_program, update_modified=False)
        frappe.logger().info(
            f"Auto-assigned loyalty program '{loyalty_program}' to customer '{doc.name}'"
        )


def get_default_loyalty_program_from_settings():
    """
    Get the default loyalty program from POS Settings.
    Checks all enabled POS Settings and returns the first configured loyalty program.

    Returns:
        str: Loyalty program name or None if not configured
    """
    # Find POS Settings with default_loyalty_program set
    pos_settings = frappe.get_all(
        "POS Settings",
        filters={"enabled": 1, "default_loyalty_program": ["is", "set"]},
        fields=["default_loyalty_program"],
        limit=1
    )

    if pos_settings and pos_settings[0].get("default_loyalty_program"):
        return pos_settings[0].default_loyalty_program

    return None


@frappe.whitelist()
def get_customer_details(customer):
    """
    Get detailed customer information.

    Args:
        customer (str): Customer ID

    Returns:
        dict: Customer details
    """
    if not customer:
        frappe.throw(_("Customer is required"))

    return frappe.get_cached_doc("Customer", customer).as_dict()


@frappe.whitelist()
def update_customer_phone(customer, mobile_no):
    """
    Update customer mobile number with Contact synchronization.

    Args:
        customer (str): Customer ID
        mobile_no (str): Mobile number

    Returns:
        dict: Updated customer details
    """
    frappe.logger().info(f"[POS-ABS] update_customer_phone called: customer={customer}, mobile={mobile_no}")

    if not customer:
        frappe.throw(_("Customer is required"))

    if not frappe.db.exists("Customer", customer):
        frappe.throw(_("Customer {0} not found").format(customer))

    # Check permission
    if not frappe.has_permission("Customer", "write"):
        frappe.logger().warning(f"[POS-ABS] Permission denied for updating customer: {customer}")
        frappe.throw(_("You don't have permission to update customers"), frappe.PermissionError)

    # Use the new integrated function
    try:
        result = update_customer_with_contact(
            customer_id=customer,
            mobile_no=mobile_no
        )
        frappe.logger().info(f"[POS-ABS] Customer phone updated successfully: {customer}")
        return result
    except Exception as e:
        frappe.logger().error(f"[POS-ABS] Failed to update customer phone: {str(e)}")
        raise


@frappe.whitelist()
def create_customer_with_contact_api(
    customer_name,
    mobile_no=None,
    email_id=None,
    customer_group="Individual",
    territory="All Territories",
    company=None
):
    """
    API endpoint for creating customer with contact from POS.
    This is the RECOMMENDED way to create customers from POS.

    Args:
        customer_name (str): Customer name (required)
        mobile_no (str): Mobile number with country code
        email_id (str): Email address
        customer_group (str): Customer group
        territory (str): Territory
        company (str): Company

    Returns:
        dict: Created customer with contact details
    """
    frappe.logger().info(
        f"[POS-ABS] create_customer_with_contact_api called: name={customer_name}, mobile={mobile_no}"
    )

    try:
        result = create_customer_with_contact(
            customer_name=customer_name,
            mobile_no=mobile_no,
            email_id=email_id,
            customer_group=customer_group,
            territory=territory,
            company=company
        )
        frappe.logger().info(f"[POS-ABS] Customer created via API: {result.get('name')}")
        return result
    except Exception as e:
        frappe.logger().error(f"[POS-ABS] Failed to create customer: {str(e)}")
        raise


@frappe.whitelist()
def update_customer_with_contact_api(
    customer_id,
    customer_name=None,
    mobile_no=None,
    email_id=None,
    customer_group=None,
    territory=None
):
    """
    API endpoint for updating customer with contact synchronization.
    This is the RECOMMENDED way to update customers from POS.

    Args:
        customer_id (str): Customer ID (required)
        customer_name (str): Customer name
        mobile_no (str): Mobile number with country code
        email_id (str): Email address
        customer_group (str): Customer group
        territory (str): Territory

    Returns:
        dict: Updated customer with contact details
    """
    frappe.logger().info(
        f"[POS-ABS] update_customer_with_contact_api called: id={customer_id}, mobile={mobile_no}"
    )

    try:
        result = update_customer_with_contact(
            customer_id=customer_id,
            customer_name=customer_name,
            mobile_no=mobile_no,
            email_id=email_id,
            customer_group=customer_group,
            territory=territory
        )
        frappe.logger().info(f"[POS-ABS] Customer updated via API: {customer_id}")
        return result
    except Exception as e:
        frappe.logger().error(f"[POS-ABS] Failed to update customer: {str(e)}")
        raise
