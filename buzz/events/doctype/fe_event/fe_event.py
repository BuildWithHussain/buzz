# Copyright (c) 2025, BWH Studios and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class FEEvent(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		from buzz.events.doctype.event_featured_speaker.event_featured_speaker import EventFeaturedSpeaker
		from buzz.events.doctype.schedule_item.schedule_item import ScheduleItem

		about: DF.TextEditor | None
		banner_image: DF.AttachImage | None
		category: DF.Link
		end_date: DF.Date | None
		end_time: DF.Time | None
		external_registration_page: DF.Check
		featured_speakers: DF.Table[EventFeaturedSpeaker]
		host: DF.Link
		is_published: DF.Check
		medium: DF.Literal["In Person", "Online"]
		name: DF.Int | None
		payment_gateway: DF.Link | None
		registration_url: DF.Data | None
		route: DF.Data | None
		schedule: DF.Table[ScheduleItem]
		short_description: DF.SmallText | None
		start_date: DF.Date
		start_time: DF.Time | None
		ticket_email_template: DF.Link | None
		ticket_print_format: DF.Link | None
		time_zone: DF.Autocomplete | None
		title: DF.Data
		venue: DF.Link | None
	# end: auto-generated types

	def validate(self):
		self.validate_route()

	def validate_route(self):
		if self.is_published and not self.route:
			self.route = frappe.website.utils.cleanup_page_name(self.title).replace("_", "-")

	@frappe.whitelist()
	def check_in(self, ticket_id: str, track: str | None = None):
		frappe.get_doc({"doctype": "Event Check In", "ticket": ticket_id, "track": track}).insert().submit()

	def after_insert(self):
		self.create_default_records()

	def create_default_records(self):
		records = [
			{"doctype": "Sponsorship Tier", "title": "Normal"},
			{"doctype": "Event Ticket Type", "title": "Normal"},
		]
		for record in records:
			frappe.get_doc({**record, "event": self.name}).insert(ignore_permissions=True)
