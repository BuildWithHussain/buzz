# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Frontend (Dashboard)
```bash
# dev server
yarn dev  # or: cd dashboard && yarn dev

# build for production
yarn build  # outputs to buzz/public/dashboard + buzz/www/dashboard.html

# lint/format frontend
cd dashboard && yarn lint
```

### Backend (Python)
```bash
# linting/formatting (via pre-commit)
pre-commit run --all-files

# run ruff directly
ruff check buzz/
ruff format buzz/

# install app to site
bench --site [site-name] install-app buzz
```

Use bench --help to see how to work with frappe bench, e.g. bench execute, bench console, etc. are very useful

### Testing

There are unit tests, run using bench run-tests. Site name is buzz.localhost, but if not found, ask user for it

To test in UI, use agent-browser. For frontend changes use :8080 since yarn dev server is running.

## Architecture

**Three-tier stack:**
1. **Backend**: Frappe Framework (Python) - DocTypes, API, permissions, scheduler
2. **Dashboard**: Vue 3 + FrappeUI + Vite - attendee/sponsor/checkin UI

**Core entity**: `Buzz Event` DocType drives everything (tickets, sponsors, schedule, payments).

**Main modules** (inside `buzz/`):
- `events/` - Event, Venue, Category, Talks, Sponsors, Check-ins
- `ticketing/` - Bookings, Tickets, Add-ons, Cancellations, Coupons
- `proposals/` - Talk Proposals, Sponsorship Enquiries
- `buzz/` - Settings, Custom Fields
- `api.py` - whitelisted API methods for dashboard
- `payments.py` - integration with frappe/payments app

**Frontend structure** (inside `dashboard/`):
- `src/pages/` - route components (BookTickets, TicketDetails, CheckInScanner, etc)
- `src/components/` - BookingForm, dialogs, shared UI
- `src/composables/` - reusable logic (useTicketValidation, usePaymentSuccess, etc)
- `src/data/` - frappe-ui resources for API calls
- Vite builds to `buzz/public/dashboard/`, router base is `/dashboard`

**Key flows:**
- Booking: load event data → fill form → create booking → generate payment link → on payment auth → submit booking → generate tickets + QR + email
- Ticket actions: transfer, cancel, change add-on (window checks from Buzz Settings)
- Sponsorship: enquiry → approval → payment link → payment auth → create sponsor record
- Check-in: scan QR → validate → create check-in record (requires Frontdesk Manager role)

**Integrations:**
- `frappe/payments` required for payment gateways
- `buildwithhussain/zoom_integration` optional for webinar creation/registration

## Key Paths for Common Tasks

**Booking changes**: `buzz/api.py`, `buzz/ticketing/doctype/event_booking/`, `dashboard/src/components/BookingForm.vue`

**Ticket lifecycle**: `buzz/ticketing/doctype/event_ticket/`, `dashboard/src/pages/TicketDetails.vue`

**Sponsorships**: `buzz/proposals/doctype/sponsorship_enquiry/`, `dashboard/src/pages/SponsorshipDetails.vue`

**Check-in**: `buzz/api.py` (validate_ticket_for_checkin, checkin_ticket), `dashboard/src/pages/CheckInScanner.vue`

**Event config**: `buzz/events/doctype/buzz_event/`

**Reports**: `buzz/events/report/` and `buzz/ticketing/report/`

## Notes

- Read `ARCHITECTURE.md` for comprehensive details on data model, API surface, flows
