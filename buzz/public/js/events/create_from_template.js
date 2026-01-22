frappe.provide("buzz.events");

// Field groups for template options
buzz.events.TEMPLATE_FIELD_GROUPS = {
	event_details: {
		label: __("Event Details"),
		fields: [
			"category",
			"host",
			"banner_image",
			"short_description",
			"about",
			"medium",
			"venue",
			"time_zone",
		],
	},
	ticketing_settings: {
		label: __("Ticketing Settings"),
		fields: [
			"apply_tax",
			"tax_label",
			"tax_percentage",
			"ticket_email_template",
			"ticket_print_format",
		],
	},
	sponsorship_settings: {
		label: __("Sponsorship Settings"),
		fields: [
			"auto_send_pitch_deck",
			"sponsor_deck_email_template",
			"sponsor_deck_reply_to",
			"sponsor_deck_cc",
			"sponsor_deck_attachments",
		],
	},
};

// Mandatory fields for Buzz Event that must be provided
buzz.events.MANDATORY_FIELDS = ["category", "host"];

buzz.events.show_create_from_template_dialog = function () {
	let dialog = new frappe.ui.Dialog({
		title: __("Create Event from Template"),
		fields: [
			{
				fieldtype: "Link",
				fieldname: "template",
				label: __("Select Template"),
				options: "Event Template",
				reqd: 1,
				change: function () {
					buzz.events.on_template_selected(dialog);
				},
			},
			{
				fieldtype: "Section Break",
				fieldname: "missing_fields_section",
				label: __("Required Fields"),
				depends_on: "eval:doc.template",
				hidden: 1,
			},
			{
				fieldtype: "HTML",
				fieldname: "missing_fields_info",
			},
			{
				fieldtype: "Link",
				fieldname: "category",
				label: __("Category"),
				options: "Event Category",
				hidden: 1,
			},
			{
				fieldtype: "Column Break",
			},
			{
				fieldtype: "Link",
				fieldname: "host",
				label: __("Host"),
				options: "Event Host",
				hidden: 1,
			},
			{
				fieldtype: "Section Break",
				fieldname: "options_section",
				label: __("Select What to Copy"),
				depends_on: "eval:doc.template",
			},
			{
				fieldtype: "HTML",
				fieldname: "select_buttons",
				depends_on: "eval:doc.template",
			},
			{
				fieldtype: "HTML",
				fieldname: "field_options",
				depends_on: "eval:doc.template",
			},
		],
		size: "large",
		primary_action_label: __("Create Event"),
		primary_action: function (values) {
			buzz.events.create_event_from_template(dialog, values);
		},
	});

	dialog.show();
};

buzz.events.on_template_selected = function (dialog) {
	let template_name = dialog.get_value("template");
	if (!template_name) {
		dialog.get_field("field_options").$wrapper.html("");
		dialog.get_field("select_buttons").$wrapper.html("");
		return;
	}

	frappe.call({
		method: "frappe.client.get",
		args: {
			doctype: "Event Template",
			name: template_name,
		},
		callback: function (r) {
			if (r.message) {
				buzz.events.render_template_options(dialog, r.message);
			}
		},
	});
};

buzz.events.render_template_options = function (dialog, template) {
	let html = "";

	// Select All / Unselect All buttons
	let buttons_html = `
		<div class="mb-3">
			<button class="btn btn-default btn-xs select-all-btn">${__("Select All")}</button>
			<button class="btn btn-default btn-xs unselect-all-btn">${__("Unselect All")}</button>
		</div>
	`;
	dialog.get_field("select_buttons").$wrapper.html(buttons_html);

	// Event Details section
	html += buzz.events.render_field_group("event_details", template);

	// Ticketing Settings section
	html += buzz.events.render_field_group("ticketing_settings", template);

	// Sponsorship Settings section
	html += buzz.events.render_field_group("sponsorship_settings", template);

	// Related Documents section
	html += '<div class="template-section mt-4">';
	html += `<h6 class="text-muted">${__("Related Documents")}</h6>`;
	html += '<div class="row">';

	// Payment Gateways
	let pg_count = template.payment_gateways ? template.payment_gateways.length : 0;
	html += `
		<div class="col-md-6 mb-2">
			<label class="d-flex align-items-center">
				<input type="checkbox" class="template-option mr-2" data-option="payment_gateways" ${
					pg_count > 0 ? "checked" : ""
				} ${pg_count === 0 ? "disabled" : ""}>
				${__("Payment Gateways")} ${
		pg_count > 0
			? `<span class="text-muted ml-1">(${pg_count})</span>`
			: '<span class="text-muted ml-1">(' + __("None") + ")</span>"
	}
			</label>
		</div>
	`;

	// Ticket Types
	let tt_count = template.template_ticket_types ? template.template_ticket_types.length : 0;
	html += `
		<div class="col-md-6 mb-2">
			<label class="d-flex align-items-center">
				<input type="checkbox" class="template-option mr-2" data-option="ticket_types" ${
					tt_count > 0 ? "checked" : ""
				} ${tt_count === 0 ? "disabled" : ""}>
				${__("Ticket Types")} ${
		tt_count > 0
			? `<span class="text-muted ml-1">(${tt_count})</span>`
			: '<span class="text-muted ml-1">(' + __("None") + ")</span>"
	}
			</label>
		</div>
	`;

	// Add-ons
	let addon_count = template.template_add_ons ? template.template_add_ons.length : 0;
	html += `
		<div class="col-md-6 mb-2">
			<label class="d-flex align-items-center">
				<input type="checkbox" class="template-option mr-2" data-option="add_ons" ${
					addon_count > 0 ? "checked" : ""
				} ${addon_count === 0 ? "disabled" : ""}>
				${__("Add-ons")} ${
		addon_count > 0
			? `<span class="text-muted ml-1">(${addon_count})</span>`
			: '<span class="text-muted ml-1">(' + __("None") + ")</span>"
	}
			</label>
		</div>
	`;

	// Custom Fields
	let cf_count = template.template_custom_fields ? template.template_custom_fields.length : 0;
	html += `
		<div class="col-md-6 mb-2">
			<label class="d-flex align-items-center">
				<input type="checkbox" class="template-option mr-2" data-option="custom_fields" ${
					cf_count > 0 ? "checked" : ""
				} ${cf_count === 0 ? "disabled" : ""}>
				${__("Custom Fields")} ${
		cf_count > 0
			? `<span class="text-muted ml-1">(${cf_count})</span>`
			: '<span class="text-muted ml-1">(' + __("None") + ")</span>"
	}
			</label>
		</div>
	`;

	html += "</div></div>";

	dialog.get_field("field_options").$wrapper.html(html);

	// Store template data on dialog for later use
	dialog.template_data = template;

	// Check and show mandatory fields that are missing from template
	buzz.events.update_mandatory_fields_visibility(dialog, template);

	// Bind select all / unselect all
	dialog
		.get_field("select_buttons")
		.$wrapper.find(".select-all-btn")
		.on("click", function () {
			dialog
				.get_field("field_options")
				.$wrapper.find(".template-option:not(:disabled)")
				.prop("checked", true);
			buzz.events.update_mandatory_fields_visibility(dialog, dialog.template_data);
		});

	dialog
		.get_field("select_buttons")
		.$wrapper.find(".unselect-all-btn")
		.on("click", function () {
			dialog
				.get_field("field_options")
				.$wrapper.find(".template-option")
				.prop("checked", false);
			buzz.events.update_mandatory_fields_visibility(dialog, dialog.template_data);
		});

	// Also update when individual checkboxes change
	dialog.get_field("field_options").$wrapper.on("change", ".template-option", function () {
		buzz.events.update_mandatory_fields_visibility(dialog, dialog.template_data);
	});
};

buzz.events.update_mandatory_fields_visibility = function (dialog, template) {
	let missing_fields = [];

	for (let field of buzz.events.MANDATORY_FIELDS) {
		let template_has_value = template[field] && template[field] !== "";
		let checkbox = dialog
			.get_field("field_options")
			.$wrapper.find(`.template-option[data-option="${field}"]`);
		let is_checked = checkbox.is(":checked");

		// If template doesn't have value OR checkbox is unchecked, we need to ask user
		if (!template_has_value || !is_checked) {
			missing_fields.push(field);
			dialog.get_field(field).df.hidden = 0;
			dialog.get_field(field).df.reqd = 1;
			dialog.get_field(field).refresh();
		} else {
			dialog.get_field(field).df.hidden = 1;
			dialog.get_field(field).df.reqd = 0;
			dialog.get_field(field).refresh();
		}
	}

	// Show/hide the section
	if (missing_fields.length > 0) {
		dialog.get_field("missing_fields_section").df.hidden = 0;
		dialog.get_field("missing_fields_section").refresh();
		dialog
			.get_field("missing_fields_info")
			.$wrapper.html(
				`<p class="text-muted small">${__(
					"The following required fields are not set in the template or not selected. Please fill them in:"
				)}</p>`
			);
	} else {
		dialog.get_field("missing_fields_section").df.hidden = 1;
		dialog.get_field("missing_fields_section").refresh();
		dialog.get_field("missing_fields_info").$wrapper.html("");
	}
};

buzz.events.render_field_group = function (group_key, template) {
	let group = buzz.events.TEMPLATE_FIELD_GROUPS[group_key];
	let html = '<div class="template-section mt-3">';
	html += `<h6 class="text-muted">${group.label}</h6>`;
	html += '<div class="row">';

	for (let field of group.fields) {
		let value = template[field];
		let has_value = value !== null && value !== undefined && value !== "" && value !== 0;

		// For child tables, check length
		if (Array.isArray(value)) {
			has_value = value.length > 0;
		}

		let label = buzz.events.get_field_label(field);

		html += `
			<div class="col-md-6 mb-2">
				<label class="d-flex align-items-center">
					<input type="checkbox" class="template-option mr-2" data-option="${field}" ${
			has_value ? "checked" : "disabled"
		}>
					${label}
					${!has_value ? '<span class="text-muted ml-1">(' + __("Not set") + ")</span>" : ""}
				</label>
			</div>
		`;
	}

	html += "</div></div>";
	return html;
};

buzz.events.get_field_label = function (field) {
	const labels = {
		category: __("Category"),
		host: __("Host"),
		banner_image: __("Banner Image"),
		short_description: __("Short Description"),
		about: __("About"),
		medium: __("Medium"),
		venue: __("Venue"),
		time_zone: __("Time Zone"),
		apply_tax: __("Tax Settings"),
		tax_label: __("Tax Label"),
		tax_percentage: __("Tax Percentage"),
		ticket_email_template: __("Ticket Email Template"),
		ticket_print_format: __("Ticket Print Format"),
		auto_send_pitch_deck: __("Auto Send Pitch Deck"),
		sponsor_deck_email_template: __("Sponsor Deck Email Template"),
		sponsor_deck_reply_to: __("Sponsor Deck Reply To"),
		sponsor_deck_cc: __("Sponsor Deck CC"),
		sponsor_deck_attachments: __("Sponsor Deck Attachments"),
		payment_gateways: __("Payment Gateways"),
		ticket_types: __("Ticket Types"),
		add_ons: __("Add-ons"),
		custom_fields: __("Custom Fields"),
	};
	return labels[field] || field;
};

buzz.events.create_event_from_template = function (dialog, values) {
	let template_name = values.template;
	let options = {};

	// Collect all checked options
	dialog
		.get_field("field_options")
		.$wrapper.find(".template-option:checked")
		.each(function () {
			options[$(this).data("option")] = 1;
		});

	// Collect additional field values (for mandatory fields not in template)
	let additional_fields = {};
	for (let field of buzz.events.MANDATORY_FIELDS) {
		let field_obj = dialog.get_field(field);
		if (!field_obj.df.hidden && values[field]) {
			additional_fields[field] = values[field];
		}
	}

	frappe.call({
		method: "buzz.events.doctype.buzz_event.buzz_event.create_from_template",
		args: {
			template_name: template_name,
			options: JSON.stringify(options),
			additional_fields: JSON.stringify(additional_fields),
		},
		freeze: true,
		freeze_message: __("Creating Event..."),
		callback: function (r) {
			if (r.message) {
				dialog.hide();
				frappe.show_alert({
					message: __("Event created successfully"),
					indicator: "green",
				});
				frappe.set_route("Form", "Buzz Event", r.message);
			}
		},
	});
};

// Save as Template Dialog
buzz.events.show_save_as_template_dialog = function (frm) {
	let dialog = new frappe.ui.Dialog({
		title: __("Save Event as Template"),
		fields: [
			{
				fieldtype: "Data",
				fieldname: "template_name",
				label: __("Template Name"),
				reqd: 1,
				default: frm.doc.title + " Template",
			},
			{
				fieldtype: "Section Break",
				label: __("Select What to Include"),
			},
			{
				fieldtype: "HTML",
				fieldname: "select_buttons",
			},
			{
				fieldtype: "HTML",
				fieldname: "field_options",
			},
		],
		size: "large",
		primary_action_label: __("Save Template"),
		primary_action: function (values) {
			buzz.events.save_event_as_template(dialog, frm, values);
		},
	});

	buzz.events.render_save_template_options(dialog, frm);
	dialog.show();
};

buzz.events.render_save_template_options = function (dialog, frm) {
	let html = "";
	let doc = frm.doc;

	// Select All / Unselect All buttons
	let buttons_html = `
		<div class="mb-3">
			<button class="btn btn-default btn-xs select-all-btn">${__("Select All")}</button>
			<button class="btn btn-default btn-xs unselect-all-btn">${__("Unselect All")}</button>
		</div>
	`;
	dialog.get_field("select_buttons").$wrapper.html(buttons_html);

	// Event Details section
	html += '<div class="template-section mt-3">';
	html += `<h6 class="text-muted">${__("Event Details")}</h6>`;
	html += '<div class="row">';

	const event_fields = [
		"category",
		"host",
		"banner_image",
		"short_description",
		"about",
		"medium",
		"venue",
		"time_zone",
	];
	for (let field of event_fields) {
		let value = doc[field];
		let has_value = value !== null && value !== undefined && value !== "" && value !== 0;
		let label = buzz.events.get_field_label(field);

		html += `
			<div class="col-md-6 mb-2">
				<label class="d-flex align-items-center">
					<input type="checkbox" class="template-option mr-2" data-option="${field}" ${
			has_value ? "checked" : "disabled"
		}>
					${label}
					${!has_value ? '<span class="text-muted ml-1">(' + __("Not set") + ")</span>" : ""}
				</label>
			</div>
		`;
	}
	html += "</div></div>";

	// Ticketing Settings section
	html += '<div class="template-section mt-3">';
	html += `<h6 class="text-muted">${__("Ticketing Settings")}</h6>`;
	html += '<div class="row">';

	const ticketing_fields = [
		"apply_tax",
		"tax_label",
		"tax_percentage",
		"ticket_email_template",
		"ticket_print_format",
	];
	for (let field of ticketing_fields) {
		let value = doc[field];
		let has_value = value !== null && value !== undefined && value !== "" && value !== 0;
		let label = buzz.events.get_field_label(field);

		html += `
			<div class="col-md-6 mb-2">
				<label class="d-flex align-items-center">
					<input type="checkbox" class="template-option mr-2" data-option="${field}" ${
			has_value ? "checked" : "disabled"
		}>
					${label}
					${!has_value ? '<span class="text-muted ml-1">(' + __("Not set") + ")</span>" : ""}
				</label>
			</div>
		`;
	}
	html += "</div></div>";

	// Sponsorship Settings section
	html += '<div class="template-section mt-3">';
	html += `<h6 class="text-muted">${__("Sponsorship Settings")}</h6>`;
	html += '<div class="row">';

	const sponsor_fields = [
		"auto_send_pitch_deck",
		"sponsor_deck_email_template",
		"sponsor_deck_reply_to",
		"sponsor_deck_cc",
		"sponsor_deck_attachments",
	];
	for (let field of sponsor_fields) {
		let value = doc[field];
		let has_value = value !== null && value !== undefined && value !== "" && value !== 0;
		if (Array.isArray(value)) {
			has_value = value.length > 0;
		}
		let label = buzz.events.get_field_label(field);

		html += `
			<div class="col-md-6 mb-2">
				<label class="d-flex align-items-center">
					<input type="checkbox" class="template-option mr-2" data-option="${field}" ${
			has_value ? "checked" : "disabled"
		}>
					${label}
					${!has_value ? '<span class="text-muted ml-1">(' + __("Not set") + ")</span>" : ""}
				</label>
			</div>
		`;
	}
	html += "</div></div>";

	// Related Documents section - need to fetch counts from linked doctypes
	html += '<div class="template-section mt-4" id="related-docs-section">';
	html += `<h6 class="text-muted">${__("Related Documents")}</h6>`;
	html += '<div class="row">';

	// Payment Gateways - from doc
	let pg_count = doc.payment_gateways ? doc.payment_gateways.length : 0;
	html += `
		<div class="col-md-6 mb-2">
			<label class="d-flex align-items-center">
				<input type="checkbox" class="template-option mr-2" data-option="payment_gateways" ${
					pg_count > 0 ? "checked" : ""
				} ${pg_count === 0 ? "disabled" : ""}>
				${__("Payment Gateways")} ${
		pg_count > 0
			? `<span class="text-muted ml-1">(${pg_count})</span>`
			: '<span class="text-muted ml-1">(' + __("None") + ")</span>"
	}
			</label>
		</div>
	`;

	// Placeholders for async-loaded counts
	html += `
		<div class="col-md-6 mb-2" id="ticket-types-option">
			<span class="text-muted">${__("Loading...")}</span>
		</div>
		<div class="col-md-6 mb-2" id="add-ons-option">
			<span class="text-muted">${__("Loading...")}</span>
		</div>
		<div class="col-md-6 mb-2" id="custom-fields-option">
			<span class="text-muted">${__("Loading...")}</span>
		</div>
	`;

	html += "</div></div>";

	dialog.get_field("field_options").$wrapper.html(html);

	// Get the wrapper element for scoped jQuery selectors
	let $wrapper = dialog.get_field("field_options").$wrapper;

	// Fetch linked document counts
	frappe.call({
		method: "frappe.client.get_count",
		args: { doctype: "Event Ticket Type", filters: { event: doc.name } },
		callback: function (r) {
			let count = r.message || 0;
			$wrapper.find("#ticket-types-option").html(`
				<label class="d-flex align-items-center">
					<input type="checkbox" class="template-option mr-2" data-option="ticket_types" ${
						count > 0 ? "checked" : ""
					} ${count === 0 ? "disabled" : ""}>
					${__("Ticket Types")} ${
				count > 0
					? `<span class="text-muted ml-1">(${count})</span>`
					: '<span class="text-muted ml-1">(' + __("None") + ")</span>"
			}
				</label>
			`);
		},
	});

	frappe.call({
		method: "frappe.client.get_count",
		args: { doctype: "Ticket Add-on", filters: { event: doc.name } },
		callback: function (r) {
			let count = r.message || 0;
			$wrapper.find("#add-ons-option").html(`
				<label class="d-flex align-items-center">
					<input type="checkbox" class="template-option mr-2" data-option="add_ons" ${
						count > 0 ? "checked" : ""
					} ${count === 0 ? "disabled" : ""}>
					${__("Add-ons")} ${
				count > 0
					? `<span class="text-muted ml-1">(${count})</span>`
					: '<span class="text-muted ml-1">(' + __("None") + ")</span>"
			}
				</label>
			`);
		},
	});

	frappe.call({
		method: "frappe.client.get_count",
		args: { doctype: "Buzz Custom Field", filters: { event: doc.name } },
		callback: function (r) {
			let count = r.message || 0;
			$wrapper.find("#custom-fields-option").html(`
				<label class="d-flex align-items-center">
					<input type="checkbox" class="template-option mr-2" data-option="custom_fields" ${
						count > 0 ? "checked" : ""
					} ${count === 0 ? "disabled" : ""}>
					${__("Custom Fields")} ${
				count > 0
					? `<span class="text-muted ml-1">(${count})</span>`
					: '<span class="text-muted ml-1">(' + __("None") + ")</span>"
			}
				</label>
			`);
		},
	});

	// Bind select all / unselect all
	dialog
		.get_field("select_buttons")
		.$wrapper.find(".select-all-btn")
		.on("click", function () {
			dialog
				.get_field("field_options")
				.$wrapper.find(".template-option:not(:disabled)")
				.prop("checked", true);
		});

	dialog
		.get_field("select_buttons")
		.$wrapper.find(".unselect-all-btn")
		.on("click", function () {
			dialog
				.get_field("field_options")
				.$wrapper.find(".template-option")
				.prop("checked", false);
		});
};

buzz.events.save_event_as_template = function (dialog, frm, values) {
	let options = {};

	// Collect all checked options
	dialog
		.get_field("field_options")
		.$wrapper.find(".template-option:checked")
		.each(function () {
			options[$(this).data("option")] = 1;
		});

	frappe.call({
		method: "buzz.events.doctype.event_template.event_template.create_template_from_event",
		args: {
			event_name: frm.doc.name,
			template_name: values.template_name,
			options: JSON.stringify(options),
		},
		freeze: true,
		freeze_message: __("Creating Template..."),
		callback: function (r) {
			if (r.message) {
				dialog.hide();
				frappe.show_alert({
					message: __("Template {0} created successfully", [r.message]),
					indicator: "green",
				});
				frappe.set_route("Form", "Event Template", r.message);
			}
		},
	});
};
