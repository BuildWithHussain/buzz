<template>
	<div>
		<div class="w-8">
			<Spinner v-if="eventBookingResource.loading" />
		</div>
		<div
			v-if="!canAccessBookingPage && !eventBookingResource.loading"
			class="flex flex-col items-center justify-center py-16 px-4"
		>
			<div class="text-center max-w-md">
				<h2 class="text-xl font-semibold text-ink-gray-8 mb-2">
					{{ __("Login Required") }}
				</h2>
				<p class="text-ink-gray-6 mb-6">
					{{ __("Please log in to book tickets for this event.") }}
				</p>
				<Button variant="solid" size="lg" @click="redirectToLogin">{{
					__("Log In")
				}}</Button>
			</div>
		</div>
		<div v-else>
			<BookingForm
				v-if="eventBookingData.availableAddOns && eventBookingData.availableTicketTypes"
				:availableAddOns="eventBookingData.availableAddOns"
				:availableTicketTypes="eventBookingData.availableTicketTypes"
				:taxSettings="eventBookingData.taxSettings"
				:eventDetails="eventBookingData.eventDetails"
				:customFields="eventBookingData.customFields"
				:eventRoute="eventRoute"
				:paymentGateways="eventBookingData.paymentGateways"
				:isGuestMode="isGuest"
			/>
		</div>
	</div>
</template>

<script setup>
import { reactive, computed } from "vue";
import BookingForm from "../components/BookingForm.vue";
import { Spinner, createResource } from "frappe-ui";
import { session } from "@/data/session";
import { redirectToLogin } from "../utils/index.js";

const eventBookingData = reactive({
	availableAddOns: null,
	availableTicketTypes: null,
	taxSettings: null,
	eventDetails: null,
	customFields: null,
	paymentGateways: [],
});

const props = defineProps({
	eventRoute: {
		type: String,
		required: true,
	},
});

const isGuest = computed(() => !session.isLoggedIn);

const canAccessBookingPage = computed(() => {
	return session.isLoggedIn || eventBookingData.eventDetails?.allow_guest_booking;
});

const eventBookingResource = createResource({
	url: "buzz.api.get_event_booking_data",
	params: {
		event_route: props.eventRoute,
	},
	auto: true,
	onSuccess: (data) => {
		eventBookingData.availableAddOns = data.available_add_ons || [];
		eventBookingData.availableTicketTypes = data.available_ticket_types || [];
		eventBookingData.taxSettings = data.tax_settings || {
			apply_tax: false,
			tax_label: "Tax",
			tax_percentage: 0,
		};
		eventBookingData.eventDetails = data.event_details || {};
		eventBookingData.customFields = data.custom_fields || [];
		eventBookingData.paymentGateways = data.payment_gateways || [];
	},
	onError: (error) => {
		if (error.message.includes("DoesNotExistError")) {
			console.error("Event not found:", error);
			// Optionally, redirect to a 404 page or show a message
			alert(__("Event not found. Please check the event URL."));
			window.location.href = "/dashboard";
		} else {
			console.error("Error loading event booking data:", error);
		}
	},
});
</script>
