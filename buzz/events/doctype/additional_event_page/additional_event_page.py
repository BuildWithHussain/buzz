# Copyright (c) 2025, BWH Studios and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class AdditionalEventPage(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		content: DF.TextEditor
		event: DF.Link
		is_published: DF.Check
		route: DF.Data | None
		title: DF.Data
	# end: auto-generated types

	def validate(self):
		self.validate_route()
		self.validate_duplicate()

	def validate_route(self):
		if self.is_published and not self.route:
			self.route = frappe.website.utils.cleanup_page_name(self.title).replace("_", "-")

	def validate_duplicate(self):
		if not self.route:
			return

		if frappe.db.exists(
			"Additional Event Page",
			{"route": self.route, "event": self.event, "name": ["!=", self.name]},
		):
			frappe.throw(
				frappe._("An Additional Event Page with the same route already exists for this event.")
			)
