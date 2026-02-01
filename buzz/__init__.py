__version__ = "0.0.1"

import os

import frappe

if os.environ.get("FRAPPE_IN_TEST"):
	frappe.in_test = True
