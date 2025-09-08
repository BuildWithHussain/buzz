<template>
	<div class="p-6 bg-gray-50 min-h-screen">
		<!-- Header Section -->
		<div class="mb-6 bg-white rounded-lg p-6 shadow-sm">
			<h1 class="text-2xl font-bold text-gray-900 mb-4">Schedule Gantt Chart POC</h1>

			<!-- Date Selector -->
			<div class="flex items-center space-x-4 mb-4">
				<label class="font-medium text-gray-700">Day/Date:</label>
				<FormControl type="date" v-model="selectedDate" class="w-48" />
				<span class="text-sm text-gray-500">
					{{ formatDate(selectedDate) }}
				</span>
			</div>

			<!-- Time Range -->
			<div class="flex items-center space-x-4 mb-4">
				<div class="flex items-center space-x-2">
					<label class="font-medium text-gray-700">Start time:</label>
					<span class="bg-blue-50 px-3 py-1 rounded text-blue-700 font-medium">
						{{ startTime }}
					</span>
				</div>
				<div class="flex items-center space-x-2">
					<label class="font-medium text-gray-700">End Time:</label>
					<span class="bg-blue-50 px-3 py-1 rounded text-blue-700 font-medium">
						{{ endTime }}
					</span>
				</div>
				<div class="flex items-center space-x-2">
					<label class="font-medium text-gray-700">Time Interval:</label>
					<FormControl
						type="select"
						:options="intervalOptions"
						v-model="selectedInterval"
						class="w-32"
					/>
				</div>
			</div>

			<!-- Action Buttons -->
			<div class="flex justify-between items-center">
				<div class="flex space-x-3">
					<Button
						variant="solid"
						@click="addTalk"
						class="bg-green-500 hover:bg-green-600"
					>
						Add Talk
					</Button>
					<Button
						variant="solid"
						@click="addBreak"
						class="bg-green-500 hover:bg-green-600"
					>
						Add Break
					</Button>
				</div>

				<!-- Storage Controls -->
				<div class="flex items-center space-x-3">
					<span class="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">
						💾 Auto-saved to local storage
					</span>
					<Button
						variant="outline"
						@click="resetToDefaults"
						class="text-red-600 hover:text-red-700 border-red-200 hover:border-red-300"
					>
						Reset to Defaults
					</Button>
				</div>
			</div>
		</div>

		<!-- Gantt Chart Container -->
		<div class="bg-white rounded-lg shadow-sm overflow-hidden max-w-4xl mx-auto">
			<div class="overflow-x-auto">
				<!-- Track Headers (Top) -->
				<div class="border-b border-gray-200 bg-gray-50">
					<div class="flex min-w-max">
						<!-- Time Column Header -->
						<div class="w-20 p-4 border-r border-gray-200 bg-gray-100 flex-shrink-0">
							<div class="text-sm font-medium text-gray-700">Time</div>
						</div>

						<!-- Track Headers -->
						<div
							v-for="(track, trackIndex) in tracks"
							:key="trackIndex"
							class="w-48 p-4 border-r border-gray-200 text-center bg-gray-50 flex-shrink-0"
						>
							<div class="text-sm font-medium text-blue-600">
								{{ track.name }}
							</div>
						</div>
					</div>
				</div>

				<!-- Time Slots and Content -->
				<div class="divide-y divide-gray-200">
					<div
						v-for="(slot, slotIndex) in timeSlots"
						:key="slotIndex"
						class="flex relative min-w-max"
						:class="{
							'border-b-2 border-blue-200':
								slotIndex > 0 &&
								slotIndex % Math.max(1, 60 / selectedInterval) === 0,
						}"
						style="height: 40px"
					>
						<!-- Time Label -->
						<div
							class="w-20 p-2 border-r border-gray-200 bg-gray-50 flex items-center justify-center flex-shrink-0"
						>
							<div class="text-xs font-medium text-blue-600">
								{{ formatTime(slot) }}
							</div>
						</div>

						<!-- Track Columns -->
						<div
							v-for="(track, trackIndex) in tracks"
							:key="trackIndex"
							class="w-48 relative border-r border-gray-100 flex-shrink-0"
							@drop="onDrop($event, trackIndex, slot)"
							@dragover="onDragOver"
							@dragenter="onDragEnter"
						>
							<!-- Schedule Items for this time slot and track -->
							<Popover
								v-for="item in getItemsForSlotAndTrack(slot, track)"
								:key="item.id"
								:show="openPopoverId === item.id"
								placement="right"
								:options="{ hideArrow: false }"
							>
								<template #target="{ togglePopover }">
									<div
										:style="getVerticalItemStyle(item, slotIndex)"
										:class="getItemClass(item)"
										class="absolute left-1 right-1 rounded-md border-2 flex items-center justify-center cursor-pointer z-10 shadow-sm hover:shadow-md transition-shadow"
										draggable="true"
										@dragstart="onDragStart($event, item, trackIndex)"
										@click="
											() => {
												openPopoverId =
													openPopoverId === item.id ? null : item.id;
											}
										"
									>
										<div class="text-center px-1 w-full overflow-hidden">
											<div class="font-medium text-xs truncate">
												{{ item.title }}
											</div>
											<div
												v-if="item.type === 'talk' && item.duration >= 30"
												class="text-xs opacity-75 truncate"
											>
												{{ item.speaker }}
											</div>
											<div
												v-if="item.duration >= 20"
												class="text-xs font-medium opacity-90"
											>
												{{ formatTime(item.startTime) }} -
												{{ getEndTime(item) }}
											</div>
										</div>

										<!-- Resize Handles -->
										<div
											class="absolute top-0 left-0 right-0 h-1 cursor-ns-resize hover:bg-black hover:bg-opacity-30"
											@mousedown="startResize($event, item, 'top')"
										></div>
										<div
											class="absolute bottom-0 left-0 right-0 h-1 cursor-ns-resize hover:bg-black hover:bg-opacity-30"
											@mousedown="startResize($event, item, 'bottom')"
										></div>
									</div>
								</template>

								<template #body>
									<div
										class="p-4 w-80 bg-white rounded-lg shadow-lg border border-gray-200"
									>
										<h3 class="text-lg font-semibold mb-4 text-gray-900">
											Edit Item
										</h3>
										<div class="space-y-4">
											<div>
												<label
													class="block text-sm font-medium text-gray-700 mb-1"
													>Title</label
												>
												<FormControl
													type="text"
													:modelValue="item.title"
													@update:modelValue="
														updateItemProperty(
															item.id,
															'title',
															$event
														)
													"
												/>
											</div>
											<div>
												<label
													class="block text-sm font-medium text-gray-700 mb-1"
													>Type</label
												>
												<FormControl
													type="select"
													:options="[
														{ label: 'Talk', value: 'talk' },
														{ label: 'Break', value: 'break' },
													]"
													:modelValue="item.type"
													@update:modelValue="
														updateItemProperty(item.id, 'type', $event)
													"
												/>
											</div>
											<div v-if="item.type === 'talk'">
												<label
													class="block text-sm font-medium text-gray-700 mb-1"
													>Speaker</label
												>
												<FormControl
													type="text"
													:modelValue="item.speaker"
													@update:modelValue="
														updateItemProperty(
															item.id,
															'speaker',
															$event
														)
													"
												/>
											</div>
											<div class="grid grid-cols-2 gap-3">
												<div>
													<label
														class="block text-sm font-medium text-gray-700 mb-1"
														>Start Time</label
													>
													<FormControl
														type="time"
														:modelValue="
															timeToHtmlFormat(item.startTime)
														"
														@update:modelValue="
															updateItemStartTime(item.id, $event)
														"
													/>
												</div>
												<div>
													<label
														class="block text-sm font-medium text-gray-700 mb-1"
														>End Time</label
													>
													<FormControl
														type="time"
														:modelValue="getItemEndTimeHtml(item)"
														@update:modelValue="
															updateItemEndTime(item.id, $event)
														"
													/>
												</div>
											</div>
											<div>
												<label
													class="block text-sm font-medium text-gray-700 mb-1"
													>Duration</label
												>
												<div
													class="bg-gray-50 px-3 py-2 rounded text-sm text-gray-600"
												>
													{{ getItemDurationDisplay(item) }}
												</div>
											</div>
											<div class="flex space-x-2 pt-2">
												<Button
													variant="solid"
													theme="red"
													@click="
														deleteItemById(item.id);
														openPopoverId = null;
													"
													>Delete</Button
												>
												<Button
													variant="outline"
													@click="openPopoverId = null"
													>Close</Button
												>
											</div>
										</div>
									</div>
								</template>
							</Popover>
						</div>
					</div>
				</div>
			</div>
			<!-- End overflow-x-auto -->
		</div>
		<!-- End Gantt Chart Container -->
	</div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from "vue";
import { FormControl, Button, Popover } from "frappe-ui";
import { useStorage } from "@vueuse/core";

// Reactive data with localStorage persistence
const selectedDate = useStorage("gantt-selected-date", "2024-09-12");
const startTime = useStorage("gantt-start-time", "9AM");
const endTime = useStorage("gantt-end-time", "7PM");
const draggedItem = ref(null);
const draggedFromTrack = ref(null);
const resizingItem = ref(null);
const resizeDirection = ref(null);
const resizeStartX = ref(0);
const resizeStartWidth = ref(0);
const resizeStartLeft = ref(0);
const isResizing = ref(false);
const openPopoverId = ref(null);

// Time interval control
const selectedInterval = useStorage("gantt-time-interval", 5);
const intervalOptions = [
	{ label: "5 minutes", value: 5 },
	{ label: "10 minutes", value: 10 },
	{ label: "15 minutes", value: 15 },
	{ label: "30 minutes", value: 30 },
];

// Default tracks data
const defaultTracks = [
	{
		name: "Track 1",
		items: [
			{
				id: 1,
				title: "Keynote",
				type: "talk",
				speaker: "John Doe",
				startTime: "9:05",
				duration: 60, // minutes
				color: "#fef3c7", // yellow
			},
			{
				id: 2,
				title: "Tea Break",
				type: "break",
				startTime: "10:05",
				duration: 15,
				color: "#f3e8ff", // purple
			},
			{
				id: 3,
				title: "Frappe Cloud",
				type: "talk",
				speaker: "Jane Smith",
				startTime: "10:20",
				duration: 30,
				color: "#fef3c7", // yellow
			},
		],
	},
	{
		name: "Track 2",
		items: [
			{
				id: 4,
				title: "Frappe v16",
				type: "talk",
				speaker: "Mike Johnson",
				startTime: "9:10",
				duration: 45,
				color: "#fef3c7", // yellow
			},
			{
				id: 5,
				title: "Tea Break",
				type: "break",
				startTime: "10:05",
				duration: 15,
				color: "#f3e8ff", // purple
			},
			{
				id: 6,
				title: "ERPNext",
				type: "talk",
				speaker: "Sarah Wilson",
				startTime: "10:20",
				duration: 30,
				color: "#fef3c7", // yellow
			},
		],
	},
];

// Persistent tracks data
const tracks = useStorage("gantt-tracks-data", defaultTracks);
const nextItemId = useStorage("gantt-next-item-id", 7);

// Generate time slots (9:00 to 9:40 in 5-minute intervals as shown in screenshot)
// Generate time slots based on selected interval
const timeSlots = computed(() => {
	const slots = [];
	const interval = selectedInterval.value;
	for (let hour = 9; hour <= 19; hour++) {
		for (let minute = 0; minute < 60; minute += interval) {
			if (hour === 19 && minute > 0) break; // Stop at 7:00 PM
			const time = `${hour}:${minute.toString().padStart(2, "0")}`;
			slots.push(time);
		}
	}
	return slots;
});

// Helper functions
const formatDate = (dateStr) => {
	const date = new Date(dateStr);
	return date.toLocaleDateString("en-US", {
		weekday: "long",
		year: "numeric",
		month: "long",
		day: "numeric",
	});
};

const timeToMinutes = (timeStr) => {
	const [hours, minutes] = timeStr.split(":").map(Number);
	return (hours - 9) * 60 + minutes; // 9 AM is our baseline
};

const minutesToTime = (minutes) => {
	const totalMinutes = minutes + 9 * 60; // Add 9 AM baseline
	const hours = Math.floor(totalMinutes / 60);
	const mins = totalMinutes % 60;
	return `${hours}:${mins.toString().padStart(2, "0")}`;
};

const formatTime = (timeStr) => {
	const [hours, minutes] = timeStr.split(":").map(Number);
	const period = hours >= 12 ? "PM" : "AM";
	const displayHours = hours > 12 ? hours - 12 : hours === 0 ? 12 : hours;
	const displayMinutes = minutes === 0 ? "" : `:${minutes.toString().padStart(2, "0")}`;
	return `${displayHours}${displayMinutes}${period}`;
};

const getEndTime = (item) => {
	const startMinutes = timeToMinutes(item.startTime);
	const endMinutes = startMinutes + item.duration;
	const endTimeStr = minutesToTime(endMinutes);
	return formatTime(endTimeStr);
};

const getItemStyle = (item) => {
	const startMinutes = timeToMinutes(item.startTime);
	const totalMinutes = 10 * 60; // 10 hours total (9 AM to 7 PM)
	const left = (startMinutes / totalMinutes) * 100;
	const width = (item.duration / totalMinutes) * 100;

	return {
		left: `${left}%`,
		width: `${width}%`,
	};
};

const getVerticalItemStyle = (item, slotIndex) => {
	const interval = selectedInterval.value;
	const itemHeightInSlots = Math.ceil(item.duration / interval); // How many interval slots the item spans
	const heightInPixels = itemHeightInSlots * 40; // 40px per slot

	// Add extra z-index during resize to keep item visible
	const zIndex = resizingItem.value && resizingItem.value.id === item.id ? 50 : 10;

	return {
		height: `${heightInPixels}px`,
		top: "2px",
		zIndex: zIndex,
		transition: isResizing.value ? "none" : "height 0.1s ease", // Disable transitions during resize
	};
};

const getItemsForSlotAndTrack = (slot, track) => {
	const slotMinutes = timeToMinutes(slot);
	const interval = selectedInterval.value;

	return track.items.filter((item) => {
		const itemStartMinutes = timeToMinutes(item.startTime);

		// Show the item in the slot where it starts, but be more tolerant during resize
		if (resizingItem.value && resizingItem.value.id === item.id) {
			// During resize, use interval-based tolerance to prevent flickering
			return Math.abs(slotMinutes - itemStartMinutes) < interval;
		}

		// Find the slot that should contain this item's start time
		// Calculate which slot the item's start time falls into
		const itemSlotIndex = Math.floor(itemStartMinutes / interval);
		const currentSlotIndex = Math.floor(slotMinutes / interval);

		// Only show the item in the slot it belongs to
		return itemSlotIndex === currentSlotIndex;
	});
};

const getItemClass = (item) => {
	const baseClass =
		item.type === "talk"
			? "border-yellow-300 text-yellow-800"
			: "border-purple-300 text-purple-800";

	const bgClass =
		item.type === "talk"
			? "bg-yellow-100 hover:bg-yellow-200"
			: "bg-purple-100 hover:bg-purple-200";

	// Add special styling during resize
	const resizeClass =
		resizingItem.value && resizingItem.value.id === item.id
			? "ring-2 ring-blue-400 shadow-lg"
			: "";

	return `${baseClass} ${bgClass} ${resizeClass}`;
};

// Drag and drop handlers
const onDragStart = (event, item, trackIndex) => {
	draggedItem.value = item;
	draggedFromTrack.value = trackIndex;
	event.dataTransfer.effectAllowed = "move";
};

const onDragOver = (event) => {
	event.preventDefault();
	event.dataTransfer.dropEffect = "move";
};

const onDragEnter = (event) => {
	event.preventDefault();
};

const onDrop = (event, trackIndex, timeSlot) => {
	event.preventDefault();

	if (!draggedItem.value) return;

	// Remove from old track
	if (draggedFromTrack.value !== null) {
		const oldTrack = tracks.value[draggedFromTrack.value];
		const itemIndex = oldTrack.items.findIndex((item) => item.id === draggedItem.value.id);
		if (itemIndex > -1) {
			oldTrack.items.splice(itemIndex, 1);
		}
	}

	// Add to new track with new time
	const newItem = { ...draggedItem.value, startTime: timeSlot };
	tracks.value[trackIndex].items.push(newItem);

	// Reset drag state
	draggedItem.value = null;
	draggedFromTrack.value = null;
};

// Resize handlers
const startResize = (event, item, direction) => {
	event.stopPropagation();
	event.preventDefault();

	isResizing.value = true;
	resizingItem.value = item;
	resizeDirection.value = direction;
	resizeStartX.value = event.clientY; // Use clientY for vertical resize
	resizeStartWidth.value = item.duration;
	resizeStartLeft.value = timeToMinutes(item.startTime);

	document.addEventListener("mousemove", handleResize);
	document.addEventListener("mouseup", endResize);
};

const handleResize = (event) => {
	if (!resizingItem.value) return;

	const interval = selectedInterval.value;
	const deltaY = event.clientY - resizeStartX.value;
	const pixelsPerMinute = 40 / interval; // 40px per interval slot
	const deltaMinutes = Math.round(deltaY / pixelsPerMinute) * interval; // Snap to interval boundaries

	if (resizeDirection.value === "bottom") {
		// Resize from bottom - change duration
		const newDuration = Math.max(interval, resizeStartWidth.value + deltaMinutes);
		// Round to nearest interval
		resizingItem.value.duration = Math.round(newDuration / interval) * interval;
	} else if (resizeDirection.value === "top") {
		// Resize from top - change start time and duration
		const newStartMinutes = Math.max(0, resizeStartLeft.value + deltaMinutes);
		const newDuration = Math.max(interval, resizeStartWidth.value - deltaMinutes);

		// Round to nearest interval
		const roundedStartMinutes = Math.round(newStartMinutes / interval) * interval;
		const roundedDuration = Math.round(newDuration / interval) * interval;

		resizingItem.value.startTime = minutesToTime(roundedStartMinutes);
		resizingItem.value.duration = roundedDuration;
	}
};

const endResize = () => {
	isResizing.value = false;
	resizingItem.value = null;
	resizeDirection.value = null;
	document.removeEventListener("mousemove", handleResize);
	document.removeEventListener("mouseup", endResize);
};

// Time conversion utilities
const timeToHtmlFormat = (timeStr) => {
	// Convert "9:05" to "09:05" for HTML time input
	const [hours, minutes] = timeStr.split(":").map(Number);
	return `${hours.toString().padStart(2, "0")}:${minutes.toString().padStart(2, "0")}`;
};

const htmlFormatToTime = (htmlTime) => {
	// Convert "09:05" to "9:05" for our internal format
	const [hours, minutes] = htmlTime.split(":").map(Number);
	return `${hours}:${minutes.toString().padStart(2, "0")}`;
};

const calculateDurationFromTimes = (startTime, endTime) => {
	const startMinutes = timeToMinutes(startTime);
	const endMinutes = timeToMinutes(endTime);
	return Math.max(0, endMinutes - startMinutes);
};

// Popover management
const togglePopover = (itemId) => {
	openPopoverId.value = openPopoverId.value === itemId ? null : itemId;
};

// Helper functions for popover editing
const updateItemProperty = (itemId, property, value) => {
	for (const track of tracks.value) {
		const item = track.items.find((item) => item.id === itemId);
		if (item) {
			item[property] = value;
			break;
		}
	}
};

const updateItemStartTime = (itemId, htmlTime) => {
	for (const track of tracks.value) {
		const item = track.items.find((item) => item.id === itemId);
		if (item && htmlTime) {
			item.startTime = htmlFormatToTime(htmlTime);
			break;
		}
	}
};

const updateItemEndTime = (itemId, htmlTime) => {
	for (const track of tracks.value) {
		const item = track.items.find((item) => item.id === itemId);
		if (item && htmlTime) {
			const endTime = htmlFormatToTime(htmlTime);
			const newDuration = calculateDurationFromTimes(item.startTime, endTime);
			item.duration = Math.max(selectedInterval.value, newDuration); // Minimum = selected interval
			break;
		}
	}
};

const getItemEndTimeHtml = (item) => {
	const startMinutes = timeToMinutes(item.startTime);
	const endMinutes = startMinutes + item.duration;
	const endTime = minutesToTime(endMinutes);
	return timeToHtmlFormat(endTime);
};

const getItemDurationDisplay = (item) => {
	const hours = Math.floor(item.duration / 60);
	const minutes = item.duration % 60;
	if (hours > 0) {
		return minutes > 0 ? `${hours}h ${minutes}m` : `${hours}h`;
	}
	return `${minutes}m`;
};

const deleteItemById = (itemId) => {
	for (const track of tracks.value) {
		const itemIndex = track.items.findIndex((item) => item.id === itemId);
		if (itemIndex !== -1) {
			track.items.splice(itemIndex, 1);
			break;
		}
	}
};

// Time slot helpers

const addTalk = () => {
	const newTalk = {
		id: nextItemId.value++,
		title: "New Talk",
		type: "talk",
		speaker: "Speaker Name",
		startTime: "10:00",
		duration: 30,
		color: "#fef3c7",
	};

	tracks.value[0].items.push(newTalk);
};

const addBreak = () => {
	const newBreak = {
		id: nextItemId.value++,
		title: "New Break",
		type: "break",
		startTime: "11:00",
		duration: 15,
		color: "#f3e8ff",
	};

	tracks.value[0].items.push(newBreak);
};

const resetToDefaults = () => {
	if (
		confirm(
			"Are you sure you want to reset to default data? This will clear all your changes."
		)
	) {
		tracks.value = JSON.parse(JSON.stringify(defaultTracks));
		nextItemId.value = 7;
		selectedDate.value = "2024-09-12";
		startTime.value = "9AM";
		endTime.value = "7PM";
		openPopoverId.value = null;
	}
};

onMounted(() => {
	// Clean up event listeners if component unmounts
	return () => {
		document.removeEventListener("mousemove", handleResize);
		document.removeEventListener("mouseup", endResize);
	};
});
</script>

<style scoped>
/* Add any additional custom styles here */
.cursor-ew-resize {
	cursor: ew-resize;
}

.cursor-ns-resize {
	cursor: ns-resize;
}

.cursor-move {
	cursor: move;
}
</style>
