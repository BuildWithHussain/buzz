<!-- AttendeeCard.vue -->
<template>
	<div class="bg-white border border-gray-300 rounded-xl p-4 md:p-6 mb-6 shadow-sm relative">
		<!-- Remove Button -->
		<Tooltip text="Remove Attendee" :hover-delay="0.5">
			<Button
				v-if="showRemove"
				@click="$emit('remove')"
				type="button"
				theme="red"
				class="absolute top-4 right-4"
				title="Remove attendee"
				icon="x"
			/>
		</Tooltip>

		<h4 class="text-lg font-semibold text-gray-800 mb-4 border-b pb-2 pr-10">
			Attendee #{{ index + 1 }}
		</h4>

		<!-- Name and Email Fields -->
		<div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
			<FormControl
				v-model="attendee.full_name"
				label="Full Name"
				placeholder="Enter full name"
				required
				type="text"
			/>
			<FormControl
				v-model="attendee.email"
				label="Email"
				placeholder="Enter email address"
				required
				type="email"
			/>
		</div>

		<!-- Ticket Type -->
		<div class="mb-4">
			<FormControl
				v-model="attendee.ticket_type"
				label="Ticket Type"
				type="select"
				:options="
					availableTicketTypes.map((tt) => ({
						label: `${tt.title} (${formatPrice(tt.price, tt.currency)})`,
						value: tt.name,
					}))
				"
				:disabled="props.isTicketTypeReadOnly"
			/>
		</div>

		<!-- Add-ons -->
		<div v-if="availableAddOns.length > 0">
			<h5 class="text-md font-semibold text-gray-700 mt-6 mb-3">Add-ons</h5>
			<div v-for="addOn in availableAddOns" :key="addOn.name" class="mb-3">
				<div class="flex items-center">
					<FormControl
						type="checkbox"
						v-model="attendee.add_ons[addOn.name].selected"
						:id="`add_on_${addOn.name}_${index}`"
						:label="`${addOn.title} (${formatPrice(addOn.price, addOn.currency)})`"
					/>
				</div>

				<div
					v-if="addOn.user_selects_option && attendee.add_ons[addOn.name].selected"
					class="mt-2 ml-6"
				>
					<FormControl
						v-model="attendee.add_ons[addOn.name].option"
						type="select"
						:options="
							addOn.options.map((option) => ({ label: option, value: option }))
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
import { formatPrice } from "../utils/currency.js";

const props = defineProps({
	attendee: { type: Object, required: true },
	index: { type: Number, required: true },
	availableTicketTypes: { type: Array, required: true },
	availableAddOns: { type: Array, required: true },
	showRemove: { type: Boolean, default: false },
	isTicketTypeReadOnly: { type: Boolean, default: false },
});

defineEmits(["remove"]);
</script>
