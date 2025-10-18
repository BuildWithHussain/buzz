import { createResource } from "frappe-ui";
import { ref } from "vue";

export function useTicketValidation() {
	const isProcessingTicket = ref(false);
	const isCheckingIn = ref(false);
	const validationResult = ref(null);
	const lastScanResult = ref(null);

	// Ticket validation resource
	const validateTicketResource = createResource({
		url: "buzz.api.validate_ticket_for_checkin",
		onSuccess: (data) => {
			validationResult.value = data;
			lastScanResult.value = {
				success: data.success,
				message: data.message,
				ticket: data.ticket,
			};
			isProcessingTicket.value = false;
		},
		onError: () => {
			lastScanResult.value = {
				success: false,
				message: "Error validating ticket",
				ticket: null,
			};
			isProcessingTicket.value = false;
		},
	});

	// Check-in resource
	const checkInResource = createResource({
		url: "buzz.api.checkin_ticket",
		onSuccess: (data) => {
			if (data.success) {
				validationResult.value = data;
				lastScanResult.value = {
					success: true,
					message: data.message,
					ticket: data.ticket,
				};
			}
			isCheckingIn.value = false;
		},
		onError: (error) => {
			isCheckingIn.value = false;
		},
	});

	// Methods
	const validateTicket = (ticketId) => {
		isProcessingTicket.value = true;
		validateTicketResource.submit({ ticket_id: ticketId });
	};

	const checkInTicket = () => {
		if (!validationResult.value?.ticket?.id) return;

		isCheckingIn.value = true;
		checkInResource.submit({ ticket_id: validationResult.value.ticket.id });
	};

	const clearResults = () => {
		validationResult.value = null;
		lastScanResult.value = null;
		isProcessingTicket.value = false;
		isCheckingIn.value = false;
	};

	return {
		// State
		isProcessingTicket,
		isCheckingIn,
		validationResult,
		lastScanResult,

		// Methods
		validateTicket,
		checkInTicket,
		clearResults,
	};
}
