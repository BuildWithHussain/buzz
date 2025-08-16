<template>
	<div>
		<div class="w-8">
			<Spinner v-if="eventBookingResource.loading" />
		</div>

		<BookingForm
			v-if="eventBookingData.availableAddOns && eventBookingData.availableTicketTypes"
			:availableAddOns="eventBookingData.availableAddOns"
			:availableTicketTypes="eventBookingData.availableTicketTypes"
			:couponCode="couponState.code"
			:couponInfo="couponInfo"
			:couponValidating="couponState.isValidating"
			@validate-coupon="handleCouponValidation"
		/>
	</div>
</template>

<script setup>
import { reactive, computed, ref } from "vue";
import { useRoute } from "vue-router";
import { useStorage } from "@vueuse/core";
import BookingForm from "../components/BookingForm.vue";
import { Spinner, createResource } from "frappe-ui";

const route = useRoute();
const storedCouponCode = useStorage("event-booking-coupon-code", "");
const initialCouponCode = route.query.coupon || storedCouponCode.value || "";

const eventBookingData = reactive({
	availableAddOns: null,
	availableTicketTypes: null,
});

const couponState = reactive({
	code: initialCouponCode,
	info: null,
	isValidating: false,
});

const props = defineProps({
	eventRoute: {
		type: String,
		required: true,
	},
});

// Computed properties for coupon status display
const couponInfo = computed(() => couponState.info);

const eventBookingResource = createResource({
	url: "events.api.get_event_booking_data",
	params: {
		event_route: props.eventRoute,
	},
	auto: true,
	onSuccess: (data) => {
		eventBookingData.availableAddOns = data.available_add_ons || [];
		eventBookingData.availableTicketTypes = data.available_ticket_types || [];
	},
	onError: (error) => {
		if (error.message.includes("DoesNotExistError")) {
			console.error("Event not found:", error);
			alert("Event not found. Please check the event URL.");
		} else {
			console.error("Error loading event booking data:", error);
		}
	},
});

const couponValidationResource = createResource({
	url: "events.api.validate_coupon",
});

// Validate coupon if initial code exists
if (initialCouponCode) {
	validateCoupon(initialCouponCode);
}

function validateCoupon(couponCode) {
	if (!couponCode || !couponCode.trim()) {
		couponState.info = null;
		couponState.isValidating = false;
		return;
	}

	couponState.isValidating = true;
	couponValidationResource.submit(
		{
			coupon_code: couponCode,
			event_route: props.eventRoute,
		},
		{
			onSuccess: (data) => {
				couponState.info = data;
				couponState.isValidating = false;
			},
			onError: (error) => {
				console.error("Error validating coupon:", error);
				couponState.info = { valid: false, error: "Error validating coupon" };
				couponState.isValidating = false;
			},
		}
	);
}

// Expose validateCoupon function to BookingForm
function handleCouponValidation(couponCode) {
	couponState.code = couponCode;
	storedCouponCode.value = couponCode || "";
	validateCoupon(couponCode);

	// If coupon is cleared, also update URL
	if (!couponCode || !couponCode.trim()) {
		const url = new URL(window.location);
		url.searchParams.delete("coupon");
		window.history.replaceState({}, "", url.toString());
	}
}
</script>
