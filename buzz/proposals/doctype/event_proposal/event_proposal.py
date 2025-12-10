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

		additional_notes: DF.SmallText | None
		description: DF.TextEditor | None
		event_category: DF.Link
		host_company: DF.Data | None
		naming_series: DF.Literal["EPR-.###"]
		status: DF.Literal["Received", "In Review", "Approved", "Rejected"]
		title: DF.Data
	# end: auto-generated types

	pass
