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

		// Check if this is a UPI payment
		let isUpiPayment = false;
		let isVerified = false;
		
		if (frm.doc.additional_fields) {
			for (let field of frm.doc.additional_fields) {
				if (field.fieldname === 'payment_method' && field.value === 'UPI') {
					isUpiPayment = true;
				}
				if (field.fieldname === 'payment_verified' && field.value === 'Yes') {
					isVerified = true;
				}
			}
		}
		
		// Hide both buttons first
		frm.toggle_display('upi_payment_verification', false);
		frm.toggle_display('upi_payment_unverify', false);
		
		// Show appropriate button based on status
		if (isUpiPayment && frappe.user.has_role('Event Manager')) {
			if (isVerified) {
				frm.toggle_display('upi_payment_unverify', true);
			} else {
				frm.toggle_display('upi_payment_verification', true);
			}
		}
	},
});