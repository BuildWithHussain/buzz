import frappe

from events.payments import get_payment_link_for_booking


@frappe.whitelist()
def validate_coupon(coupon_code: str, event_route: str) -> dict:
	"""Validate a coupon code for a specific event."""
	frappe.errprint(f"Validating coupon: {coupon_code} for event: {event_route}")
	try:
		event_doc = frappe.get_cached_doc("FE Event", {"route": event_route})
		coupon_doc = frappe.get_cached_doc("Bulk Ticket Coupon", coupon_code)

		# Check if coupon is for the correct event
		if int(coupon_doc.event) != int(event_doc.name):
			frappe.errprint(f"Coupon {coupon_doc.event} is not valid for event {event_doc.name}")
			return {"valid": False, "error": "Coupon is not valid for this event"}

		# Check if coupon has remaining tickets
		remaining_tickets = coupon_doc.number_of_granted_tickets - coupon_doc.number_of_claimed_tickets
		if remaining_tickets <= 0:
			return {"valid": False, "error": "Coupon has been fully used"}

		# Get ticket type details
		ticket_type_doc = frappe.get_cached_doc("Event Ticket Type", coupon_doc.ticket_type)

		# Get free add-ons included in the coupon
		free_add_ons = []
		for free_add_on in coupon_doc.free_add_ons:
			add_on_doc = frappe.get_cached_doc("Ticket Add-on", free_add_on.add_on)
			free_add_ons.append(
				{
					"name": add_on_doc.name,
					"title": add_on_doc.title,
					"price": add_on_doc.price,
					"currency": add_on_doc.currency,
					"user_selects_option": add_on_doc.user_selects_option,
					"options": add_on_doc.options.split("\n")
					if add_on_doc.user_selects_option and add_on_doc.options
					else None,
				}
			)

		return {
			"valid": True,
			"coupon_name": coupon_doc.name,
			"ticket_type": ticket_type_doc.name,
			"ticket_type_title": ticket_type_doc.title,
			"remaining_tickets": remaining_tickets,
			"granted_tickets": coupon_doc.number_of_granted_tickets,
			"claimed_tickets": coupon_doc.number_of_claimed_tickets,
			"free_add_ons": free_add_ons,
		}

	except frappe.DoesNotExistError:
		return {"valid": False, "error": "Invalid coupon code"}
	except Exception as e:
		frappe.log_error(f"Error validating coupon: {e!s}")
		return {"valid": False, "error": "Error validating coupon"}


@frappe.whitelist()
def get_event_booking_data(event_route: str) -> dict:
	data = frappe._dict()
	event_doc = frappe.get_cached_doc("FE Event", {"route": event_route})

	# Ticket Types
	available_ticket_types = []
	published_ticket_types = frappe.db.get_all(
		"Event Ticket Type", filters={"is_published": True, "event": event_doc.name}, pluck="name"
	)

	for ticket_type in published_ticket_types:
		tt = frappe.get_cached_doc("Event Ticket Type", ticket_type)
		if tt.are_tickets_available(1):
			available_ticket_types.append(tt)

	data.available_ticket_types = available_ticket_types

	# Ticket Add-ons
	add_ons = frappe.db.get_all(
		"Ticket Add-on",
		filters={"event": event_doc.name},
		fields=["name", "title", "price", "currency", "user_selects_option", "options"],
	)

	for add_on in add_ons:
		if add_on.user_selects_option:
			add_on.options = add_on.options.split("\n")

	data.available_add_ons = add_ons
	return data


@frappe.whitelist()
def process_booking(attendees: list[dict], event: str, coupon_code: str | None = None) -> dict:
	booking = frappe.new_doc("Event Booking")
	booking.event = event
	booking.user = frappe.session.user

	# Validate coupon if provided
	coupon_info = None
	if coupon_code:
		event_doc = frappe.get_cached_doc("FE Event", event)
		coupon_info = validate_coupon(coupon_code, event_doc.route)
		if not coupon_info.get("valid"):
			frappe.throw(coupon_info.get("error", "Invalid coupon"))

		# Check if we're not exceeding the remaining tickets
		coupon_ticket_count = sum(
			1 for attendee in attendees if attendee.get("ticket_type") == coupon_info.get("ticket_type")
		)
		if coupon_ticket_count > coupon_info.get("remaining_tickets", 0):
			frappe.throw(f"Only {coupon_info.get('remaining_tickets')} tickets remaining for this coupon")

		# Set the coupon in the booking
		booking.coupon_used = coupon_info.get("coupon_name")

	for attendee in attendees:
		add_ons = attendee.get("add_ons", None)
		if add_ons:
			add_ons = create_add_on_doc(
				attendee_name=attendee["full_name"],
				add_ons=add_ons,
			)

		booking.append(
			"attendees",
			{
				"full_name": attendee.get("full_name"),
				"email": attendee.get("email"),
				"ticket_type": attendee.get("ticket_type"),
				"add_ons": add_ons.name if add_ons else None,
			},
		)

	booking.insert(ignore_permissions=True)
	frappe.db.commit()

	if booking.total_amount == 0:
		booking.flags.ignore_permissions = True
		booking.submit()
		return {"booking_name": booking.name}

	return {
		"payment_link": get_payment_link_for_booking(
			booking.name, redirect_to=f"/dashboard/bookings/{booking.name}?success=true"
		)
	}


def create_add_on_doc(attendee_name: str, add_ons: list[dict]):
	"""Create a new Attendee Ticket Add-on document."""
	return frappe.get_doc(
		{"doctype": "Attendee Ticket Add-on", "add_ons": add_ons, "attendee_name": attendee_name}
	).insert(ignore_permissions=True)
