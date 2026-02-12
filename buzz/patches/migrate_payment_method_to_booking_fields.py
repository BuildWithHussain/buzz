import frappe


def execute():
	"""Migrate payment_method and offline_payment_method from additional_fields child table to direct fields on Event Booking."""
	bookings_with_payment_method = frappe.db.get_all(
		"Additional Field",
		filters={
			"parenttype": "Event Booking",
			"fieldname": "payment_method",
		},
		fields=["parent", "value"],
	)

	for row in bookings_with_payment_method:
		frappe.db.set_value("Event Booking", row.parent, "payment_method", row.value, update_modified=False)

	bookings_with_offline_method = frappe.db.get_all(
		"Additional Field",
		filters={
			"parenttype": "Event Booking",
			"fieldname": "offline_payment_method",
		},
		fields=["parent", "value"],
	)

	for row in bookings_with_offline_method:
		frappe.db.set_value(
			"Event Booking", row.parent, "offline_payment_method", row.value, update_modified=False
		)

	# Clean up the migrated rows from additional_fields
	frappe.db.delete(
		"Additional Field",
		{
			"parenttype": "Event Booking",
			"fieldname": ("in", ["payment_method", "offline_payment_method"]),
		},
	)
