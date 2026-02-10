# Copyright (c) 2025, BWH Studios and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase

from buzz.events.doctype.buzz_event.buzz_event import create_from_template
from buzz.events.doctype.event_template.event_template import create_template_from_event


class TestBuzzEvent(FrappeTestCase):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		cls.create_test_fixtures()

	@classmethod
	def create_test_fixtures(cls):
		if not frappe.db.exists("Event Category", "Test Category"):
			frappe.get_doc({"doctype": "Event Category", "category_name": "Test Category"}).insert(
				ignore_permissions=True
			)

		if not frappe.db.exists("Event Host", "Test Host"):
			frappe.get_doc({"doctype": "Event Host", "host_name": "Test Host"}).insert(
				ignore_permissions=True
			)

	def tearDown(self):
		frappe.db.rollback()

	# ==================== Create from Template Tests ====================

	def test_create_from_template_copies_direct_fields(self):
		"""Test that direct fields are copied from template to event"""
		template = frappe.get_doc(
			{
				"doctype": "Event Template",
				"template_name": "Direct Fields Template",
				"category": "Test Category",
				"host": "Test Host",
				"medium": "Online",
				"about": "About text",
				"short_description": "Short desc",
				"time_zone": "Asia/Kolkata",
				"allow_guest_booking": 1,
				"guest_verification_method": "Email OTP",
				"send_ticket_email": 1,
				"apply_tax": 1,
				"tax_label": "GST",
				"tax_percentage": 18,
			}
		)
		template.insert()

		options = {
			"category": 1,
			"host": 1,
			"medium": 1,
			"about": 1,
			"short_description": 1,
			"time_zone": 1,
			"allow_guest_booking": 1,
			"guest_verification_method": 1,
			"send_ticket_email": 1,
			"apply_tax": 1,
			"tax_label": 1,
			"tax_percentage": 1,
		}

		event_name = create_from_template(template.name, frappe.as_json(options))
		event = frappe.get_doc("Buzz Event", event_name)

		self.assertEqual(event.category, "Test Category")
		self.assertEqual(event.host, "Test Host")
		self.assertEqual(event.medium, "Online")
		self.assertEqual(event.about, "About text")
		self.assertEqual(event.short_description, "Short desc")
		self.assertEqual(event.time_zone, "Asia/Kolkata")
		self.assertEqual(event.allow_guest_booking, 1)
		self.assertEqual(event.guest_verification_method, "Email OTP")
		self.assertEqual(event.send_ticket_email, 1)
		self.assertEqual(event.apply_tax, 1)
		self.assertEqual(event.tax_label, "GST")
		self.assertEqual(event.tax_percentage, 18)

	def test_create_from_template_respects_unselected_options(self):
		"""Test that unselected options are not copied"""
		template = frappe.get_doc(
			{
				"doctype": "Event Template",
				"template_name": "Selective Template",
				"category": "Test Category",
				"host": "Test Host",
				"medium": "In Person",
				"about": "Should not appear",
				"apply_tax": 1,
				"tax_percentage": 18,
			}
		)
		template.insert()

		options = {"category": 1, "host": 1, "medium": 0, "about": 0, "apply_tax": 0}

		event_name = create_from_template(template.name, frappe.as_json(options))
		event = frappe.get_doc("Buzz Event", event_name)

		self.assertEqual(event.category, "Test Category")
		self.assertEqual(event.host, "Test Host")
		self.assertFalse(event.about)
		self.assertFalse(event.apply_tax)

	def test_create_from_template_additional_fields_override(self):
		"""Test that additional_fields override template values"""
		template = frappe.get_doc(
			{
				"doctype": "Event Template",
				"template_name": "Override Template",
				"category": "Test Category",
				"host": "Test Host",
			}
		)
		template.insert()

		# Don't copy category from template, provide via additional_fields
		options = {"host": 1}
		additional_fields = {"category": "Test Category"}

		event_name = create_from_template(
			template.name, frappe.as_json(options), frappe.as_json(additional_fields)
		)
		event = frappe.get_doc("Buzz Event", event_name)

		self.assertEqual(event.category, "Test Category")
		self.assertEqual(event.host, "Test Host")

	def test_create_from_template_creates_ticket_types(self):
		"""Test that ticket types are created as linked documents"""
		template = frappe.get_doc(
			{
				"doctype": "Event Template",
				"template_name": "Ticket Template",
				"category": "Test Category",
				"host": "Test Host",
				"template_ticket_types": [
					{
						"title": "Early Bird",
						"price": 500,
						"currency": "INR",
						"is_published": 1,
						"max_tickets_available": 100,
					},
					{"title": "Regular", "price": 1000, "currency": "INR", "is_published": 1},
				],
			}
		)
		template.insert()

		options = {"category": 1, "host": 1, "ticket_types": 1}
		event_name = create_from_template(template.name, frappe.as_json(options))

		ticket_types = frappe.get_all(
			"Event Ticket Type",
			filters={"event": event_name, "title": ["in", ["Early Bird", "Regular"]]},
			fields=["title", "price", "max_tickets_available"],
			order_by="price",
		)
		self.assertEqual(len(ticket_types), 2)
		self.assertEqual(ticket_types[0].title, "Early Bird")
		self.assertEqual(ticket_types[0].price, 500)
		self.assertEqual(ticket_types[0].max_tickets_available, 100)
		self.assertEqual(ticket_types[1].title, "Regular")
		self.assertEqual(ticket_types[1].price, 1000)

	def test_create_from_template_creates_add_ons(self):
		"""Test that add-ons are created as linked documents"""
		template = frappe.get_doc(
			{
				"doctype": "Event Template",
				"template_name": "AddOn Template",
				"category": "Test Category",
				"host": "Test Host",
				"template_add_ons": [
					{
						"title": "Workshop Access",
						"price": 2000,
						"currency": "INR",
						"enabled": 1,
						"user_selects_option": 1,
						"options": "Morning\nAfternoon",
					}
				],
			}
		)
		template.insert()

		options = {"category": 1, "host": 1, "add_ons": 1}
		event_name = create_from_template(template.name, frappe.as_json(options))

		add_ons = frappe.get_all(
			"Ticket Add-on",
			filters={"event": event_name},
			fields=["title", "price", "user_selects_option", "options"],
		)
		self.assertEqual(len(add_ons), 1)
		self.assertEqual(add_ons[0].title, "Workshop Access")
		self.assertEqual(add_ons[0].price, 2000)
		self.assertEqual(add_ons[0].user_selects_option, 1)
		self.assertEqual(add_ons[0].options, "Morning\nAfternoon")

	def test_create_from_template_creates_custom_fields(self):
		"""Test that custom fields are created as linked documents"""
		template = frappe.get_doc(
			{
				"doctype": "Event Template",
				"template_name": "CustomField Template",
				"category": "Test Category",
				"host": "Test Host",
				"template_custom_fields": [
					{
						"label": "Company",
						"fieldname": "company",
						"fieldtype": "Data",
						"applied_to": "Booking",
						"mandatory": 1,
						"enabled": 1,
						"placeholder": "Enter company name",
					}
				],
			}
		)
		template.insert()

		options = {"category": 1, "host": 1, "custom_fields": 1}
		event_name = create_from_template(template.name, frappe.as_json(options))

		custom_fields = frappe.get_all(
			"Buzz Custom Field",
			filters={"event": event_name},
			fields=["label", "fieldtype", "mandatory", "placeholder"],
		)
		self.assertEqual(len(custom_fields), 1)
		self.assertEqual(custom_fields[0].label, "Company")
		self.assertEqual(custom_fields[0].fieldtype, "Data")
		self.assertEqual(custom_fields[0].mandatory, 1)
		self.assertEqual(custom_fields[0].placeholder, "Enter company name")

	def test_create_from_template_skips_linked_docs_when_unselected(self):
		"""Test that linked docs are not created when options are 0"""
		template = frappe.get_doc(
			{
				"doctype": "Event Template",
				"template_name": "Skip Linked Template",
				"category": "Test Category",
				"host": "Test Host",
				"template_ticket_types": [
					{"title": "Skipped", "price": 100, "currency": "INR", "is_published": 1}
				],
				"template_add_ons": [
					{"title": "Skipped Addon", "price": 50, "currency": "INR", "enabled": 1}
				],
				"template_custom_fields": [
					{
						"label": "Skipped Field",
						"fieldname": "skipped",
						"fieldtype": "Data",
						"applied_to": "Booking",
						"enabled": 1,
					}
				],
			}
		)
		template.insert()

		options = {"category": 1, "host": 1, "ticket_types": 0, "add_ons": 0, "custom_fields": 0}
		event_name = create_from_template(template.name, frappe.as_json(options))

		self.assertEqual(
			len(frappe.get_all("Event Ticket Type", filters={"event": event_name, "title": "Skipped"})), 0
		)
		self.assertEqual(len(frappe.get_all("Ticket Add-on", filters={"event": event_name})), 0)
		self.assertEqual(len(frappe.get_all("Buzz Custom Field", filters={"event": event_name})), 0)

	def test_create_from_template_sets_default_title_and_date(self):
		"""Test that event gets a default title and today's date"""
		template = frappe.get_doc(
			{
				"doctype": "Event Template",
				"template_name": "Defaults Template",
				"category": "Test Category",
				"host": "Test Host",
			}
		)
		template.insert()

		options = {"category": 1, "host": 1}
		event_name = create_from_template(template.name, frappe.as_json(options))
		event = frappe.get_doc("Buzz Event", event_name)

		self.assertIn("Defaults Template", event.title)
		self.assertEqual(str(event.start_date), frappe.utils.today())

	def test_create_from_template_copies_sponsorship_settings(self):
		"""Test that sponsorship settings are copied"""
		template = frappe.get_doc(
			{
				"doctype": "Event Template",
				"template_name": "Sponsor Template",
				"category": "Test Category",
				"host": "Test Host",
				"auto_send_pitch_deck": 1,
				"sponsor_deck_reply_to": "test@example.com",
				"sponsor_deck_cc": "cc@example.com",
			}
		)
		template.insert()

		options = {
			"category": 1,
			"host": 1,
			"auto_send_pitch_deck": 1,
			"sponsor_deck_reply_to": 1,
			"sponsor_deck_cc": 1,
		}

		event_name = create_from_template(template.name, frappe.as_json(options))
		event = frappe.get_doc("Buzz Event", event_name)

		self.assertEqual(event.auto_send_pitch_deck, 1)
		self.assertEqual(event.sponsor_deck_reply_to, "test@example.com")
		self.assertEqual(event.sponsor_deck_cc, "cc@example.com")

	# ==================== Save as Template Tests ====================

	def test_save_event_as_template_all_options(self):
		"""Test saving an event as template with all field options"""
		event = frappe.get_doc(
			{
				"doctype": "Buzz Event",
				"title": "Full Save Event",
				"category": "Test Category",
				"host": "Test Host",
				"start_date": frappe.utils.today(),
				"start_time": "09:00:00",
				"end_time": "18:00:00",
				"medium": "Online",
				"about": "Full event description",
				"apply_tax": 1,
				"tax_label": "GST",
				"tax_percentage": 18,
			}
		)
		event.insert()

		# Create linked docs
		frappe.get_doc(
			{
				"doctype": "Event Ticket Type",
				"event": event.name,
				"title": "Gold",
				"price": 5000,
				"currency": "INR",
				"is_published": 1,
			}
		).insert()

		frappe.get_doc(
			{
				"doctype": "Ticket Add-on",
				"event": event.name,
				"title": "Parking",
				"price": 200,
				"currency": "INR",
				"enabled": 1,
			}
		).insert()

		frappe.get_doc(
			{
				"doctype": "Buzz Custom Field",
				"event": event.name,
				"label": "Designation",
				"fieldname": "designation",
				"fieldtype": "Data",
				"applied_to": "Booking",
				"enabled": 1,
			}
		).insert()

		options = {
			"category": 1,
			"host": 1,
			"medium": 1,
			"about": 1,
			"apply_tax": 1,
			"tax_label": 1,
			"tax_percentage": 1,
			"ticket_types": 1,
			"add_ons": 1,
			"custom_fields": 1,
		}

		template_name = create_template_from_event(
			str(event.name), "Full Save Template", frappe.as_json(options)
		)
		template = frappe.get_doc("Event Template", template_name)

		self.assertEqual(template.category, "Test Category")
		self.assertEqual(template.host, "Test Host")
		self.assertEqual(template.medium, "Online")
		self.assertEqual(template.about, "Full event description")
		self.assertEqual(template.apply_tax, 1)
		self.assertEqual(template.tax_percentage, 18)

		# Check linked docs (ticket types include default "Normal" created on event insert)
		gold_tickets = [t for t in template.template_ticket_types if t.title == "Gold"]
		self.assertEqual(len(gold_tickets), 1)
		self.assertEqual(gold_tickets[0].price, 5000)

		self.assertEqual(len(template.template_add_ons), 1)
		self.assertEqual(template.template_add_ons[0].title, "Parking")

		self.assertEqual(len(template.template_custom_fields), 1)
		self.assertEqual(template.template_custom_fields[0].label, "Designation")

	def test_save_event_as_template_partial(self):
		"""Test saving event as template with partial options"""
		event = frappe.get_doc(
			{
				"doctype": "Buzz Event",
				"title": "Partial Save Event",
				"category": "Test Category",
				"host": "Test Host",
				"start_date": frappe.utils.today(),
				"start_time": "09:00:00",
				"end_time": "18:00:00",
				"medium": "In Person",
				"about": "Included",
				"apply_tax": 1,
				"tax_percentage": 18,
			}
		)
		event.insert()

		options = {"category": 1, "about": 1, "medium": 0, "apply_tax": 0}

		template_name = create_template_from_event(
			str(event.name), "Partial Save Template", frappe.as_json(options)
		)
		template = frappe.get_doc("Event Template", template_name)

		self.assertEqual(template.category, "Test Category")
		self.assertEqual(template.about, "Included")
		self.assertFalse(template.host)
		self.assertFalse(template.apply_tax)

	# ==================== Round Trip Test ====================

	def test_round_trip_preserves_data(self):
		"""Test Event -> Template -> Event preserves all data"""
		original = frappe.get_doc(
			{
				"doctype": "Buzz Event",
				"title": "Round Trip Event",
				"category": "Test Category",
				"host": "Test Host",
				"start_date": frappe.utils.today(),
				"start_time": "09:00:00",
				"end_time": "18:00:00",
				"medium": "Online",
				"about": "Round trip description",
				"apply_tax": 1,
				"tax_label": "Service Tax",
				"tax_percentage": 12,
			}
		)
		original.insert()

		frappe.get_doc(
			{
				"doctype": "Event Ticket Type",
				"event": original.name,
				"title": "Platinum",
				"price": 10000,
				"currency": "INR",
				"is_published": 1,
				"max_tickets_available": 25,
			}
		).insert()

		# Event -> Template
		all_options = {
			"category": 1,
			"host": 1,
			"medium": 1,
			"about": 1,
			"apply_tax": 1,
			"tax_label": 1,
			"tax_percentage": 1,
			"ticket_types": 1,
		}
		template_name = create_template_from_event(
			str(original.name), "Round Trip Template", frappe.as_json(all_options)
		)

		# Template -> New Event
		new_event_name = create_from_template(template_name, frappe.as_json(all_options))
		new_event = frappe.get_doc("Buzz Event", new_event_name)

		self.assertEqual(new_event.category, original.category)
		self.assertEqual(new_event.host, original.host)
		self.assertEqual(new_event.medium, original.medium)
		self.assertEqual(new_event.about, original.about)
		self.assertEqual(new_event.tax_label, original.tax_label)
		self.assertEqual(new_event.tax_percentage, original.tax_percentage)

		platinum_tickets = frappe.get_all(
			"Event Ticket Type",
			filters={"event": new_event_name, "title": "Platinum"},
			fields=["price", "max_tickets_available"],
		)
		self.assertEqual(len(platinum_tickets), 1)
		self.assertEqual(platinum_tickets[0].price, 10000)
		self.assertEqual(platinum_tickets[0].max_tickets_available, 25)

	# ==================== Permission Tests ====================

	def test_create_from_template_requires_template_read_permission(self):
		"""Test that creating from template requires read permission on Event Template"""
		template = frappe.get_doc(
			{
				"doctype": "Event Template",
				"template_name": "Perm Test Template",
				"category": "Test Category",
				"host": "Test Host",
			}
		)
		template.insert()

		# Create a user without Event Template read permission
		frappe.set_user("Guest")
		try:
			with self.assertRaises(frappe.exceptions.ValidationError):
				create_from_template(template.name, frappe.as_json({"category": 1, "host": 1}))
		finally:
			frappe.set_user("Administrator")

	def test_save_as_template_requires_create_permission(self):
		"""Test that saving as template requires create permission on Event Template"""
		event = frappe.get_doc(
			{
				"doctype": "Buzz Event",
				"title": "Perm Event",
				"category": "Test Category",
				"host": "Test Host",
				"start_date": frappe.utils.today(),
				"start_time": "09:00:00",
				"end_time": "18:00:00",
			}
		)
		event.insert()

		frappe.set_user("Guest")
		try:
			with self.assertRaises(frappe.exceptions.ValidationError):
				create_template_from_event(str(event.name), "Perm Template", frappe.as_json({"category": 1}))
		finally:
			frappe.set_user("Administrator")