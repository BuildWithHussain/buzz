<template>
	<Dialog v-model="showTicketModal">
		<template #body-title>
			<h3 class="text-lg font-semibold text-gray-900 dark:text-white">
				{{ validationResult ? "Valid Ticket" : "Invalid Ticket" }}
			</h3>
		</template>

		<template #body-content>
			<!-- Success State -->
			<div v-if="validationResult">
				<div class="text-center mb-6">
					<div
						class="w-16 h-16 bg-green-100 dark:bg-green-900/30 rounded-full flex items-center justify-center mx-auto mb-4"
					>
						<LucideCheckCircle class="w-8 h-8 text-green-600 dark:text-green-400" />
					</div>
					<h4 class="text-lg font-semibold text-gray-900 dark:text-white">
						Valid Ticket
					</h4>
					<p class="text-gray-600 dark:text-gray-400">Ready for check-in</p>
				</div>

				<div class="space-y-4 mb-6">
					<div class="grid grid-cols-2 gap-4">
						<div>
							<label
								class="block text-sm font-medium text-gray-700 dark:text-gray-300"
								>Attendee</label
							>
							<p class="text-gray-900 dark:text-white">
								{{ validationResult?.ticket?.attendee_name }}
							</p>
						</div>
						<div>
							<label
								class="block text-sm font-medium text-gray-700 dark:text-gray-300"
								>Email</label
							>
							<p class="text-gray-900 dark:text-white text-sm">
								{{ validationResult?.ticket?.attendee_email }}
							</p>
						</div>
						<div>
							<label
								class="block text-sm font-medium text-gray-700 dark:text-gray-300"
								>Ticket Type</label
							>
							<p class="text-gray-900 dark:text-white">
								{{ validationResult?.ticket?.ticket_type }}
							</p>
						</div>
						<div>
							<label
								class="block text-sm font-medium text-gray-700 dark:text-gray-300"
								>Ticket ID</label
							>
							<p class="text-gray-900 dark:text-white font-mono text-sm">
								{{ validationResult?.ticket?.id }}
							</p>
						</div>
					</div>

					<!-- Add-ons -->
					<div
						v-if="validationResult?.ticket?.add_ons?.length"
						class="border-t border-gray-200 dark:border-gray-600 pt-4"
					>
						<label
							class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
							>Add-ons</label
						>
						<div class="space-y-2">
							<div
								v-for="addon in validationResult?.ticket?.add_ons"
								:key="addon.add_on"
								class="flex justify-between text-sm"
							>
								<span class="text-gray-900 dark:text-white">{{
									addon.add_on_title || addon.add_on
								}}</span>
								<span class="text-gray-600 dark:text-gray-400">{{
									addon.value
								}}</span>
							</div>
						</div>
					</div>
				</div>
			</div>

			<!-- Error State -->
			<div v-else>
				<div class="text-center mb-6">
					<div
						class="w-16 h-16 bg-red-100 dark:bg-red-900/30 rounded-full flex items-center justify-center mx-auto mb-4"
					>
						<LucideXCircle class="w-8 h-8 text-red-600 dark:text-red-400" />
					</div>
					<h4 class="text-lg font-semibold text-gray-900 dark:text-white">
						{{ validationResult?.error || "Invalid Ticket" }}
					</h4>
					<p class="text-gray-600 dark:text-gray-400">
						{{ validationResult?.message }}
					</p>
				</div>
			</div>
		</template>

		<template #actions>
			<div v-if="!validationResult?.ticket?.is_checked_in" class="flex gap-3 flex-col">
				<Button @click="handleCheckIn" :loading="isCheckingIn" class="w-full">
					<template #prefix>
						<LucideUserCheck class="w-4 h-4" />
					</template>
					Check In
				</Button>
				<Button @click="handleModalClose" variant="outline" class="w-full">
					Cancel
				</Button>
			</div>

			<div v-else>
				<Button @click="handleModalClose" class="w-full" variant="outline"> Close </Button>
			</div>
		</template>
	</Dialog>
</template>

<script setup>
import { Button, Dialog, dayjsLocal } from "frappe-ui";
import LucideCheckCircle from "~icons/lucide/check-circle";
import LucideUserCheck from "~icons/lucide/user-check";
import LucideXCircle from "~icons/lucide/x-circle";
import { useTicketValidation } from "../composables/useTicketValidation.js";

const props = defineProps({
	selectedEvent: {
		type: Object,
		default: null,
	},
});

const { showTicketModal, isCheckingIn, validationResult, checkInTicket, closeModal } =
	useTicketValidation();

const handleCheckIn = () => {
	checkInTicket();
};

const handleModalClose = () => {
	closeModal();
};

const formatDateTime = (datetime) => {
	if (!datetime) return "";
	return dayjsLocal(datetime).format("MMM DD, YYYY [at] h:mm A");
};
</script>
