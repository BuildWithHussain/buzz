# Copyright (c) 2025, BWH Studios and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
from frappe.utils.data import get_url_to_form


class EventProposal(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		about: DF.TextEditor
		additional_notes: DF.SmallText | None
		amended_from: DF.Link | None
		category: DF.Link
		end_date: DF.Date | None
		end_time: DF.Time | None
		free_webinar: DF.Check
		host: DF.Link | None
		host_company: DF.Data | None
		host_company_logo: DF.AttachImage | None
		medium: DF.Literal["Online", "In Person"]
		naming_series: DF.Literal["EPR-.###"]
		short_description: DF.SmallText | None
		start_date: DF.Date
		start_time: DF.Time | None
		status: DF.Literal["Received", "In Review", "Approved", "Event Created", "Rejected"]
		title: DF.Data
	# end: auto-generated types

	def before_submit(self):
		if self.status not in ("Approved", "Rejected"):
			frappe.throw(frappe._("Only Approved or Rejected proposals can be submitted."))

		self.create_event()

	def create_event(self):
		if self.status == "Rejected":
			return

		if not self.host:
			frappe.throw(frappe._("Please create or set a Host before submitting the proposal."))

		buzz_event = get_mapped_doc(
			"Event Proposal", self.name, {"Event Proposal": {"doctype": "Buzz Event"}}
		)
		buzz_event.proposal = self.name
		buzz_event.insert()

		self.status = "Event Created"

		frappe.msgprint(
			frappe._("Buzz Event {0} created successfully.").format(
				f'<a href="{get_url_to_form("Buzz Event", buzz_event.name)}">{buzz_event.title}</a>'
			)
		)
