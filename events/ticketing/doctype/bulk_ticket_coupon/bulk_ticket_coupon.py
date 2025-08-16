# Copyright (c) 2025, BWH Studios and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class BulkTicketCoupon(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		from events.ticketing.doctype.free_add_on.free_add_on import FreeAddOn

		code: DF.Data | None
		event: DF.Link
		free_add_ons: DF.Table[FreeAddOn]
		number_of_granted_tickets: DF.Int
		ticket_type: DF.Link
	# end: auto-generated types

	def autoname(self):
		if not self.code:
			self.code = frappe.generate_hash(length=6)

	def is_used_up(self):
		return self.number_of_granted_tickets == self.number_of_claimed_tickets

	@property
	def number_of_claimed_tickets(self):
		return frappe.db.count("Event Ticket", {"coupon_used": self.name, "docstatus": 1})
