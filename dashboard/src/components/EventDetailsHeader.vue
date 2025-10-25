<!-- EventDetailsHeader.vue -->
<template>
	<div v-if="eventDetails" class="mb-8">
		<!-- Banner Image -->
		<div
			v-if="eventDetails.banner_image"
			class="relative w-full h-48 md:h-64 lg:h-80 rounded-lg overflow-hidden mb-6"
		>
			<img
				:src="eventDetails.banner_image"
				:alt="eventDetails.title"
				class="w-full h-full object-cover"
			/>
			<div class="absolute inset-0 bg-black bg-opacity-30"></div>
			<div class="absolute bottom-4 left-4 text-white">
				<h1 class="text-2xl md:text-3xl lg:text-4xl font-bold mb-2">
					{{ eventDetails.title }}
				</h1>
			</div>
		</div>

		<!-- Event Info without banner -->
		<div v-else class="mb-6">
			<h1 class="text-2xl md:text-3xl lg:text-4xl font-bold text-ink-gray-9 mb-4">
				{{ eventDetails.title }}
			</h1>
		</div>

		<!-- Event Details -->
		<div class="bg-surface-gray-1 rounded-lg p-6">
			<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 gap-6 text-sm">
				<!-- Date -->
				<div v-if="eventDetails.start_date" class="flex flex-col items-start gap-3">
					<div class="flex items-center gap-2">
						<LucideCalendar class="h-4 w-4 text-ink-gray-6" />
						<p class="text-ink-gray-6 text-base">Date</p>
					</div>
					<div>
						<p class="font-medium text-ink-gray-8">
							{{ formatEventDates(eventDetails.start_date, eventDetails.end_date) }}
						</p>
					</div>
				</div>

				<!-- Time -->
				<div v-if="eventDetails.start_time" class="flex flex-col items-start gap-3">
					<div class="flex gap-2 items-center">
						<LucideClock class="h-4 w-4 text-ink-gray-6" />
						<p class="text-ink-gray-6 text-base">Time</p>
					</div>
					<div>
						<p class="font-medium text-ink-gray-8">
							{{ formatEventTime(eventDetails.start_time, eventDetails.end_time) }}
						</p>
					</div>
				</div>

				<!-- Venue -->
				<div v-if="eventDetails.venue" class="flex flex-col items-start gap-3">
					<div class="flex items-center gap-2">
						<LucideMapPin class="h-4 w-4 text-ink-gray-6" />
						<p class="text-ink-gray-6 text-base">Venue</p>
					</div>
					<div>
						<p class="font-medium text-ink-gray-8">{{ eventDetails.venue }}</p>
					</div>
				</div>
			</div>

			<!-- Description -->
			<div
				v-if="eventDetails.short_description"
				class="mt-4 pt-4 border-t border-outline-gray-2"
			>
				<p class="text-ink-gray-7 leading-relaxed">{{ eventDetails.short_description }}</p>
			</div>
		</div>
	</div>
</template>

<script setup>
import LucideCalendar from "~icons/lucide/calendar";
import LucideClock from "~icons/lucide/clock";
import LucideMapPin from "~icons/lucide/map-pin";
import { dayjsLocal } from "frappe-ui/src/utils/dayjs";

const props = defineProps({
	eventDetails: {
		type: Object,
		default: () => ({}),
	},
});

// --- UTILITY FUNCTIONS ---
const formatEventDates = (startDate, endDate) => {
	if (!startDate) return "";

	const start = dayjsLocal(startDate);
	const startFormatted = start.format("ddd, MMM D, YYYY");

	if (!endDate || startDate === endDate) {
		return startFormatted;
	}

	const end = dayjsLocal(endDate);
	const endFormatted = end.format("ddd, MMM D, YYYY");

	return `${startFormatted} - ${endFormatted}`;
};

const formatEventTime = (startTime, endTime) => {
	if (!startTime) return "";

	// Create a date object for today with the given time
	const startDateTime = dayjsLocal()
		.hour(Number.parseInt(startTime.split(":")[0]))
		.minute(Number.parseInt(startTime.split(":")[1]));
	const startFormatted = startDateTime.format("h:mm A");

	if (!endTime) {
		return startFormatted;
	}

	const endDateTime = dayjsLocal()
		.hour(Number.parseInt(endTime.split(":")[0]))
		.minute(Number.parseInt(endTime.split(":")[1]));
	const endFormatted = endDateTime.format("h:mm A");

	return `${startFormatted} - ${endFormatted}`;
};
</script>
