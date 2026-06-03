"""
POS Next Customer & Contact Integration API
Handles synchronized updates between Customer and Contact documents
"""

import frappe
from frappe import _


@frappe.whitelist()
def create_customer_with_contact(
    customer_name,
    mobile_no=None,
    email_id=None,
    customer_group="Individual",
    territory="All Territories",
    company=None,
):
    """
    Create a new customer with linked Contact document.

    Args:
        customer_name (str): Customer name (required)
        mobile_no (str): Mobile number (optional, format: +XXX-XXXXXXXX)
        email_id (str): Email address (optional)
        customer_group (str): Customer group (default: Individual)
        territory (str): Territory (default: All Territories)
        company (str): Company (optional, used to auto-assign loyalty program)

    Returns:
        dict: Created customer document with contact info
    """
    frappe.logger().info(f"[POS Next] Creating customer: {customer_name}, mobile: {mobile_no}")

    # Check permissions
    if not frappe.has_permission("Customer", "create"):
        frappe.throw(_("You don't have permission to create customers"), frappe.PermissionError)

    if not customer_name:
        frappe.throw(_("Customer name is required"))

    # Validate mobile format if provided
    if mobile_no:
        mobile_no = _normalize_phone_number(mobile_no)

    # Auto-assign loyalty program
    loyalty_program = _get_default_loyalty_program(company) if company else None

    try:
        # 1. Create Customer
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
        frappe.logger().info(f"[POS Next] Customer created: {customer.name}")

        # 2. Create Contact linked to Customer
        contact = _create_or_update_contact(
            customer=customer,
            mobile_no=mobile_no,
            email_id=email_id,
            is_new=True
        )

        result = customer.as_dict()
        result["contact"] = contact.as_dict() if contact else None
        result["contact_created"] = contact is not None

        frappe.logger().info(f"[POS Next] Customer+Contact creation completed: {customer.name}")
        return result

    except Exception as e:
        frappe.logger().error(f"[POS Next] Error creating customer: {str(e)}")
        raise


@frappe.whitelist()
def update_customer_with_contact(
    customer_id,
    customer_name=None,
    mobile_no=None,
    email_id=None,
    customer_group=None,
    territory=None,
):
    """
    Update customer and synchronize with linked Contact document.

    Args:
        customer_id (str): Customer ID/name (required)
        customer_name (str): Customer name (optional)
        mobile_no (str): Mobile number (optional, format: +XXX-XXXXXXXX)
        email_id (str): Email address (optional)
        customer_group (str): Customer group (optional)
        territory (str): Territory (optional)

    Returns:
        dict: Updated customer document with contact info
    """
    frappe.logger().info(
        f"[POS Next] Updating customer: {customer_id}, mobile: {mobile_no}, email: {email_id}"
    )

    # Validate inputs
    if not customer_id:
        frappe.throw(_("Customer ID is required"))

    if not frappe.db.exists("Customer", customer_id):
        frappe.throw(_("Customer {0} not found").format(customer_id))

    # Check permissions
    if not frappe.has_permission("Customer", "write"):
        frappe.throw(_("You don't have permission to update customers"), frappe.PermissionError)

    try:
        # 1. Update Customer
        customer = frappe.get_doc("Customer", customer_id)
        
        if customer_name is not None:
            customer.customer_name = customer_name
        if mobile_no is not None:
            mobile_no = _normalize_phone_number(mobile_no)
            customer.mobile_no = mobile_no
        if email_id is not None:
            customer.email_id = email_id
        if customer_group is not None:
            customer.customer_group = customer_group
        if territory is not None:
            customer.territory = territory

        customer.save()
        frappe.logger().info(f"[POS Next] Customer updated: {customer.name}")

        # 2. Update or Create Contact
        contact = _create_or_update_contact(
            customer=customer,
            mobile_no=mobile_no or customer.mobile_no,
            email_id=email_id or customer.email_id,
            is_new=False
        )

        result = customer.as_dict()
        result["contact"] = contact.as_dict() if contact else None
        result["contact_updated"] = contact is not None

        frappe.logger().info(f"[POS Next] Customer+Contact update completed: {customer.name}")
        return result

    except Exception as e:
        frappe.logger().error(f"[POS Next] Error updating customer: {str(e)}")
        frappe.logger().error(frappe.get_traceback())
        raise


def _create_or_update_contact(customer, mobile_no, email_id, is_new=False):
    """
    Create or update Contact document linked to Customer.

    Args:
        customer: Customer document
        mobile_no: Mobile number
        email_id: Email ID
        is_new: Whether customer is newly created

    Returns:
        Contact document or None
    """
    try:
        # Search for existing Contact linked to this Customer
        contact_links = frappe.get_all(
            "Contact",
            filters={
                "link_doctype": "Customer",
                "link_name": customer.name
            },
            fields=["name"],
            order_by="is_primary_contact DESC, creation ASC"
        )

        if contact_links:
            # Update existing contact
            contact = frappe.get_doc("Contact", contact_links[0].name)
            
            if mobile_no:
                contact.mobile_no = mobile_no
                contact.phone = mobile_no  # Sync both fields
            if email_id:
                contact.email_id = email_id
                
            # Ensure name is synced
            contact.first_name = customer.customer_name
            
            contact.save()
            frappe.logger().info(f"[POS Next] Contact updated: {contact.name}")
            return contact
        else:
            # Create new contact
            contact = frappe.get_doc({
                "doctype": "Contact",
                "first_name": customer.customer_name,
                "mobile_no": mobile_no or "",
                "phone": mobile_no or "",
                "email_id": email_id or "",
                "is_primary_contact": 1,
                "links": [{
                    "link_doctype": "Customer",
                    "link_name": customer.name,
                    "link_title": customer.customer_name
                }]
            })
            contact.insert()
            frappe.logger().info(f"[POS Next] Contact created: {contact.name}")
            return contact

    except Exception as e:
        frappe.logger().error(f"[POS Next] Error in contact operation: {str(e)}")
        # Don't fail the entire operation if contact fails
        return None


def _normalize_phone_number(phone_number):
    """
    Normalize phone number format.
    Handles: +966-0555123456, +9660555123456, 0555123456

    Args:
        phone_number (str): Raw phone number

    Returns:
        str: Normalized phone number (+XXX-XXXXXXXX)
    """
    if not phone_number:
        return ""

    # Remove all non-digit characters except + at start
    cleaned = phone_number.strip()
    
    # If already has correct format with dash, keep it
    if cleaned.startswith("+") and "-" in cleaned:
        return cleaned
    
    # If starts with + but no dash, add dash after country code
    if cleaned.startswith("+"):
        # Find where country code ends (usually 2-4 digits after +)
        digits = cleaned[1:]
        # Common country codes: +1, +44, +966, +971, +20, +49, etc.
        # Try to detect country code length
        for code_len in [4, 3, 2, 1]:
            if len(digits) > code_len:
                country_code = digits[:code_len]
                rest = digits[code_len:]
                return f"+{country_code}-{rest}"
    
    # No country code, return as-is (user can add country code manually)
    return cleaned


def _get_default_loyalty_program(company):
    """Get default loyalty program for company."""
    if not company:
        return None
    
    # Try auto_opt_in first
    program = frappe.db.get_value(
        "Loyalty Program",
        {"company": company, "auto_opt_in": 1},
        "name"
    )
    
    if not program:
        program = frappe.db.get_value(
            "Loyalty Program",
            {"company": company},
            "name"
        )
    
    return program


@frappe.whitelist()
def get_customer_with_contact(customer_id):
    """
    Get customer details with linked contact info.

    Args:
        customer_id (str): Customer ID

    Returns:
        dict: Customer with contact details
    """
    if not customer_id or not frappe.db.exists("Customer", customer_id):
        frappe.throw(_("Customer not found"))

    customer = frappe.get_cached_doc("Customer", customer_id)
    result = customer.as_dict()

    # Get primary contact
    contacts = frappe.get_all(
        "Contact",
        filters={
            "link_doctype": "Customer",
            "link_name": customer_id
        },
        fields=["name", "mobile_no", "phone", "email_id", "is_primary_contact"],
        order_by="is_primary_contact DESC, creation DESC",
        limit=1
    )

    if contacts:
        result["contact_details"] = contacts[0]
    else:
        result["contact_details"] = None

    return result
