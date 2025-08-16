# Copyright (c) 2025, BWH Studios and contributors
# For license information, please see license.txt
import json

import frappe
from frappe import _
from frappe.model.document import Document

from events.payments import mark_payment_as_received


class EventBooking(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		from events.ticketing.doctype.event_booking_attendee.event_booking_attendee import (
			EventBookingAttendee,
		)

		amended_from: DF.Link | None
		attendees: DF.Table[EventBookingAttendee]
		coupon_used: DF.Link | None
		currency: DF.Link
		event: DF.Link
		total_amount: DF.Currency
		user: DF.Link
	# end: auto-generated types

	def validate(self):
		self.set_total()
		self.set_currency()
		self.validate_ticket_availability()

	def set_currency(self):
		self.currency = self.attendees[0].currency

	def set_total(self):
		self.total_amount = 0

		# Get coupon info if coupon is used
		coupon_doc = None
		coupon_free_add_ons = set()
		if self.coupon_used:
			coupon_doc = frappe.get_cached_doc("Bulk Ticket Coupon", self.coupon_used)
			# Get list of free add-on names from the coupon
			for free_add_on in coupon_doc.free_add_ons:
				coupon_free_add_ons.add(free_add_on.add_on)

		for attendee in self.attendees:
			# Check if this attendee's ticket is covered by coupon (free)
			is_coupon_ticket = coupon_doc and str(attendee.ticket_type) == str(coupon_doc.ticket_type)

			if not is_coupon_ticket:
				self.total_amount += attendee.amount

			# Handle add-ons
			if attendee.add_ons:
				attendee.add_on_total = self.get_attendee_add_on_total(attendee.add_ons, coupon_free_add_ons)
				attendee.number_of_add_ons = attendee.get_number_of_add_ons()
				self.total_amount += attendee.add_on_total

	def get_attendee_add_on_total(self, add_ons_doc_name, coupon_free_add_ons):
		"""Calculate add-on total considering free add-ons from coupon."""
		if not add_ons_doc_name:
			return 0

		doc = frappe.get_cached_doc("Attendee Ticket Add-on", add_ons_doc_name)
		add_ons = doc.add_ons
		total = 0

		for add_on in add_ons:
			# If this add-on is in the coupon's free add-ons, don't charge for it
			if add_on.add_on not in coupon_free_add_ons:
				total += add_on.price

		return total

	def validate_ticket_availability(self):
		num_tickets_by_type = {}
		for attendee in self.attendees:
			if attendee.ticket_type not in num_tickets_by_type:
				num_tickets_by_type[attendee.ticket_type] = 0
			num_tickets_by_type[attendee.ticket_type] += 1

		for ticket_type, num_tickets in num_tickets_by_type.items():
			ticket_type_doc = frappe.get_cached_doc("Event Ticket Type", ticket_type)
			if not ticket_type_doc.is_published:
				frappe.throw(frappe._(f"{ticket_type} tickets no longer available!"))

			if not ticket_type_doc.are_tickets_available(num_tickets):
				frappe.throw(
					frappe._(
						f"Only {ticket_type_doc.remaining_tickets} tickets available for {ticket_type}, you are trying to book {num_tickets}!"
					)
				)

	def on_submit(self):
		self.generate_tickets()

	def generate_tickets(self):
		for attendee in self.attendees:
			ticket = frappe.new_doc("Event Ticket")
			ticket.event = self.event
			ticket.booking = self.name
			ticket.ticket_type = attendee.ticket_type
			ticket.attendee_name = attendee.full_name
			ticket.attendee_email = attendee.email
			ticket.coupon_used = self.coupon_used

			if attendee.add_ons:
				add_ons_list = frappe.get_cached_doc("Attendee Ticket Add-on", attendee.add_ons).add_ons
				ticket.add_ons = add_ons_list
			ticket.flags.ignore_permissions = 1
			ticket.insert().submit()

	def on_payment_authorized(self, payment_status: str):
		if payment_status in ("Authorized", "Completed"):
			# payment success, submit the booking
			self.update_payment_record()

	def update_payment_record(self):
		try:
			mark_payment_as_received(self.doctype, self.name)
			self.flags.ignore_permissions = 1
			self.submit()
		except Exception:
			frappe.log_error(frappe.get_traceback(), _("Booking Failed"))
			frappe.throw(frappe._("Booking Failed! Please contact support."))
