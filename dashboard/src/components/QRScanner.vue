<template>
	<div
		class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden"
	>
		<div class="p-4 border-b border-gray-200 dark:border-gray-700">
			<h3 class="font-medium text-gray-900 dark:text-white">Scan Ticket QR Code</h3>
		</div>

		<!-- Scanner Container -->
		<div class="relative">
			<div
				id="qr-reader"
				class="w-full text-ink-gray-7"
				:class="{ 'opacity-50': isProcessingTicket }"
			></div>

			<!-- Processing Overlay -->
			<div
				v-if="isProcessingTicket"
				class="absolute inset-0 bg-white dark:bg-gray-800 bg-opacity-75 flex items-center justify-center"
			>
				<Spinner class="w-8 h-8" />
			</div>
		</div>

		<!-- Scanner Controls -->
		<div class="p-4 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-700">
			<div class="flex gap-2">
				<Button
					@click="startScanner"
					v-if="!scannerActive"
					variant="outline"
					class="flex-1"
				>
					<template #prefix>
						<LucideQrCode class="w-4 h-4" />
					</template>
					Start Scanner
				</Button>
				<Button
					@click="stopScanner"
					v-else
					variant="outline"
					class="flex-1"
					icon-left="square"
				>
					Stop Scanner
				</Button>
			</div>

			<!-- Manual Entry -->
			<div class="mt-3 pt-3 border-t border-gray-200 dark:border-gray-600">
				<div class="flex gap-2">
					<TextInput
						v-model="manualTicketId"
						placeholder="Enter ticket ID manually"
						class="flex-1"
						:disabled="isProcessingTicket"
					/>
					<Button
						@click="handleManualEntry"
						:loading="isProcessingTicket"
						:disabled="!manualTicketId.trim()"
					>
						Check
					</Button>
				</div>
			</div>
		</div>
	</div>
</template>

<script setup>
import { Button, Spinner, TextInput, toast } from "frappe-ui";
import { Html5QrcodeScanner } from "html5-qrcode";
import { onUnmounted, ref } from "vue";
import LucideQrCode from "~icons/lucide/qr-code";
import { useTicketValidation } from "../composables/useTicketValidation.js";

const { validateTicket, isProcessingTicket } = useTicketValidation();

const qrScanner = ref(null);
const scannerActive = ref(false);
const manualTicketId = ref("");
const lastScannedTicketId = ref(null);
const scanTimeout = ref(null);

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
	// Extract ticket ID from QR code
	const ticketId = extractTicketId(decodedText);
	if (!ticketId) {
		toast.error("Invalid QR code format");
		return;
	}

	// Prevent duplicate scans of the same ticket within 2 seconds
	if (lastScannedTicketId.value === ticketId) {
		return;
	}

	if (scanTimeout.value) {
		clearTimeout(scanTimeout.value);
	}
	lastScannedTicketId.value = ticketId;
	validateTicket(ticketId);

	scanTimeout.value = setTimeout(() => {
		lastScannedTicketId.value = null;
	}, 2000);
};

const onScanFailure = (error) => {
	console.warn("QR Scanner Error:", error);
};

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

const handleManualEntry = () => {
	const ticketId = manualTicketId.value.trim();
	if (!ticketId) return;

	validateTicket(ticketId);
	manualTicketId.value = "";
};

onUnmounted(() => {
	if (qrScanner.value) {
		qrScanner.value.clear();
		qrScanner.value = null;
		scannerActive.value = false;
	}

	if (scanTimeout.value) {
		clearTimeout(scanTimeout.value);
		scanTimeout.value = null;
	}
});

defineExpose({
	startScanner,
	stopScanner,
});
</script>

<style scoped>
#qr-reader {
	width: 100%;
}

:global(#qr-reader img[alt="Info icon"]) {
	display: none !important;
}

:global(#qr-reader img[alt="Camera based scan"]) {
	display: none !important;
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
