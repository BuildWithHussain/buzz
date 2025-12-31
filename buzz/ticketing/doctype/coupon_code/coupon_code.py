# Copyright (c) 2025, BWH Studios and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class CouponCode(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from buzz.ticketing.doctype.coupon_free_add_on.coupon_free_add_on import CouponFreeAddon
		from frappe.types import DF

		code: DF.Data | None
		coupon_type: DF.Literal["Free Tickets", "Discount"]
		discount_type: DF.Literal["Percentage", "Flat Amount"]
		discount_value: DF.Float
		event: DF.Link | None
		event_category: DF.Link | None
		free_add_ons: DF.Table[CouponFreeAddon]
		is_active: DF.Check
		max_usage_count: DF.Int
		number_of_free_tickets: DF.Int
		ticket_type: DF.Link | None
	# end: auto-generated types

	def autoname(self):
		if not self.code:
			self.code = frappe.generate_hash(length=8).upper()

	def validate(self):
		self.validate_discount_value()
		self.validate_scope()
		self.validate_free_tickets_event()

	def validate_discount_value(self):
		if self.coupon_type == "Discount":
			if self.discount_value <= 0:
				frappe.throw(_("Discount value must be greater than 0"))
			if self.discount_type == "Percentage" and self.discount_value > 100:
				frappe.throw(_("Percentage discount cannot exceed 100%"))

	def validate_scope(self):
		if self.event and self.event_category:
			frappe.throw(_("Select either Event or Category, not both"))

	def validate_free_tickets_event(self):
		if self.coupon_type == "Free Tickets" and not self.event:
			frappe.throw(_("Event is required for Free Tickets coupon"))

	def is_valid_for_event(self, event_name):
		if not self.is_active:
			return False, _("Coupon is not active")

		if not self.event and not self.event_category:
			return True, ""

		if self.event and str(self.event) != str(event_name):
			return False, _("Coupon is not valid for this event")
		if self.event_category:
			event_category = frappe.db.get_value("Buzz Event", event_name, "category")
			if event_category and str(event_category) != str(self.event_category):
				return False, _("Coupon is not valid for this event category")

		return True, ""

	def get_times_used(self):
		return frappe.db.count("Event Booking", {"coupon_code": self.name, "docstatus": 1})

	def get_free_tickets_claimed(self):
		"""Calculate total attendees from all submitted bookings using this coupon"""
		from frappe.query_builder.functions import Count

		EventBooking = frappe.qb.DocType("Event Booking")
		EventBookingAttendee = frappe.qb.DocType("Event Booking Attendee")

		count = (
			frappe.qb.from_(EventBookingAttendee)
			.join(EventBooking)
			.on(EventBooking.name == EventBookingAttendee.parent)
			.where(EventBooking.coupon_code == self.name)
			.where(EventBooking.docstatus == 1)
			.select(Count(EventBookingAttendee.name))
		).run()[0][0]

		return count or 0

	def is_usage_available(self):
		if self.max_usage_count > 0:
			if self.get_times_used() >= self.max_usage_count:
				return False, _("Coupon usage limit reached")
		return True, ""

	@property
	def times_used(self):
		return self.get_times_used()

	@property
	def free_tickets_claimed(self):
		return self.get_free_tickets_claimed()