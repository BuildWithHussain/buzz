<!-- AttendeeCard.vue -->
<template>
	<div
		class="bg-surface-white border border-outline-gray-3 rounded-xl p-4 md:p-6 mb-6 shadow-sm relative"
	>
		<!-- Remove Button -->
		<Tooltip :text="__('Remove Attendee')" :hover-delay="0.5">
			<Button
				v-if="showRemove"
				@click="$emit('remove')"
				type="button"
				theme="red"
				class="absolute top-4 right-4"
				:title="__('Remove attendee')"
				icon="x"
			/>
		</Tooltip>

		<h4 class="text-lg font-semibold text-ink-gray-9 mb-4 border-b pb-2 pr-10">
			{{ __("Attendee") }} #{{ index + 1 }}
		</h4>

		<!-- Name, Email and Custom Fields -->
		<div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
			<FormControl
				v-model="attendee.full_name"
				:label="__('Full Name')"
				:placeholder="__('Enter full name')"
				required
				type="text"
			/>
			<FormControl
				v-model="attendee.email"
				:label="__('Email')"
				:placeholder="__('Enter email address')"
				required
				type="email"
			/>

			<!-- Ticket Type -->

			<!-- Show selector only if there are multiple ticket types -->
			<FormControl
				v-if="availableTicketTypes.length > 1"
				v-model="attendee.ticket_type"
				:label="__('Ticket Type')"
				type="select"
				:options="
					availableTicketTypes.map((tt) => ({
						label: `${__(tt.title)} (${formatPriceOrFree(tt.price, tt.currency)})`,
						value: tt.name,
					}))
				"
			/>

			<!-- Custom Fields for Tickets integrated with basic fields -->
			<template v-if="customFields.length > 0">
				<CustomFieldInput
					v-for="field in customFields"
					:key="field.fieldname"
					:field="field"
					:model-value="getCustomFieldValue(field.fieldname)"
					@update:model-value="updateCustomFieldValue(field.fieldname, $event)"
				/>
			</template>
		</div>

		<!-- Add-ons -->
		<div v-if="availableAddOns.length > 0">
			<hr class="my-4" />

			<div v-for="addOn in availableAddOns" :key="addOn.name" class="mb-4">
				<div class="flex flex-col gap-3">
					<FormControl
						type="checkbox"
						:model-value="getAddOnSelected(addOn.name)"
						@update:model-value="updateAddOnSelection(addOn.name, $event)"
						:id="`add_on_${addOn.name}_${index}`"
						:label="addOn.title"
					/>

					<div class="text-ink-gray-5 text-sm" v-if="addOn.description">
						<p>
							{{ __(addOn.description) }}
						</p>
					</div>
				</div>

				<div
					v-if="addOn.user_selects_option && getAddOnSelected(addOn.name)"
					class="mt-2 ml-6"
				>
					<FormControl
						:model-value="getAddOnOption(addOn.name)"
						@update:model-value="updateAddOnOption(addOn.name, $event)"
						type="select"
						:options="
							addOn.options.map((option) => ({ label: __(option), value: option }))
						"
						size="sm"
					/>
				</div>
			</div>
		</div>
	</div>
</template>

<script setup>
import { Tooltip } from "frappe-ui";
import { formatPrice, formatPriceOrFree } from "../utils/currency.js";
import CustomFieldInput from "./CustomFieldInput.vue";
import { getFieldOptions, getFieldDefaultValue } from "@/composables/useCustomFields.js";

const props = defineProps({
	attendee: { type: Object, required: true },
	index: { type: Number, required: true },
	availableTicketTypes: { type: Array, required: true },
	availableAddOns: { type: Array, required: true },
	customFields: { type: Array, default: () => [] },
	showRemove: { type: Boolean, default: false },
});

defineEmits(["remove"]);

// Helper methods to safely access add-on properties
const ensureAddOnExists = (addOnName) => {
	if (!props.attendee.add_ons) {
		props.attendee.add_ons = {};
	}
	if (!props.attendee.add_ons[addOnName]) {
		const addOn = props.availableAddOns.find((a) => a.name === addOnName);
		props.attendee.add_ons[addOnName] = {
			selected: false,
			option: addOn?.options ? addOn.options[0] || null : null,
		};
	}
};

const getAddOnSelected = (addOnName) => {
	ensureAddOnExists(addOnName);
	return props.attendee.add_ons[addOnName].selected;
};

const getAddOnOption = (addOnName) => {
	ensureAddOnExists(addOnName);
	return props.attendee.add_ons[addOnName].option;
};

const updateAddOnSelection = (addOnName, selected) => {
	ensureAddOnExists(addOnName);
	props.attendee.add_ons[addOnName].selected = selected;

	// If selecting an add-on and it has options, ensure the first option is selected
	if (selected) {
		const addOn = props.availableAddOns.find((a) => a.name === addOnName);
		if (
			addOn?.options &&
			addOn.options.length > 0 &&
			!props.attendee.add_ons[addOnName].option
		) {
			props.attendee.add_ons[addOnName].option = addOn.options[0];
		}
	}
};

const updateAddOnOption = (addOnName, option) => {
	ensureAddOnExists(addOnName);
	props.attendee.add_ons[addOnName].option = option;
};

// Custom fields helper methods
const ensureCustomFieldsExists = () => {
	if (!props.attendee.custom_fields) {
		props.attendee.custom_fields = {};
	}
};

const getCustomFieldValue = (fieldname) => {
	ensureCustomFieldsExists();
	const currentValue = props.attendee.custom_fields[fieldname];

	// Apply default for fields that don't have values yet
	if (!currentValue && currentValue !== "") {
		const field = props.customFields.find((f) => f.fieldname === fieldname);
		if (field) {
			const defaultValue = getFieldDefaultValue(field);
			if (defaultValue) {
				updateCustomFieldValue(fieldname, defaultValue);
				return defaultValue;
			}
		}
	}

	return currentValue || "";
};

const updateCustomFieldValue = (fieldname, value) => {
	ensureCustomFieldsExists();
	props.attendee.custom_fields[fieldname] = value;
};
</script>
