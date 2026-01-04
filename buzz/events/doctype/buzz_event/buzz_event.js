// Copyright (c) 2025, BWH Studios and contributors
// For license information, please see license.txt

frappe.ui.form.on("Buzz Event", {
	refresh(frm) {
		frappe.call("frappe.geo.country_info.get_country_timezone_info").then(({ message }) => {
			frm.fields_dict.time_zone.set_data(message.all_timezones);
		});

		if (frm.doc.route && frm.doc.is_published) {
			frm.add_web_link(`/events/${frm.doc.route}`);
		}

		if (frm.doc.route) {
			frm.add_web_link(`/dashboard/book-tickets/${frm.doc.route}`, "View Registration Page");
		}

		const button_label = frm.doc.is_published ? __("Unpublish") : __("Publish");
		frm.add_custom_button(button_label, () => {
			frm.set_value("is_published", !frm.doc.is_published);
			frm.save();
		});

		frm.set_query("track", "schedule", (doc, cdt, cdn) => {
			return {
				filters: {
					event: doc.name,
				},
			};
		});

		frm.set_query("default_ticket_type", (doc) => {
			return {
				filters: {
					event: doc.name,
					is_published: 1,
				},
			};
		});

		// Save as Template button
		if (!frm.is_new()) {
			frm.add_custom_button(
				__("Save as Template"),
				function () {
					buzz.events.show_save_as_template_dialog(frm);
				},
				__("Actions")
			);
		}

		frm.trigger("add_zoom_custom_actions");
	},

	add_zoom_custom_actions(frm) {
		const installed_apps = frappe.boot.app_data.map((app) => app.app_name);
		if (!installed_apps.includes("zoom_integration") || frm.doc.category != "Webinars") {
			return;
		}

		if (frm.doc.zoom_webinar) {
			frm.add_custom_button(__("View Webinar on Zoom"), () => {
				window.open(`https://zoom.us/webinar/${frm.doc.zoom_webinar}`, "_blank");
			});
			return;
		}

		const btn = frm.add_custom_button(__("Create Webinar on Zoom"), () => {
			frm.call({
				doc: frm.doc,
				method: "create_webinar_on_zoom",
				btn,
				freeze: true,
			}).then(({ message }) => {
				frm.layout.tabs.find((t) => t.label == "Zoom Integration").set_active();
			});
		});
	},
});
