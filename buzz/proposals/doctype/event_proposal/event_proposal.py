# Copyright (c) 2025, BWH Studios and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class EventProposal(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		end_date: DF.Date | None
		start_date: DF.Date
		title: DF.Data
	# end: auto-generated types

	pass
