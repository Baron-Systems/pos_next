# -*- coding: utf-8 -*-
# Copyright (c) 2025, BrainWise and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt, cint, getdate, nowdate


@frappe.whitelist()
def get_sales_orders(pos_profile=None, status=None, limit=50, customer=None):
	"""
	Get sales orders for the POS.
	
	Args:
		pos_profile: POS Profile name (optional)
		status: Filter by status (Draft, To Deliver and Bill, To Bill, To Deliver, Completed, Cancelled)
		limit: Maximum number of records to return
		customer: Filter by customer name (optional)
	
	Returns:
		List of sales order documents with relevant fields
	"""
	try:
		filters = {"docstatus": ["in", [0, 1]]}  # Show both draft and submitted orders
		
		if status:
			filters["status"] = status
		else:
			# Default: show draft and submitted orders that can be invoiced
			filters["status"] = ["in", ["Draft", "To Deliver and Bill", "To Bill", "To Deliver"]]
		
		if customer:
			filters["customer"] = customer
		
		# If POS profile is provided, filter by company
		if pos_profile:
			company = frappe.db.get_value("POS Profile", pos_profile, "company")
			if company:
				filters["company"] = company
		
		sales_orders = frappe.get_list(
			"Sales Order",
			filters=filters,
			fields=[
				"name",
				"customer",
				"customer_name",
				"transaction_date",
				"delivery_date",
				"status",
				"grand_total",
				"total",
				"net_total",
				"per_billed",
				"per_delivered",
				"company",
				"currency",
				"order_type",
			],
			order_by="transaction_date desc, creation desc",
			limit_page_length=cint(limit)
		)
		
		# Get additional details for each order
		for order in sales_orders:
			# Get items count
			order["items_count"] = frappe.db.count(
				"Sales Order Item",
				{"parent": order.name}
			)
			
			# Format dates
			if order.get("transaction_date"):
				order["formatted_date"] = frappe.utils.format_date(order["transaction_date"])
			
			# Calculate remaining amount to bill
			if order.get("per_billed") is not None:
				order["remaining_amount"] = flt(order["grand_total"]) * (100 - flt(order["per_billed"])) / 100
			else:
				order["remaining_amount"] = order["grand_total"]
		
		return sales_orders
		
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Get Sales Orders Error")
		return []


@frappe.whitelist()
def get_sales_order_details(name):
	"""
	Get full details of a specific sales order including items.
	
	Args:
		name: Sales Order name
	
	Returns:
		Sales Order document with items
	"""
	try:
		if not frappe.db.exists("Sales Order", name):
			frappe.throw(_("Sales Order {0} not found").format(name))
		
		sales_order = frappe.get_doc("Sales Order", name)
		
		# Prepare items with necessary fields for cart
		items = []
		for item in sales_order.items:
			item_data = {
				"item_code": item.item_code,
				"item_name": item.item_name,
				"qty": flt(item.qty),
				"uom": item.uom,
				"rate": flt(item.rate),
				"amount": flt(item.amount),
				"discount_percentage": flt(item.discount_percentage),
				"discount_amount": flt(item.discount_amount),
				"warehouse": item.warehouse,
				"description": item.description,
				"stock_uom": item.stock_uom,
				"conversion_factor": flt(item.conversion_factor or 1),
				"against_sales_order": name,
				"so_detail": item.name,
			}
			
			# Get item details for stock validation
			item_details = frappe.db.get_value(
				"Item",
				item.item_code,
				["is_stock_item", "has_batch_no", "has_serial_no"],
				as_dict=True
			)
			if item_details:
				item_data.update(item_details)
			
			items.append(item_data)
		
		return {
			"name": sales_order.name,
			"customer": sales_order.customer,
			"customer_name": sales_order.customer_name,
			"transaction_date": sales_order.transaction_date,
			"delivery_date": sales_order.delivery_date,
			"status": sales_order.status,
			"grand_total": flt(sales_order.grand_total),
			"total": flt(sales_order.total),
			"net_total": flt(sales_order.net_total),
			"per_billed": flt(sales_order.per_billed),
			"per_delivered": flt(sales_order.per_delivered),
			"company": sales_order.company,
			"currency": sales_order.currency,
			"order_type": sales_order.order_type,
			"items": items,
			"taxes": [t.as_dict() for t in sales_order.taxes] if sales_order.taxes else [],
			"additional_discount_percentage": flt(sales_order.additional_discount_percentage),
			"discount_amount": flt(sales_order.discount_amount),
		}
		
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Get Sales Order Details Error")
		raise


@frappe.whitelist()
def get_sales_order_summary(pos_profile=None):
	"""
	Get summary statistics of sales orders for the POS.
	
	Args:
		pos_profile: POS Profile name
	
	Returns:
		Dictionary with counts and totals by status
	"""
	try:
		filters = {"docstatus": ["in", [0, 1]]}  # Show both draft and submitted orders
		
		if pos_profile:
			company = frappe.db.get_value("POS Profile", pos_profile, "company")
			if company:
				filters["company"] = company
		
		# Get counts by status
		status_counts = frappe.get_all(
			"Sales Order",
			filters=filters,
			fields=["status", "count(*) as count", "sum(grand_total) as total"],
			group_by="status"
		)
		
		# Calculate totals
		total_orders = sum(s["count"] for s in status_counts)
		total_value = sum(flt(s["total"]) for s in status_counts)
		
		# Orders awaiting invoice (draft and submitted orders)
		awaiting_invoice = sum(
			s["count"] for s in status_counts 
			if s["status"] in ["Draft", "To Deliver and Bill", "To Bill", "To Deliver"]
		)
		
		return {
			"total_orders": total_orders,
			"total_value": total_value,
			"awaiting_invoice": awaiting_invoice,
			"by_status": status_counts
		}
		
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Get Sales Order Summary Error")
		return {
			"total_orders": 0,
			"total_value": 0,
			"awaiting_invoice": 0,
			"by_status": []
		}


@frappe.whitelist()
def make_invoice_from_sales_order(sales_order_name, pos_profile=None):
	"""
	Create a Sales Invoice from a Sales Order for POS.
	
	Args:
		sales_order_name: Name of the Sales Order
		pos_profile: POS Profile name
	
	Returns:
		Sales Invoice document (draft)
	"""
	try:
		from erpnext.selling.doctype.sales_order.sales_order import make_sales_invoice
		
		# Create Sales Invoice from Sales Order
		sales_invoice = make_sales_invoice(sales_order_name)
		
		# Set POS-specific fields
		sales_invoice.is_pos = 1
		sales_invoice.update_stock = 1
		
		if pos_profile:
			sales_invoice.pos_profile = pos_profile
			# Get company and other details from POS Profile
			profile = frappe.get_doc("POS Profile", pos_profile)
			if profile.company:
				sales_invoice.company = profile.company
		
		# Set posting date/time
		sales_invoice.posting_date = nowdate()
		sales_invoice.posting_time = frappe.utils.nowtime()
		
		# Return the invoice document without saving yet
		# The POS will handle saving and submission
		return sales_invoice.as_dict()
		
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Make Invoice From Sales Order Error")
		raise
