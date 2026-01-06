# Copyright (c) 2025, BWH Studios and contributors
# For license information, please see license.txt
import json

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import get_datetime, get_datetime_in_timezone, now_datetime

from buzz.payments import mark_payment_as_received


class EventBooking(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		from buzz.events.doctype.utm_parameter.utm_parameter import UTMParameter
		from buzz.ticketing.doctype.additional_field.additional_field import AdditionalField
		from buzz.ticketing.doctype.event_booking_attendee.event_booking_attendee import EventBookingAttendee

		additional_fields: DF.Table[AdditionalField]
		amended_from: DF.Link | None
		attendees: DF.Table[EventBookingAttendee]
		currency: DF.Link
		event: DF.Link
		naming_series: DF.Literal["B.###"]
		net_amount: DF.Currency
		tax_amount: DF.Currency
		tax_percentage: DF.Percent
		total_amount: DF.Currency
		user: DF.Link
		utm_parameters: DF.Table[UTMParameter]
	# end: auto-generated types

	def validate(self):
		self.validate_event_has_ended()
		self.validate_ticket_availability()
		self.fetch_amounts_from_ticket_types()
		self.set_currency()
		self.set_total()
		self.apply_taxes_if_applicable()

	def set_currency(self):
		self.currency = self.attendees[0].currency

	def set_total(self):
		self.net_amount = 0
		for attendee in self.attendees:
			self.net_amount += attendee.amount
			if attendee.add_ons:
				attendee.add_on_total = attendee.get_add_on_total()
				attendee.number_of_add_ons = attendee.get_number_of_add_ons()
				self.net_amount += attendee.add_on_total
		self.total_amount = self.net_amount

	def apply_taxes_if_applicable(self):
		"""Apply tax based on event-level tax configuration."""
		self.tax_percentage = 0
		self.tax_amount = 0
		self.tax_label = None

		event = frappe.get_cached_doc("Buzz Event", self.event)
		if not event.apply_tax:
			return

		self.tax_label = event.tax_label or "Tax"
		self.tax_percentage = event.tax_percentage or 0

		if self.tax_percentage > 0:
			self.tax_amount = self.net_amount * (self.tax_percentage / 100)
			self.total_amount += self.tax_amount

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

	def fetch_amounts_from_ticket_types(self):
		for attendee in self.attendees:
			price, currency = frappe.get_cached_value(
				"Event Ticket Type", attendee.ticket_type, ["price", "currency"]
			)
			if attendee.amount is None:
				attendee.amount = price
			if not attendee.currency:
				attendee.currency = currency

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

			if attendee.add_ons:
				add_ons_list = frappe.get_cached_doc("Attendee Ticket Add-on", attendee.add_ons).add_ons
				ticket.add_ons = add_ons_list

			# Add custom fields from attendee to ticket
			if attendee.custom_fields:
				custom_fields_data = attendee.custom_fields
				if isinstance(custom_fields_data, str):
					try:
						custom_fields_data = json.loads(custom_fields_data)
					except (json.JSONDecodeError, TypeError):
						custom_fields_data = {}

				# Get custom field definitions for this event to get proper labels and types
				custom_field_defs = frappe.db.get_all(
					"Buzz Custom Field",
					filters={"event": self.event, "enabled": 1, "applied_to": "Ticket"},
					fields=["fieldname", "label", "fieldtype"],
				)
				custom_field_map = {cf["fieldname"]: cf for cf in custom_field_defs}

				for field_name, field_value in custom_fields_data.items():
					if field_value and field_name in custom_field_map:
						field_def = custom_field_map[field_name]
						ticket.append(
							"additional_fields",
							{
								"fieldname": field_name,
								"value": str(field_value),
								"label": field_def["label"],
								"fieldtype": field_def["fieldtype"],
							},
						)

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

	def on_cancel(self):
		self.ignore_linked_doctypes = ["Ticket Cancellation Request"]
		self.cancel_all_tickets()

	def cancel_all_tickets(self):
		tickets = frappe.db.get_all("Event Ticket", filters={"booking": self.name}, pluck="name")
		for ticket in tickets:
			frappe.get_cached_doc("Event Ticket", ticket).cancel()

	def validate_event_has_ended(self):
		event_doc = frappe.get_cached_doc("Buzz Event", self.event)

		if not event_doc.end_date:
			return

		time_part = str(event_doc.end_time) if event_doc.end_time else "23:59:59"
		event_end_naive = get_datetime(f"{event_doc.end_date} {time_part}")

		if event_doc.time_zone:
			current_time_aware = get_datetime_in_timezone(event_doc.time_zone)
			current_time_at_venue = current_time_aware.replace(tzinfo=None)

			if current_time_at_venue > event_end_naive:
				frappe.throw(_("Cannot book tickets. This event has already ended."), title=_("Event Ended"))

		else:
			if now_datetime() > event_end_naive:
				frappe.throw(_("Cannot book tickets. This event has already ended."), title=_("Event Ended"))
