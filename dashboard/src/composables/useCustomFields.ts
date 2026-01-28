/**
 * Composable for handling custom field logic
 * Provides utilities for converting Frappe field types to form control types,
 * parsing field options, and generating placeholders.
 */

import type { BuzzCustomField } from "@/types/doctypes";

export interface FieldOption {
	label: string;
	value: string;
}

/**
 * Convert Frappe field types to FormControl types
 * @param {string} fieldtype - Frappe field type
 * @returns {any} - FormControl type (any to avoid strict mapping issues in templates)
 */
export function getFormControlType(fieldtype: string): any {
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
export function isDateField(fieldtype: string): boolean {
	return fieldtype === "Date";
}

/**
 * Check if a field type requires a datetime picker
 * @param {string} fieldtype - Frappe field type
 * @returns {boolean}
 */
export function isDateTimeField(fieldtype: string): boolean {
	return fieldtype === "Datetime";
}

/**
 * Get field options for select fields
 * @param {BuzzCustomField} field - Field definition object
 * @returns {FieldOption[]} - Array of { label, value } objects
 */
export function getFieldOptions(field: BuzzCustomField): FieldOption[] {
	const isSelectType = field.fieldtype === "Select" || field.fieldtype === "Multi Select";
	if (isSelectType && field.options) {
		let options: string[] = [];

		if (typeof field.options === "string") {
			// Split by newlines and filter out empty options
			options = field.options
				.split("\n")
				.map((option: string) => option.trim())
				.filter((option: string) => option.length > 0);
		}

		const formattedOptions = options.map((option: string) => {
			const optionStr = option.trim();
			return {
				label: optionStr,
				value: optionStr,
			};
		});

		// Debug log for development
		if (
			import.meta.env.DEV &&
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
 * @param {BuzzCustomField} field - Field definition object
 * @returns {string} - Placeholder text
 */
export function getFieldPlaceholder(field: BuzzCustomField): string {
	// If custom placeholder is provided, use it
	if (field.placeholder?.trim()) {
		const placeholder = field.placeholder.trim();
		// @ts-ignore: __ is global
		return field.mandatory ? `${placeholder} (${__("required")})` : placeholder;
	}

	// If no custom placeholder is provided, return empty string
	return "";
}

/**
 * Get the default value for a field
 * @param {BuzzCustomField} field - Field definition object
 * @returns {any} - Default value or empty string
 */
export function getFieldDefaultValue(field: BuzzCustomField): any {
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
