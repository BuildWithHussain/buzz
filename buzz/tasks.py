import frappe
from frappe.utils import add_days, nowdate, today


def unpublish_ticket_types_after_last_date():
	frappe.db.set_value(
		"Event Ticket Type",
		{"is_published": True, "auto_unpublish_after": ("<", today())},
		"is_published",
		False,
	)
	frappe.db.commit()


def send_feedback_requests():
	yesterday = add_days(nowdate(), -1)
	ended_events = frappe.get_all("Buzz Event", filters={"end_date": yesterday}, fields=["name", "title"])

	if not ended_events:
		return

	for event in ended_events:
		tickets = frappe.get_all(
			"Event Ticket", filters={"event": event.name, "docstatus": 1}, fields=["name"]
		)

		for ticket in tickets:
			try:
				ticket_doc = frappe.get_doc("Event Ticket", ticket.name)
				ticket_doc.send_feedback_email()
			except Exception:
				frappe.log_error(
					title="Feedback email send failed",
					message=f"Ticket: {ticket.name}, Event: {event.name}",
				)
