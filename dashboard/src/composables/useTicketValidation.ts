import { createResource, toast } from "frappe-ui";
import { ref } from "vue";
import beepFailSound from "../assets/audio/beep-fail.wav";
import beepSound from "../assets/audio/beep.wav";

let ticketValidationState: any = null;

const isProcessingTicket = ref(false);
const isCheckingIn = ref(false);
const validationResult = ref<any>(null);
const showTicketModal = ref(false);

let lastToastMessage: string | null = null;
let lastToastTime = 0;
const TOAST_DEBOUNCE_MS = 500;

const playSuccessSound = () => {
	const audio = new Audio(beepSound);
	audio.play();
};

const playErrorSound = () => {
	const audio = new Audio(beepFailSound);
	audio.play();
};

const showDebouncedToast = (message: string, type: "error" | "success" = "error") => {
	const now = Date.now();
	if (lastToastMessage === message && now - lastToastTime < TOAST_DEBOUNCE_MS) {
		return;
	}
	lastToastMessage = message;
	lastToastTime = now;

	if (type === "error") {
		toast.error(message);
	} else {
		toast.success(message);
	}
};

// Ticket validation resource
const validateTicketResource = createResource({
	url: "buzz.api.validate_ticket_for_checkin",
	onSuccess: (data: any) => {
		validationResult.value = data;
		showTicketModal.value = true;
		playSuccessSound();
		isProcessingTicket.value = false;
	},
	onError: (error: any) => {
		validationResult.value = null;
		isProcessingTicket.value = false;
		const errorData = JSON.stringify(error);

		if (errorData.includes("Ticket not found")) {
			showDebouncedToast("Ticket not found");
		} else if (
			errorData.includes("This ticket is not confirmed and cannot be used for check-in")
		) {
			showDebouncedToast("This ticket is not confirmed and cannot be used for check-in");
		} else if (errorData.includes("This ticket was already checked in today")) {
			showDebouncedToast("This ticket was already checked in today.");
		} else if (errorData.includes("cancelled")) {
			showDebouncedToast("This ticket has been cancelled and cannot be checked in");
		} else {
			showDebouncedToast("Error validating ticket");
		}
		playErrorSound();
	},
});

// Check-in resource
const checkInResource = createResource({
	url: "buzz.api.checkin_ticket",
	onSuccess: (data: any) => {
		validationResult.value = data;
		showTicketModal.value = false;
		isCheckingIn.value = false;
	},
	onError: () => {
		isCheckingIn.value = false;
	},
});

export function useTicketValidation() {
	if (ticketValidationState) {
		return ticketValidationState;
	}

	// Methods
	const validateTicket = (ticketId: string) => {
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
		isProcessingTicket.value = false;
		isCheckingIn.value = false;
		showTicketModal.value = false;
	};

	const closeModal = () => {
		showTicketModal.value = false;
	};

	ticketValidationState = {
		// State
		isProcessingTicket,
		isCheckingIn,
		validationResult,
		showTicketModal,

		// Methods
		validateTicket,
		checkInTicket,
		clearResults,
		closeModal,
	};

	return ticketValidationState;
}
