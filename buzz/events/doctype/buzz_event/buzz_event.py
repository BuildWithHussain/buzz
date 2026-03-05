# Copyright (c) 2025, BWH Studios and contributors
# For license information, please see license.txt

import frappe
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
		from buzz.events.doctype.schedule_item.schedule_item import ScheduleItem
		from buzz.proposals.doctype.sponsorship_deck_item.sponsorship_deck_item import SponsorshipDeckItem

		about: DF.TextEditor | None
		auto_send_pitch_deck: DF.Check
		banner_image: DF.AttachImage | None
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
		name: DF.Int | None
		payment_gateway: DF.Link | None
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
def get_clone_dialog_html(template_name, context=None):
	"""Render a Jinja template from buzz/templates/ and return the HTML string."""
	import json
	import os

	template_path = os.path.join(
		frappe.get_app_path("buzz"), "templates", "clone_event_dialog", f"{template_name}.html"
	)
	if not os.path.exists(template_path):
		frappe.throw(frappe._("Template {0} not found").format(template_name))

	with open(template_path) as f:
		template_str = f.read()

	ctx = {}
	if context:
		ctx = json.loads(context) if isinstance(context, str) else context

	return frappe.render_template(template_str, ctx)


@frappe.whitelist()
def clone_buzz_event(name, dates, host=None):
	"""
	Clone a Buzz Event for each entry in `dates`.

	Args:
		name    : name of the source Buzz Event
		dates   : JSON list of {"start_date": "YYYY-MM-DD", "start_time": "HH:MM:SS"}
		host    : optional Event Host to override on clones

	Returns:
		list of newly created Buzz Event names
	"""
	import json

	from frappe.utils import add_days, date_diff

	if isinstance(dates, str):
		dates = json.loads(dates)

	if not dates:
		frappe.throw(frappe._("Please provide at least one date."))

	source = frappe.get_doc("Buzz Event", name)

	# Preserve the original duration (end_date - start_date offset in days)
	duration_days = 0
	if source.end_date and source.start_date:
		duration_days = date_diff(source.end_date, source.start_date)

	created = []

	for entry in dates:
		new_doc = frappe.copy_doc(source)
		new_doc.start_date = entry.get("start_date")
		new_doc.start_time = entry.get("start_time") or source.start_time

		if duration_days:
			new_doc.end_date = add_days(new_doc.start_date, duration_days)
		else:
			new_doc.end_date = new_doc.start_date

		# New clone starts as a draft
		new_doc.is_published = 0
		new_doc.route = ""

		if host:
			new_doc.host = host

		# Adjust schedule item dates by the same offset
		if source.start_date and new_doc.schedule:
			for row in new_doc.schedule:
				if row.date:
					row_offset = date_diff(row.date, source.start_date)
					row.date = add_days(new_doc.start_date, row_offset)

		new_doc.insert()
		created.append(new_doc.name)

	return created
