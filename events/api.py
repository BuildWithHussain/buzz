import frappe
from frappe.utils import days_diff, format_date, format_time, today

from events.payments import get_payment_link_for_booking


def is_ticket_transfer_allowed(event_id: str | int) -> bool:
	"""Check if ticket transfer is allowed based on event start date and settings."""
	try:
		# Get event details
		event = frappe.get_cached_doc("FE Event", event_id)

		# Get event management settings
		settings = frappe.get_single("Event Management Settings")

		# Default to 7 days if no setting is found
		transfer_cutoff_days = settings.get("allow_transfer_ticket_before_event_start_days", 7)

		# Calculate days difference between today and event start date
		event_start_date = event.start_date
		if not event_start_date:
			return False

		# Get days remaining until event starts
		days_until_event = days_diff(event_start_date, today())

		# Transfer is allowed if there are more days remaining than the cutoff
		return days_until_event >= transfer_cutoff_days

	except Exception as e:
		frappe.log_error(f"Error checking ticket transfer eligibility: {e!s}")
		return False


def is_add_on_change_allowed(event_id: str | int) -> bool:
	"""Check if add-on changes are allowed based on event start date and settings."""
	try:
		# Get event details
		event = frappe.get_cached_doc("FE Event", event_id)

		# Get event management settings
		settings = frappe.get_cached_doc("Event Management Settings")

		# Default to 7 days if no setting is found
		add_on_change_cutoff_days = settings.get("allow_add_ons_change_before_event_start_days", 7)

		# Calculate days difference between today and event start date
		event_start_date = event.start_date
		if not event_start_date:
			return False

		# Get days remaining until event starts
		days_until_event = days_diff(event_start_date, today())

		# Add-on changes are allowed if there are more days remaining than the cutoff
		return days_until_event >= add_on_change_cutoff_days

	except Exception as e:
		frappe.log_error(f"Error checking add-on change eligibility: {e!s}")
		return False


@frappe.whitelist()
def can_transfer_ticket(event_id: str | int) -> dict:
	"""API endpoint to check if ticket transfer is allowed for an event."""
	return {"can_transfer": is_ticket_transfer_allowed(event_id), "event_id": event_id}


@frappe.whitelist()
def can_change_add_ons(event_id: str | int) -> dict:
	"""API endpoint to check if add-on changes are allowed for an event."""
	return {"can_change_add_ons": is_add_on_change_allowed(event_id), "event_id": event_id}


def is_cancellation_request_allowed(event_id: str | int) -> bool:
	"""Check if cancellation request is allowed based on event start date and settings."""
	try:
		# Get event details
		event = frappe.get_cached_doc("FE Event", event_id)

		# Get event management settings
		settings = frappe.get_cached_doc("Event Management Settings")

		# Default to 7 days if no setting is found
		cancellation_cutoff_days = settings.get(
			"allow_ticket_cancellation_request_before_event_start_days", 7
		)

		# Calculate days difference between today and event start date
		event_start_date = event.start_date
		if not event_start_date:
			return False

		# Get days remaining until event starts
		days_until_event = days_diff(event_start_date, today())

		# Cancellation request is allowed if there are more days remaining than the cutoff
		return days_until_event >= cancellation_cutoff_days

	except Exception as e:
		frappe.log_error(f"Error checking cancellation request eligibility: {e!s}")
		return False


@frappe.whitelist()
def can_request_cancellation(event_id: str | int) -> dict:
	"""API endpoint to check if cancellation request is allowed for an event."""
	return {"can_request_cancellation": is_cancellation_request_allowed(event_id), "event_id": event_id}


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

	# GST Settings
	event_settings = frappe.get_cached_doc("Event Management Settings")
	data.gst_settings = {
		"apply_gst_on_bookings": event_settings.apply_gst_on_bookings,
		"gst_percentage": event_settings.gst_percentage or 18,
	}

	return data


@frappe.whitelist()
def process_booking(attendees: list[dict], event: str) -> str:
	booking = frappe.new_doc("Event Booking")
	booking.event = event
	booking.user = frappe.session.user
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

	return get_payment_link_for_booking(
		booking.name, redirect_to=f"/dashboard/bookings/{booking.name}?success=true"
	)


def create_add_on_doc(attendee_name: str, add_ons: list[dict]):
	"""Create a new Attendee Ticket Add-on document."""
	return frappe.get_doc(
		{"doctype": "Attendee Ticket Add-on", "add_ons": add_ons, "attendee_name": attendee_name}
	).insert(ignore_permissions=True)


@frappe.whitelist()
def transfer_ticket(ticket_id: str, new_name: str, new_email: str):
	"""Transfer a ticket to a new attendee."""
	# Validate ticket exists
	if not frappe.db.exists("Event Ticket", ticket_id):
		frappe.throw(frappe._("Ticket not found."))

	ticket = frappe.get_doc("Event Ticket", ticket_id)

	# Check if ticket transfer is allowed
	if not is_ticket_transfer_allowed(ticket.event):
		frappe.throw(frappe._("Ticket transfer is not allowed at this time. The transfer window has closed."))

	# Store old attendee info for notification
	old_name = ticket.attendee_name
	old_email = ticket.attendee_email

	ticket.attendee_name = new_name
	ticket.attendee_email = new_email
	ticket.save(ignore_permissions=True)

	# Send email notifications
	send_ticket_transfer_emails(ticket.name, old_name, old_email, new_name, new_email)


def send_ticket_transfer_emails(ticket_id: str, old_name: str, old_email: str, new_name: str, new_email: str):
	"""Send email notifications for ticket transfer."""
	try:
		# Get ticket and event details
		ticket = frappe.get_doc("Event Ticket", ticket_id)
		event = frappe.get_doc("FE Event", ticket.event)
		booking = frappe.get_doc("Event Booking", ticket.booking)

		# Email to old attendee - notification of transfer
		old_attendee_subject = f"Your ticket for {event.title} has been transferred"
		old_attendee_message = f"""
		<p>Dear {old_name},</p>

		<p>This is to inform you that your ticket for <strong>{event.title}</strong> has been transferred to {new_name} ({new_email}).</p>

		<p><strong>Event Details:</strong></p>
		<ul>
			<li><strong>Event:</strong> {event.title}</li>
			<li><strong>Date:</strong> {format_date(event.start_date)}</li>
			<li><strong>Ticket Type:</strong> {ticket.ticket_type}</li>
			<li><strong>Booking ID:</strong> {booking.name}</li>
		</ul>

		<p>If you have any questions about this transfer, please contact us.</p>

		<p>Best regards,<br>
		{event.title} Team</p>
		"""

		frappe.sendmail(
			recipients=[old_email], subject=old_attendee_subject, message=old_attendee_message, delayed=False
		)

		# Email to new attendee - welcome and ticket details
		new_attendee_subject = f"Welcome! Your ticket for {event.title}"
		new_attendee_message = f"""
		<p>Dear {new_name},</p>

		<p>Great news! A ticket for <strong>{event.title}</strong> has been transferred to you.</p>

		<p><strong>Event Details:</strong></p>
		<ul>
			<li><strong>Event:</strong> {event.title}</li>
			<li><strong>Date:</strong> {format_date(event.start_date)}</li>
			<li><strong>Time:</strong> {format_time(event.start_time) if event.start_time else 'TBA'}</li>
			<li><strong>Venue:</strong> {event.venue or 'TBA'}</li>
			<li><strong>Ticket Type:</strong> {ticket.ticket_type}</li>
			<li><strong>Booking ID:</strong> {booking.name}</li>
		</ul>

		<p><strong>Your Ticket Details:</strong></p>
		<ul>
			<li><strong>Ticket ID:</strong> {ticket.name}</li>
			<li><strong>Attendee Name:</strong> {new_name}</li>
			<li><strong>Email:</strong> {new_email}</li>
		</ul>

		<p>Please save this email for your records. You may need to present this ticket information at the event entrance.</p>

		<p>We look forward to seeing you at the event!</p>

		<p>Best regards,<br>
		{event.title} Team</p>
		"""

		frappe.sendmail(
			recipients=[new_email], subject=new_attendee_subject, message=new_attendee_message, delayed=False
		)

	except Exception as e:
		frappe.log_error(f"Failed to send ticket transfer emails for ticket {ticket_id}: {e!s}")
		# Don't raise the exception to avoid failing the main transfer process


@frappe.whitelist()
def get_booking_details(booking_id: str) -> dict:
	"""Get detailed information about a specific booking."""
	details = frappe._dict()
	booking_doc = frappe.get_cached_doc("Event Booking", booking_id)
	details.doc = booking_doc

	tickets = frappe.db.get_all(
		"Event Ticket",
		filters={"booking": booking_id},
		fields=[
			"name",
			"attendee_name",
			"attendee_email",
			"ticket_type.title as ticket_type",
			"qr_code",
			"event",
		],
	)

	add_ons = frappe.db.get_all(
		"Ticket Add-on Value",
		filters={"parent": ("in", (ticket.name for ticket in tickets))},
		fields=["parent", "name", "add_on", "value", "add_on.title as add_on_title"],
	)

	# Get available options for add-ons
	event_add_ons = frappe.db.get_all(
		"Ticket Add-on",
		filters={"event": booking_doc.event, "user_selects_option": True},
		fields=["name", "title", "user_selects_option", "options"],
	)

	add_on_options_map = {}
	for event_add_on in event_add_ons:
		if event_add_on.user_selects_option:
			add_on_options_map[event_add_on.name] = (
				event_add_on.options.split("\n") if event_add_on.options else []
			)

	for ticket in tickets:
		ticket.add_ons = []
		for add_on in add_ons:
			if add_on.parent == ticket.name:
				add_on_data = {
					"id": add_on.name,
					"name": add_on.add_on,
					"title": add_on.add_on_title,
					"value": add_on.value,
					"options": add_on_options_map.get(add_on.add_on, []),
				}
				ticket.add_ons.append(add_on_data)
		ticket.add_ons = sorted(ticket.add_ons, key=lambda x: x["title"])

	details.tickets = tickets
	details.event = frappe.get_cached_doc("FE Event", booking_doc.event)
	details.can_transfer_ticket = can_transfer_ticket(details.event.name)
	details.can_change_add_ons = can_change_add_ons(details.event.name)
	details.can_request_cancellation = can_request_cancellation(details.event.name)

	# Check for existing cancellation request
	existing_cancellation = frappe.db.get_value(
		"Ticket Cancellation Request",
		{"booking": booking_id},
		["name", "cancel_full_booking", "creation"],
		as_dict=True,
	)
	details.cancellation_request = existing_cancellation

	# If there's a cancellation request, determine which tickets are cancelled
	if existing_cancellation:
		if existing_cancellation.cancel_full_booking:
			# If full booking cancellation, all tickets are considered cancelled
			details.cancelled_tickets = [ticket.name for ticket in tickets]
		else:
			# If partial cancellation, get specific tickets
			cancelled_tickets = frappe.db.get_all(
				"Ticket Cancellation Item", filters={"parent": existing_cancellation.name}, fields=["ticket"]
			)
			details.cancelled_tickets = [item.ticket for item in cancelled_tickets]
	else:
		details.cancelled_tickets = []

	return details


@frappe.whitelist()
def change_add_on_preference(add_on_id: str, new_value: str):
	"""Change the preference value for a ticket add-on."""
	# Validate that the add-on value exists
	if not frappe.db.exists("Ticket Add-on Value", add_on_id):
		frappe.throw(frappe._("Add-on value not found."))

	# Get the add-on value to find the associated ticket and event
	add_on_value = frappe.get_cached_doc("Ticket Add-on Value", add_on_id)

	# Get the ticket to find the event
	ticket = frappe.get_cached_doc("Event Ticket", add_on_value.parent)

	# Check if add-on changes are allowed for this event
	if not is_add_on_change_allowed(ticket.event):
		frappe.throw(
			frappe._(
				"Add-on changes are not allowed at this time. The change window has closed as the event is approaching."
			)
		)

	frappe.db.set_value(
		"Ticket Add-on Value",
		add_on_id,
		"value",
		new_value,
	)


@frappe.whitelist()
def get_sponsorship_details(enquiry_id: str) -> dict:
	"""Get detailed information about a sponsorship enquiry including event and sponsor details."""
	# Get the sponsorship enquiry
	enquiry = frappe.get_doc("Sponsorship Enquiry", enquiry_id)

	# Check if user has permission to view this enquiry
	if enquiry.owner != frappe.session.user and not frappe.has_permission(
		"Sponsorship Enquiry", "read", enquiry
	):
		frappe.throw(frappe._("Not permitted to view this sponsorship enquiry"))

	# Get tier title if tier exists
	tier_title = ""
	if enquiry.tier:
		tier_title = frappe.db.get_value("Sponsorship Tier", enquiry.tier, "title") or enquiry.tier

	# Get event details
	event_details = {}
	if enquiry.event:
		event = frappe.get_cached_doc("FE Event", enquiry.event)
		event_details = {
			"title": event.title,
			"short_description": getattr(event, "short_description", ""),
			"about": getattr(event, "about", ""),
			"start_date": event.start_date,
			"end_date": getattr(event, "end_date", ""),
			"venue": getattr(event, "venue", ""),
			"route": getattr(event, "route", ""),
		}

	# Check if there's a corresponding Event Sponsor
	sponsor_details = None
	sponsors = frappe.db.get_all(
		"Event Sponsor",
		filters={"enquiry": enquiry_id},
		fields=["name", "company_name", "company_logo", "creation", "event", "tier"],
		limit=1,
	)

	if sponsors:
		sponsor_details = sponsors[0]
		# Get sponsor tier title too
		if sponsor_details.get("tier"):
			sponsor_tier_title = frappe.db.get_value("Sponsorship Tier", sponsor_details["tier"], "title")
			sponsor_details["tier_title"] = sponsor_tier_title or sponsor_details["tier"]

	return {
		"enquiry": {
			"name": enquiry.name,
			"company_name": enquiry.company_name,
			"company_logo": enquiry.company_logo,
			"event": enquiry.event,
			"tier": enquiry.tier,
			"tier_title": tier_title,
			"status": enquiry.status,
			"creation": enquiry.creation,
			"owner": enquiry.owner,
		},
		"event_details": event_details,
		"sponsor_details": sponsor_details,
		"has_sponsor": bool(sponsor_details),
	}


@frappe.whitelist()
def get_user_sponsorship_inquiries() -> list:
	"""Get all sponsorship inquiries for the current user."""
	inquiries = frappe.db.get_all(
		"Sponsorship Enquiry",
		filters={"owner": frappe.session.user},
		fields=["name", "company_name", "event", "tier", "status", "creation"],
		order_by="creation desc",
	)

	# Get event titles and tier titles
	for inquiry in inquiries:
		if inquiry.event:
			event_title = frappe.db.get_value("FE Event", inquiry.event, "title")
			inquiry["event_title"] = event_title

		if inquiry.tier:
			tier_title = frappe.db.get_value("Sponsorship Tier", inquiry.tier, "title")
			inquiry["tier_title"] = tier_title or inquiry.tier
		else:
			inquiry["tier_title"] = ""

	# Check which inquiries have corresponding sponsors
	inquiry_names = [inquiry.name for inquiry in inquiries]
	if inquiry_names:
		sponsors = frappe.db.get_all(
			"Event Sponsor",
			filters={"enquiry": ["in", inquiry_names]},
			fields=["enquiry"],
		)
		sponsored_inquiries = {sponsor.enquiry for sponsor in sponsors}

		for inquiry in inquiries:
			inquiry["has_sponsor"] = inquiry.name in sponsored_inquiries
	else:
		for inquiry in inquiries:
			inquiry["has_sponsor"] = False

	return inquiries


@frappe.whitelist()
def create_sponsorship_payment_link(enquiry_id: str, tier_id: str) -> str:
	"""Create a payment link for a sponsorship enquiry with selected tier."""
	from events.payments import get_payment_link_for_sponsorship

	# Verify the enquiry belongs to the current user
	enquiry = frappe.get_doc("Sponsorship Enquiry", enquiry_id)
	if enquiry.owner != frappe.session.user:
		frappe.throw(frappe._("Not permitted to create payment for this enquiry"))

	# Create payment link
	redirect_url = f"/dashboard/account/sponsorships/{enquiry_id}?success=true"
	return get_payment_link_for_sponsorship(enquiry_id, tier_id, redirect_url)


@frappe.whitelist()
def withdraw_sponsorship_enquiry(enquiry_id: str):
	"""Withdraw a sponsorship enquiry if it's not paid yet."""
	# Verify the enquiry exists and belongs to the current user
	enquiry = frappe.get_cached_doc("Sponsorship Enquiry", enquiry_id)
	if enquiry.owner != frappe.session.user:
		frappe.throw(frappe._("Not permitted to withdraw this enquiry"))

	# Check if the enquiry can be withdrawn (not paid)
	if enquiry.status == "Paid":
		frappe.throw(frappe._("Cannot withdraw a paid sponsorship enquiry"))

	if enquiry.status == "Withdrawn":
		frappe.throw(frappe._("This sponsorship enquiry has already been withdrawn"))

	# Update status to withdrawn
	enquiry.status = "Withdrawn"
	enquiry.save(ignore_permissions=True)


@frappe.whitelist()
def get_ticket_details(ticket_id: str) -> dict:
	"""Get detailed information about a specific ticket."""
	details = frappe._dict()
	ticket_doc = frappe.get_cached_doc("Event Ticket", ticket_id)

	if frappe.session.user != "Administrator":
		# Verify the ticket belongs to the current user
		if ticket_doc.attendee_email != frappe.session.user:
			frappe.throw(frappe._("Not permitted to view this ticket"))

	details.doc = ticket_doc

	# Get add-ons with their details
	add_ons = frappe.db.get_all(
		"Ticket Add-on Value",
		filters={"parent": ticket_id},
		fields=["name", "add_on", "add_on.title as add_on_title", "value", "price", "currency"],
	)

	# Get available options for add-ons (for preference management)
	event_add_ons = frappe.db.get_all(
		"Ticket Add-on",
		filters={"event": ticket_doc.event, "user_selects_option": True},
		fields=["name", "title", "user_selects_option", "options"],
	)

	add_on_options_map = {}
	for event_add_on in event_add_ons:
		if event_add_on.user_selects_option:
			add_on_options_map[event_add_on.name] = (
				event_add_on.options.split("\n") if event_add_on.options else []
			)

	# Enhance add-ons data with options
	enhanced_add_ons = []
	for add_on in add_ons:
		add_on_data = {
			"id": add_on.name,
			"name": add_on.add_on,
			"title": add_on.add_on_title,
			"value": add_on.value,
			"price": add_on.price,
			"currency": add_on.currency,
			"options": add_on_options_map.get(add_on.add_on, []),
		}
		enhanced_add_ons.append(add_on_data)

	details.add_ons = enhanced_add_ons
	details.event = frappe.get_cached_doc("FE Event", ticket_doc.event)

	# Only include booking information if the current user is the owner of the booking
	booking_doc = None
	if ticket_doc.booking:
		booking_doc = frappe.get_cached_doc("Event Booking", ticket_doc.booking)
		# Check if current user is the owner of the booking
		if booking_doc.owner == frappe.session.user:
			details.booking = booking_doc
		else:
			details.booking = None
	else:
		details.booking = None

	details.ticket_type = frappe.get_cached_doc("Event Ticket Type", ticket_doc.ticket_type)
	details.can_transfer_ticket = (
		can_transfer_ticket(details.event.name) if details.event else {"can_transfer": False}
	)
	details.can_change_add_ons = (
		can_change_add_ons(details.event.name) if details.event else {"can_change_add_ons": False}
	)
	details.can_request_cancellation = (
		can_request_cancellation(details.event.name) if details.event else {"can_request_cancellation": False}
	)

	return details


@frappe.whitelist()
def create_cancellation_request(booking_id: str, ticket_ids: list | None = None) -> dict:
	"""Create a cancellation request for a booking and optionally specific tickets."""
	# Get booking details
	booking_doc = frappe.get_cached_doc("Event Booking", booking_id)

	# Check if cancellation request is allowed for this event
	if not is_cancellation_request_allowed(booking_doc.event):
		frappe.throw("Cancellation requests are no longer allowed for this event.")

	# Check if a cancellation request already exists for this booking
	existing_request = frappe.db.exists("Ticket Cancellation Request", {"booking": booking_id})
	if existing_request:
		frappe.throw("A cancellation request already exists for this booking.")

	# Determine if this is a full booking cancellation
	all_tickets = frappe.db.get_all("Event Ticket", filters={"booking": booking_id}, fields=["name"])
	cancel_full_booking = not ticket_ids or len(ticket_ids) == len(all_tickets)

	# Create the cancellation request
	cancellation_request = frappe.new_doc("Ticket Cancellation Request")
	cancellation_request.booking = booking_id
	cancellation_request.cancel_full_booking = cancel_full_booking

	# If not full booking cancellation, add specific tickets to the child table
	if not cancel_full_booking and ticket_ids:
		for ticket_id in ticket_ids:
			# Verify ticket belongs to this booking
			ticket_booking = frappe.db.get_value("Event Ticket", ticket_id, "booking")
			if ticket_booking != booking_id:
				frappe.throw(f"Ticket {ticket_id} does not belong to booking {booking_id}")

			cancellation_request.append("tickets", {"ticket": ticket_id})

	cancellation_request.insert(ignore_permissions=True)

	return {
		"success": True,
		"message": "Cancellation request submitted successfully.",
		"cancellation_request": cancellation_request.name,
	}


@frappe.whitelist()
def validate_ticket_for_checkin(ticket_id: str) -> dict:
	"""Validate a ticket for check-in without requiring user authentication."""
	try:
		# Check if ticket exists
		if not frappe.db.exists("Event Ticket", ticket_id):
			return {
				"success": False,
				"error": "Ticket not found",
				"message": "The scanned ticket ID does not exist.",
			}

		# Get ticket details
		ticket_doc = frappe.get_cached_doc("Event Ticket", ticket_id)

		# Get event details
		event_doc = frappe.get_cached_doc("FE Event", ticket_doc.event)

		# Get booking details
		booking_doc = (
			frappe.get_cached_doc("Event Booking", ticket_doc.booking) if ticket_doc.booking else None
		)

		# Get ticket type details
		ticket_type_doc = (
			frappe.get_cached_doc("Event Ticket Type", ticket_doc.ticket_type)
			if ticket_doc.ticket_type
			else None
		)

		# Check if booking is confirmed
		if booking_doc and booking_doc.docstatus != 1:
			return {
				"success": False,
				"error": "Invalid ticket",
				"message": "This ticket is not confirmed and cannot be used for check-in.",
			}

		# Check if ticket is already checked in
		existing_checkin = frappe.db.exists("Event Check In", {"ticket": ticket_id})
		if existing_checkin:
			checkin_doc = frappe.get_doc("Event Check In", existing_checkin)
			return {
				"success": False,
				"error": "Already checked in",
				"message": f"This ticket was already checked in on {checkin_doc.creation}.",
				"ticket": {
					"id": ticket_doc.name,
					"attendee_name": ticket_doc.attendee_name,
					"attendee_email": ticket_doc.attendee_email,
					"event_title": event_doc.title,
					"ticket_type": ticket_type_doc.title if ticket_type_doc else ticket_doc.ticket_type,
					"check_in_time": checkin_doc.creation,
					"is_checked_in": True,
				},
			}

		# Get add-ons
		add_ons = frappe.db.get_all(
			"Ticket Add-on Value",
			filters={"parent": ticket_id},
			fields=["add_on", "add_on.title as add_on_title", "value", "price", "currency"],
		)

		return {
			"success": True,
			"message": "Valid ticket ready for check-in",
			"ticket": {
				"id": ticket_doc.name,
				"attendee_name": ticket_doc.attendee_name,
				"attendee_email": ticket_doc.attendee_email,
				"event_title": event_doc.title,
				"ticket_type": ticket_type_doc.title if ticket_type_doc else ticket_doc.ticket_type,
				"venue": event_doc.venue,
				"start_date": event_doc.start_date,
				"start_time": event_doc.start_time,
				"end_date": event_doc.end_date,
				"end_time": event_doc.end_time,
				"is_checked_in": False,
				"check_in_time": None,
				"booking_id": ticket_doc.booking,
				"add_ons": add_ons,
				"amount": booking_doc.total_amount if booking_doc else 0,
				"currency": booking_doc.currency if booking_doc else "USD",
			},
		}

	except Exception as e:
		frappe.log_error(f"Error validating ticket for check-in: {e!s}")
		return {
			"success": False,
			"error": "System error",
			"message": "An error occurred while validating the ticket. Please try again.",
		}


@frappe.whitelist()
def checkin_ticket(ticket_id: str) -> dict:
	"""Check in a ticket."""
	try:
		# Validate ticket first
		validation_result = validate_ticket_for_checkin(ticket_id)

		if not validation_result["success"]:
			return validation_result

		# Create check-in record
		checkin_doc = frappe.new_doc("Event Check In")
		checkin_doc.ticket = ticket_id
		# Event will be auto-fetched from ticket based on the fetch_from setting
		checkin_doc.insert(ignore_permissions=True)
		checkin_doc.submit()

		return {
			"success": True,
			"message": f"Successfully checked in {validation_result['ticket']['attendee_name']}",
			"ticket": {
				**validation_result["ticket"],
				"is_checked_in": True,
				"check_in_time": checkin_doc.creation,
			},
		}

	except Exception as e:
		frappe.log_error(f"Error checking in ticket: {e!s}")
		return {
			"success": False,
			"error": "Check-in failed",
			"message": "An error occurred while checking in the ticket. Please try again.",
		}
