# Copyright (c) 2025, BWH Studios and contributors
# For license information, please see license.txt

import frappe
from frappe.core.api.user_invitation import invite_by_email
from frappe.model.document import Document


class EventTicket(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		from buzz.ticketing.doctype.ticket_add_on_value.ticket_add_on_value import TicketAddonValue

		add_ons: DF.Table[TicketAddonValue]
		amended_from: DF.Link | None
		attendee_email: DF.Data
		attendee_name: DF.Data
		booking: DF.Link | None
		coupon_used: DF.Link | None
		event: DF.Link | None
		qr_code: DF.AttachImage | None
		ticket_type: DF.Link
	# end: auto-generated types

	def before_submit(self):
		self.validate_coupon_usage()
		self.generate_qr_code()

	def on_submit(self):
		try:
			self.send_ticket_email()
		except Exception as e:
			frappe.log_error("Error sending ticket email: " + str(e))

		try:
			self.send_user_invitation()
		except Exception as e:
			frappe.log_error("Error sending user invitation: " + str(e))

	def send_user_invitation(self):
		invite_by_email(
			emails=self.attendee_email,
			roles=["Buzz User"],
			redirect_to_path="/dashboard/account/tickets",
			app_name="buzz",
		)

	def send_ticket_email(self, now: bool = False):
		event_title, ticket_template, ticket_print_format, venue = frappe.get_cached_value(
			"FE Event", self.event, ["title", "ticket_email_template", "ticket_print_format", "venue"]
		)
		subject = frappe._("Your ticket to {0} 🎟️").format(event_title)
		args = {
			"doc": self,
			"event_doc": frappe.get_cached_doc("FE Event", self.event),
			"event_title": event_title,
			"venue": venue,
		}

		if ticket_template:
			from frappe.email.doctype.email_template.email_template import get_email_template

			email_template = get_email_template(ticket_template, args)
			subject = email_template.get("subject")
			content = email_template.get("message")

		frappe.sendmail(
			recipients=[self.attendee_email],
			subject=subject,
			content=content if ticket_template else None,
			template="ticket" if not ticket_template else None,
			args=args,
			reference_doctype=self.doctype,
			reference_name=self.name,
			now=now,
			attachments=[
				{
					"print_format_attachment": 1,
					"doctype": self.doctype,
					"name": self.name,
					"print_format": ticket_print_format or "Standard Ticket",
				}
			],
		)

	def validate_coupon_usage(self):
		if not self.coupon_used:
			return

		coupon = frappe.get_cached_doc("Bulk Ticket Coupon", self.coupon_used)
		if coupon.is_used_up():
			frappe.throw(frappe._("Coupon has been already used up maximum number of times!"))

	def generate_qr_code(self):
		qr_data = make_qr_image_with_data(f"{self.name}")
		qr_code_file = frappe.get_doc(
			{
				"doctype": "File",
				"content": qr_data,
				"attached_to_doctype": "Event Ticket",
				"attached_to_name": self.name,
				"attached_to_field": "qr_code",
				"file_name": f"ticket-qr-code-{self.name}.png",
			}
		).save(ignore_permissions=True)
		self.qr_code = qr_code_file.file_url


def make_qr_image_with_data(data: str) -> bytes:
	import io

	import qrcode
	from qrcode.image.styledpil import StyledPilImage
	from qrcode.image.styles.moduledrawers.pil import HorizontalBarsDrawer

	qr = qrcode.QRCode(
		version=1,
		error_correction=qrcode.constants.ERROR_CORRECT_H,
		box_size=10,
		border=4,
	)
	qr.add_data(data)
	qr.make(fit=True)

	img = qr.make_image(image_factory=StyledPilImage, module_drawer=HorizontalBarsDrawer())
	output = io.BytesIO()
	img.save(output, format="PNG")
	return output.getvalue()
