# -*- coding: utf-8 -*-
# Copyright (c) 2025, BrainWise and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _


@frappe.whitelist()
def force_update_sales_order_status_direct(sales_order_name, new_status="Completed"):
    """
    Force update sales order status using direct database update.
    This is a more aggressive approach when update_status doesn't work.
    
    Args:
        sales_order_name: Name of the Sales Order to update
        new_status: New status to set (default: "Completed")
        
    Returns:
        Dictionary with update result
    """
    try:
        if not frappe.db.exists("Sales Order", sales_order_name):
            return {"success": False, "message": _("Sales Order not found")}
            
        # Get current status
        old_status = frappe.db.get_value("Sales Order", sales_order_name, "status")
        
        # Direct database update
        frappe.db.set_value("Sales Order", sales_order_name, "status", new_status)
        
        # Verify the update
        new_status_db = frappe.db.get_value("Sales Order", sales_order_name, "status")
        
        frappe.db.commit()
        
        return {
            "success": True,
            "message": _("Sales order status updated from {0} to {1}").format(old_status, new_status_db),
            "old_status": old_status,
            "new_status": new_status_db
        }
        
    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), "Force Update Sales Order Status Error")
        return {
            "success": False,
            "message": str(e)
        }
