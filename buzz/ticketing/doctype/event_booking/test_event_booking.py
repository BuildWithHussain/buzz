# Copyright (c) 2025, BWH Studios and Contributors
# See license.txt

import frappe
from frappe.tests import IntegrationTestCase

# On IntegrationTestCase, the doctype test records and all
# link-field test record dependencies are recursively loaded
# Use these module variables to add/remove to/from that list
EXTRA_TEST_RECORD_DEPENDENCIES = []  # eg. ["User"]
IGNORE_TEST_RECORD_DEPENDENCIES = []  # eg. ["User"]

TEST_ADD_ON_PRICE = 100
TEST_VIP_TICKET_TYPE_PRICE = 500


class IntegrationTestEventBooking(IntegrationTestCase):
	"""
	Integration tests for EventBooking.
	Use this class for testing interactions between multiple components.
	"""

	def test_total_calculation_without_taxes(self):
		test_event = frappe.get_doc("Buzz Event", {"route": "test-route"})

		# Disable tax at event level
		test_event.apply_tax = False
		test_event.save()

		test_ticket_add_on = frappe.get_doc(
			{
				"doctype": "Ticket Add-on",
				"event": test_event.name,
				"title": "T-Shirt",
				"price": TEST_ADD_ON_PRICE,
			}
		).insert()

		test_ticket_type = frappe.get_doc(
			{
				"doctype": "Event Ticket Type",
				"event": test_event.name,
				"title": "VIP",
				"price": TEST_VIP_TICKET_TYPE_PRICE,
			}
		).insert()

		test_booking = frappe.get_doc(
			{
				"doctype": "Event Booking",
				"event": test_event.name,
				"user": "Administrator",
				"attendees": [
					{"ticket_type": test_ticket_type.name, "full_name": "John", "email": "john@email.com"},
					{"ticket_type": test_ticket_type.name, "full_name": "Jenny", "email": "jenny@email.com"},
				],
			}
		).insert()

		# without add ons
		self.assertEqual(test_booking.total_amount, 1000)

		test_attendee_add_on = frappe.get_doc(
			{
				"doctype": "Attendee Ticket Add-on",
				"add_ons": [{"add_on": test_ticket_add_on.name, "value": "XL"}],
			}
		).insert()

		test_booking.attendees[0].add_ons = test_attendee_add_on.name
		test_booking.save()

		# with one add-on
		self.assertEqual(test_booking.attendees[0].number_of_add_ons, 1)
		self.assertEqual(test_booking.attendees[0].add_on_total, TEST_ADD_ON_PRICE)
		self.assertEqual(test_booking.net_amount, 1100)
		self.assertEqual(test_booking.total_amount, 1100)

	def test_total_calculation_with_taxes(self):
		test_event = frappe.get_doc("Buzz Event", {"route": "test-route"})

		# Enable tax at event level (exclusive)
		test_event.apply_tax = True
		test_event.tax_inclusive = False
		test_event.tax_label = "GST"
		test_event.tax_percentage = 18
		test_event.save()

		test_ticket_type = frappe.get_doc(
			{
				"doctype": "Event Ticket Type",
				"event": test_event.name,
				"title": "VIP",
				"price": TEST_VIP_TICKET_TYPE_PRICE,
			}
		).insert()

		test_booking = frappe.get_doc(
			{
				"doctype": "Event Booking",
				"event": test_event.name,
				"user": "Administrator",
				"attendees": [
					{"ticket_type": test_ticket_type.name, "full_name": "John", "email": "john@email.com"},
					{"ticket_type": test_ticket_type.name, "full_name": "Jenny", "email": "jenny@email.com"},
				],
			}
		).insert()

		self.assertEqual(test_booking.net_amount, 1000)
		self.assertEqual(test_booking.tax_label, "GST")
		self.assertEqual(test_booking.tax_percentage, 18)
		self.assertEqual(test_booking.tax_amount, 180)
		self.assertEqual(test_booking.total_amount, 1180)

	def test_total_calculation_with_custom_tax_label(self):
		"""Test that custom tax labels (e.g., VAT) work correctly."""
		test_event = frappe.get_doc("Buzz Event", {"route": "test-route"})

		# Enable tax with custom VAT label (exclusive)
		test_event.apply_tax = True
		test_event.tax_inclusive = False
		test_event.tax_label = "VAT"
		test_event.tax_percentage = 20
		test_event.save()

		test_ticket_type = frappe.get_doc(
			{
				"doctype": "Event Ticket Type",
				"event": test_event.name,
				"title": "Standard",
				"price": 100,
			}
		).insert()

		test_booking = frappe.get_doc(
			{
				"doctype": "Event Booking",
				"event": test_event.name,
				"user": "Administrator",
				"attendees": [
					{"ticket_type": test_ticket_type.name, "full_name": "John", "email": "john@email.com"},
				],
			}
		).insert()

		self.assertEqual(test_booking.tax_label, "VAT")
		self.assertEqual(test_booking.tax_percentage, 20)
		self.assertEqual(test_booking.tax_amount, 20)
		self.assertEqual(test_booking.total_amount, 120)

	def test_tax_inclusive_calculation(self):
		"""Test that tax-inclusive prices back-calculate tax without increasing total."""
		test_event = frappe.get_doc("Buzz Event", {"route": "test-route"})

		# Enable tax-inclusive pricing
		test_event.apply_tax = True
		test_event.tax_inclusive = True
		test_event.tax_label = "GST"
		test_event.tax_percentage = 18
		test_event.save()

		test_ticket_type = frappe.get_doc(
			{
				"doctype": "Event Ticket Type",
				"event": test_event.name,
				"title": "VIP",
				"price": TEST_VIP_TICKET_TYPE_PRICE,
			}
		).insert()

		test_booking = frappe.get_doc(
			{
				"doctype": "Event Booking",
				"event": test_event.name,
				"user": "Administrator",
				"attendees": [
					{"ticket_type": test_ticket_type.name, "full_name": "John", "email": "john@email.com"},
					{"ticket_type": test_ticket_type.name, "full_name": "Jenny", "email": "jenny@email.com"},
				],
			}
		).insert()

		# net_amount = 2 * 500 = 1000
		self.assertEqual(test_booking.net_amount, 1000)
		self.assertEqual(test_booking.tax_label, "GST")
		self.assertEqual(test_booking.tax_percentage, 18)
		# tax_amount = 1000 * 18 / 118 = 152.54 (rounded to 2 decimals)
		self.assertAlmostEqual(test_booking.tax_amount, round(1000 * 18 / 118, 2), places=2)
		# total stays the same — tax is included in the price
		self.assertEqual(test_booking.total_amount, 1000)

	def test_tax_inclusive_with_single_ticket(self):
		"""Test tax-inclusive with a single ticket at a round price."""
		test_event = frappe.get_doc("Buzz Event", {"route": "test-route"})

		test_event.apply_tax = True
		test_event.tax_inclusive = True
		test_event.tax_label = "VAT"
		test_event.tax_percentage = 20
		test_event.save()

		test_ticket_type = frappe.get_doc(
			{
				"doctype": "Event Ticket Type",
				"event": test_event.name,
				"title": "Standard",
				"price": 120,
			}
		).insert()

		test_booking = frappe.get_doc(
			{
				"doctype": "Event Booking",
				"event": test_event.name,
				"user": "Administrator",
				"attendees": [
					{"ticket_type": test_ticket_type.name, "full_name": "John", "email": "john@email.com"},
				],
			}
		).insert()

		# Price is 120 inclusive of 20% VAT
		# tax_amount = 120 * 20 / 120 = 20
		self.assertEqual(test_booking.net_amount, 120)
		self.assertEqual(test_booking.tax_amount, 20)
		self.assertEqual(test_booking.total_amount, 120)

	def test_tax_exclusive_still_works(self):
		"""Ensure that when tax_inclusive is False, tax is still added on top."""
		test_event = frappe.get_doc("Buzz Event", {"route": "test-route"})

		test_event.apply_tax = True
		test_event.tax_inclusive = False
		test_event.tax_label = "GST"
		test_event.tax_percentage = 18
		test_event.save()

		test_ticket_type = frappe.get_doc(
			{
				"doctype": "Event Ticket Type",
				"event": test_event.name,
				"title": "VIP",
				"price": TEST_VIP_TICKET_TYPE_PRICE,
			}
		).insert()

		test_booking = frappe.get_doc(
			{
				"doctype": "Event Booking",
				"event": test_event.name,
				"user": "Administrator",
				"attendees": [
					{"ticket_type": test_ticket_type.name, "full_name": "John", "email": "john@email.com"},
					{"ticket_type": test_ticket_type.name, "full_name": "Jenny", "email": "jenny@email.com"},
				],
			}
		).insert()

		# Exclusive: tax added on top
		self.assertEqual(test_booking.net_amount, 1000)
		self.assertEqual(test_booking.tax_amount, 180)
		self.assertEqual(test_booking.total_amount, 1180)

	def test_prevents_booking_if_tickets_unavailable(self):
		test_event = frappe.get_doc("Buzz Event", {"route": "test-route"})
		test_vip_ticket_type = frappe.get_doc(
			{
				"doctype": "Event Ticket Type",
				"event": test_event.name,
				"title": "VIP",
				"price": 500,
				"is_published": True,
				"max_tickets_available": 2,
			}
		).insert()

		test_normal_ticket_type = frappe.get_doc(
			{
				"doctype": "Event Ticket Type",
				"event": test_event.name,
				"title": "Normal",
				"price": 500,
				"is_published": True,
			}
		).insert()

		# VIP Ticket 1
		frappe.get_doc(
			{
				"doctype": "Event Ticket",
				"ticket_type": test_vip_ticket_type.name,
				"attendee_name": "John Doe",
				"attendee_email": "john@email.com",
			}
		).insert().submit()

		# VIP Ticket 2 with Normal Ticket 1
		frappe.get_doc(
			{
				"doctype": "Event Booking",
				"user": frappe.session.user,
				"event": test_event.name,
				"attendees": [
					{
						"full_name": "John Doe",
						"ticket_type": test_vip_ticket_type.name,
						"email": "john@email.com",
					},
					{
						"full_name": "Jenny Doe",
						"ticket_type": test_normal_ticket_type.name,
						"email": "jenny@email.com",
					},
				],
			}
		).insert().submit()

		# VIP Ticket 3 with Normal Ticket 2
		with self.assertRaises(frappe.ValidationError):
			frappe.get_doc(
				{
					"doctype": "Event Booking",
					"user": frappe.session.user,
					"event": test_event.name,
					"attendees": [
						{
							"full_name": "John Doe",
							"ticket_type": test_vip_ticket_type.name,
							"email": "john@email.com",
						},
						{
							"full_name": "John Doe",
							"ticket_type": test_normal_ticket_type.name,
							"email": "john@email.com",
						},
					],
				}
			).insert()

		# Unpublish normal ticket type
		test_normal_ticket_type.is_published = False
		test_normal_ticket_type.save()

		# Booking with unpublished ticket type
		with self.assertRaises(frappe.ValidationError):
			frappe.get_doc(
				{
					"doctype": "Event Booking",
					"user": frappe.session.user,
					"event": test_event.name,
					"attendees": [
						{
							"full_name": "John Doe",
							"ticket_type": test_normal_ticket_type.name,
							"email": "john@email.com",
						}
					],
				}
			).insert()

	def test_utm_parameters_are_saved(self):
		"""Test that UTM parameters are correctly saved with bookings."""
		test_event = frappe.get_doc("Buzz Event", {"route": "test-route"})

		test_ticket_type = frappe.get_doc(
			{
				"doctype": "Event Ticket Type",
				"event": test_event.name,
				"title": "Standard",
				"price": 100,
			}
		).insert()

		test_booking = frappe.get_doc(
			{
				"doctype": "Event Booking",
				"event": test_event.name,
				"user": "Administrator",
				"attendees": [
					{"ticket_type": test_ticket_type.name, "full_name": "John", "email": "john@email.com"},
				],
				"utm_parameters": [
					{"utm_name": "utm_source", "value": "google"},
					{"utm_name": "utm_medium", "value": "cpc"},
					{"utm_name": "utm_campaign", "value": "summer_sale"},
				],
			}
		).insert()

		self.assertEqual(len(test_booking.utm_parameters), 3)
		self.assertEqual(test_booking.utm_parameters[0].utm_name, "utm_source")
		self.assertEqual(test_booking.utm_parameters[0].value, "google")
		self.assertEqual(test_booking.utm_parameters[1].utm_name, "utm_medium")
		self.assertEqual(test_booking.utm_parameters[1].value, "cpc")
		self.assertEqual(test_booking.utm_parameters[2].utm_name, "utm_campaign")
		self.assertEqual(test_booking.utm_parameters[2].value, "summer_sale")

	def test_booking_without_utm_parameters(self):
		"""Test that bookings work correctly without UTM parameters."""
		test_event = frappe.get_doc("Buzz Event", {"route": "test-route"})

		test_ticket_type = frappe.get_doc(
			{
				"doctype": "Event Ticket Type",
				"event": test_event.name,
				"title": "Standard",
				"price": 100,
			}
		).insert()

		test_booking = frappe.get_doc(
			{
				"doctype": "Event Booking",
				"event": test_event.name,
				"user": "Administrator",
				"attendees": [
					{"ticket_type": test_ticket_type.name, "full_name": "John", "email": "john@email.com"},
				],
			}
		).insert()

		self.assertEqual(len(test_booking.utm_parameters), 0)

	def test_custom_utm_parameters(self):
		"""Test that custom UTM parameters (beyond standard ones) are saved."""
		test_event = frappe.get_doc("Buzz Event", {"route": "test-route"})

		test_ticket_type = frappe.get_doc(
			{
				"doctype": "Event Ticket Type",
				"event": test_event.name,
				"title": "Standard",
				"price": 100,
			}
		).insert()

		test_booking = frappe.get_doc(
			{
				"doctype": "Event Booking",
				"event": test_event.name,
				"user": "Administrator",
				"attendees": [
					{"ticket_type": test_ticket_type.name, "full_name": "John", "email": "john@email.com"},
				],
				"utm_parameters": [
					{"utm_name": "utm_source", "value": "newsletter"},
					{"utm_name": "utm_custom_param", "value": "special_offer"},
				],
			}
		).insert()

		self.assertEqual(len(test_booking.utm_parameters), 2)
		# Check custom utm parameter is saved
		custom_param = next(
			(p for p in test_booking.utm_parameters if p.utm_name == "utm_custom_param"), None
		)
		self.assertIsNotNone(custom_param)
		self.assertEqual(custom_param.value, "special_offer")


class TestProcessBookingAPI(IntegrationTestCase):
	"""Test the process_booking API endpoint for UTM parameter handling."""

	def test_process_booking_with_utm_parameters(self):
		"""Test that process_booking API correctly saves UTM parameters."""
		from buzz.api import process_booking

		test_event = frappe.get_doc("Buzz Event", {"route": "test-route"})

		test_ticket_type = frappe.get_doc(
			{
				"doctype": "Event Ticket Type",
				"event": test_event.name,
				"title": "API Test Ticket",
				"price": 0,  # Free ticket to avoid payment flow
				"is_published": True,
			}
		).insert()

		# Disable tax at event level
		test_event.apply_tax = False
		test_event.save()

		attendees = [
			{
				"full_name": "API Test User",
				"email": "apitest@email.com",
				"ticket_type": str(test_ticket_type.name),
				"add_ons": [],
			}
		]

		utm_parameters = [
			{"utm_name": "utm_source", "value": "facebook"},
			{"utm_name": "utm_medium", "value": "social"},
			{"utm_name": "utm_campaign", "value": "winter_promo"},
			{"utm_name": "utm_content", "value": "banner_ad"},
			{"utm_name": "utm_term", "value": "event tickets"},
		]

		result = process_booking(
			attendees=attendees,
			event=str(test_event.name),
			utm_parameters=utm_parameters,
		)

		# Verify booking was created
		self.assertIn("booking_name", result)

		# Fetch the booking and verify UTM parameters
		booking = frappe.get_doc("Event Booking", result["booking_name"])
		self.assertEqual(len(booking.utm_parameters), 5)

		# Verify each UTM parameter
		utm_dict = {p.utm_name: p.value for p in booking.utm_parameters}
		self.assertEqual(utm_dict["utm_source"], "facebook")
		self.assertEqual(utm_dict["utm_medium"], "social")
		self.assertEqual(utm_dict["utm_campaign"], "winter_promo")
		self.assertEqual(utm_dict["utm_content"], "banner_ad")
		self.assertEqual(utm_dict["utm_term"], "event tickets")

	def test_process_booking_without_utm_parameters(self):
		"""Test that process_booking API works without UTM parameters."""
		from buzz.api import process_booking

		test_event = frappe.get_doc("Buzz Event", {"route": "test-route"})

		test_ticket_type = frappe.get_doc(
			{
				"doctype": "Event Ticket Type",
				"event": test_event.name,
				"title": "API Test Ticket No UTM",
				"price": 0,
				"is_published": True,
			}
		).insert()

		# Disable tax at event level
		test_event.apply_tax = False
		test_event.save()

		attendees = [
			{
				"full_name": "No UTM User",
				"email": "noutm@email.com",
				"ticket_type": str(test_ticket_type.name),
				"add_ons": [],
			}
		]

		result = process_booking(
			attendees=attendees,
			event=str(test_event.name),
			utm_parameters=None,
		)

		self.assertIn("booking_name", result)

		booking = frappe.get_doc("Event Booking", result["booking_name"])
		self.assertEqual(len(booking.utm_parameters), 0)

	def test_process_booking_with_empty_utm_parameters(self):
		"""Test that process_booking API handles empty UTM list."""
		from buzz.api import process_booking

		test_event = frappe.get_doc("Buzz Event", {"route": "test-route"})

		test_ticket_type = frappe.get_doc(
			{
				"doctype": "Event Ticket Type",
				"event": test_event.name,
				"title": "API Test Ticket Empty UTM",
				"price": 0,
				"is_published": True,
			}
		).insert()

		# Disable tax at event level
		test_event.apply_tax = False
		test_event.save()

		attendees = [
			{
				"full_name": "Empty UTM User",
				"email": "emptyutm@email.com",
				"ticket_type": str(test_ticket_type.name),
				"add_ons": [],
			}
		]

		result = process_booking(
			attendees=attendees,
			event=str(test_event.name),
			utm_parameters=[],
		)

		self.assertIn("booking_name", result)

		booking = frappe.get_doc("Event Booking", result["booking_name"])
		self.assertEqual(len(booking.utm_parameters), 0)
