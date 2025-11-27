# Copyright (c) 2025, BWH Studios and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class BuzzCustomField(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		applied_to: DF.Literal["Booking", "Ticket"]
		enabled: DF.Check
		event: DF.Link
		fieldname: DF.Data | None
		fieldtype: DF.Literal["Data", "Phone", "Email", "Select"]
		label: DF.Data
		mandatory: DF.Check
		options: DF.SmallText | None
		order: DF.Int
		placeholder: DF.Data | None
	# end: auto-generated types

	pass
