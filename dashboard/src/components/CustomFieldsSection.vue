<template>
	<div v-if="customFields.length > 0" class="space-y-4">
		<h5 v-if="showTitle" class="text-base font-medium text-ink-gray-8 border-b pb-2">
			{{ __(title) || __("Additional Information") }}
		</h5>

		<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
			<CustomFieldInput
				v-for="field in customFields"
				:key="field.fieldname"
				:field="field"
				:model-value="getFieldValue(field.fieldname)"
				@update:model-value="updateFieldValue(field.fieldname, $event)"
			/>
		</div>
	</div>
</template>

<script setup>
import CustomFieldInput from "./CustomFieldInput.vue";
import { getFieldOptions, getFieldDefaultValue } from "@/composables/useCustomFields.js";

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
	if (field) {
		const defaultValue = getFieldDefaultValue(field);
		if (defaultValue) {
			updateFieldValue(fieldname, defaultValue);
			return defaultValue;
		}
	}

	return "";
};

// Update field value in model
const updateFieldValue = (fieldname, value) => {
	const updatedValue = { ...props.modelValue, [fieldname]: value };
	emit("update:modelValue", updatedValue);
};
</script>
