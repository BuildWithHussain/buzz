// Copyright (c) 2025, BWH Studios and contributors
// For license information, please see license.txt

window.event_route = "";

frappe.ui.form.on("Additional Event Page", {
	onload(frm) {
		frappe.db.get_value("Buzz Event", frm.doc.event, "route").then(({ message }) => {
			window.event_route = message.route;
		});
	},
	refresh(frm) {
		if (frm.doc.is_published) {
			frm.add_web_link(`/events/${window.event_route}/${frm.doc.route}`);
		}
	},
});
