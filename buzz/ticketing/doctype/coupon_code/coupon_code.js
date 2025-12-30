// Copyright (c) 2025, BWH Studios and contributors
// For license information, please see license.txt

frappe.ui.form.on("Coupon Code", {
	refresh(frm) {
		frm.set_query("ticket_type", () => {
			return {
				filters: {
					event: frm.doc.event,
				},
			};
		});

		frm.set_query("add_on", "free_add_ons", () => {
			return {
				filters: {
					event: frm.doc.event,
				},
			};
		});
	},
});
