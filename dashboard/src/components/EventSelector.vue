<template>
	<div class="mb-6 size-full">
		<!-- Header - only show when there are events -->
		<h2
			v-if="availableEvents.length > 0"
			class="text-lg font-semibold mb-4 text-gray-900 dark:text-white"
		>
			Select Event
		</h2>

		<!-- Loading State -->
		<div v-if="eventsResource.loading" class="min-h-[50vh] flex justify-center items-center">
			<div class="flex flex-col items-center gap-2">
				<Spinner class="w-6 h-6" />
				<div class="flex flex-col items-center">
					<p class="text-gray-600 dark:text-gray-400">Loading events...</p>
					<p class="text-gray-600 dark:text-gray-400">
						Please wait while we load the events...
					</p>
				</div>
			</div>
		</div>

		<!-- No Events State -->
		<div v-else-if="availableEvents.length === 0" class="text-center py-16">
			<div
				class="mx-auto w-20 h-20 mb-6 flex items-center justify-center rounded-full bg-gray-100 dark:bg-gray-800"
			>
				<LucideCalendarX class="w-10 h-10 text-gray-400 dark:text-gray-500" />
			</div>

			<div class="max-w-sm mx-auto">
				<h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-2">
					No Events Available
				</h3>
				<p class="text-gray-600 dark:text-gray-400 mb-6 leading-relaxed">
					There are currently no active events available for check-in. Events may be
					scheduled for later dates or may need to be published.
				</p>

				<Button
					@click="loadEvents"
					variant="solid"
					:loading="eventsResource.loading"
					icon-left="refresh-cw"
					class="w-full"
				>
					Refresh Events
				</Button>

				<div
					class="mt-6 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800"
				>
					<div
						class="flex flex-col items-start gap-2 text-sm text-blue-800 dark:text-blue-200"
					>
						<div class="flex items-center gap-2">
							<LucideInfo
								class="size-4 text-blue-600 dark:text-blue-400 flex-shrink-0"
							/>
							<p class="font-medium">Need help?</p>
						</div>
						<p class="leading-4 text-left">
							Contact your event organizer if you're expecting to see events here, or
							check back later for upcoming events.
						</p>
					</div>
				</div>
			</div>
		</div>

		<!-- Custom Events List -->
		<div
			v-else
			class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 shadow-sm overflow-hidden"
		>
			<!-- Header -->
			<div
				class="bg-gray-50 dark:bg-gray-700/50 border-b border-gray-200 dark:border-gray-600 p-4"
			>
				<div
					class="grid grid-cols-3 gap-4 text-sm font-semibold text-gray-700 dark:text-gray-300"
				>
					<div class="col-span-1">Event</div>
					<div class="col-span-1">Starts At</div>
					<div class="col-span-1">Ends At</div>
				</div>
			</div>

			<!-- Events List -->
			<div class="divide-y divide-gray-200 dark:divide-gray-700">
				<div
					v-for="event in availableEvents"
					:key="event.name"
					@click="handleEventSelect(event)"
					class="p-4 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors duration-200 cursor-pointer"
				>
					<div class="grid grid-cols-3 gap-4 items-center">
						<!-- Event Column -->
						<div class="col-span-1">
							<div class="text-sm">
								<div class="font-semibold text-gray-900 dark:text-white text-base">
									{{ event.title }}
								</div>
							</div>
						</div>

						<!-- Start Date & Time Column -->
						<div class="col-span-1">
							<div class="text-sm">
								<div class="font-medium text-gray-900 dark:text-white text-base">
									{{ formatTimestamp(event.start_date, event.start_time) }}
								</div>
							</div>
						</div>

						<!-- End Date & Time Column -->
						<div class="col-span-1">
							<div class="text-sm">
								<div class="font-medium text-gray-900 dark:text-white text-base">
									{{ formatTimestamp(event.end_date, event.end_time) }}
								</div>
							</div>
						</div>
					</div>
				</div>
			</div>
		</div>
	</div>
</template>

<script setup>
import { Button, createListResource, dayjsLocal, Spinner } from "frappe-ui";
import { onMounted, ref } from "vue";
import LucideCalendarX from "~icons/lucide/calendar-x";
import LucideInfo from "~icons/lucide/info";

defineProps({
	selectedEvent: {
		type: Object,
		default: null,
	},
});

const emit = defineEmits(["select"]);

const availableEvents = ref([]);

const eventsResource = createListResource({
	doctype: "FE Event",
	fields: ["name", "title", "start_date", "start_time", "end_date", "end_time"],
	order_by: "start_date desc",
	filters: {
		is_published: 1,
		end_date: [">=", dayjsLocal().format("YYYY-MM-DD")],
	},
	auto: true,
	onSuccess: (data) => {
		availableEvents.value = data;
	},
});

const loadEvents = () => {
	eventsResource.fetch();
};

const formatTimestamp = (date, time) => {
	let formattedDate = "";
	let formattedTime = "";

	if (date || time) {
		const dateTimeStr = date ? `${date}${time ? "T" + time : "T00:00:00"}` : undefined;

		const parsed = dayjsLocal(dateTimeStr);

		if (parsed.isValid()) {
			formattedDate = parsed.format("MMM DD, YYYY");
			formattedTime = parsed.format("h:mm A");
		}
	}

	if (!formattedDate && !formattedTime) return "No date specified";
	if (formattedDate && !formattedTime) return formattedDate;
	if (!formattedDate && formattedTime) return formattedTime;
	return `${formattedDate} ${formattedTime}`;
};

const handleEventSelect = (event) => {
	emit("select", event);
};

onMounted(() => {
	loadEvents();
});

defineExpose({
	loadEvents,
});
</script>
