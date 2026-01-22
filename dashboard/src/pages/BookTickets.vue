<template>
	<div>
		<div class="w-8">
			<Spinner v-if="eventBookingResource.loading" />
		</div>
		<div>
			<BookingForm
				v-if="eventBookingData.availableAddOns && eventBookingData.availableTicketTypes"
				:availableAddOns="eventBookingData.availableAddOns"
				:availableTicketTypes="eventBookingData.availableTicketTypes"
				:taxSettings="eventBookingData.taxSettings"
				:eventDetails="eventBookingData.eventDetails"
				:customFields="eventBookingData.customFields"
				:eventRoute="eventRoute"
				:paymentGateways="eventBookingData.paymentGateways"
			/>
		</div>
	</div>
</template>

<script setup>
import { reactive } from "vue";
import BookingForm from "../components/BookingForm.vue";
import { Spinner, createResource } from "frappe-ui";

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
			total_includes_taxes: false,
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
