<template>
	<div class="bg-surface-cards border border-outline-gray-1 rounded-lg p-6">
		<div class="flex items-center justify-between mb-4">
			<h3 class="text-lg font-semibold text-ink-gray-9">{{ __("Payment Summary") }}</h3>
			<Badge v-if="(booking.total_amount || 0) > 0" variant="subtle" theme="green" size="sm">
				<template #prefix>
					<LucideCheck class="w-3 h-3" />
				</template>
				{{ __("Paid") }}
			</Badge>
		</div>

		<div class="space-y-3">
			<!-- Net Amount -->
			<div class="flex justify-between items-center text-ink-gray-7">
				<span>{{ __("Subtotal") }}</span>
				<span class="font-medium">{{
					formatPrice(booking.net_amount || 0, booking.currency || "INR")
				}}</span>
			</div>

			<!-- Coupon Code -->
			<div
				v-if="booking.coupon_code"
				class="flex justify-between items-center text-ink-gray-7"
			>
				<span>{{ __("Coupon") }}</span>
				<span class="font-medium text-green-600">{{ booking.coupon_code }}</span>
			</div>

			<!-- Discount -->
			<div
				v-if="(booking.discount_amount || 0) > 0"
				class="flex justify-between items-center text-green-600"
			>
				<span>{{ __("Discount") }}</span>
				<span class="font-medium"
					>-{{ formatPrice(booking.discount_amount, booking.currency || "INR") }}</span
				>
			</div>

			<!-- Tax Information -->
			<div v-if="hasTax" class="flex justify-between items-center text-ink-gray-7">
				<span
					>{{ __(booking.tax_label || "Tax") }} ({{
						booking.tax_percentage || 0
					}}%)</span
				>
				<span class="font-medium">{{
					formatPrice(booking.tax_amount || 0, booking.currency || "INR")
				}}</span>
			</div>

			<!-- Divider -->
			<hr class="border-outline-gray-1" />

			<!-- Total Amount -->
			<div class="flex justify-between items-center text-lg font-semibold text-ink-gray-9">
				<span>{{ __("Total Paid") }}</span>
				<span class="text-ink-green-2">{{
					formatPrice(booking.total_amount || 0, booking.currency || "INR")
				}}</span>
			</div>
		</div>
	</div>
</template>

<script setup>
import { computed } from "vue";
import { Badge } from "frappe-ui";
import { formatPrice } from "../utils/currency.js";
import LucideCheck from "~icons/lucide/check";

const props = defineProps({
	booking: {
		type: Object,
		required: true,
		validator: (value) => {
			return typeof value === "object" && value !== null;
		},
	},
});

const hasTax = computed(() => {
	return Boolean(props.booking.tax_amount && props.booking.tax_amount > 0);
});
</script>
