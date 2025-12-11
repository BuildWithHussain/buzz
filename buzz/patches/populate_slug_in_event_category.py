import frappe


def execute():
	categories = frappe.db.get_all("Event Category", pluck="name")
	for category in categories:
		doc = frappe.get_cached_doc("Event Category", category)
		doc.set_slug()
		doc.save()
