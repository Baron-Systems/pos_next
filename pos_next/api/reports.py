import datetime

import frappe
from frappe import _
from frappe.utils import flt

@frappe.whitelist()
def get_shift_report(pos_profile):
	"""
	Get shift report data for the current open shift and all shifts
	"""
	if not pos_profile:
		return {
			"invoice_count": 0,
			"total_sales": 0,
			"average_invoice": 0,
			"customer_count": 0,
			"out_of_stock_items": [],
			"top_products": []
		}
	
	# Get current open shift for this POS profile
	open_shift = frappe.db.get_value(
		"POS Opening Shift",
		{
			"pos_profile": pos_profile,
			"status": "Open",
			"docstatus": 1
		},
		"name"
	)
	
	if not open_shift:
		return {
			"invoice_count": 0,
			"total_sales": 0,
			"average_invoice": 0,
			"customer_count": 0,
			"out_of_stock_items": [],
			"top_products": []
		}
	
	# Get invoices for current shift
	invoices = frappe.db.get_all(
		"Sales Invoice",
		filters={
			"posa_pos_opening_shift": open_shift,
			"docstatus": 1,
			"is_return": 0
		},
		fields=["name", "grand_total", "customer"]
	)
	
	invoice_count = len(invoices)
	total_sales = sum(flt(inv.grand_total) for inv in invoices)
	average_invoice = total_sales / invoice_count if invoice_count > 0 else 0
	
	# Get unique customer count
	customers = set(inv.customer for inv in invoices if inv.customer)
	customer_count = len(customers)
	
	# Get out of stock items (qty <= 0)
	out_of_stock_items = frappe.db.sql("""
		SELECT 
			b.item_code,
			i.item_name,
			b.warehouse,
			b.actual_qty
		FROM 
			`tabBin` b
		INNER JOIN 
			`tabItem` i ON b.item_code = i.item_code
		WHERE 
			b.actual_qty <= 0
			AND i.is_stock_item = 1
			AND i.disabled = 0
		ORDER BY 
			b.actual_qty ASC
	""", as_dict=True)
	
	# Get period filter
	period_months = int(frappe.form_dict.get("period_months", 1))
	start_date = datetime.datetime.now() - datetime.timedelta(days=30 * period_months)
	
	# Get top 20 products across all shifts for this POS profile within period
	top_products = frappe.db.sql("""
		SELECT 
			isi.item_code,
			isi.item_name,
			SUM(isi.qty) as qty,
			SUM(isi.amount) as total
		FROM 
			`tabSales Invoice Item` isi
		INNER JOIN 
			`tabSales Invoice` si ON isi.parent = si.name
		WHERE 
			si.pos_profile = %s
			AND si.docstatus = 1
			AND si.is_return = 0
			AND si.posting_date >= %s
		GROUP BY 
			isi.item_code, isi.item_name
		ORDER BY 
			qty DESC
		LIMIT 20
	""", (pos_profile, start_date.date()), as_dict=True)
	
	return {
		"invoice_count": invoice_count,
		"total_sales": total_sales,
		"average_invoice": average_invoice,
		"customer_count": customer_count,
		"out_of_stock_items": out_of_stock_items,
		"top_products": top_products
	}
