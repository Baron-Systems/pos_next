# -*- coding: utf-8 -*-
# Copyright (c) 2025, BrainWise and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _


@frappe.whitelist()
def update_sales_order_status_after_invoice(invoice_name):
    """
    Update sales order status after invoice submission.
    This handles the case where ERPNext doesn't properly update the status.
    
    Args:
        invoice_name: Name of the submitted Sales Invoice
        
    Returns:
        Dictionary with updated sales orders and their new statuses
    """
    try:
        if not frappe.db.exists("Sales Invoice", invoice_name):
            frappe.throw(_("Sales Invoice {0} not found").format(invoice_name))
            
        invoice = frappe.get_doc("Sales Invoice", invoice_name)
        
        # Check if invoice is submitted and paid
        if invoice.docstatus != 1:
            return {"success": False, "message": _("Invoice is not submitted")}
            
        # Get all sales orders linked to this invoice
        sales_orders = []
        
        for item in invoice.get("items", []):
            # Use correct ERPNext field names
            so_name = item.get('sales_order')  # Correct field name in ERPNext
            so_detail = item.get('so_detail')
            
            if so_name:
                sales_orders.append(so_name)
        
        # Remove duplicates
        sales_orders = list(set(sales_orders))
        
        updated_orders = []
        
        for so_name in sales_orders:
            so = frappe.get_doc("Sales Order", so_name)
            old_status = so.status
            
            # Refresh the sales order to get updated billing/delivery percentages
            so.reload()
            
            # Determine the correct status based on billing and delivery
            per_billed = flt(so.per_billed or 0)
            per_delivered = flt(so.per_delivered or 0)
            
            # Check if invoice is fully paid
            invoice_paid = (getattr(invoice, 'outstanding_amount', 0) or 0) <= 0
            
            # Update status based on billing and payment status
            if invoice_paid and per_billed >= 100:
                # Fully billed and paid - mark as completed for POS transactions
                so.update_status("Completed")
            elif per_billed >= 100:
                # Fully billed but not necessarily paid
                if per_delivered >= 100:
                    so.update_status("Completed")
                else:
                    so.update_status("To Deliver")
            elif per_billed > 0:
                # Partially billed
                if per_delivered >= 100:
                    so.update_status("To Bill")
                else:
                    so.update_status("To Deliver and Bill")
            else:
                # Not billed
                if per_delivered >= 100:
                    so.status = "To Bill"
                else:
                    so.status = "To Deliver and Bill"
            
            # Save the updated status
            so.flags.ignore_permissions = True
            so.save()
            
            updated_orders.append({
                "name": so.name,
                "old_status": old_status,
                "new_status": so.status,
                "per_billed": per_billed,
                "per_delivered": per_delivered,
                "invoice_paid": invoice_paid
            })
        
        frappe.db.commit()
        
        return {
            "success": True,
            "message": _("Updated {0} sales order(s)").format(len(updated_orders)),
            "updated_orders": updated_orders
        }
        
    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), "Update Sales Order Status Error")
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
