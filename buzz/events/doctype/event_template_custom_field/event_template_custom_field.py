# Copyright (c) 2025, Frappe Technologies and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class EventTemplateCustomField(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		applied_to: DF.Literal["Booking", "Ticket"]
		default_value: DF.Data | None
		enabled: DF.Check
		fieldname: DF.Data | None
		fieldtype: DF.Literal["Data", "Phone", "Email", "Select", "Date", "Number"]
		label: DF.Data
		mandatory: DF.Check
		options: DF.SmallText | None
		order: DF.Int
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		placeholder: DF.Data | None
	# end: auto-generated types

	pass
