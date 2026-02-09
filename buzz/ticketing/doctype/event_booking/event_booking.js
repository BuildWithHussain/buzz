// Copyright (c) 2025, BWH Studios and contributors
// For license information, please see license.txt

frappe.ui.form.on("Event Booking", {
	refresh(frm) {
		frm.set_query("ticket_type", "attendees", (doc, cdt, cdn) => {
			return {
				filters: {
					event: doc.event,
				},
			};
		});

		// Add custom buttons for Event Managers
		if (frappe.user.has_role('Event Manager')) {
			// Show Approve/Reject buttons for pending bookings
			if (frm.doc.status === 'Approval Pending') {
				frm.add_custom_button(__('Approve'), function() {
					frappe.confirm(
						'Are you sure you want to approve this booking?',
						function() {
							frm.call('approve_booking').then(() => {
								frm.refresh();
							});
						}
					);
				}, __('Actions'));
				
				frm.add_custom_button(__('Reject'), function() {
					frappe.confirm(
						'Are you sure you want to reject this booking?',
						function() {
							frm.call('reject_booking').then(() => {
								frm.refresh();
							});
						}
					);
				}, __('Actions'));
			}
		}
	},
});