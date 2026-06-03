# -*- coding: utf-8 -*-
# API module for POS Next

import frappe

# Import API modules to make them accessible
from . import invoices
from . import items
from . import shifts
from . import pos_profile
from . import customers
from . import offers
from . import promotions
from . import utilities
from . import sales_orders
from . import sales_order_utils
from . import sales_order_status
from . import sales_order_status_force
from . import sales_order_status_force_direct
from . import customer_payment

@frappe.whitelist(allow_guest=True)
def ping():
    """Simple ping endpoint for connectivity checks"""
    return "pong"
