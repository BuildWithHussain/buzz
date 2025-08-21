<template>
	<div class="min-h-screen bg-gray-50">
		<!-- Header -->
		<div class="bg-white shadow-sm border-b">
			<div class="max-w-md mx-auto px-4 py-4">
				<h1 class="text-xl font-bold text-gray-900 text-center">Event Check-in Scanner</h1>
			</div>
		</div>

		<!-- Main Content -->
		<div class="max-w-md mx-auto px-4 py-6">
			<!-- Event Selection -->
			<div v-if="!selectedEvent" class="mb-6">
				<h2 class="text-lg font-semibold text-gray-800 mb-4">Select Event</h2>
				<div v-if="eventsResource.loading" class="flex justify-center py-8">
					<Spinner class="w-6 h-6" />
				</div>
				<div v-else-if="availableEvents.length === 0" class="text-center py-8">
					<p class="text-gray-600">No active events found</p>
					<Button @click="loadEvents" variant="outline" class="mt-4"> Refresh </Button>
				</div>
				<div v-else class="space-y-3">
					<Button
						v-for="event in availableEvents"
						:key="event.name"
						@click="selectEvent(event)"
						variant="outline"
						class="w-full text-left justify-start p-4 h-auto"
					>
						<div>
							<div class="font-medium text-gray-900">{{ event.title }}</div>
							<div class="text-sm text-gray-500">{{ formatEventDate(event) }}</div>
							<div class="text-sm text-gray-500">{{ event.venue }}</div>
						</div>
					</Button>
				</div>
			</div>

			<!-- Scanner Interface -->
			<div v-else class="space-y-6">
				<!-- Selected Event Info -->
				<div class="bg-white rounded-lg p-4 shadow-sm border">
					<div class="flex justify-between items-start">
						<div>
							<h3 class="font-medium text-gray-900">{{ selectedEvent.title }}</h3>
							<p class="text-sm text-gray-500">
								{{ formatEventDate(selectedEvent) }}
							</p>
							<p class="text-sm text-gray-500">{{ selectedEvent.venue }}</p>
						</div>
						<Button
							@click="clearEventSelection"
							variant="ghost"
							size="sm"
							class="text-blue-600"
						>
							Change
						</Button>
					</div>
				</div>

				<!-- QR Scanner -->
				<div class="bg-white rounded-lg shadow-sm border overflow-hidden">
					<div class="p-4 border-b">
						<h3 class="font-medium text-gray-900">Scan Ticket QR Code</h3>
					</div>

					<!-- Scanner Container -->
					<div class="relative">
						<div
							id="qr-reader"
							class="w-full"
							:class="{ 'opacity-50': isProcessingTicket }"
						></div>

						<!-- Processing Overlay -->
						<div
							v-if="isProcessingTicket"
							class="absolute inset-0 bg-white bg-opacity-75 flex items-center justify-center"
						>
							<Spinner class="w-8 h-8" />
						</div>
					</div>

					<!-- Scanner Controls -->
					<div class="p-4 border-t bg-gray-50">
						<div class="flex gap-2">
							<Button
								@click="startScanner"
								v-if="!scannerActive"
								variant="solid"
								class="flex-1"
							>
								<template #prefix>
									<LucideQrCode class="w-4 h-4" />
								</template>
								Start Scanner
							</Button>
							<Button @click="stopScanner" v-else variant="outline" class="flex-1">
								<template #prefix>
									<LucideSquare class="w-4 h-4" />
								</template>
								Stop Scanner
							</Button>
						</div>

						<!-- Manual Entry -->
						<div class="mt-3 pt-3 border-t border-gray-200">
							<div class="flex gap-2">
								<TextInput
									v-model="manualTicketId"
									placeholder="Enter ticket ID manually"
									class="flex-1"
									:disabled="isProcessingTicket"
								/>
								<Button
									@click="validateManualTicket"
									:loading="isProcessingTicket"
									:disabled="!manualTicketId.trim()"
								>
									Check
								</Button>
							</div>
						</div>
					</div>
				</div>

				<!-- Last Scan Status -->
				<div v-if="lastScanResult" class="bg-white rounded-lg shadow-sm border p-4">
					<h3 class="font-medium text-gray-900 mb-2">Last Scan Result</h3>
					<div
						class="p-3 rounded-lg"
						:class="
							lastScanResult.success
								? 'bg-green-50 border border-green-200'
								: 'bg-red-50 border border-red-200'
						"
					>
						<p
							class="text-sm font-medium"
							:class="lastScanResult.success ? 'text-green-800' : 'text-red-800'"
						>
							{{ lastScanResult.message }}
						</p>
						<p
							v-if="lastScanResult.ticket"
							class="text-xs mt-1"
							:class="lastScanResult.success ? 'text-green-600' : 'text-red-600'"
						>
							Ticket ID: {{ lastScanResult.ticket.id }}
						</p>
					</div>
				</div>
			</div>
		</div>

		<!-- Ticket Details Modal -->
		<Dialog v-model="showTicketModal">
			<template #body-title>
				<h3 class="text-lg font-semibold text-gray-900">
					{{ validationResult?.success ? "Valid Ticket" : "Invalid Ticket" }}
				</h3>
			</template>

			<template #body-content>
				<div v-if="validationResult">
					<!-- Debug: Show raw validation result -->
					<div class="mb-4 p-2 bg-gray-100 rounded text-xs">
						<strong>Debug:</strong> {{ JSON.stringify(validationResult, null, 2) }}
					</div>

					<!-- Success State -->
					<div
						v-if="validationResult.success && !validationResult.ticket?.is_checked_in"
					>
						<div class="text-center mb-6">
							<div
								class="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4"
							>
								<LucideCheckCircle class="w-8 h-8 text-green-600" />
							</div>
							<h4 class="text-lg font-semibold text-gray-900">Valid Ticket</h4>
							<p class="text-gray-600">Ready for check-in</p>
						</div>

						<div class="space-y-4 mb-6">
							<div class="grid grid-cols-2 gap-4">
								<div>
									<label class="block text-sm font-medium text-gray-700"
										>Attendee</label
									>
									<p class="text-gray-900">
										{{ validationResult.ticket.attendee_name }}
									</p>
								</div>
								<div>
									<label class="block text-sm font-medium text-gray-700"
										>Email</label
									>
									<p class="text-gray-900 text-sm">
										{{ validationResult.ticket.attendee_email }}
									</p>
								</div>
								<div>
									<label class="block text-sm font-medium text-gray-700"
										>Ticket Type</label
									>
									<p class="text-gray-900">
										{{ validationResult.ticket.ticket_type }}
									</p>
								</div>
								<div>
									<label class="block text-sm font-medium text-gray-700"
										>Ticket ID</label
									>
									<p class="text-gray-900 font-mono text-sm">
										{{ validationResult.ticket.id }}
									</p>
								</div>
							</div>

							<!-- Add-ons -->
							<div
								v-if="validationResult.ticket.add_ons?.length"
								class="border-t pt-4"
							>
								<label class="block text-sm font-medium text-gray-700 mb-2"
									>Add-ons</label
								>
								<div class="space-y-2">
									<div
										v-for="addon in validationResult.ticket.add_ons"
										:key="addon.add_on"
										class="flex justify-between text-sm"
									>
										<span>{{ addon.add_on_title || addon.add_on }}</span>
										<span class="text-gray-600">{{ addon.value }}</span>
									</div>
								</div>
							</div>
						</div>
					</div>

					<!-- Already Checked In State -->
					<div
						v-else-if="
							validationResult.success && validationResult.ticket?.is_checked_in
						"
					>
						<div class="text-center mb-6">
							<div
								class="w-16 h-16 bg-yellow-100 rounded-full flex items-center justify-center mx-auto mb-4"
							>
								<LucideAlertTriangle class="w-8 h-8 text-yellow-600" />
							</div>
							<h4 class="text-lg font-semibold text-gray-900">Already Checked In</h4>
							<p class="text-gray-600">{{ validationResult.message }}</p>
						</div>

						<div class="space-y-4 mb-6">
							<div class="grid grid-cols-2 gap-4">
								<div>
									<label class="block text-sm font-medium text-gray-700"
										>Attendee</label
									>
									<p class="text-gray-900">
										{{ validationResult.ticket.attendee_name }}
									</p>
								</div>
								<div>
									<label class="block text-sm font-medium text-gray-700"
										>Check-in Time</label
									>
									<p class="text-gray-900 text-sm">
										{{ formatDateTime(validationResult.ticket.check_in_time) }}
									</p>
								</div>
							</div>
						</div>
					</div>

					<!-- Error State -->
					<div v-else>
						<div class="text-center mb-6">
							<div
								class="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4"
							>
								<LucideXCircle class="w-8 h-8 text-red-600" />
							</div>
							<h4 class="text-lg font-semibold text-gray-900">
								{{ validationResult.error || "Invalid Ticket" }}
							</h4>
							<p class="text-gray-600">{{ validationResult.message }}</p>
						</div>
					</div>
				</div>
			</template>

			<template #actions="{ close }">
				<!-- Success State Actions -->
				<div
					v-if="validationResult?.success && !validationResult.ticket?.is_checked_in"
					class="flex gap-3"
				>
					<Button @click="checkInTicket" :loading="isCheckingIn" class="flex-1">
						<template #prefix>
							<LucideUserCheck class="w-4 h-4" />
						</template>
						Check In
					</Button>
					<Button @click="close" variant="outline"> Cancel </Button>
				</div>

				<!-- Already Checked In Actions -->
				<div
					v-else-if="validationResult?.success && validationResult.ticket?.is_checked_in"
				>
					<Button @click="close" class="w-full"> Close </Button>
				</div>

				<!-- Error State Actions -->
				<div v-else>
					<Button @click="close" class="w-full" variant="outline"> Close </Button>
				</div>
			</template>
		</Dialog>
	</div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from "vue";
import { Html5QrcodeScanner } from "html5-qrcode";
import { createResource, Button, TextInput, Dialog, Spinner } from "frappe-ui";
import { dayjsLocal } from "frappe-ui";
import LucideQrCode from "~icons/lucide/qr-code";
import LucideSquare from "~icons/lucide/square";
import LucideCheckCircle from "~icons/lucide/check-circle";
import LucideXCircle from "~icons/lucide/x-circle";
import LucideAlertTriangle from "~icons/lucide/alert-triangle";
import LucideUserCheck from "~icons/lucide/user-check";

// State
const selectedEvent = ref(null);
const availableEvents = ref([]);
const qrScanner = ref(null);
const scannerActive = ref(false);
const manualTicketId = ref("");
const isProcessingTicket = ref(false);
const isCheckingIn = ref(false);
const showTicketModal = ref(false);
const validationResult = ref(null);
const lastScanResult = ref(null);

// Audio for feedback
const successAudio = ref(null);
const errorAudio = ref(null);
const audioContext = ref(null);
const lastSoundTime = ref(0);
const soundCooldown = 500; // 500ms cooldown between sounds

onMounted(() => {
	// Initialize audio context once
	generateAudioTones();
	loadEvents();
});

onUnmounted(() => {
	if (qrScanner.value) {
		qrScanner.value.clear();
	}
	// Clean up audio context
	if (audioContext.value) {
		audioContext.value.close();
	}
});

// Load available events
const eventsResource = createResource({
	url: "frappe.client.get_list",
	params: {
		doctype: "FE Event",
		fields: ["name", "title", "start_date", "start_time", "end_date", "end_time", "venue"],
		order_by: "start_date desc",
	},
	auto: false,
	onSuccess: (data) => {
		availableEvents.value = data;
	},
});

const loadEvents = () => {
	eventsResource.fetch();
};

// Event selection
const selectEvent = (event) => {
	selectedEvent.value = event;
	nextTick(() => {
		startScanner();
	});
};

const clearEventSelection = () => {
	stopScanner();
	selectedEvent.value = null;
	lastScanResult.value = null;
	validationResult.value = null;
};

// Date formatting
const formatEventDate = (event) => {
	if (!event.start_date) return "";
	const date = dayjsLocal(event.start_date);
	if (event.start_time) {
		return date.format("MMM DD, YYYY [at] h:mm A");
	}
	return date.format("MMM DD, YYYY");
};

const formatDateTime = (datetime) => {
	if (!datetime) return "";
	return dayjsLocal(datetime).format("MMM DD, YYYY [at] h:mm A");
};

// QR Scanner functions
const startScanner = () => {
	if (scannerActive.value) return;

	qrScanner.value = new Html5QrcodeScanner(
		"qr-reader",
		{
			fps: 10,
			qrbox: { width: 250, height: 250 },
			aspectRatio: 1.0,
		},
		false
	);

	qrScanner.value.render(onScanSuccess, onScanFailure);
	scannerActive.value = true;
};

const stopScanner = () => {
	if (!scannerActive.value || !qrScanner.value) return;

	qrScanner.value.clear();
	qrScanner.value = null;
	scannerActive.value = false;
};

const onScanSuccess = (decodedText) => {
	// Stop scanner temporarily while processing
	isProcessingTicket.value = true;

	// Extract ticket ID from QR code (assuming it contains the ticket ID)
	const ticketId = extractTicketId(decodedText);

	if (ticketId) {
		validateTicket(ticketId);
	} else {
		playErrorSound();
		lastScanResult.value = {
			success: false,
			message: "Invalid QR code format",
			ticket: null,
		};
		isProcessingTicket.value = false;
	}
};

const onScanFailure = (error) => {
	// Silently handle scan failures - they happen frequently
};

// Extract ticket ID from QR code data
const extractTicketId = (qrData) => {
	// If QR contains just the ticket ID
	if (qrData.match(/^[A-Z0-9\-]+$/)) {
		return qrData;
	}

	// If QR contains a URL with ticket ID
	const urlMatch = qrData.match(/ticket[\/=]([A-Z0-9\-]+)/i);
	if (urlMatch) {
		return urlMatch[1];
	}

	// Try to extract any alphanumeric string that looks like a ticket ID
	const idMatch = qrData.match(/([A-Z0-9\-]{10,})/i);
	if (idMatch) {
		return idMatch[1];
	}

	return null;
};

// Manual ticket validation
const validateManualTicket = () => {
	const ticketId = manualTicketId.value.trim();
	if (!ticketId) return;

	validateTicket(ticketId);
	manualTicketId.value = "";
};

// Ticket validation
const validateTicketResource = createResource({
	url: "events.api.validate_ticket_for_checkin",
	onSuccess: (data) => {
		console.log("Validation result received:", data);
		validationResult.value = data;
		lastScanResult.value = {
			success: data.success,
			message: data.message,
			ticket: data.ticket,
		};

		if (data.success) {
			// Only play sound for validation, not for already checked in tickets
			if (!data.ticket?.is_checked_in) {
				playSuccessSound();
			}
			showTicketModal.value = true;
		} else {
			playErrorSound();
			if (data.error === "Already checked in") {
				showTicketModal.value = true;
			}
		}

		isProcessingTicket.value = false;
	},
	onError: (error) => {
		playErrorSound();
		lastScanResult.value = {
			success: false,
			message: "Error validating ticket",
			ticket: null,
		};
		isProcessingTicket.value = false;
	},
});

const validateTicket = (ticketId) => {
	isProcessingTicket.value = true;
	validateTicketResource.submit({ ticket_id: ticketId });
};

// Check-in
const checkInResource = createResource({
	url: "events.api.checkin_ticket",
	onSuccess: (data) => {
		if (data.success) {
			// Don't play sound here as we already played it during validation
			validationResult.value = data;
			lastScanResult.value = {
				success: true,
				message: data.message,
				ticket: data.ticket,
			};
			showTicketModal.value = false;
		} else {
			playErrorSound();
		}
		isCheckingIn.value = false;
	},
	onError: (error) => {
		playErrorSound();
		isCheckingIn.value = false;
	},
});

const checkInTicket = () => {
	if (!validationResult.value?.ticket?.id) return;

	isCheckingIn.value = true;
	checkInResource.submit({ ticket_id: validationResult.value.ticket.id });
};

// Generate audio tones programmatically
const generateAudioTones = () => {
	try {
		// Create audio context for generating tones only if not already created
		if (!audioContext.value) {
			audioContext.value = new (window.AudioContext || window.webkitAudioContext)();
		}

		// Success tone (800Hz for 150ms) - shorter duration
		const createSuccessTone = () => {
			if (!audioContext.value) return;

			const oscillator = audioContext.value.createOscillator();
			const gainNode = audioContext.value.createGain();

			oscillator.connect(gainNode);
			gainNode.connect(audioContext.value.destination);

			oscillator.frequency.setValueAtTime(800, audioContext.value.currentTime);
			oscillator.type = "sine";

			gainNode.gain.setValueAtTime(0.2, audioContext.value.currentTime); // Lower volume
			gainNode.gain.exponentialRampToValueAtTime(
				0.01,
				audioContext.value.currentTime + 0.15
			);

			oscillator.start(audioContext.value.currentTime);
			oscillator.stop(audioContext.value.currentTime + 0.15);
		};

		// Error tone (400Hz for 200ms) - shorter duration
		const createErrorTone = () => {
			if (!audioContext.value) return;

			const oscillator = audioContext.value.createOscillator();
			const gainNode = audioContext.value.createGain();

			oscillator.connect(gainNode);
			gainNode.connect(audioContext.value.destination);

			oscillator.frequency.setValueAtTime(400, audioContext.value.currentTime);
			oscillator.type = "sine";

			gainNode.gain.setValueAtTime(0.2, audioContext.value.currentTime); // Lower volume
			gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.value.currentTime + 0.2);

			oscillator.start(audioContext.value.currentTime);
			oscillator.stop(audioContext.value.currentTime + 0.2);
		};

		// Store tone generators
		successAudio.value = { play: createSuccessTone };
		errorAudio.value = { play: createErrorTone };
	} catch (e) {
		console.warn("Audio context not supported, using fallback sounds");
	}
};

// Audio feedback
const playSuccessSound = () => {
	const now = Date.now();
	if (now - lastSoundTime.value < soundCooldown) {
		return; // Skip if too soon after last sound
	}

	try {
		successAudio.value?.play();
		lastSoundTime.value = now;
	} catch (e) {
		// Audio play failed, ignore
		console.warn("Failed to play success sound:", e);
	}
};

const playErrorSound = () => {
	const now = Date.now();
	if (now - lastSoundTime.value < soundCooldown) {
		return; // Skip if too soon after last sound
	}

	try {
		errorAudio.value?.play();
		lastSoundTime.value = now;
	} catch (e) {
		// Audio play failed, ignore
		console.warn("Failed to play error sound:", e);
	}
};
</script>

<style scoped>
/* Ensure proper mobile styling */
#qr-reader {
	width: 100%;
}

/* Override html5-qrcode styles for better mobile experience */
:global(#qr-reader > div:first-child) {
	border: none !important;
}

:global(#qr-reader video) {
	border-radius: 0 !important;
}

:global(#qr-reader__dashboard) {
	padding: 16px !important;
}

:global(#qr-reader__dashboard button) {
	margin: 4px !important;
	padding: 8px 16px !important;
	border-radius: 6px !important;
}
</style>
