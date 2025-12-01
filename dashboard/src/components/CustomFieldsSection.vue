<template>
	<div v-if="customFields.length > 0" class="space-y-4">
		<h5 v-if="showTitle" class="text-base font-medium text-ink-gray-8 border-b pb-2">
			{{ __(title) || __("Additional Information") }}
		</h5>

		<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
			<template v-for="field in customFields" :key="field.fieldname">
				<!-- Date field -->
				<div v-if="field.fieldtype === 'Date'" class="space-y-1.5">
					<label class="text-xs text-ink-gray-5 block">
						{{ __(field.label) }}
						<span v-if="field.mandatory" class="text-ink-red-4">*</span>
					</label>
					<DatePicker
						:model-value="getFieldValue(field.fieldname)"
						@update:model-value="updateFieldValue(field.fieldname, $event)"
						:placeholder="getFieldPlaceholder(field)"
					/>
				</div>

				<!-- DateTime field -->
				<div v-else-if="field.fieldtype === 'Datetime'">
					<label class="block text-xs text-ink-gray-5">
						{{ __(field.label) }}
						<span v-if="field.mandatory" class="text-ink-red-4">*</span>
					</label>
					<DateTimePicker
						:model-value="getFieldValue(field.fieldname)"
						@update:model-value="updateFieldValue(field.fieldname, $event)"
						:placeholder="getFieldPlaceholder(field)"
					/>
				</div>

				<!-- All other field types -->
				<FormControl
					v-else
					:model-value="getFieldValue(field.fieldname)"
					@update:model-value="updateFieldValue(field.fieldname, $event)"
					:label="__(field.label)"
					:type="getFormControlType(field.fieldtype)"
					:options="getFieldOptions(field)"
					:required="field.mandatory"
					:placeholder="getFieldPlaceholder(field)"
				/>
			</template>
		</div>
	</div>
</template>

<script setup>
import { DatePicker, DateTimePicker } from "frappe-ui";

const props = defineProps({
	customFields: {
		type: Array,
		default: () => [],
	},
	modelValue: {
		type: Object,
		default: () => ({}),
	},
	title: {
		type: String,
		default: "",
	},
	showTitle: {
		type: Boolean,
		default: true,
	},
});

const emit = defineEmits(["update:modelValue"]);

// Get field value from model
const getFieldValue = (fieldname) => {
	const currentValue = props.modelValue[fieldname];

	// If field already has a value, return it
	if (currentValue !== undefined && currentValue !== null && currentValue !== "") {
		return currentValue;
	}

	// Apply default value if available
	const field = props.customFields.find((f) => f.fieldname === fieldname);
	if (field && field.default_value) {
		updateFieldValue(fieldname, field.default_value);
		return field.default_value;
	}

	// Apply default for select fields that don't have values yet
	if (field && field.fieldtype === "Select") {
		const options = getFieldOptions(field);
		if (options.length > 0) {
			// Set the first option as default
			const firstOptionValue = options[0].value;
			updateFieldValue(fieldname, firstOptionValue);
			return firstOptionValue;
		}
	}

	return "";
};

// Update field value in model
const updateFieldValue = (fieldname, value) => {
	const updatedValue = { ...props.modelValue, [fieldname]: value };
	emit("update:modelValue", updatedValue);
};

// Convert Frappe field types to form control types
const getFormControlType = (fieldtype) => {
	switch (fieldtype) {
		case "Phone":
			return "text";
		case "Email":
			return "email";
		case "Select":
			return "select";
		case "Number":
			return "number";
		default:
			return "text";
	}
};

// Get field options for select fields
const getFieldOptions = (field) => {
	if (field.fieldtype === "Select" && field.options) {
		// Handle different formats of options
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
};

// Get placeholder text - use custom placeholder if available, otherwise no placeholder
const getFieldPlaceholder = (field) => {
	// If custom placeholder is provided, use it
	if (field.placeholder?.trim()) {
		const placeholder = field.placeholder.trim();
		return field.mandatory ? `${placeholder} (${__("required")})` : placeholder;
	}

	// If no custom placeholder is provided, return empty string (no placeholder)
	return "";
};
</script>
