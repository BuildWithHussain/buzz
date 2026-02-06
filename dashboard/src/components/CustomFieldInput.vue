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

	<div v-else-if="field.fieldtype === 'Multi Select'" class="space-y-1.5">
		<label class="text-xs text-ink-gray-5 block">
			{{ __(field.label) }}
			<span v-if="field.mandatory" class="text-ink-red-4">*</span>
		</label>
		<MultiSelect
			:options="multiSelectOptions"
			v-model="multiSelectProxy"
			:placeholder="getFieldPlaceholder(field)"
		/>
	</div>

	<!-- Checkbox field -->
	<FormControl
		v-else-if="field.fieldtype === 'Check'"
		type="checkbox"
		:model-value="checkboxValue"
		@update:model-value="$emit('update:modelValue', $event ? 1 : 0)"
		:label="__(field.label)"
	/>

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
import { computed } from "vue";
import { DatePicker, DateTimePicker, MultiSelect } from "frappe-ui";
import {
	getFormControlType,
	getFieldOptions,
	getFieldPlaceholder,
	isDateField,
	isDateTimeField,
} from "@/composables/useCustomFields.js";

const props = defineProps({
	field: {
		type: Object,
		required: true,
	},
});

const model = defineModel();
const multiSelectOptions = computed(() => getFieldOptions(props.field));
const checkboxValue = computed(() => model.value === 1 || model.value === "1");

const multiSelectProxy = computed({
	get() {
		if (!model.value) return [];
		return Array.isArray(model.value) ? model.value : String(model.value).split(",");
	},
	set(val) {
		if (!val || val.length === 0) {
			model.value = "";
		} else {
			const values = val.map((item) => item.value || item);
			model.value = values.join(",");
		}
	},
});
</script>
