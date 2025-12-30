<!-- BookingSummary.vue -->
<template>
	<div class="bg-surface-gray-1 border border-outline-gray-1 rounded-lg p-4">
		<h2 class="text-xl font-bold text-ink-gray-9 mb-4">{{ __("Booking Summary") }}</h2>

		<!-- Tickets Section -->
		<div v-if="Object.keys(summary.tickets).length" class="mb-4">
			<h3 class="text-lg font-semibold text-ink-gray-8 mb-2">{{ __("Tickets") }}</h3>
			<div
				v-for="(ticket, name) in summary.tickets"
				:key="name"
				class="flex justify-between items-start text-ink-gray-7 mb-2"
			>
				<div class="flex flex-col">
					<span>{{ __(ticket.title) }}</span>
					<span v-if="total > 0" class="text-sm text-ink-gray-5">
						{{ ticket.count }} x {{ formatPriceOrFree(ticket.price, ticket.currency) }}
					</span>
					<span v-else class="text-sm text-ink-gray-5">x {{ ticket.count }}</span>
				</div>
				<span v-if="total > 0" class="font-medium">{{
					formatPriceOrFree(ticket.amount, ticket.currency)
				}}</span>
			</div>
		</div>

		<!-- Add-ons Section -->
		<div v-if="Object.keys(summary.add_ons).length" class="mb-4">
			<h3 class="text-lg font-semibold text-ink-gray-8 mb-2">{{ __("Add-ons") }}</h3>
			<div
				v-for="(addOn, name) in summary.add_ons"
				:key="name"
				class="flex justify-between items-start text-ink-gray-7 mb-2"
			>
				<div class="flex flex-col">
					<span>{{ __(addOn.title) }}</span>
					<span v-if="total > 0" class="text-sm text-ink-gray-5">
						{{ addOn.count }} x {{ formatPriceOrFree(addOn.price, addOn.currency) }}
					</span>
					<span v-else class="text-sm text-ink-gray-5">x {{ addOn.count }}</span>
				</div>
				<span v-if="total > 0" class="font-medium">{{
					formatPriceOrFree(addOn.amount, addOn.currency)
				}}</span>
			</div>
		</div>

		<!-- Only show pricing summary if total > 0 -->
		<template v-if="total > 0">
			<hr class="my-4 border-t border-outline-gray-1" />

			<!-- Subtotal -->
			<div class="flex justify-between items-center text-ink-gray-7 mb-2">
				<span>{{ __("Subtotal") }}</span>
				<span class="font-medium">{{ formatPriceOrFree(netAmount, totalCurrency) }}</span>
			</div>

			<!-- Tax Section -->
			<div
				v-if="shouldApplyTax"
				class="flex justify-between items-center text-ink-gray-7 mb-2"
			>
				<span>{{ __(taxLabel) }} ({{ taxPercentage }}%)</span>
				<span class="font-medium">{{ formatPriceOrFree(taxAmount, totalCurrency) }}</span>
			</div>

			<!-- Final Total Section -->
			<hr v-if="shouldApplyTax" class="my-2 border-t border-outline-gray-1" />
			<div class="flex justify-between items-center text-xl font-bold text-ink-gray-9">
				<h3>{{ __("Total") }}</h3>
				<span>{{ formatPriceOrFree(total, totalCurrency) }}</span>
			</div>
		</template>

		<!-- Free event message -->
		<template v-else>
			<hr class="my-2 border-t border-outline-gray-1" />
			<div class="text-center pt-2">
				<div class="text-xl font-bold text-green-600">{{ __("Free Event") }}</div>
			</div>
		</template>
	</div>
</template>

<script setup>
import { formatPriceOrFree } from "../utils/currency.js";

defineProps({
	summary: {
		type: Object,
		required: true,
	},
	netAmount: {
		type: Number,
		required: true,
	},
	taxAmount: {
		type: Number,
		default: 0,
	},
	taxPercentage: {
		type: Number,
		default: 0,
	},
	taxLabel: {
		type: String,
		default: "Tax",
	},
	shouldApplyTax: {
		type: Boolean,
		default: false,
	},
	total: {
		type: Number,
		required: true,
	},
	totalCurrency: {
		type: String,
		default: "INR",
	},
});
</script>
