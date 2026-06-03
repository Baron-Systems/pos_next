# -*- coding: utf-8 -*-
# Copyright (c) 2025, BrainWise and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _


@frappe.whitelist()
def submit_sales_order(sales_order_name):
    """
    Submit a sales order to enable invoice linking.
    
    Args:
        sales_order_name: Name of the Sales Order to submit
        
    Returns:
        Dictionary with success status and updated order details
    """
    try:
        if not frappe.db.exists("Sales Order", sales_order_name):
            frappe.throw(_("Sales Order {0} not found").format(sales_order_name))
            
        sales_order = frappe.get_doc("Sales Order", sales_order_name)
        
        # Check if already submitted
        if sales_order.docstatus == 1:
            return {
                "success": True,
                "message": _("Sales Order already submitted"),
                "status": sales_order.status,
                "docstatus": sales_order.docstatus
            }
        
        # Check if cancelled
        if sales_order.docstatus == 2:
            frappe.throw(_("Cannot submit cancelled Sales Order {0}").format(sales_order_name))
        
        # Submit the sales order
        sales_order.submit()
        
        frappe.db.commit()
        
        return {
            "success": True,
            "message": _("Sales Order {0} submitted successfully").format(sales_order_name),
            "status": sales_order.status,
            "docstatus": sales_order.docstatus
        }
        
    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), "Submit Sales Order Error")
        return {
            "success": False,
            "message": str(e)
        }
