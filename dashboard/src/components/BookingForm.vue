<!-- BookingForm.vue -->
<template>
	<div>
		<EventDetailsHeader :event-details="eventDetails" />

		<form @submit.prevent="submit">
			<div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
				<!-- Left Side: Form Inputs -->
				<div class="lg:col-span-2">
					<AttendeeFormControl
						v-for="(attendee, index) in attendees"
						:key="attendee.id"
						:attendee="attendee"
						:index="index"
						:available-ticket-types="availableTicketTypes"
						:available-add-ons="availableAddOns"
						:show-remove="attendees.length > 1"
						@remove="removeAttendee(index)"
					/>

					<!-- Add Attendee Button -->
					<div class="text-center mt-6">
						<Button
							variant="outline"
							size="lg"
							@click="addAttendee"
							class="w-full max-w-md border-dashed border-2 border-outline-gray-2 hover:border-outline-gray-3 text-ink-gray-7 hover:text-ink-gray-8 py-4"
						>
							+ Add Another Attendee
						</Button>
					</div>
				</div>

				<!-- Right Side: Summary and Submit -->
				<div class="lg:col-span-1">
					<div class="sticky top-4 w-full">
						<BookingSummary
							:summary="summary"
							:net-amount="netAmount"
							:tax-amount="taxAmount"
							:tax-percentage="taxPercentage"
							:should-apply-gst="shouldApplyGST"
							:total="finalTotal"
							:total-currency="totalCurrency"
						/>
						<div class="w-full">
							<Button
								variant="solid"
								size="lg"
								class="w-full mt-6"
								type="submit"
								:loading="processBooking.loading"
							>
								{{
									processBooking.loading
										? "Processing..."
										: finalTotal > 0
										? "Pay & Book"
										: "Book Tickets"
								}}
							</Button>
						</div>
					</div>
				</div>
			</div>
		</form>
	</div>
</template>

<script setup>
import { computed, watch } from "vue";
import AttendeeFormControl from "./AttendeeFormControl.vue";
import BookingSummary from "./BookingSummary.vue";
import EventDetailsHeader from "./EventDetailsHeader.vue";
import { createResource } from "frappe-ui";
import { useBookingFormStorage } from "../composables/useBookingFormStorage.js";
import { useRouter } from "vue-router";
import { userResource } from "../data/user.js";

const router = useRouter();

const props = defineProps({
	availableAddOns: {
		type: Array,
		default: () => [],
	},
	availableTicketTypes: {
		type: Array,
		default: () => [],
	},
	gstSettings: {
		type: Object,
		default: () => ({
			apply_gst_on_bookings: false,
			gst_percentage: 18,
		}),
	},
	eventDetails: {
		type: Object,
		default: () => ({}),
	},
});

// --- STATE ---
// Use the booking form storage composable
const { attendees, attendeeIdCounter } = useBookingFormStorage();

// Ensure user data is loaded
if (!userResource.data) {
	userResource.fetch();
}

// --- HELPERS / DERIVED STATE ---
const addOnsMap = computed(() =>
	Object.fromEntries(props.availableAddOns.map((a) => [a.name, a]))
);
const ticketTypesMap = computed(() =>
	Object.fromEntries(props.availableTicketTypes.map((t) => [t.name, t]))
);
const eventId = computed(() => props.availableTicketTypes[0]?.event || null);

// --- METHODS ---
const createNewAttendee = () => {
	attendeeIdCounter.value++;
	const newAttendee = {
		id: attendeeIdCounter.value,
		full_name: "",
		email: "",
		// Auto-select ticket type if there's only one available
		ticket_type:
			props.availableTicketTypes.length === 1
				? props.availableTicketTypes[0]?.name
				: props.availableTicketTypes[0]?.name || "",
		add_ons: {},
	};
	for (const addOn of props.availableAddOns) {
		newAttendee.add_ons[addOn.name] = {
			selected: false,
			option: addOn.options ? addOn.options[0] || null : null,
		};
	}
	return newAttendee;
};

const addAttendee = () => {
	attendees.value.push(createNewAttendee());
};

const removeAttendee = (index) => {
	attendees.value.splice(index, 1);
};

// --- COMPUTED PROPERTIES FOR SUMMARY ---
const summary = computed(() => {
	const summaryData = { tickets: {}, add_ons: {} };

	for (const attendee of attendees.value) {
		const ticketType = attendee.ticket_type;
		if (ticketType && ticketTypesMap.value[ticketType]) {
			const ticketInfo = ticketTypesMap.value[ticketType];
			if (!summaryData.tickets[ticketType]) {
				summaryData.tickets[ticketType] = {
					count: 0,
					amount: 0,
					price: ticketInfo.price,
					title: ticketInfo.title,
					currency: ticketInfo.currency,
				};
			}
			summaryData.tickets[ticketType].count++;
			summaryData.tickets[ticketType].amount += ticketInfo.price;
		}

		for (const addOnName in attendee.add_ons) {
			if (attendee.add_ons[addOnName].selected) {
				const addOnInfo = addOnsMap.value[addOnName];
				if (!summaryData.add_ons[addOnName]) {
					summaryData.add_ons[addOnName] = {
						count: 0,
						amount: 0,
						price: addOnInfo.price,
						title: addOnInfo.title,
						currency: addOnInfo.currency,
					};
				}
				summaryData.add_ons[addOnName].count++;
				summaryData.add_ons[addOnName].amount += addOnInfo.price;
			}
		}
	}
	return summaryData;
});

const total = computed(() => {
	let currentTotal = 0;
	for (const key in summary.value.tickets) {
		currentTotal += summary.value.tickets[key].amount;
	}
	for (const key in summary.value.add_ons) {
		currentTotal += summary.value.add_ons[key].amount;
	}
	return currentTotal;
});

// Net amount (before tax)
const netAmount = computed(() => total.value);

// Tax calculations
const shouldApplyGST = computed(() => {
	return props.gstSettings?.apply_gst_on_bookings && totalCurrency.value === "INR";
});

const taxPercentage = computed(() => {
	return shouldApplyGST.value ? props.gstSettings?.gst_percentage || 18 : 0;
});

const taxAmount = computed(() => {
	return shouldApplyGST.value ? (netAmount.value * taxPercentage.value) / 100 : 0;
});

const finalTotal = computed(() => {
	return netAmount.value + taxAmount.value;
});

// Determine the primary currency for the total (use the first ticket type's currency)
const totalCurrency = computed(() => {
	const firstTicket = Object.values(summary.value.tickets)[0];
	return firstTicket ? firstTicket.currency : "INR";
});

// --- WATCHER ---
// Initialize with one attendee when component mounts (only if no data in storage)
watch(
	() => props.availableTicketTypes,
	() => {
		if (attendees.value.length === 0 && props.availableTicketTypes.length > 0) {
			const newAttendee = createNewAttendee();

			// Pre-populate with current user's information if available
			if (userResource.data) {
				newAttendee.full_name = userResource.data.full_name || "";
				newAttendee.email = userResource.data.email || "";
			}

			attendees.value.push(newAttendee);
		}
	},
	{ immediate: true }
);

// Ensure existing attendees have proper add-on structure when availableAddOns changes
watch(
	() => props.availableAddOns,
	(newAddOns) => {
		if (newAddOns && newAddOns.length > 0) {
			for (const attendee of attendees.value) {
				if (!attendee.add_ons) {
					attendee.add_ons = {};
				}
				// Ensure all available add-ons are represented in the attendee's add_ons
				for (const addOn of newAddOns) {
					if (!attendee.add_ons[addOn.name]) {
						attendee.add_ons[addOn.name] = {
							selected: false,
							option: addOn.options ? addOn.options[0] || null : null,
						};
					}
				}
			}
		}
	},
	{ immediate: true, deep: true }
);

// Auto-select ticket type if there's only one available
watch(
	() => props.availableTicketTypes,
	(newTicketTypes) => {
		if (newTicketTypes && newTicketTypes.length === 1) {
			// Auto-select the only ticket type for all attendees
			for (const attendee of attendees.value) {
				if (!attendee.ticket_type || attendee.ticket_type === "") {
					attendee.ticket_type = newTicketTypes[0].name;
				}
			}
		}
	},
	{ immediate: true }
);

const processBooking = createResource({
	url: "buzz.api.process_booking",
});

// --- FORM SUBMISSION ---
async function submit() {
	if (processBooking.loading) return;

	const attendees_payload = attendees.value.map((attendee) => {
		const cleanAttendee = JSON.parse(JSON.stringify(attendee));
		const selected_add_ons = [];
		for (const addOnName in cleanAttendee.add_ons) {
			const addOnState = cleanAttendee.add_ons[addOnName];
			if (addOnState.selected) {
				selected_add_ons.push({
					add_on: addOnName,
					value: addOnState.option || true,
				});
			}
		}
		cleanAttendee.add_ons = selected_add_ons;
		return cleanAttendee;
	});

	const final_payload = {
		event: eventId.value,
		attendees: attendees_payload,
	};

	processBooking.submit(final_payload, {
		onSuccess: (data) => {
			if (data.payment_link) {
				window.location.href = data.payment_link;
			} else {
				// free event
				router.replace(`/bookings/${data.booking_name}`);
			}
		},
	});
}
</script>
