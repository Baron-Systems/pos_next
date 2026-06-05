"""
POS-ABS Customer & Contact Integration API - ERPNext v16 Compatible
Handles synchronized updates between Customer and Contact documents
Using official ERPNext v16 Contact API with phone_nos child table
"""

import frappe
from frappe import _


@frappe.whitelist()
def create_customer_with_contact_v16(
    customer_name,
    mobile_no=None,
    email_id=None,
    customer_group="Individual",
    territory="All Territories",
    company=None,
):
    """
    Create a new customer with linked Contact document (ERPNext v16 compatible).

    Critical: ERPNext v16 stores phone numbers in Contact Phone child table (phone_nos),
    NOT in Contact.mobile_no directly (which is READ-ONLY).

    Args:
        customer_name (str): Customer name (required)
        mobile_no (str): Mobile number (optional, format: +XXX-XXXXXXXX)
        email_id (str): Email address (optional)
        customer_group (str): Customer group (default: Individual)
        territory (str): Territory (default: All Territories)
        company (str): Company (optional)

    Returns:
        dict: Created customer document with contact info
    """
    # Check permissions
    if not frappe.has_permission("Customer", "create"):
        frappe.throw(_("You don't have permission to create customers"), frappe.PermissionError)

    if not customer_name:
        frappe.throw(_("Customer name is required"))

    # Normalize mobile format if provided
    if mobile_no:
        mobile_no = _normalize_phone_number_v16(mobile_no)

    # Validate territory exists, fallback to empty if not found
    if territory and not frappe.db.exists("Territory", territory):
        territory = None
    if customer_group and not frappe.db.exists("Customer Group", customer_group):
        customer_group = "Individual"

    try:
        # 1. Create Customer
        customer = frappe.get_doc(
            {
                "doctype": "Customer",
                "customer_name": customer_name,
                "customer_type": "Individual",
                "customer_group": customer_group or "Individual",
                "territory": territory,
                "mobile_no": mobile_no or "",
                "email_id": email_id or "",
            }
        )
        customer.insert()

        # 2. Create Contact with phone_nos child table (ERPNext v16 way)
        contact = _create_contact_v16(
            customer=customer,
            mobile_no=mobile_no,
            email_id=email_id
        )

        result = customer.as_dict()
        result["contact"] = _get_contact_dict(contact) if contact else None
        result["contact_created"] = contact is not None

        return result

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "POS-ABS: Create Customer Failed")
        raise


@frappe.whitelist()
def update_customer_with_contact_v16(
    customer_id,
    customer_name=None,
    mobile_no=None,
    email_id=None,
    customer_group=None,
    territory=None,
):
    """
    Update customer and synchronize with linked Contact document (ERPNext v16 compatible).

    Critical: Updates Contact.phone_nos child table, NOT Contact.mobile_no directly.

    Args:
        customer_id (str): Customer ID/name (required)
        customer_name (str): Customer name (optional)
        mobile_no (str): Mobile number (optional)
        email_id (str): Email address (optional)
        customer_group (str): Customer group (optional)
        territory (str): Territory (optional)

    Returns:
        dict: Updated customer document with contact info
    """
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
            mobile_no = _normalize_phone_number_v16(mobile_no)
        if email_id is not None:
            customer.email_id = email_id
        if customer_group is not None:
            if frappe.db.exists("Customer Group", customer_group):
                customer.customer_group = customer_group
        if territory is not None:
            if frappe.db.exists("Territory", territory):
                customer.territory = territory

        customer.save()
        
        # Use db_set for mobile_no and email_id to avoid hooks that might clear them
        if mobile_no is not None:
            frappe.db.set_value("Customer", customer_id, "mobile_no", mobile_no, update_modified=False)
        
        if email_id is not None:
            frappe.db.set_value("Customer", customer_id, "email_id", email_id, update_modified=False)
        
        if mobile_no is not None or email_id is not None:
            frappe.db.commit()

        # 2. Update or Create Contact using ERPNext v16 API
        contact = _update_or_create_contact_v16(
            customer=customer,
            mobile_no=mobile_no,
            email_id=email_id
        )

        # 3. Get fresh customer data for result
        customer_fresh = frappe.get_doc("Customer", customer_id)

        result = customer_fresh.as_dict()
        result["contact"] = _get_contact_dict(contact) if contact else None
        result["contact_updated"] = contact is not None

        return result

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "POS-ABS: Update Customer Failed")
        raise


def _create_contact_v16(customer, mobile_no, email_id):
    """
    Create Contact document using ERPNext v16 official API.
    Uses phone_nos child table (NOT contact.mobile_no directly).

    Args:
        customer: Customer document
        mobile_no: Mobile number
        email_id: Email ID

    Returns:
        Contact document
    """
    try:
        # Create Contact document with all fields
        contact_data = {
            "doctype": "Contact",
            "first_name": customer.customer_name,
            "is_primary_contact": 1,
            "links": [{
                "link_doctype": "Customer",
                "link_name": customer.name,
                "link_title": customer.customer_name
            }]
        }

        # Add email_id if provided (avoid validation errors)
        if email_id:
            contact_data["email_id"] = email_id

        contact = frappe.get_doc(contact_data)

        # Add phone to phone_nos child table (ERPNext v16 way)
        if mobile_no:
            contact.append("phone_nos", {
                "phone": mobile_no,
                "is_primary_phone": 0,
                "is_primary_mobile_no": 1  # Mark as primary mobile
            })

        # Add email to email_ids child table (ERPNext v16 way)
        if email_id:
            contact.append("email_ids", {
                "email_id": email_id,
                "is_primary": 1
            })

        # Insert the contact with ignore_mandatory if email is empty
        try:
            contact.insert()
        except frappe.MandatoryError as e:
            if "email_id" in str(e).lower():
                contact.flags.ignore_mandatory = True
                contact.insert()
            else:
                raise

        return contact

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "POS-ABS: Create Contact Failed")
        return None


def _update_or_create_contact_v16(customer, mobile_no, email_id):
    """
    Update or Create Contact using ERPNext v16 official API.

    Strategy for phone update:
    1. Find existing contact linked to customer
    2. If exists:
       - Update phone_nos
       - Add new phone with is_primary_mobile_no=1
    3. If not exists: Create new contact

    Args:
        customer: Customer document
        mobile_no: Mobile number (or None to skip update)
        email_id: Email ID (or None to skip update)

    Returns:
        Contact document or None
    """
    try:
        # Method 1: Find via Dynamic Link (official way)
        contact_links = frappe.get_all(
            "Dynamic Link",
            filters={
                "link_doctype": "Customer",
                "link_name": customer.name,
                "parenttype": "Contact"
            },
            fields=["parent"],
            order_by="creation ASC",
            limit=1
        )

        # Method 2: Also try by guessing the contact name (autoname pattern)
        expected_contact_name = f"{customer.customer_name}-{customer.name}"
        alternative_contact = None
        if frappe.db.exists("Contact", expected_contact_name):
            alternative_contact = expected_contact_name

        contact_name = None
        if contact_links:
            contact_name = contact_links[0].parent
        elif alternative_contact:
            contact_name = alternative_contact

        if contact_name:
            # Update existing contact - get fresh copy to avoid timestamp issues
            contact = frappe.get_doc("Contact", contact_name)

            # Update name if changed
            if customer.customer_name != contact.first_name:
                contact.first_name = customer.customer_name

            # Update phone in phone_nos child table (ERPNext v16 way)
            if mobile_no is not None:
                _update_contact_phone_v16(contact, mobile_no)

            # Update email in email_ids child table (ERPNext v16 way)
            if email_id is not None and email_id.strip():
                _update_contact_email_v16(contact, email_id)
            elif not contact.email_id:
                # If no email and contact doesn't have one, set dummy to pass validation
                contact.email_id = "temp@placeholder.com"

            # Save with ignore_mandatory to prevent validation errors
            contact.flags.ignore_mandatory = True
            
            try:
                contact.save()
            except frappe.TimestampMismatchError:
                # If timestamp mismatch, get fresh copy and retry
                contact = frappe.get_doc("Contact", contact_name)
                
                # Re-apply changes
                if customer.customer_name != contact.first_name:
                    contact.first_name = customer.customer_name
                if mobile_no is not None:
                    _update_contact_phone_v16(contact, mobile_no)
                if email_id is not None and email_id.strip():
                    _update_contact_email_v16(contact, email_id)
                elif not contact.email_id:
                    contact.email_id = "temp@placeholder.com"
                
                contact.flags.ignore_mandatory = True
                contact.save()

            return contact

        else:
            # Create new contact
            return _create_contact_v16(customer, mobile_no, email_id)

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "POS-ABS: Update/Create Contact Failed")
        return None


def _update_contact_phone_v16(contact, mobile_no):
    """
    Update phone in Contact using ERPNext v16 phone_nos child table.

    Strategy:
    1. Remove existing mobile entries or update existing
    2. Add new entry with is_primary_mobile_no=1

    Args:
        contact: Contact document
        mobile_no: New mobile number
    """
    # Find if there's already a primary mobile entry
    existing_primary_idx = None
    for idx, p in enumerate(contact.phone_nos):
        if p.is_primary_mobile_no:
            existing_primary_idx = idx
            break

    if existing_primary_idx is not None:
        # Update existing primary mobile
        contact.phone_nos[existing_primary_idx].phone = mobile_no
    else:
        # Clear all phone_nos and add new primary mobile
        contact.phone_nos = []  # Clear all
        contact.append("phone_nos", {
            "phone": mobile_no,
            "is_primary_phone": 0,
            "is_primary_mobile_no": 1
        })


def _update_contact_email_v16(contact, email_id):
    """
    Update email in Contact using ERPNext v16 email_ids child table.
    """
    # Find if there's already a primary email entry
    existing_primary_idx = None
    for idx, e in enumerate(contact.email_ids):
        if e.is_primary:
            existing_primary_idx = idx
            break

    if existing_primary_idx is not None:
        contact.email_ids[existing_primary_idx].email_id = email_id
    else:
        contact.email_ids = []  # Clear all
        contact.append("email_ids", {
            "email_id": email_id,
            "is_primary": 1
        })


def _normalize_phone_number_v16(phone_number):
    """
    Normalize phone number format for ERPNext v16.
    ERPNext expects clean phone numbers.

    Args:
        phone_number (str): Raw phone number

    Returns:
        str: Normalized phone number
    """
    if not phone_number:
        return ""

    cleaned = phone_number.strip()

    # If format is +XXX-XXXXXXXX, keep the dash
    if cleaned.startswith("+") and "-" in cleaned:
        return cleaned

    # If starts with + but no dash, add dash after country code
    if cleaned.startswith("+"):
        # Remove all non-digit characters after the +
        digits = ''.join(c for c in cleaned[1:] if c.isdigit())
        # Try common country code lengths
        for code_len in [4, 3, 2, 1]:
            if len(digits) > code_len:
                return f"+{digits[:code_len]}-{digits[code_len:]}"

    return cleaned


def _get_contact_dict(contact):
    """
    Get contact as dict with full details including phone_nos.
    """
    if not contact:
        return None

    result = contact.as_dict()

    # Include child tables explicitly
    result["phone_nos"] = [
        {
            "phone": p.phone,
            "is_primary_phone": p.is_primary_phone,
            "is_primary_mobile_no": p.is_primary_mobile_no
        }
        for p in contact.phone_nos
    ]

    result["email_ids"] = [
        {
            "email_id": e.email_id,
            "is_primary": e.is_primary
        }
        for e in contact.email_ids
    ]

    return result


# =============================================================================
# API Endpoints
# =============================================================================

@frappe.whitelist()
def create_customer_v16_api(
    customer_name,
    mobile_no=None,
    email_id=None,
    customer_group="Individual",
    territory="All Territories",
    company=None
):
    """API wrapper for creating customer with v16 compatibility."""
    return create_customer_with_contact_v16(
        customer_name=customer_name,
        mobile_no=mobile_no,
        email_id=email_id,
        customer_group=customer_group,
        territory=territory,
        company=company
    )


@frappe.whitelist()
def update_customer_v16_api(
    customer_id,
    customer_name=None,
    mobile_no=None,
    email_id=None,
    customer_group=None,
    territory=None
):
    """API wrapper for updating customer with v16 compatibility."""
    return update_customer_with_contact_v16(
        customer_id=customer_id,
        customer_name=customer_name,
        mobile_no=mobile_no,
        email_id=email_id,
        customer_group=customer_group,
        territory=territory
    )
