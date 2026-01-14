# Copyright (c) 2025, BWH Studios and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils.data import time_diff_in_seconds

from buzz.utils import only_if_app_installed


class BuzzEvent(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		from buzz.events.doctype.event_featured_speaker.event_featured_speaker import EventFeaturedSpeaker
		from buzz.events.doctype.event_payment_gateway.event_payment_gateway import EventPaymentGateway
		from buzz.events.doctype.schedule_item.schedule_item import ScheduleItem
		from buzz.proposals.doctype.sponsorship_deck_item.sponsorship_deck_item import SponsorshipDeckItem

		about: DF.TextEditor | None
		apply_tax: DF.Check
		auto_send_pitch_deck: DF.Check
		banner_image: DF.AttachImage | None
		card_image: DF.AttachImage | None
		category: DF.Link
		default_ticket_type: DF.Link | None
		end_date: DF.Date | None
		end_time: DF.Time | None
		external_registration_page: DF.Check
		featured_speakers: DF.Table[EventFeaturedSpeaker]
		free_webinar: DF.Check
		host: DF.Link
		is_published: DF.Check
		medium: DF.Literal["In Person", "Online"]
		meta_image: DF.AttachImage | None
		name: DF.Int | None
		payment_gateways: DF.Table[EventPaymentGateway]
		proposal: DF.Link | None
		registration_url: DF.Data | None
		route: DF.Data | None
		schedule: DF.Table[ScheduleItem]
		short_description: DF.SmallText | None
		sponsor_deck_attachments: DF.Table[SponsorshipDeckItem]
		sponsor_deck_cc: DF.SmallText | None
		sponsor_deck_email_template: DF.Link | None
		sponsor_deck_reply_to: DF.Data | None
		start_date: DF.Date
		start_time: DF.Time | None
		tax_label: DF.Data | None
		tax_percentage: DF.Percent
		ticket_email_template: DF.Link | None
		ticket_print_format: DF.Link | None
		time_zone: DF.Autocomplete | None
		title: DF.Data
		venue: DF.Link | None
	# end: auto-generated types

	def validate(self):
		self.validate_dates()
		self.validate_schedule()
		self.validate_route()
		self.validate_tax_settings()

	def validate_schedule(self):
		end_date = self.end_date or self.start_date
		for item in self.schedule:
			if item.date < self.start_date or item.date > end_date:
				frappe.throw(
					frappe._("<b>Schedule</b> row #{0}: <b>Date</b> must be within event dates").format(
						item.idx
					)
				)

			if time_diff_in_seconds(item.end_time, item.start_time) <= 0:
				frappe.throw(
					frappe._(
						"<b>Schedule</b> row #{0}: <b>End Time</b> must be after <b>Start Time</b>"
					).format(item.idx)
				)

			if item.date == self.start_date and self.start_time and item.start_time < self.start_time:
				frappe.throw(
					frappe._(
						"<b>Schedule</b> row #{0}: <b>Start Time</b> cannot be before event start time"
					).format(item.idx)
				)

			if item.date == end_date and self.end_time and item.end_time > self.end_time:
				frappe.throw(
					frappe._(
						"<b>Schedule</b> row #{0}: <b>End Time</b> cannot be after event end time"
					).format(item.idx)
				)

	def validate_dates(self):
		self.validate_from_to_dates("start_date", "end_date")
		if (
			(not self.end_date or self.start_date == self.end_date)
			and self.start_time
			and self.end_time
			and time_diff_in_seconds(self.end_time, self.start_time) <= 0
		):
			frappe.throw(frappe._("<b>End Time</b> must be after <b>Start Time</b>"))

	def validate_tax_settings(self):
		"""Set default tax values when tax is enabled."""
		if self.apply_tax:
			if not self.tax_label:
				self.tax_label = "GST"
			if not self.tax_percentage:
				self.tax_percentage = 18

	def validate_route(self):
		if self.is_published and not self.route:
			self.route = frappe.website.utils.cleanup_page_name(self.title).replace("_", "-")

	@frappe.whitelist()
	def after_insert(self):
		self.create_default_records()

	def create_default_records(self):
		records = [
			{"doctype": "Sponsorship Tier", "title": "Normal"},
			{"doctype": "Event Ticket Type", "title": "Normal"},
		]
		for record in records:
			frappe.get_doc({**record, "event": self.name}).insert(ignore_permissions=True)

	@frappe.whitelist()
	@only_if_app_installed("zoom_integration", raise_exception=True)
	def create_webinar_on_zoom(self):
		if not self.end_time:
			frappe.throw(frappe._("End time is needed for Zoom Webinar creation"))

		zoom_webinar = frappe.get_doc(
			{
				"doctype": "Zoom Webinar",
				"title": self.title,
				"date": self.start_date,
				"start_time": self.start_time,
				"duration": int(time_diff_in_seconds(self.end_time, self.start_time)),
				"timezone": self.time_zone,
				"template": frappe.get_cached_doc("Buzz Settings").default_webinar_template,
			}
		).insert()

		self.db_set("zoom_webinar", zoom_webinar.name)

		return zoom_webinar

	def on_update(self):
		self.update_zoom_webinar()

	@only_if_app_installed("zoom_integration")
	def update_zoom_webinar(self):
		if not self.zoom_webinar:
			return

		if (
			self.has_value_changed("start_date")
			or self.has_value_changed("end_time")
			or self.has_value_changed("start_time")
		):
			webinar = frappe.get_doc("Zoom Webinar", self.zoom_webinar)
			webinar.update(
				{
					"date": self.start_date,
					"start_time": self.start_time,
					"duration": int(time_diff_in_seconds(self.end_time, self.start_time)),
				}
			)
			webinar.save()


@frappe.whitelist()
def create_from_template(template_name: str, options: str, additional_fields: str = "{}") -> str:
	"""
	Create a new Buzz Event from a template.

	Args:
	    template_name: Name of the Event Template
	    options: JSON string of what to copy (e.g., {"category": 1, "ticket_types": 1, ...})
	    additional_fields: JSON string of additional field values for mandatory fields not in template

	Returns:
	    New Buzz Event document name
	"""
	if not frappe.has_permission("Event Template", "read"):
		frappe.throw(_("You don't have permission to use templates"))

	if not frappe.has_permission("Buzz Event", "create"):
		frappe.throw(_("You don't have permission to create events"))

	template = frappe.get_doc("Event Template", template_name)
	options = frappe.parse_json(options)
	additional_fields = frappe.parse_json(additional_fields)

	# Create new event with required fields
	event = frappe.new_doc("Buzz Event")
	event.title = f"New Event from {template.template_name}"
	event.start_date = frappe.utils.today()

	# Apply additional fields first (these are mandatory fields provided by user)
	for field, value in additional_fields.items():
		if value:
			event.set(field, value)

	# Field mapping for direct copy
	field_map = {
		"category": "category",
		"host": "host",
		"banner_image": "banner_image",
		"short_description": "short_description",
		"about": "about",
		"medium": "medium",
		"venue": "venue",
		"time_zone": "time_zone",
		"ticket_email_template": "ticket_email_template",
		"ticket_print_format": "ticket_print_format",
		"apply_tax": "apply_tax",
		"tax_label": "tax_label",
		"tax_percentage": "tax_percentage",
		"auto_send_pitch_deck": "auto_send_pitch_deck",
		"sponsor_deck_email_template": "sponsor_deck_email_template",
		"sponsor_deck_reply_to": "sponsor_deck_reply_to",
		"sponsor_deck_cc": "sponsor_deck_cc",
	}

	for option_key, field_name in field_map.items():
		if options.get(option_key):
			event.set(field_name, template.get(field_name))

	# Copy child tables
	if options.get("payment_gateways"):
		for pg in template.payment_gateways:
			event.append("payment_gateways", {"payment_gateway": pg.payment_gateway})

	if options.get("sponsor_deck_attachments"):
		for attachment in template.sponsor_deck_attachments:
			event.append("sponsor_deck_attachments", {"file": attachment.file})

	event.insert()

	# Create linked documents (Ticket Types, Add-ons, Custom Fields)
	if options.get("ticket_types"):
		for tt in template.template_ticket_types:
			ticket_type = frappe.new_doc("Event Ticket Type")
			ticket_type.event = event.name
			ticket_type.title = tt.title
			ticket_type.price = tt.price
			ticket_type.currency = tt.currency
			ticket_type.is_published = tt.is_published
			ticket_type.max_tickets_available = tt.max_tickets_available
			ticket_type.auto_unpublish_after = tt.auto_unpublish_after
			ticket_type.insert()

	if options.get("add_ons"):
		for addon in template.template_add_ons:
			add_on = frappe.new_doc("Ticket Add-on")
			add_on.event = event.name
			add_on.title = addon.title
			add_on.price = addon.price
			add_on.currency = addon.currency
			add_on.description = addon.description
			add_on.user_selects_option = addon.user_selects_option
			add_on.options = addon.options
			add_on.enabled = addon.enabled
			add_on.insert()

	if options.get("custom_fields"):
		for cf in template.template_custom_fields:
			custom_field = frappe.new_doc("Buzz Custom Field")
			custom_field.event = event.name
			custom_field.label = cf.label
			custom_field.fieldname = cf.fieldname
			custom_field.fieldtype = cf.fieldtype
			custom_field.options = cf.options
			custom_field.applied_to = cf.applied_to
			custom_field.enabled = cf.enabled
			custom_field.mandatory = cf.mandatory
			custom_field.placeholder = cf.placeholder
			custom_field.default_value = cf.default_value
			custom_field.order = cf.order
			custom_field.insert()

	return event.name
