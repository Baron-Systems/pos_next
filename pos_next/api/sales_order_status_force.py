# -*- coding: utf-8 -*-
# Copyright (c) 2025, BrainWise and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _


@frappe.whitelist()
def force_update_sales_order_status(sales_order_name):
    """
    Force update sales order status by recalculating billing/delivery percentages.
    This is a more aggressive approach to ensure status is correct.
    
    Args:
        sales_order_name: Name of the Sales Order to update
        
    Returns:
        Dictionary with update result
    """
    try:
        if not frappe.db.exists("Sales Order", sales_order_name):
            return {"success": False, "message": _("Sales Order not found")}
            
        so = frappe.get_doc("Sales Order", sales_order_name)
        old_status = so.status
        
        # Force recalculate billing percentage
        so.update_billed_amount()
        so.update_delivered_qty()
        
        # Reload to get updated values
        so.reload()
        
        per_billed = flt(so.per_billed or 0)
        per_delivered = flt(so.per_delivered or 0)
        
        # Get all invoices against this sales order
        invoices = frappe.db.sql("""
            SELECT name, outstanding_amount, docstatus
            FROM `tabSales Invoice`
            WHERE against_sales_order = %s
            AND docstatus = 1
        """, sales_order_name, as_dict=True)
        
        # Check if all invoices are fully paid
        all_paid = True
        total_outstanding = 0
        
        for inv in invoices:
            outstanding = flt(inv.outstanding_amount or 0)
            total_outstanding += outstanding
            if outstanding > 0:
                all_paid = False
        
        # Log for debugging
        frappe.log_error(
            f"Force Update SO {sales_order_name}: per_billed={per_billed}%, per_delivered={per_delivered}%, "
            f"all_paid={all_paid}, total_outstanding={total_outstanding}, invoices={len(invoices)}",
            "Force Sales Order Status Update"
        )
        
        # Determine status with more aggressive logic for POS
        if per_billed >= 100 and all_paid:
            # Fully billed and all invoices paid - mark as completed
            so.status = "Completed"
        elif per_billed >= 100:
            # Fully billed but some payments outstanding
            so.status = "To Deliver"
        elif per_billed > 0:
            # Partially billed
            so.status = "To Deliver and Bill"
        else:
            # Not billed
            so.status = "To Deliver and Bill"
        
        # Save the updated status
        so.flags.ignore_permissions = True
        so.save()
        
        frappe.db.commit()
        
        return {
            "success": True,
            "message": _("Sales order status updated from {0} to {1}").format(old_status, so.status),
            "old_status": old_status,
            "new_status": so.status,
            "per_billed": per_billed,
            "per_delivered": per_delivered,
            "all_paid": all_paid,
            "invoices_count": len(invoices)
        }
        
    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), "Force Update Sales Order Status Error")
        return {
            "success": False,
            "message": str(e)
        }


def flt(value, default=0):
    """Convert value to float with default"""
    try:
        return float(value) if value is not None else default
    except (ValueError, TypeError):
        return default
