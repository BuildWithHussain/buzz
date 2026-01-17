import frappe
from frappe import _
from frappe.translate import get_all_translations
from frappe.utils import days_diff, format_date, format_time, today

from buzz.payments import get_payment_gateways_for_event, get_payment_link_for_booking


@frappe.whitelist()
def get_event_payment_gateways(event: str) -> list[str]:
	"""Get available payment gateways for an event."""
	return get_payment_gateways_for_event(event)


def is_ticket_transfer_allowed(event_id: str | int) -> bool:
	"""Check if ticket transfer is allowed based on event start date and settings."""
	try:
		# Get event details
		event = frappe.get_cached_doc("Buzz Event", event_id)

		# Get event management settings
		settings = frappe.get_single("Buzz Settings")

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
		event = frappe.get_cached_doc("Buzz Event", event_id)

		# Get event management settings
		settings = frappe.get_cached_doc("Buzz Settings")

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
		event = frappe.get_cached_doc("Buzz Event", event_id)

		# Get event management settings
		settings = frappe.get_cached_doc("Buzz Settings")

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
	event_doc = frappe.get_cached_doc("Buzz Event", {"route": event_route})

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
		"Ticket Add-on", filters={"event": event_doc.name, "enabled": 1}, fields=["*"], order_by="title"
	)

	for add_on in add_ons:
		if add_on.user_selects_option:
			add_on.options = add_on.options.split("\n")

	data.available_add_ons = add_ons

	# Tax Settings (from Event)
	data.tax_settings = {
		"apply_tax": event_doc.apply_tax,
		"tax_label": event_doc.tax_label or "Tax",
		"tax_percentage": event_doc.tax_percentage or 0,
	}

	data.event_details = event_doc

	# Custom Fields
	custom_fields = frappe.db.get_all(
		"Buzz Custom Field",
		filters={"event": event_doc.name, "enabled": 1},
		fields=["*"],
		order_by="order",
	)
	data.custom_fields = custom_fields

	# Payment Gateways
	data.payment_gateways = get_payment_gateways_for_event(event_doc.name)

	return data


@frappe.whitelist()
def process_booking(
	attendees: list[dict],
	event: str,
	coupon_code: str | None = None,
	booking_custom_fields: dict | None = None,
	payment_gateway: str | None = None,
	utm_parameters: list[dict] | None = None,
) -> dict:
	booking = frappe.new_doc("Event Booking")
	booking.event = event
	booking.coupon_code = coupon_code
	booking.user = frappe.session.user

	# Add UTM parameters (captured from URL query params starting with utm_)
	if utm_parameters:
		for utm_param in utm_parameters:
			booking.append(
				"utm_parameters",
				{
					"utm_name": utm_param.get("utm_name"),
					"value": utm_param.get("value"),
				},
			)

	# Add booking-level custom fields
	if booking_custom_fields:
		# Get custom field definitions for this event to get proper labels and types
		booking_custom_field_defs = frappe.db.get_all(
			"Buzz Custom Field",
			filters={"event": event, "enabled": 1, "applied_to": "Booking"},
			fields=["fieldname", "label", "fieldtype"],
		)
		custom_field_map = {cf["fieldname"]: cf for cf in booking_custom_field_defs}

		for field_name, field_value in booking_custom_fields.items():
			if field_value and field_name in custom_field_map:  # Only add non-empty values and valid fields
				field_def = custom_field_map[field_name]
				booking.append(
					"additional_fields",
					{
						"fieldname": field_name,
						"value": str(field_value),
						"label": field_def["label"],
						"fieldtype": field_def["fieldtype"],
					},
				)
	for attendee in attendees:
		add_ons = attendee.get("add_ons", None)
		if add_ons:
			add_ons = create_add_on_doc(
				attendee_name=attendee["full_name"],
				add_ons=add_ons,
			)

		# Process custom fields for this attendee
		custom_fields = attendee.get("custom_fields", {})
		attendee_row = {
			"full_name": attendee.get("full_name"),
			"email": attendee.get("email"),
			"ticket_type": attendee.get("ticket_type"),
			"add_ons": add_ons.name if add_ons else None,
			"custom_fields": custom_fields if custom_fields else None,
		}

		booking.append("attendees", attendee_row)

	booking.insert(ignore_permissions=True)
	frappe.db.commit()

	if booking.total_amount == 0:
		booking.flags.ignore_permissions = True
		booking.submit()
		return {"booking_name": booking.name}

	return {
		"payment_link": get_payment_link_for_booking(
			booking.name,
			redirect_to=f"/dashboard/bookings/{booking.name}?success=true",
			payment_gateway=payment_gateway,
		)
	}


def create_add_on_doc(attendee_name: str, add_ons: list[dict]):
	"""Create a new Attendee Ticket Add-on document."""
	for add_on in add_ons:
		add_on["currency"] = frappe.db.get_value("Ticket Add-on", add_on["add_on"], "currency")

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
	booking_user = frappe.db.get_value("Event Booking", ticket.booking, "user")

	if (
		ticket.attendee_email != frappe.session.user
		and booking_user != frappe.session.user
		and not frappe.has_permission("Event Ticket", "write", ticket)
	):
		frappe.throw(frappe._("Not permitted to transfer this ticket."))

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
		event = frappe.get_doc("Buzz Event", ticket.event)
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
			"docstatus",
		],
	)

	add_ons = frappe.db.get_all(
		"Ticket Add-on Value",
		filters={"parent": ("in", [ticket.name for ticket in tickets])},
		fields=[
			"parent",
			"name",
			"add_on",
			"value",
			"add_on.title as add_on_title",
			"add_on.user_selects_option as user_selects_option",
		],
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
					"user_selects_option": add_on.user_selects_option,
					"options": add_on_options_map.get(add_on.add_on, []),
				}
				ticket.add_ons.append(add_on_data)
		ticket.add_ons = sorted(ticket.add_ons, key=lambda x: x["title"])

	details.tickets = tickets
	details.event = frappe.get_cached_doc("Buzz Event", booking_doc.event)

	# Get venue details if venue is set
	if details.event.venue:
		details.venue = frappe.get_cached_doc("Event Venue", details.event.venue)

	details.can_transfer_ticket = can_transfer_ticket(details.event.name)
	details.can_change_add_ons = can_change_add_ons(details.event.name)
	details.can_request_cancellation = can_request_cancellation(details.event.name)

	# Payment
	frappe.db.get_all("Event Payment", filters={})

	# Check for existing cancellation request
	existing_cancellation = frappe.db.get_value(
		"Ticket Cancellation Request",
		{"booking": booking_id},
		["name", "cancel_full_booking", "creation", "status", "docstatus"],
		as_dict=True,
	)
	details.cancellation_request = existing_cancellation

	# Determine which tickets have cancellation requested (not yet submitted/accepted)
	# and which tickets are actually cancelled (docstatus = 2)
	details.cancellation_requested_tickets = []

	if existing_cancellation and existing_cancellation.docstatus == 0:
		# Cancellation request exists but not yet submitted (status is "In Review")
		if existing_cancellation.cancel_full_booking:
			# If full booking cancellation requested, all tickets have pending cancellation
			details.cancellation_requested_tickets = [ticket.name for ticket in tickets]
		else:
			# If partial cancellation requested, get specific tickets
			requested_tickets = frappe.db.get_all(
				"Ticket Cancellation Item", filters={"parent": existing_cancellation.name}, fields=["ticket"]
			)
			details.cancellation_requested_tickets = [item.ticket for item in requested_tickets]

	# Get list of actually cancelled tickets (docstatus = 2)
	details.cancelled_tickets = [ticket.name for ticket in tickets if ticket.docstatus == 2]

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
		event = frappe.get_cached_doc("Buzz Event", enquiry.event)
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
			event_title = frappe.db.get_value("Buzz Event", inquiry.event, "title")
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
def create_sponsorship_payment_link(enquiry_id: str, tier_id: str, payment_gateway: str | None = None) -> str:
	"""Create a payment link for a sponsorship enquiry with selected tier."""
	from buzz.payments import get_payment_link_for_sponsorship

	# Verify the enquiry belongs to the current user
	enquiry = frappe.get_doc("Sponsorship Enquiry", enquiry_id)
	if enquiry.owner != frappe.session.user:
		frappe.throw(frappe._("Not permitted to create payment for this enquiry"))

	# Create payment link
	redirect_url = f"/dashboard/account/sponsorships/{enquiry_id}?success=true"
	return get_payment_link_for_sponsorship(
		enquiry_id, tier_id, redirect_url, payment_gateway=payment_gateway
	)


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
		fields=[
			"name",
			"add_on",
			"add_on.title as add_on_title",
			"value",
			"price",
			"currency",
			"add_on.user_selects_option as user_selects_option",
		],
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

	# Enhance add-ons data with options - include all add-ons but pass user_selects_option flag
	enhanced_add_ons = []
	for add_on in add_ons:
		add_on_data = {
			"id": add_on.name,
			"name": add_on.add_on,
			"title": add_on.add_on_title,
			"value": add_on.value,
			"price": add_on.price,
			"currency": add_on.currency,
			"user_selects_option": add_on.user_selects_option,
			"options": add_on_options_map.get(add_on.add_on, []),
		}
		enhanced_add_ons.append(add_on_data)

	details.add_ons = enhanced_add_ons
	details.event = frappe.get_cached_doc("Buzz Event", ticket_doc.event)

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

	# Get Zoom webinar join URL if applicable
	details.zoom_join_url = None
	if hasattr(ticket_doc, "zoom_webinar_registration") and ticket_doc.zoom_webinar_registration:
		zoom_registration = frappe.db.get_value(
			"Zoom Webinar Registration",
			ticket_doc.zoom_webinar_registration,
			["join_url", "webinar"],
			as_dict=True,
		)
		if zoom_registration:
			details.zoom_join_url = zoom_registration.join_url
			details.zoom_webinar = zoom_registration.webinar

	return details


@frappe.whitelist()
def create_cancellation_request(booking_id: str, ticket_ids: list | None = None) -> dict:
	"""Create a cancellation request for a booking and optionally specific tickets."""
	# Get booking details
	booking_doc = frappe.get_cached_doc("Event Booking", booking_id)

	# Check permission - allow booking user or users with write permission
	if booking_doc.user != frappe.session.user and not frappe.has_permission(
		"Event Booking", "write", booking_doc
	):
		frappe.throw(frappe._("Not permitted to request cancellation for this booking."))

	# Check if cancellation request is allowed for this event
	if not is_cancellation_request_allowed(booking_doc.event):
		frappe.throw("Cancellation requests are no longer allowed for this event.")

	# Check if a cancellation request already exists for this booking
	existing_request = frappe.db.exists(
		"Ticket Cancellation Request", {"booking": booking_id, "docstatus": 0}
	)
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


@frappe.whitelist()
def get_user_info() -> dict:
	"""Get basic information about the logged-in user."""
	if frappe.session.user == "Guest":
		return {"is_logged_in": False}

	user = frappe.get_cached_doc("User", frappe.session.user)

	return {
		"name": user.name,
		"is_logged_in": True,
		"first_name": user.first_name,
		"last_name": user.last_name,
		"full_name": user.full_name,
		"email": user.email,
		"user_image": user.user_image,
		"roles": user.roles,
		"brand_image": frappe.get_single_value("Website Settings", "banner_image"),
		"language": user.language,
	}


@frappe.whitelist()
def validate_ticket_for_checkin(ticket_id: str) -> dict:
	frappe.only_for("Frontdesk Manager", True)
	if not frappe.db.exists("Event Ticket", ticket_id):
		frappe.throw(_("Ticket not found"))

	ticket_doc = frappe.get_cached_doc("Event Ticket", ticket_id)

	if ticket_doc.docstatus == 2:
		frappe.throw(_("This ticket has been cancelled and cannot be checked in"))

	event_doc = frappe.get_cached_doc("Buzz Event", ticket_doc.event)
	ticket_type_doc = (
		frappe.get_cached_doc("Event Ticket Type", ticket_doc.ticket_type) if ticket_doc.ticket_type else None
	)

	# Check if ticket is already checked in today
	checkin_date = frappe.utils.today()
	existing_checkin = frappe.db.exists("Event Check In", {"ticket": ticket_id, "date": checkin_date})

	if existing_checkin:
		checkin_doc = frappe.get_doc("Event Check In", existing_checkin)
		# Format the check-in time for display
		formatted_checkin_time = (
			format_date(checkin_doc.creation) + " at " + format_time(checkin_doc.creation)
		)

		frappe.throw(_("This ticket was already checked in today ({0}).").format(formatted_checkin_time))

	# Get add-ons
	add_ons = frappe.db.get_all(
		"Ticket Add-on Value",
		filters={"parent": ticket_id},
		fields=[
			"add_on",
			"add_on.title as add_on_title",
			"add_on.user_selects_option as add_on_selects_option",
			"value",
			"price",
			"currency",
		],
	)

	return {
		"message": _("Valid ticket ready for check-in"),
		"ticket": {
			"id": ticket_doc.name,
			"attendee_name": ticket_doc.attendee_name,
			"attendee_email": ticket_doc.attendee_email,
			"event_title": event_doc.title,
			"ticket_type": (ticket_type_doc.title if ticket_type_doc else ticket_doc.ticket_type),
			"venue": event_doc.venue,
			"start_date": event_doc.start_date,
			"start_time": event_doc.start_time,
			"end_date": event_doc.end_date,
			"end_time": event_doc.end_time,
			"is_checked_in": False,
			"check_in_time": None,
			"booking_id": ticket_doc.booking,
			"add_ons": add_ons,
		},
		"payment_details": get_payment_details_for_ticket(ticket_id),
	}


def get_payment_details_for_ticket(ticket_id: str) -> dict | None:
	booking = frappe.get_cached_doc(
		"Event Booking", frappe.get_cached_value("Event Ticket", ticket_id, "booking")
	)
	payments = frappe.db.get_all(
		"Event Payment",
		filters={
			"reference_doctype": "Event Booking",
			"reference_docname": booking.name,
			"payment_received": 1,
		},
		fields=["name", "amount", "currency"],
		limit=1,
	)

	if payments:
		return payments[0]


@frappe.whitelist()
def checkin_ticket(ticket_id: str) -> dict:
	"""Check in a ticket for today."""
	frappe.only_for("Frontdesk Manager", True)

	# Validate the ticket for check-in
	checkin_date = frappe.utils.today()
	validation_result = validate_ticket_for_checkin(ticket_id)

	# Create check-in record
	checkin_doc = frappe.new_doc("Event Check In")
	checkin_doc.ticket = ticket_id
	checkin_doc.date = checkin_date
	checkin_doc.insert(ignore_permissions=True)
	checkin_doc.submit()

	return {
		"message": _("Successfully checked in {attendee_name} for {checkin_date}").format(
			attendee_name=validation_result["ticket"]["attendee_name"],
			checkin_date=frappe.format(checkin_date, {"fieldtype": "Date"}),
		),
		"ticket": {
			**validation_result["ticket"],
			"is_checked_in": True,
			"check_in_time": checkin_doc.creation,
			"check_in_date": checkin_date,
		},
	}


@frappe.whitelist()
def get_enabled_languages():
	"""Get all enabled languages from the Language doctype."""
	languages = frappe.get_all(
		"Language",
		filters={"enabled": 1},
		fields=["name", "language_name", "language_code"],
		order_by="language_name",
	)
	return languages


@frappe.whitelist()
def update_user_language(language_code: str):
	"""Update the current user's preferred language."""
	if not frappe.db.exists("Language", {"language_code": language_code}):
		frappe.throw(_("Invalid language"))

	frappe.db.set_value("User", frappe.session.user, "language", language_code)


@frappe.whitelist(allow_guest=True)
def get_translations():
	if frappe.session.user != "Guest":
		language = frappe.db.get_value("User", frappe.session.user, "language")
	else:
		language = frappe.db.get_single_value("System Settings", "language")

	return get_all_translations(language)


def has_app_permission():
	return True


@frappe.whitelist()
def validate_coupon(coupon_code: str, event: str) -> dict:
	if not frappe.db.exists("Buzz Coupon Code", coupon_code):
		return {"valid": False, "error": _("Invalid coupon code")}

	coupon = frappe.get_doc("Buzz Coupon Code", coupon_code)

	is_valid, error = coupon.is_valid_for_event(event)
	if not is_valid:
		return {"valid": False, "error": error}

	is_available, error = coupon.is_usage_available()
	if not is_available:
		return {"valid": False, "error": error}

	is_limited, error = coupon.is_user_limit_reached()
	if is_limited:
		return {"valid": False, "error": error}

	if coupon.coupon_type == "Discount":
		return {
			"valid": True,
			"coupon_type": "Discount",
			"discount_type": coupon.discount_type,
			"discount_value": coupon.discount_value,
			"max_discount_amount": coupon.maximum_discount_amount or 0,
			"min_order_value": coupon.minimum_order_value or 0,
		}

	remaining = coupon.number_of_free_tickets - coupon.free_tickets_claimed
	if remaining <= 0:
		return {"valid": False, "error": _("All free tickets have been claimed")}

	return {
		"valid": True,
		"coupon_type": "Free Tickets",
		"ticket_type": coupon.ticket_type,
		"remaining_tickets": remaining,
		"free_add_ons": [a.add_on for a in coupon.free_add_ons],
	}


@frappe.whitelist(allow_guest=True)
def get_feedback(ticket: str | None = None) -> dict:
	if not ticket:
		frappe.throw(_("Please provide a Ticket ID"))

	if not frappe.db.exists("Event Ticket", ticket):
		frappe.throw(_("Ticket not found"))

	try:
		# Fetch ticket details
		data = frappe.db.get_value(
			"Event Ticket", {"name": ticket, "docstatus": 1}, ["attendee_name", "event.title"], as_dict=True
		)

		if not data:
			frappe.throw(_("Ticket has been cancelled"))

		response = {"attendee_name": data.attendee_name, "event_title": data.title}

		# Check for existing feedback
		existing = frappe.db.get_value(
			"Event Feedback", {"ticket": ticket}, ["comment", "rating"], as_dict=True
		)

		if existing:
			response.update(
				{
					"status": "submitted",
					"comment": existing.comment,
					"rating": existing.rating * 5,  # Convert back to 0-5 scale
				}
			)
		else:
			response["status"] = "pending"

		return response

	except Exception as e:
		frappe.log_error(f"Error fetching feedback for ticket {ticket}: {e!s}")
		frappe.throw(_("An unexpected error occurred while fetching feedback"))


@frappe.whitelist(allow_guest=True)
def submit_feedback(ticket: str | None = None, comment: str | None = None, rating: int = 0) -> dict:
	if not ticket:
		frappe.throw(_("Please provide a Ticket ID"))

	if not frappe.db.exists("Event Ticket", ticket):
		frappe.throw(_("Ticket not found"))

	try:
		rating = int(rating)
	except (ValueError, TypeError):
		frappe.throw(_("Invalid rating value"))
	if rating < 0 or rating > 5:
		frappe.throw(_("Rating must be between 0 and 5"))

	if frappe.db.exists("Event Feedback", {"ticket": ticket}):
		frappe.throw(_("Feedback has already been submitted for this ticket"))

	try:
		ticket_doc = frappe.get_doc("Event Ticket", ticket)

		if ticket_doc.docstatus == 2:
			frappe.throw(_("Ticket has been cancelled"))

		doc = frappe.get_doc(
			{
				"doctype": "Event Feedback",
				"event": ticket_doc.event,
				"ticket": ticket_doc.name,
				"comment": comment,
				"rating": rating / 5,  # Normalize to 0-1 scale
			}
		)
		doc.insert(ignore_permissions=True)
		return {"status": "success", "message": _("Thank you for your feedback!")}

	except Exception as e:
		frappe.log_error(f"Error submitting feedback for ticket {ticket}: {e!s}")
		frappe.throw(_("An unexpected error occurred while submitting feedback"))
