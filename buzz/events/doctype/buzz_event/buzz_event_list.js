frappe.listview_settings["Buzz Event"] = {
	onload: function (listview) {
		if (frappe.perm.has_perm("Event Template", 0, "read")) {
			listview.page.add_inner_button(__("Create from Template"), function () {
				buzz.events.show_create_from_template_dialog();
			});
		}
	},
};
