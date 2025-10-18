<template>
	<div
		class="min-h-[75vh] border border-gray-200 dark:border-gray-700 shadow-sm mx-4 rounded-md"
	>
		<!-- Header -->
		<div class="shadow-sm border-b">
			<div class="max-w-md mx-auto px-4 py-4">
				<h1 class="text-xl font-bold text-center text-gray-900 dark:text-white">
					Event Check-in Scanner
				</h1>
			</div>
		</div>

		<!-- Main Content -->
		<div class="size-full px-4 py-6">
			<!-- Event Selection -->
			<EventSelector
				v-if="!selectedEvent"
				:selected-event="selectedEvent"
				@select="selectEvent"
			/>

			<!-- Scanner Interface -->
			<div v-else class="space-y-6">
				<!-- Selected Event Info -->
				<Button @click="clearEventSelection" class="w-full" icon-left="arrow-left">
					{{ selectedEvent.title }}
				</Button>

				<!-- QR Scanner -->
				<QRScanner
					:is-processing="isProcessingTicket"
					@scan="handleScan"
					@manual-entry="handleManualEntry"
				/>

				<!-- Last Scan Status -->
				<div
					v-if="lastScanResult"
					class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-4"
				>
					<h3 class="font-medium text-gray-900 dark:text-white mb-2">
						Last Scan Result
					</h3>
					<div
						class="p-3 rounded-lg"
						:class="
							lastScanResult.success
								? 'bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800'
								: 'bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800'
						"
					>
						<p
							class="text-sm font-medium"
							:class="
								lastScanResult.success
									? 'text-green-800 dark:text-green-200'
									: 'text-red-800 dark:text-red-200'
							"
						>
							{{ lastScanResult.message }}
						</p>
						<p
							v-if="lastScanResult.ticket"
							class="text-xs mt-1"
							:class="
								lastScanResult.success
									? 'text-green-600 dark:text-green-400'
									: 'text-red-600 dark:text-red-400'
							"
						>
							Ticket ID: {{ lastScanResult.ticket.id }}
						</p>
					</div>
				</div>
			</div>
		</div>

		<!-- Ticket Details Modal -->
		<TicketDetailsModal
			v-model="showTicketModal"
			:validation-result="validationResult"
			:is-checking-in="isCheckingIn"
			@check-in="handleCheckIn"
		/>
	</div>
</template>

<script setup>
import { Button } from "frappe-ui";
import { ref, watch } from "vue";
import beepFailSound from "../assets/audio/beep-fail.wav";
import beepSound from "../assets/audio/beep.wav";
import EventSelector from "../components/EventSelector.vue";
import QRScanner from "../components/QRScanner.vue";
import TicketDetailsModal from "../components/TicketDetailsModal.vue";
import { useTicketValidation } from "../composables/useTicketValidation.js";

const {
	isProcessingTicket,
	isCheckingIn,
	validationResult,
	lastScanResult,
	validateTicket,
	checkInTicket,
	clearResults,
} = useTicketValidation();

// State
const selectedEvent = ref(null);
const showTicketModal = ref(false);

// Event selection
const selectEvent = (event) => {
	selectedEvent.value = event;
	clearResults();
};

const clearEventSelection = () => {
	selectedEvent.value = null;
	clearResults();
	showTicketModal.value = false;
};

const playSuccessSound = () => {
	const audio = new Audio(beepSound);
	audio.play();
};

const playErrorSound = () => {
	const audio = new Audio(beepFailSound);
	audio.play();
};

// Handle scan results
const handleScan = (ticketId, error) => {
	if (ticketId) {
		validateTicket(ticketId);
	} else {
		playErrorSound();
		lastScanResult.value = {
			success: false,
			message: error || "Invalid QR code format",
			ticket: null,
		};
	}
};

// Handle manual entry
const handleManualEntry = (ticketId) => {
	validateTicket(ticketId);
};

// Handle check-in
const handleCheckIn = () => {
	checkInTicket();
	showTicketModal.value = false;
};

// Watch for validation results to show modal and play sounds
watch(validationResult, (newResult) => {
	if (newResult) {
		if (newResult.success) {
			if (!newResult.ticket?.is_checked_in) {
				playSuccessSound();
			}
			showTicketModal.value = true;
		} else {
			playErrorSound();
			if (newResult.error === "Already checked in") {
				showTicketModal.value = true;
			}
		}
	}
});
</script>
