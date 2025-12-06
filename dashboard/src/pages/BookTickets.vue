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
				:gstSettings="eventBookingData.gstSettings"
				:eventDetails="eventBookingData.eventDetails"
				:customFields="eventBookingData.customFields"
				:eventRoute="eventRoute"
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
	gstSettings: null,
	eventDetails: null,
	customFields: null,
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
		eventBookingData.gstSettings = data.gst_settings || {
			apply_gst_on_bookings: false,
			gst_percentage: 18,
		};
		eventBookingData.eventDetails = data.event_details || {};
		eventBookingData.customFields = data.custom_fields || [];
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
