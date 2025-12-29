<template>
	<BookingHeader :booking-id="bookingId" />

	<div class="w-4" v-if="bookingDetails.loading">
		<Spinner />
	</div>

	<div v-else-if="bookingDetails.data">
		<!-- Event Information and Payment Summary in two columns -->
		<div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
			<!-- Event Information -->
			<BookingEventInfo
				v-if="bookingDetails.data.event"
				:event="bookingDetails.data.event"
				:venue="bookingDetails.data.venue"
			/>

			<!-- Booking Financial Summary -->
			<BookingFinancialSummary
				v-if="!bookingDetails.data.event.free_webinar && bookingDetails.data.doc"
				:booking="bookingDetails.data.doc"
			/>

			<!-- Booking Financial Summary -->
			<BookingFinancialSummary
				v-if="
					!bookingDetails.data.event.free_webinar && bookingDetails.data.booking_summary
				"
				:summary="bookingDetails.data.booking_summary"
			/>
		</div>

		<!-- Cancellation Request Section -->
		<!-- Only show if there's a pending cancellation request (not yet submitted/accepted) -->
		<CancellationRequestNotice
			v-if="!bookingDetails.data.event.free_webinar && hasPendingCancellationRequest"
			:cancellation-request="bookingDetails.data.cancellation_request"
		/>

		<!-- Tickets Section -->
		<TicketsSection
			v-if="!bookingDetails.data.event.free_webinar"
			:tickets="bookingDetails.data.tickets"
			:can-request-cancellation="canRequestCancellation"
			:can-transfer-tickets="canTransferTickets"
			:can-change-add-ons="canChangeAddOns"
			:cancellation-request="bookingDetails.data.cancellation_request"
			:cancellation-requested-tickets="bookingDetails.data.cancellation_requested_tickets"
			:cancelled-tickets="bookingDetails.data.cancelled_tickets"
			@request-cancellation="showCancellationDialog = true"
			@transfer-success="onTicketTransferSuccess"
		/>

		<CancellationRequestDialog
			v-model="showCancellationDialog"
			:tickets="bookingDetails.data.tickets"
			:booking-id="bookingId"
			:cancellation-requested-tickets="bookingDetails.data.cancellation_requested_tickets"
			:cancelled-tickets="bookingDetails.data.cancelled_tickets"
			@success="onCancellationRequestSuccess"
		/>
	</div>
</template>

<script setup>
import { ref, computed } from "vue";
import { createResource, Spinner } from "frappe-ui";
import { useRoute } from "vue-router";
import { usePaymentSuccess } from "../composables/usePaymentSuccess.js";
import { useBookingFormStorage } from "../composables/useBookingFormStorage.js";
import BookingHeader from "../components/BookingHeader.vue";
import SuccessMessage from "../components/SuccessMessage.vue";
import CancellationRequestNotice from "../components/CancellationRequestNotice.vue";
import TicketsSection from "../components/TicketsSection.vue";
import CancellationRequestDialog from "../components/CancellationRequestDialog.vue";
import BookingFinancialSummary from "../components/BookingFinancialSummary.vue";
import BookingEventInfo from "../components/BookingEventInfo.vue";

const route = useRoute();

const props = defineProps({
	bookingId: {
		type: String,
		required: true,
	},
});

// Check if this is a successful payment redirect (check URL immediately)
const isPaymentSuccess = route.query.success === "true";

// Use payment success composable for UI effects (confetti, message, URL cleanup)
const { showSuccessMessage } = usePaymentSuccess();

const showCancellationDialog = ref(false);

const bookingDetails = createResource({
	url: "buzz.api.get_booking_details",
	params: { booking_id: props.bookingId },
	auto: true,
	onSuccess: (data) => {
		// Clear stored booking form data if this was a successful payment
		if (isPaymentSuccess && data?.event?.route) {
			const { clearStoredData } = useBookingFormStorage(data.event.route);
			clearStoredData();
		}
	},
});

const canTransferTickets = computed(() => {
	return bookingDetails.data?.can_transfer_ticket?.can_transfer || false;
});

const canChangeAddOns = computed(() => {
	return bookingDetails.data?.can_change_add_ons?.can_change_add_ons || false;
});

const canRequestCancellation = computed(() => {
	return bookingDetails.data?.can_request_cancellation?.can_request_cancellation || false;
});

// Only show cancellation notice if there's a pending request (not yet submitted)
const hasPendingCancellationRequest = computed(() => {
	const cancellationRequest = bookingDetails.data?.cancellation_request;
	const cancellationRequestedTickets = bookingDetails.data?.cancellation_requested_tickets || [];

	// Show notice only if there's a cancellation request AND there are tickets with pending cancellation
	return cancellationRequest && cancellationRequestedTickets.length > 0;
});

const onTicketTransferSuccess = () => {
	bookingDetails.reload();
};

const onCancellationRequestSuccess = (data) => {
	bookingDetails.reload();
};
</script>
