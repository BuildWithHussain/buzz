import frappe


def execute():
	events = frappe.get_all(
		"Buzz Event", filters={"payment_gateway": ("is", "set")}, fields=["name", "payment_gateway"]
	)

	frappe.reload_doc("Events", "doctype", "buzz_event")
	frappe.reload_doc("Events", "doctype", "event_payment_gateway")

	for event in events:
		doc = frappe.get_cached_doc("Buzz Event", event.name)
		doc.append(
			"payment_gateways",
			{
				"payment_gateway": event.payment_gateway,
			},
		)
		doc.save()
