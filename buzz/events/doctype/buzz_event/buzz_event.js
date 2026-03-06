// Copyright (c) 2025, BWH Studios

/* ─────────────────────────────────────────────────────────────
   FORM CONTROLLER
   ───────────────────────────────────────────────────────────── */

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

		// Clone Event button – only shown on saved documents
		if (!frm.is_new()) {
			frm.add_custom_button(__("Clone Event"), () => {
				show_clone_event_dialog(frm);
			});
		}

		frm.set_query("track", "schedule", (doc, cdt, cdn) => {
			return { filters: { event: doc.name } };
		});

		frm.set_query("default_ticket_type", (doc) => {
			return { filters: { event: doc.name, is_published: 1 } };
		});

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
			}).then(() => {
				frm.layout.tabs.find((t) => t.label == "Zoom Integration").set_active();
			});
		});
	},
});

/* ─────────────────────────────────────────────────────────────────────────────
   SHARED HELPERS
   ───────────────────────────────────────────────────────────────────────────── */

/** Format "HH:MM:SS" → "HH : MM AM/PM" */
function buzz_fmt_time(t) {
	if (!t) return "—";
	const [hh, mm] = t.split(":");
	let h = parseInt(hh);
	const ampm = h >= 12 ? "PM" : "AM";
	h = h % 12 || 12;
	return `${String(h).padStart(2, "0")} : ${mm || "00"} ${ampm}`;
}

/** Format "YYYY-MM-DD" → "Mon, Mar 3" */
function buzz_fmt_date(d) {
	if (!d) return "—";
	return frappe.datetime
		.str_to_obj(d)
		.toLocaleDateString("en-US", { weekday: "short", month: "short", day: "numeric" });
}

/* ─────────────────────────────────────────────────────────────────────────────
   COMPUTE OCCURRENCES  (pure JS, no library)
   ───────────────────────────────────────────────────────────────────────────── */

/**
 * @param {string}   start_date   "YYYY-MM-DD"
 * @param {string}   start_time   "HH:MM:SS"
 * @param {string}   repeat_type  "Daily" | "Weekly" | "Monthly"
 * @param {number[]} weekdays     ISO indices 0=Mon … 6=Sun (only used for Weekly)
 * @param {string}   end_type     "Until" | "For"
 * @param {string}   until_date   "YYYY-MM-DD" (used when end_type === "Until")
 * @param {number}   for_count    integer      (used when end_type === "For")
 */
function buzz_compute_occurrences(
	start_date,
	start_time,
	repeat_type,
	weekdays,
	end_type,
	until_date,
	for_count
) {
	const SAFETY = 500;
	const results = [];
	const cur = frappe.datetime.str_to_obj(start_date);

	// Compute the end fence date
	let limit_date = null;
	if (end_type === "Until" && until_date) {
		limit_date = frappe.datetime.str_to_obj(until_date);
	} else if (end_type === "For") {
		const n = Math.max(1, parseInt(for_count) || 1);
		limit_date = new Date(cur);
		if (repeat_type === "Daily") {
			limit_date.setDate(limit_date.getDate() + n - 1);
		} else if (repeat_type === "Weekly") {
			limit_date.setDate(limit_date.getDate() + n * 7 - 1);
		} else if (repeat_type === "Monthly") {
			limit_date.setMonth(limit_date.getMonth() + n);
			limit_date.setDate(limit_date.getDate() - 1);
		}
	}

	// Hard fence: two years out
	const fence = new Date(cur);
	fence.setFullYear(fence.getFullYear() + 2);

	let iters = 0;

	while (iters < SAFETY) {
		iters++;
		if (cur > fence) break;
		if (limit_date && cur > limit_date) break;

		const date_str = frappe.datetime.obj_to_str(cur);

		if (repeat_type === "Daily") {
			results.push({ start_date: date_str, start_time });
			cur.setDate(cur.getDate() + 1);
		} else if (repeat_type === "Weekly") {
			// JS getDay(): 0=Sun … 6=Sat → convert to ISO 0=Mon … 6=Sun
			const js_day = cur.getDay();
			const iso_day = js_day === 0 ? 6 : js_day - 1;
			if (weekdays.includes(iso_day)) {
				results.push({ start_date: date_str, start_time });
			}
			cur.setDate(cur.getDate() + 1);
		} else if (repeat_type === "Monthly") {
			results.push({ start_date: date_str, start_time });
			cur.setMonth(cur.getMonth() + 1);
		}
	}

	return results;
}

/* ─────────────────────────────────────────────────────────────────────────────
   CLONE EVENT DIALOG
   ───────────────────────────────────────────────────────────────────────────── */

function show_clone_event_dialog(frm) {
	frappe.call({
		method: "buzz.events.doctype.buzz_event.buzz_event.get_clone_dialog_html",
		args: {
			template_name: "clone_event_dialog",
			context: JSON.stringify({ title: frm.doc.title }),
		},
		callback(r) {
			_build_clone_dialog(frm, r.message);
		},
	});
}

function _build_clone_dialog(frm, body_html) {
	let selected_dates = [];

	// Render the date-rows list inside #clone-dates-list
	function render_dates() {
		const $list = clone_dialog.$body.find("#clone-dates-list");
		$list.empty();

		if (!selected_dates.length) {
			$list.html(
				`<p class="text-muted" style="font-size:12px;margin:4px 0 8px;">
					${__("No times added yet.")}
				</p>`
			);
			return;
		}

		selected_dates.forEach((entry, idx) => {
			const $row = $(`
				<div style="display:flex;align-items:center;gap:8px;padding:6px 10px;
				     border:1px solid var(--border-color);border-radius:8px;
				     background:var(--control-bg);margin-bottom:6px;">
					<div class="row-date-wrap" style="flex:1;min-width:0;"></div>
					<div class="row-time-wrap" style="flex:1;min-width:0;"></div>
					<button class="btn btn-link row-remove-btn"
						style="padding:0 4px;color:var(--text-muted);font-size:20px;line-height:1;flex-shrink:0;"
						title="${__("Remove")}">×</button>
				</div>
			`);
			$list.append($row);

			// Date control
			const date_ctrl = frappe.ui.form.make_control({
				df: { fieldtype: "Date", fieldname: `row_date_${idx}`, label: "" },
				parent: $row.find(".row-date-wrap")[0],
				render_input: true,
			});
			date_ctrl.refresh();
			$row.find(".row-date-wrap .frappe-control").css({ margin: 0, padding: 0 });
			$row.find(".row-date-wrap .form-group").css({ margin: 0 });
			$row.find(".row-date-wrap label").hide();
			date_ctrl.set_value(entry.start_date || "");
			date_ctrl.$input.on("change blur", () => {
				const v = date_ctrl.get_value();
				if (v) selected_dates[idx].start_date = v;
				sync_primary_label();
			});

			// Time control
			const time_ctrl = frappe.ui.form.make_control({
				df: { fieldtype: "Time", fieldname: `row_time_${idx}`, label: "" },
				parent: $row.find(".row-time-wrap")[0],
				render_input: true,
			});
			time_ctrl.refresh();
			$row.find(".row-time-wrap .frappe-control").css({ margin: 0, padding: 0 });
			$row.find(".row-time-wrap .form-group").css({ margin: 0 });
			$row.find(".row-time-wrap label").hide();
			time_ctrl.set_value(entry.start_time || "");
			time_ctrl.$input.on("change blur", () => {
				const v = time_ctrl.get_value();
				if (v) selected_dates[idx].start_time = v;
			});

			// Remove
			$row.find(".row-remove-btn").on("click", () => {
				selected_dates.splice(idx, 1);
				render_dates();
				sync_primary_label();
			});
		});
	}

	function sync_primary_label() {
		const n = selected_dates.length;
		clone_dialog.set_primary_action(
			n > 0 ? __("Clone {0} Event(s)", [n]) : __("Clone Event"),
			null
		);
	}

	const clone_dialog = new frappe.ui.Dialog({
		title: __("Clone Event"),
		fields: [
			{
				fieldname: "body_html",
				fieldtype: "HTML",
				options: body_html,
			},
			{
				label: __("Host"),
				fieldname: "host",
				fieldtype: "Link",
				options: "Event Host",
				default: frm.doc.host,
				reqd: 1,
			},
		],
		primary_action_label: __("Clone Event"),
		primary_action(values) {
			if (!selected_dates.length) {
				frappe.msgprint({
					message: __("Please add at least one date."),
					indicator: "orange",
				});
				return;
			}
			clone_dialog.disable_primary_action();
			frappe.call({
				method: "buzz.events.doctype.buzz_event.buzz_event.clone_buzz_event",
				args: { name: frm.doc.name, dates: selected_dates, host: values.host },
				callback(r) {
					clone_dialog.hide();
					if (r.message && r.message.length) {
						const links = r.message
							.map((n) => `<a href="/app/buzz-event/${n}" target="_blank">#${n}</a>`)
							.join(", ");
						frappe.msgprint({
							title: __("Events Created"),
							message: __("{0} Buzz Event(s) created: {1}", [
								r.message.length,
								links,
							]),
							indicator: "green",
						});
					}
				},
				error() {
					clone_dialog.enable_primary_action();
				},
			});
		},
	});

	clone_dialog.show();
	render_dates();

	const $host_field = clone_dialog.fields_dict.host.$wrapper;
	const $body_html = clone_dialog.$body.find('[data-fieldname="body_html"]');
	$body_html.before($host_field.detach());

	clone_dialog.$body.on("click", "#clone-add-time-btn", () => {
		show_add_time_dialog(
			frm.doc.start_date || frappe.datetime.get_today(),
			frm.doc.start_time || "15:00:00",
			(entry) => {
				selected_dates.push(entry);
				render_dates();
				sync_primary_label();
			}
		);
	});

	clone_dialog.$body.on("click", "#clone-recurrence-btn", () => {
		show_recurrence_dialog(
			frm.doc.start_date || frappe.datetime.get_today(),
			frm.doc.start_time || "15:00:00",
			(entries) => {
				selected_dates = selected_dates.concat(entries);
				render_dates();
				sync_primary_label();
			}
		);
	});
}

/* ─────────────────────────────────────────────────────────────────────────────
   ADD SINGLE TIME DIALOG
   ───────────────────────────────────────────────────────────────────────────── */

function show_add_time_dialog(default_date, default_time, on_add) {
	const d = new frappe.ui.Dialog({
		title: __("Add Time"),
		fields: [
			{
				label: __("Date"),
				fieldname: "start_date",
				fieldtype: "Date",
				reqd: 1,
				default: default_date,
			},
			{
				label: __("Time"),
				fieldname: "start_time",
				fieldtype: "Time",
				default: default_time,
			},
		],
		primary_action_label: __("Add"),
		primary_action(values) {
			on_add({ start_date: values.start_date, start_time: values.start_time });
			d.hide();
		},
	});
	d.show();
}

/* ─────────────────────────────────────────────────────────────────────────────
   CHOOSE TIMES  (RECURRENCE DIALOG)
   ───────────────────────────────────────────────────────────────────────────── */

function show_recurrence_dialog(default_date, default_time, on_add) {
	frappe.call({
		method: "buzz.events.doctype.buzz_event.buzz_event.get_clone_dialog_html",
		args: { template_name: "recurrence_dialog" },
		callback(r) {
			_build_recurrence_dialog(default_date, default_time, on_add, r.message);
		},
	});
}

function _build_recurrence_dialog(default_date, default_time, on_add, body_html) {
	// ISO weekday index: 0=Mon … 6=Sun
	const DAY_META = [
		{ idx: 0, label: "M", full: "Monday" },
		{ idx: 1, label: "T", full: "Tuesday" },
		{ idx: 2, label: "W", full: "Wednesday" },
		{ idx: 3, label: "T", full: "Thursday" },
		{ idx: 4, label: "F", full: "Friday" },
		{ idx: 5, label: "S", full: "Saturday" },
		{ idx: 6, label: "S", full: "Sunday" },
	];

	// Pre-select the ISO weekday of the starting date
	const init_obj = frappe.datetime.str_to_obj(default_date);
	const js_day = init_obj.getDay(); // 0=Sun
	let selected_weekdays = [js_day === 0 ? 6 : js_day - 1];

	// JS-owned state for the end conditions (not Frappe fields)
	let current_end_type = "For"; // "Until" | "For"
	let until_date_state = ""; // set by ControlDate
	let for_count_state = 5; // set by number input
	// Keep a reference to the live ControlDate so we can read it in refresh_preview
	let until_date_ctrl = null;

	const recurrence_dialog = new frappe.ui.Dialog({
		title: __("Choose Times"),
		fields: [
			{
				label: __("Starting on"),
				fieldname: "start_date",
				fieldtype: "Date",
				reqd: 1,
				default: default_date,
			},
			{ fieldtype: "Column Break" },
			{
				label: __("Time"),
				fieldname: "start_time",
				fieldtype: "Time",
				default: default_time,
			},
			{ fieldtype: "Section Break" },
			{
				label: __("Repeats"),
				fieldname: "repeat_type",
				fieldtype: "Select",
				options: ["Daily", "Weekly", "Monthly"].join("\n"),
				default: "Weekly",
				reqd: 1,
			},
			{
				fieldname: "recurrence_body",
				fieldtype: "HTML",
				options: body_html,
			},
		],
		primary_action_label: __("Add Times"),
		primary_action(values) {
			// Read until_date from our ctrl if it exists
			if (current_end_type === "Until" && until_date_ctrl) {
				until_date_state = until_date_ctrl.get_value() || until_date_state;
			}
			const occurrences = buzz_compute_occurrences(
				values.start_date,
				values.start_time || default_time,
				values.repeat_type,
				selected_weekdays,
				current_end_type,
				until_date_state,
				for_count_state
			);
			if (!occurrences.length) {
				frappe.msgprint({
					message: __("No dates generated. Check your recurrence settings."),
					indicator: "orange",
				});
				return;
			}
			on_add(occurrences);
			recurrence_dialog.hide();
		},
	});

	recurrence_dialog.show();

	/* ── helpers ── */

	function get_repeat_type() {
		return recurrence_dialog.get_field("repeat_type").get_value() || "Weekly";
	}

	function get_start_date() {
		return recurrence_dialog.get_field("start_date").get_value() || default_date;
	}

	function get_start_time() {
		return recurrence_dialog.get_field("start_time").get_value() || default_time;
	}

	/* ── Weekday button styles ── */
	function render_weekday_buttons() {
		recurrence_dialog.$body.find(".recurrence-day-btn").each(function () {
			const day = parseInt($(this).data("day"));
			const active = selected_weekdays.includes(day);
			$(this)
				.toggleClass("btn-primary", active)
				.toggleClass("btn-default", !active)
				.css("border", "");
		});
	}

	/* ── Show/hide weekday section ── */
	function toggle_weekday_section() {
		const $s = recurrence_dialog.$body.find("#recurrence-weekday-section");
		get_repeat_type() === "Weekly" ? $s.show() : $s.hide();
	}

	/* ── End condition: "Until" date or "For N units" ── */
	function render_end_condition() {
		const $wrapper = recurrence_dialog.$body.find("#end-condition-wrapper");
		$wrapper.empty();
		until_date_ctrl = null;

		// Update toggle button active state using Frappe classes
		recurrence_dialog.$body.find(".end-type-btn").each(function () {
			const active = $(this).data("type") === current_end_type;
			$(this).toggleClass("btn-primary", active).toggleClass("btn-default", !active);
		});

		if (current_end_type === "Until") {
			// Use Frappe's ControlDate rendered directly into the wrapper
			until_date_ctrl = frappe.ui.form.make_control({
				df: {
					fieldtype: "Date",
					fieldname: "recurrence_until_date",
					label: "",
					placeholder: __("End date"),
				},
				parent: $wrapper[0],
				render_input: true,
			});
			until_date_ctrl.refresh();
			// Strip extra spacing that make_control adds so it sits flush inline
			$wrapper.find(".frappe-control").css({ margin: "0", padding: "0" });
			$wrapper.find(".form-group").css({ margin: "0" });
			$wrapper.find(".frappe-control label").hide();
			// Restore previously chosen date
			if (until_date_state) {
				until_date_ctrl.set_value(until_date_state);
			}
			// Wire change
			until_date_ctrl.$input.on("change blur", function () {
				until_date_state = until_date_ctrl.get_value() || "";
				refresh_preview();
			});
		} else {
			// "For N weeks/days/months"
			const unit_map = {
				Daily: __("days"),
				Weekly: __("weeks"),
				Monthly: __("months"),
			};
			const unit = unit_map[get_repeat_type()] || __("occurrences");

			$wrapper.html(`
				<input type="number" id="end-for-count" min="1" max="365"
					class="form-control"
					style="width:64px;font-size:13px;text-align:center;padding:4px 8px;"
					value="${for_count_state}" />
				<span style="font-size:13px;color:var(--text-muted);white-space:nowrap;">${unit}</span>
			`);

			$wrapper.find("#end-for-count").on("input change", function () {
				for_count_state = Math.max(1, parseInt($(this).val()) || 1);
				// Keep the input aligned with state
				$(this).val(for_count_state);
				refresh_preview();
			});
		}
	}

	/* ── Occurrence preview chips ── */
	function refresh_preview() {
		const start_date = get_start_date();
		const start_time = get_start_time();
		const repeat_type = get_repeat_type();

		if (!start_date) return;

		// If Until mode, try to read the latest value from the live ctrl
		let effective_until = until_date_state;
		if (current_end_type === "Until" && until_date_ctrl) {
			effective_until = until_date_ctrl.get_value() || until_date_state;
		}

		const occurrences = buzz_compute_occurrences(
			start_date,
			start_time,
			repeat_type,
			selected_weekdays,
			current_end_type,
			effective_until,
			for_count_state
		);

		const $preview = recurrence_dialog.$body.find("#recurrence-preview");
		$preview.empty();

		if (!occurrences.length) {
			$preview.html(
				`<span class="text-muted" style="font-size:12px;align-self:center;">
					${__("No dates match these settings.")}
				</span>`
			);
			recurrence_dialog.set_primary_action(__("Add Times"), null);
			return;
		}

		const MAX_CHIPS = 4;
		const visible = occurrences.slice(0, MAX_CHIPS);
		const overflow = occurrences.length - MAX_CHIPS;

		visible.forEach((entry) => {
			const d_obj = frappe.datetime.str_to_obj(entry.start_date);
			$preview.append(`
				<div style="display:flex;flex-direction:column;align-items:center;
					padding:6px 8px;border:1px solid var(--border-color);border-radius:8px;
					background:var(--card-bg);min-width:0;flex:1;text-align:center;">
					<span style="font-size:9px;color:var(--text-muted);
					     text-transform:uppercase;letter-spacing:.5px;line-height:1.4;">
						${d_obj.toLocaleDateString("en-US", { month: "short" })}
					</span>
					<span style="font-size:16px;font-weight:700;line-height:1.2;">
						${d_obj.getDate()}
					</span>
					<span style="font-size:9px;color:var(--text-muted);line-height:1.4;">
						${d_obj.toLocaleDateString("en-US", { weekday: "short" }).toUpperCase()}
					</span>
				</div>
			`);
		});

		if (overflow > 0) {
			$preview.append(`
				<div style="display:flex;flex-direction:column;align-items:center;justify-content:center;
					padding:6px 8px;border:1px solid var(--border-color);border-radius:8px;
					background:var(--card-bg);min-width:0;flex:1;text-align:center;
					color:var(--text-muted);font-size:13px;font-weight:700;">
					+${overflow}
				</div>
			`);
		}

		recurrence_dialog.set_primary_action(__("Add {0} Time(s)", [occurrences.length]), null);
	}

	/* ── Initial render ── */
	render_weekday_buttons();
	toggle_weekday_section();
	render_end_condition();
	refresh_preview();

	/* ── Event bindings ── */

	// Weekday toggle
	recurrence_dialog.$body.on("click", ".recurrence-day-btn", function () {
		const day = parseInt($(this).data("day"));
		const idx = selected_weekdays.indexOf(day);
		if (idx === -1) {
			selected_weekdays.push(day);
		} else if (selected_weekdays.length > 1) {
			selected_weekdays.splice(idx, 1); // keep at least one day selected
		}
		render_weekday_buttons();
		refresh_preview();
	});

	// Until / For toggle
	recurrence_dialog.$body.on("click", ".end-type-btn", function () {
		const type = $(this).data("type");
		if (current_end_type === type) return;
		current_end_type = type;
		render_end_condition();
		refresh_preview();
	});

	// Repeat type change
	recurrence_dialog.get_field("repeat_type").$input.on("change", function () {
		toggle_weekday_section();
		render_end_condition(); // update "weeks/days/months" unit label in For mode
		refresh_preview();
	});

	// Start date / time changes
	recurrence_dialog.get_field("start_date").$input.on("change", () => refresh_preview());
	recurrence_dialog.get_field("start_time").$input.on("change", () => refresh_preview());
}
