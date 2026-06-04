import frappe
from frappe import _
from frappe.model.document import Document


class BuzzEventForm(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		auto_close_at: DF.Datetime | None
		closed_message: DF.SmallText | None
		closed_title: DF.Data | None
		form_doctype: DF.Link
		login_required: DF.Check
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		publish: DF.Check
		route: DF.Data
		success_message: DF.MarkdownEditor | None
		success_title: DF.Data | None
	# end: auto-generated types

	def validate(self):
		self.validate_unique_route()

	def validate_unique_route(self):
		for row in self.parentdoc.custom_forms:
			if row.name != self.name and row.route == self.route:
				frappe.throw(
					_("Duplicate route '{0}' in custom forms. Each form must have a unique route.").format(
						self.route
					)
				)
