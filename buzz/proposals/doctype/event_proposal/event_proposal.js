// Copyright (c) 2025, BWH Studios and contributors
// For license information, please see license.txt

frappe.ui.form.on("Event Proposal", {
	refresh(frm) {
		if (!frm.is_new() && frm.doc.docstatus == 0) {
			frm.set_intro("Buzz Event will be created on submission of this document", "yellow");
		}
	},
});
