// Copyright (c) 2025, BWH Studios and contributors
// For license information, please see license.txt

frappe.ui.form.on("Talk Proposal", {
	refresh(frm) {
		if (frm.doc.status != "Approved") {
			const btn = frm.add_custom_button(__("Approve and Create Talk"), () => {
				frm.call({
					method: "create_talk",
					doc: frm.doc,
					btn,
				}).then(({ message: talk }) => {
					frm.set_value("status", "Approved");
					frm.save();
					frm.refresh();
					frappe.set_route("Form", "Event Talk", talk.name);
				});
			});
		}
	},
});
