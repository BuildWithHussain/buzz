<!-- BookingSummary.vue -->
<template>
	<div class="bg-surface-gray-1 border border-gray-200 rounded-lg p-6">
		<h2 class="text-xl font-bold text-ink-gray-8 mb-4">Booking Summary</h2>

		<!-- Tickets Section -->
		<div v-if="Object.keys(summary.tickets).length" class="mb-4">
			<h3 class="text-lg font-semibold text-ink-gray-7 mb-2">Tickets</h3>
			<div v-for="(ticket, name) in summary.tickets" :key="name" class="mb-2">
				<div class="flex justify-between items-center text-ink-gray-6">
					<span>{{ ticket.title }} ({{ ticket.count }} tickets)</span>
					<span class="font-medium">{{
						formatPrice(ticket.amount, ticket.currency)
					}}</span>
				</div>
				<div v-if="ticket.isCouponTicket" class="text-xs text-ink-green-3 ml-2">
					<span class="line-through">{{
						formatPrice(ticket.originalPrice * ticket.count, ticket.currency)
					}}</span>
					<span class="ml-2">Coupon Applied - FREE!</span>
				</div>
				<div v-else class="text-xs text-gray-500 ml-2">
					{{ formatPrice(ticket.price, ticket.currency) }} each
				</div>
			</div>
		</div>

		<!-- Add-ons Section -->
		<div v-if="Object.keys(summary.add_ons).length" class="mb-4">
			<h3 class="text-lg font-semibold text-gray-700 mb-2">Add-ons</h3>
			<div v-for="(addOn, name) in summary.add_ons" :key="name" class="mb-2">
				<div class="flex justify-between items-center text-gray-600">
					<span>{{ addOn.title }} ({{ addOn.count }} items)</span>
					<span class="font-medium">{{
						formatPrice(addOn.amount, addOn.currency)
					}}</span>
				</div>
				<div v-if="addOn.isFreeAddOn" class="text-xs text-green-600 ml-2">
					<span>Included with coupon - FREE!</span>
				</div>
				<div v-else class="text-xs text-gray-500 ml-2">
					{{ formatPrice(addOn.price, addOn.currency) }} each
				</div>
			</div>
		</div>

		<hr class="my-4 border-t border-gray-200" />

		<!-- Total Section -->
		<div class="flex justify-between items-center text-xl font-bold text-gray-900">
			<h3>Total</h3>
			<span>{{ formatPrice(total, totalCurrency) }}</span>
		</div>
	</div>
</template>

<script setup>
import { formatPrice } from "../utils/currency.js";

defineProps({
	summary: {
		type: Object,
		required: true,
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
