<template>
	<!-- Date field -->
	<div v-if="isDateField(field.fieldtype)" class="space-y-1.5">
		<label class="text-xs text-ink-gray-5 block">
			{{ __(field.label) }}
			<span v-if="field.mandatory" class="text-ink-red-4">*</span>
		</label>
		<DatePicker
			:model-value="modelValue"
			@update:model-value="$emit('update:modelValue', $event)"
			:placeholder="getFieldPlaceholder(field)"
		/>
	</div>

	<!-- DateTime field -->
	<div v-else-if="isDateTimeField(field.fieldtype)" class="space-y-1.5">
		<label class="text-xs text-ink-gray-5 block">
			{{ __(field.label) }}
			<span v-if="field.mandatory" class="text-ink-red-4">*</span>
		</label>
		<DateTimePicker
			:model-value="modelValue"
			@update:model-value="$emit('update:modelValue', $event)"
			:placeholder="getFieldPlaceholder(field)"
		/>
	</div>

	<!-- All other field types -->
	<FormControl
		v-else
		:model-value="modelValue"
		@update:model-value="$emit('update:modelValue', $event)"
		:label="__(field.label)"
		:type="getFormControlType(field.fieldtype)"
		:options="getFieldOptions(field)"
		:required="field.mandatory"
		:placeholder="getFieldPlaceholder(field)"
	/>
</template>

<script setup>
import { DatePicker, DateTimePicker } from "frappe-ui";
import {
	getFormControlType,
	getFieldOptions,
	getFieldPlaceholder,
	isDateField,
	isDateTimeField,
} from "@/composables/useCustomFields.js";

defineProps({
	field: {
		type: Object,
		required: true,
	},
	modelValue: {
		type: [String, Number, Boolean, Date],
		default: "",
	},
});

defineEmits(["update:modelValue"]);
</script>
