# Copyright (c) 2026, BWH Studios and Contributors
# See license.txt

import frappe
from frappe.tests import IntegrationTestCase


class TestOfflinePaymentMethod(IntegrationTestCase):
	def test_unique_title_per_event(self):
		"""Test that two methods with the same title cannot exist for the same event."""
		test_event = frappe.get_doc("Buzz Event", {"route": "test-route"})

		frappe.get_doc(
			{
				"doctype": "Offline Payment Method",
				"title": "Bank Transfer",
				"event": test_event.name,
				"enabled": 1,
			}
		).insert()

		with self.assertRaises(frappe.ValidationError):
			frappe.get_doc(
				{
					"doctype": "Offline Payment Method",
					"title": "Bank Transfer",
					"event": test_event.name,
					"enabled": 1,
				}
			).insert()

	def test_same_title_different_events(self):
		"""Test that two methods with the same title can exist for different events."""
		events = frappe.get_all("Buzz Event", limit=2, pluck="name")
		if len(events) < 2:
			self.skipTest("Need at least 2 events")

		frappe.get_doc(
			{
				"doctype": "Offline Payment Method",
				"title": "UPI Payment",
				"event": events[0],
				"enabled": 1,
			}
		).insert()

		# Should not raise
		method2 = frappe.get_doc(
			{
				"doctype": "Offline Payment Method",
				"title": "UPI Payment",
				"event": events[1],
				"enabled": 1,
			}
		).insert()

		self.assertTrue(method2.name)
