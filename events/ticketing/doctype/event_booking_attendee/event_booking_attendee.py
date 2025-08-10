# Copyright (c) 2025, BWH Studios and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class EventBookingAttendee(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		add_on_total: DF.Currency
		add_ons: DF.Link | None
		amount: DF.Currency
		currency: DF.Link
		email: DF.Data
		full_name: DF.Data
		number_of_add_ons: DF.Int
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		ticket_type: DF.Link
	# end: auto-generated types

	def get_add_on_total(self):
		if not self.add_ons:
			return 0
		doc = frappe.get_cached_doc("Attendee Ticket Add-on", self.add_ons)
		add_ons = doc.add_ons
		return sum(r.price for r in add_ons)

	def get_number_of_add_ons(self):
		return len(frappe.get_cached_doc("Attendee Ticket Add-on", self.add_ons).add_ons)
