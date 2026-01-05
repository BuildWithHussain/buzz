/**
 * Composable for handling custom field logic
 * Provides utilities for converting Frappe field types to form control types,
 * parsing field options, and generating placeholders.
 */

/**
 * Convert Frappe field types to FormControl types
 * @param {string} fieldtype - Frappe field type
 * @returns {string} - FormControl type
 */
export function getFormControlType(fieldtype) {
	switch (fieldtype) {
		case "Phone":
			return "text";
		case "Email":
			return "email";
		case "Select":
			return "select";
		case "Number":
		case "Int":
		case "Float":
			return "number";
		case "Check":
			return "checkbox";
		default:
			return "text";
	}
}

/**
 * Check if a field type requires a special date/time picker
 * @param {string} fieldtype - Frappe field type
 * @returns {boolean}
 */
export function isDateField(fieldtype) {
	return fieldtype === "Date";
}

/**
 * Check if a field type requires a datetime picker
 * @param {string} fieldtype - Frappe field type
 * @returns {boolean}
 */
export function isDateTimeField(fieldtype) {
	return fieldtype === "Datetime";
}

/**
 * Get field options for select fields
 * @param {Object} field - Field definition object
 * @returns {Array} - Array of { label, value } objects
 */
export function getFieldOptions(field) {
	const isSelectType = field.fieldtype === "Select" || field.fieldtype === "Multi Select";
	if (isSelectType && field.options) {
		let options = [];

		if (typeof field.options === "string") {
			// Split by newlines and filter out empty options
			options = field.options
				.split("\n")
				.map((option) => option.trim())
				.filter((option) => option.length > 0);
		} else if (Array.isArray(field.options)) {
			// If options is already an array
			options = field.options.filter((option) => {
				try {
					return option != null && String(option).trim().length > 0;
				} catch {
					return false;
				}
			});
		}

		const formattedOptions = options.map((option) => {
			const optionStr = String(option).trim();
			return {
				label: optionStr,
				value: optionStr,
			};
		});

		// Debug log for development
		if (
			process.env.NODE_ENV === "development" &&
			formattedOptions.length === 0 &&
			field.options
		) {
			console.warn(
				`CustomField "${field.fieldname}" has Select type but no valid options:`,
				field.options
			);
		}

		return formattedOptions;
	}
	return [];
}

/**
 * Get placeholder text for a field
 * @param {Object} field - Field definition object
 * @returns {string} - Placeholder text
 */
export function getFieldPlaceholder(field) {
	// If custom placeholder is provided, use it
	if (field.placeholder?.trim()) {
		const placeholder = field.placeholder.trim();
		return field.mandatory ? `${placeholder} (${__("required")})` : placeholder;
	}

	// If no custom placeholder is provided, return empty string
	return "";
}

/**
 * Get the default value for a field
 * @param {Object} field - Field definition object
 * @param {Function} getFieldOptionsFn - Function to get field options
 * @returns {*} - Default value or empty string
 */
export function getFieldDefaultValue(field) {
	// Check for explicit default value
	if (field.default_value) {
		return field.default_value;
	}

	// For select fields, return the first option as default
	if (field.fieldtype === "Select") {
		const options = getFieldOptions(field);
		if (options.length > 0) {
			return options[0].value;
		}
	}

	return "";
}
