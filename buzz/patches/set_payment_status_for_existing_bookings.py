import frappe


def execute():
	EventBooking = frappe.qb.DocType("Event Booking")

	# Set payment_status to "Paid" and status to "Confirmed" for all submitted bookings
	(
		frappe.qb.update(EventBooking)
		.set(EventBooking.payment_status, "Paid")
		.set(EventBooking.status, "Confirmed")
		.where(EventBooking.docstatus == 1)
	).run()
