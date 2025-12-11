# Copyright (c) 2025, BWH Studios and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class EventCategory(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		banner_image: DF.AttachImage | None
		description: DF.SmallText | None
		enabled: DF.Check
		icon_svg: DF.Code | None
		slug: DF.Data | None
	# end: auto-generated types

	def validate(self):
		if not self.slug:
			self.set_slug()

	def set_slug(self):
		self.slug = frappe.website.utils.cleanup_page_name(self.name).replace("_", "-")
