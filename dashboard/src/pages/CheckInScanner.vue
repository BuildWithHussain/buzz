<template>
	<div
		class="min-h-[75vh] border border-gray-200 dark:border-gray-700 shadow-sm mx-4 rounded-md"
	>
		<!-- Header -->
		<div class="shadow-sm border-b">
			<div class="max-w-md mx-auto px-4 py-4">
				<h1 class="text-xl font-bold text-center text-gray-900 dark:text-white">
					{{ __("Event Check-in Scanner") }}
				</h1>
			</div>
		</div>

		<!-- Access Denied Message -->
		<div
			v-if="!hasRequiredRole"
			class="size-full flex justify-center items-center p-6 text-center min-h-[50vh]"
		>
			<div class="flex flex-col items-center space-y-4">
				<div
					class="w-16 h-16 bg-red-100 dark:bg-red-900/20 rounded-full flex items-center justify-center"
				>
					<LucideShieldX class="w-8 h-8 text-red-600 dark:text-red-400" />
				</div>
				<div>
					<h4 class="text-lg font-medium text-gray-900 dark:text-white mb-2">
						{{ __("Access Denied") }}
					</h4>
					<p class="text-gray-600 dark:text-gray-400">
						{{
							__(
								"You don't have the required permissions to access the ticket scanner."
							)
						}}
					</p>
				</div>
			</div>
		</div>

		<!-- Main Content -->
		<div v-else class="size-full px-4 py-6">
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
				<QRScanner ref="qrScannerRef" />

				<!-- Last Scan Status -->
				<div
					v-if="validationResult"
					class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-4"
				>
					<h3 class="font-medium text-gray-900 dark:text-white mb-2">
						{{ __("Last Scan Result") }}
					</h3>
					<div
						class="p-3 rounded-lg bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800"
					>
						<p class="text-sm font-medium text-green-800 dark:text-green-200">
							{{ validationResult.message }}
						</p>
						<p
							v-if="validationResult.ticket"
							class="text-xs mt-1 text-green-600 dark:text-green-400"
						>
							{{ __("Ticket ID") }}: {{ validationResult.ticket.id }}
						</p>
					</div>
				</div>
			</div>
		</div>

		<!-- Ticket Details Modal -->
		<TicketDetailsModal :selected-event="selectedEvent" />
	</div>
</template>

<script setup>
import { Button } from "frappe-ui";
import { computed, onMounted, ref } from "vue";
import EventSelector from "../components/EventSelector.vue";
import QRScanner from "../components/QRScanner.vue";
import TicketDetailsModal from "../components/TicketDetailsModal.vue";
import { useTicketValidation } from "../composables/useTicketValidation.js";
import LucideShieldX from "~icons/lucide/shield-x";
import { userResource } from "../data/user.js";

const userProfile = ref({});

const hasRequiredRole = computed(() => {
	if (!userProfile.value || !userProfile.value.roles) return false;
	return userProfile.value.roles.some((role) => role.role === "Frontdesk Manager");
});

const { validationResult, clearResults } = useTicketValidation();

// State
const selectedEvent = ref(null);
const qrScannerRef = ref(null);

// Event selection
const selectEvent = (event) => {
	selectedEvent.value = event;
	clearResults();
};

const clearEventSelection = () => {
	selectedEvent.value = null;
	clearResults();
};

onMounted(() => {
	userProfile.value = { ...userResource.data };
});
</script>
