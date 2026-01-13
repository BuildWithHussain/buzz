# Copyright (c) 2025, BWH Studios and Contributors
# See license.txt

from unittest.mock import patch

import frappe
from frappe.tests import IntegrationTestCase

EXTRA_TEST_RECORD_DEPENDENCIES = []
IGNORE_TEST_RECORD_DEPENDENCIES = ["Bulk Ticket Coupon"]


class TestEventTicketEmail(IntegrationTestCase):
	"""Tests for Event Ticket email sending with template fallback logic."""

	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		cls.test_event = frappe.get_doc("Buzz Event", {"route": "test-route"})
		cls.test_event.ticket_email_template = None
		cls.test_event.save()

		# Clear global settings
		settings = frappe.get_doc("Buzz Settings")
		settings.default_ticket_email_template = None
		settings.save()

	def setUp(self):
		self.test_ticket_type = frappe.get_doc(
			{
				"doctype": "Event Ticket Type",
				"event": self.test_event.name,
				"title": "Email Test Ticket",
				"price": 100,
			}
		).insert()

		self.test_ticket = frappe.get_doc(
			{
				"doctype": "Event Ticket",
				"event": self.test_event.name,
				"ticket_type": self.test_ticket_type.name,
				"attendee_name": "Test Attendee",
				"attendee_email": "test@example.com",
			}
		).insert()

	def tearDown(self):
		frappe.delete_doc("Event Ticket", self.test_ticket.name, force=True)
		frappe.delete_doc("Event Ticket Type", self.test_ticket_type.name, force=True)

	def _create_template(self, name, subject_prefix):
		if frappe.db.exists("Email Template", name):
			frappe.delete_doc("Email Template", name, force=True)
		return frappe.get_doc(
			{
				"doctype": "Email Template",
				"name": name,
				"subject": f"{subject_prefix} - {{{{ event_title }}}}",
				"response": f"<p>{subject_prefix} content</p>",
			}
		).insert()

	@patch("frappe.sendmail")
	def test_uses_event_template_when_set(self, mock_sendmail):
		template = self._create_template("Event Ticket Template", "EVENT")
		try:
			self.test_event.ticket_email_template = template.name
			self.test_event.save()

			self.test_ticket.send_ticket_email(now=True)

			mock_sendmail.assert_called_once()
			self.assertIn("EVENT", mock_sendmail.call_args[1]["subject"])
		finally:
			self.test_event.ticket_email_template = None
			self.test_event.save()
			frappe.delete_doc("Email Template", template.name, force=True)

	@patch("frappe.sendmail")
	def test_falls_back_to_global_template(self, mock_sendmail):
		template = self._create_template("Global Ticket Template", "GLOBAL")
		try:
			self.test_event.ticket_email_template = None
			self.test_event.save()

			settings = frappe.get_doc("Buzz Settings")
			settings.default_ticket_email_template = template.name
			settings.save()

			self.test_ticket.send_ticket_email(now=True)

			mock_sendmail.assert_called_once()
			self.assertIn("GLOBAL", mock_sendmail.call_args[1]["subject"])
		finally:
			settings.default_ticket_email_template = None
			settings.save()
			frappe.delete_doc("Email Template", template.name, force=True)

	@patch("frappe.sendmail")
	def test_event_template_takes_precedence(self, mock_sendmail):
		event_template = self._create_template("Event Template", "EVENT")
		global_template = self._create_template("Global Template", "GLOBAL")
		try:
			self.test_event.ticket_email_template = event_template.name
			self.test_event.save()

			settings = frappe.get_doc("Buzz Settings")
			settings.default_ticket_email_template = global_template.name
			settings.save()

			self.test_ticket.send_ticket_email(now=True)

			mock_sendmail.assert_called_once()
			self.assertIn("EVENT", mock_sendmail.call_args[1]["subject"])
			self.assertNotIn("GLOBAL", mock_sendmail.call_args[1]["subject"])
		finally:
			self.test_event.ticket_email_template = None
			self.test_event.save()
			settings.default_ticket_email_template = None
			settings.save()
			frappe.delete_doc("Email Template", event_template.name, force=True)
			frappe.delete_doc("Email Template", global_template.name, force=True)

	@patch("frappe.sendmail")
	def test_uses_inline_template_when_none_configured(self, mock_sendmail):
		self.test_event.ticket_email_template = None
		self.test_event.save()

		settings = frappe.get_doc("Buzz Settings")
		settings.default_ticket_email_template = None
		settings.save()

		self.test_ticket.send_ticket_email(now=True)

		mock_sendmail.assert_called_once()
		self.assertEqual(mock_sendmail.call_args[1]["template"], "ticket")
