import frappe


def execute():
	frappe.reload_doc("events", "doctype", "offline_payment_method")

	events_with_offline = frappe.get_all(
		"Buzz Event",
		filters={"enable_offline_payments": 1},
		fields=["name", "offline_payment_label", "offline_payment_details", "collect_payment_proof"],
	)

	for event in events_with_offline:
		title = event.offline_payment_label or "Offline Payment"

		method = frappe.get_doc(
			{
				"doctype": "Offline Payment Method",
				"title": title,
				"event": event.name,
				"enabled": 1,
				"collect_payment_proof": event.collect_payment_proof,
				"description": event.offline_payment_details,
			}
		)
		method.insert(ignore_permissions=True)

		# Link any existing Buzz Custom Fields scoped to "Offline Payment Form" for this event
		custom_fields = frappe.get_all(
			"Buzz Custom Field",
			filters={"event": event.name, "applied_to": "Offline Payment Form"},
			pluck="name",
		)
		for cf_name in custom_fields:
			frappe.db.set_value("Buzz Custom Field", cf_name, "offline_payment_method", method.name)

	frappe.reload_doc("events", "doctype", "buzz_event")
