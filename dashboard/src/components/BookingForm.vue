<!-- BookingForm.vue -->
<template>
	<form @submit.prevent="submit">
		<div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
			<!-- Left Side: Form Inputs -->
			<div class="lg:col-span-2">
				<AttendeeFormControl
					v-for="(attendee, index) in attendees"
					:key="attendee.id"
					:attendee="attendee"
					:index="index"
					:available-ticket-types="filteredTicketTypes"
					:available-add-ons="filteredAddOns"
					:show-remove="attendees.length > 1"
					:is-ticket-type-read-only="props.couponInfo?.valid || false"
					@remove="removeAttendee(index)"
				/>

				<!-- Add Attendee Button -->
				<div class="text-center mt-6">
					<!-- Coupon limit warning -->
					<div
						v-if="couponLimitWarning"
						class="mb-3 p-3 bg-yellow-50 border border-yellow-200 rounded-lg text-yellow-800 text-sm"
					>
						{{ couponLimitWarning }}
					</div>

					<Button
						variant="outline"
						size="lg"
						@click="addAttendee"
						:disabled="isAddAttendeeDisabled"
						class="w-full max-w-md border-dashed border-2 border-gray-300 hover:border-gray-400 text-gray-600 hover:text-gray-700 py-4 disabled:opacity-50 disabled:cursor-not-allowed"
					>
						+ Add Another Attendee
					</Button>
				</div>
			</div>

			<!-- Right Side: Summary and Submit -->
			<div class="lg:col-span-1">
				<div class="sticky top-4">
					<BookingSummary
						:summary="summary"
						:total="total"
						:total-currency="totalCurrency"
					/>

					<!-- Coupon Code Input Section -->
					<div class="mt-4 p-4 bg-surface-gray-1 border border-gray-200 rounded-lg">
						<h3 class="text-sm font-semibold text-gray-700 mb-3">
							Have a Coupon Code?
						</h3>
						<div class="flex gap-2">
							<div class="flex-1">
								<FormControl
									type="text"
									size="sm"
									v-model="localCouponCode"
									placeholder="Coupon code"
									class="w-full font-mono"
									:disabled="isCurrentCouponApplied || props.couponValidating"
									@keyup.enter="handleCouponAction"
								/>
							</div>
							<Button
								variant="outline"
								size="sm"
								@click="handleCouponAction"
								:loading="props.couponValidating"
								:disabled="
									(!localCouponCode.trim() && !isCurrentCouponApplied) ||
									props.couponValidating
								"
							>
								{{ buttonText }}
							</Button>
						</div>
						<div
							v-if="isCurrentCouponApplied && props.couponInfo"
							class="mt-2 text-xs text-green-600"
						>
							✓ Coupon applied - {{ props.couponInfo.remaining_tickets }} tickets
							remaining
						</div>
						<div
							v-else-if="props.couponInfo && !props.couponInfo.valid"
							class="mt-2 text-xs text-red-600"
						>
							{{ props.couponInfo.error || "Invalid coupon code" }}
						</div>
					</div>

					<Button
						variant="solid"
						size="lg"
						class="w-full mt-3"
						type="submit"
						:loading="processBooking.loading"
					>
						{{ submitButtonText }}
					</Button>
				</div>
			</div>
		</div>
	</form>
</template>

<script setup>
import { computed, watch, ref } from "vue";
import { useStorage } from "@vueuse/core";
import AttendeeFormControl from "./AttendeeFormControl.vue";
import BookingSummary from "./BookingSummary.vue";
import { createResource, Button } from "frappe-ui";
import FormControl from "frappe-ui/src/components/FormControl/FormControl.vue";
import { useRouter } from "vue-router";

const router = useRouter();
// Props are passed from the parent context (e.g., your main app or page)
const props = defineProps({
	availableAddOns: {
		type: Array,
		default: () => [],
	},
	availableTicketTypes: {
		type: Array,
		default: () => [],
	},
	couponCode: {
		type: String,
		default: "",
	},
	couponInfo: {
		type: Object,
		default: null,
	},
	couponValidating: {
		type: Boolean,
		default: false,
	},
});

const emit = defineEmits(["validate-coupon"]);

// Use localStorage to persist coupon code across page refreshes
const storedCouponCode = useStorage("event-booking-coupon-code", "");

// Local coupon code state - initialize from storage or props
const localCouponCode = ref(storedCouponCode.value || props.couponCode || "");

// Watch for changes in localCouponCode and sync to storage
watch(localCouponCode, (newCode) => {
	storedCouponCode.value = newCode || "";
});

// Watch for changes in props.couponCode and update local state
watch(
	() => props.couponCode,
	(newCode) => {
		if (newCode && newCode !== localCouponCode.value) {
			localCouponCode.value = newCode;
		}
	}
);

function applyCoupon() {
	if (localCouponCode.value.trim()) {
		emit("validate-coupon", localCouponCode.value.trim());
	}
}

function removeCoupon() {
	localCouponCode.value = "";
	storedCouponCode.value = "";
	emit("validate-coupon", "");
}

function handleCouponAction() {
	if (isCurrentCouponApplied.value) {
		removeCoupon();
	} else {
		applyCoupon();
	}
}

// Computed properties for coupon UI
const isCurrentCouponApplied = computed(() => {
	return props.couponInfo?.valid && localCouponCode.value === props.couponCode;
});

const buttonText = computed(() => {
	if (props.couponValidating) return "Validating...";
	if (isCurrentCouponApplied.value) return "Remove";
	return "Apply";
});

// --- STATE ---
// Use localStorage to persist attendees data across page refreshes
const attendees = useStorage("event-booking-attendees", []);
const attendeeIdCounter = useStorage("event-booking-counter", 0);

// --- HELPERS / DERIVED STATE ---
const addOnsMap = computed(() => Object.fromEntries(filteredAddOns.value.map((a) => [a.name, a])));

const ticketTypesMap = computed(() =>
	Object.fromEntries(props.availableTicketTypes.map((t) => [t.name, t]))
);

// Filter available ticket types based on coupon
const filteredTicketTypes = computed(() => {
	if (props.couponInfo?.valid) {
		// If coupon is valid, only show the coupon's ticket type
		return props.availableTicketTypes.filter((tt) => tt.name === props.couponInfo.ticket_type);
	}
	return props.availableTicketTypes;
});

const filteredAddOns = computed(() => {
	if (props.couponInfo?.valid && props.couponInfo.free_add_ons) {
		// If coupon is valid, only show the coupon's free add-ons
		return props.couponInfo.free_add_ons;
	}
	return props.availableAddOns;
});

const eventId = computed(() => props.availableTicketTypes[0]?.event || null);

// --- METHODS ---
const createNewAttendee = () => {
	attendeeIdCounter.value++;
	const newAttendee = {
		id: attendeeIdCounter.value,
		full_name: "",
		email: "",
		ticket_type: filteredTicketTypes.value[0]?.name || "",
		add_ons: {},
	};
	for (const addOn of filteredAddOns.value) {
		newAttendee.add_ons[addOn.name] = {
			selected: false,
			option: addOn.options ? addOn.options[0] || null : null,
		};
	}
	return newAttendee;
};

const addAttendee = () => {
	// Check coupon limits if applicable
	if (props.couponInfo?.valid) {
		const couponTicketCount = attendees.value.filter(
			(attendee) => attendee.ticket_type === props.couponInfo.ticket_type
		).length;

		if (couponTicketCount >= props.couponInfo.remaining_tickets) {
			alert(
				`You can only book ${props.couponInfo.remaining_tickets} tickets with this coupon.`
			);
			return;
		}
	}

	attendees.value.push(createNewAttendee());
};

const removeAttendee = (index) => {
	attendees.value.splice(index, 1);
};

// Clear stored data (useful after successful booking)
const clearStoredData = () => {
	attendees.value = [];
	attendeeIdCounter.value = 0;
	storedCouponCode.value = "";
	localCouponCode.value = "";
};

// --- COMPUTED PROPERTIES FOR SUMMARY ---
const summary = computed(() => {
	const summaryData = { tickets: {}, add_ons: {} };

	for (const attendee of attendees.value) {
		const ticketType = attendee.ticket_type;
		if (ticketType && ticketTypesMap.value[ticketType]) {
			const ticketInfo = ticketTypesMap.value[ticketType];

			// Check if this ticket type qualifies for coupon discount
			const isCouponTicket =
				props.couponInfo?.valid && props.couponInfo.ticket_type === ticketType;
			const ticketPrice = isCouponTicket ? 0 : ticketInfo.price;

			if (!summaryData.tickets[ticketType]) {
				summaryData.tickets[ticketType] = {
					count: 0,
					amount: 0,
					price: ticketPrice,
					originalPrice: ticketInfo.price,
					title: ticketInfo.title,
					currency: ticketInfo.currency,
					isCouponTicket: isCouponTicket,
				};
			}
			summaryData.tickets[ticketType].count++;
			summaryData.tickets[ticketType].amount += ticketPrice;
		}

		for (const addOnName in attendee.add_ons) {
			if (attendee.add_ons[addOnName].selected) {
				const addOnInfo = addOnsMap.value[addOnName];
				// Skip if add-on is not available in current context (e.g., coupon vs non-coupon)
				if (!addOnInfo) continue;

				// Check if this add-on is free (from coupon)
				const isFreeAddOn =
					props.couponInfo?.valid &&
					props.couponInfo.free_add_ons?.some(
						(freeAddOn) => freeAddOn.name === addOnName
					);
				const addOnPrice = isFreeAddOn ? 0 : addOnInfo.price;

				if (!summaryData.add_ons[addOnName]) {
					summaryData.add_ons[addOnName] = {
						count: 0,
						amount: 0,
						price: addOnPrice,
						title: addOnInfo.title,
						currency: addOnInfo.currency,
						isFreeAddOn: isFreeAddOn,
					};
				}
				summaryData.add_ons[addOnName].count++;
				summaryData.add_ons[addOnName].amount += addOnPrice;
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

// Determine the primary currency for the total (use the first ticket type's currency)
const totalCurrency = computed(() => {
	const firstTicket = Object.values(summary.value.tickets)[0];
	return firstTicket ? firstTicket.currency : "INR";
});

// Submit button text based on total amount
const submitButtonText = computed(() => {
	if (processBooking.loading) return "Processing...";
	return total.value === 0 ? "Book" : "Pay & Book";
});

// Coupon-related computed properties
const currentCouponTicketCount = computed(() => {
	if (!props.couponInfo?.valid) return 0;
	return attendees.value.filter(
		(attendee) => attendee.ticket_type === props.couponInfo.ticket_type
	).length;
});

const isAddAttendeeDisabled = computed(() => {
	if (!props.couponInfo?.valid) return false;
	return currentCouponTicketCount.value >= props.couponInfo.remaining_tickets;
});

const couponLimitWarning = computed(() => {
	if (!props.couponInfo?.valid) return null;
	const remaining = props.couponInfo.remaining_tickets - currentCouponTicketCount.value;
	if (remaining === 0) {
		return "You have reached the maximum number of tickets for this coupon.";
	}
	if (remaining <= 2) {
		return `You can book ${remaining} more ticket${
			remaining === 1 ? "" : "s"
		} with this coupon.`;
	}
	return null;
});

// --- WATCHER ---
// Initialize with one attendee when component mounts (only if no data in storage)
watch(
	() => filteredTicketTypes.value,
	() => {
		if (attendees.value.length === 0 && filteredTicketTypes.value.length > 0) {
			attendees.value.push(createNewAttendee());
		}
	},
	{ immediate: true }
);

// Watch for coupon changes and update attendees' ticket types and add-ons if needed
watch(
	() => props.couponInfo,
	(newCouponInfo, oldCouponInfo) => {
		// If coupon becomes valid and it's different from before
		if (newCouponInfo?.valid && newCouponInfo.ticket_type !== oldCouponInfo?.ticket_type) {
			// Update all attendees to use the coupon's ticket type and reset add-ons
			for (const attendee of attendees.value) {
				attendee.ticket_type = newCouponInfo.ticket_type;
				// Reset add-ons to only include coupon's free add-ons
				attendee.add_ons = {};
				for (const addOn of newCouponInfo.free_add_ons || []) {
					attendee.add_ons[addOn.name] = {
						selected: false,
						option: addOn.options ? addOn.options[0] || null : null,
					};
				}
			}
		}
		// If coupon becomes invalid, reset to first available ticket type and all add-ons
		else if (!newCouponInfo?.valid && oldCouponInfo?.valid) {
			const defaultTicketType = props.availableTicketTypes[0]?.name || "";
			for (const attendee of attendees.value) {
				attendee.ticket_type = defaultTicketType;
				// Reset add-ons to include all available add-ons
				attendee.add_ons = {};
				for (const addOn of props.availableAddOns) {
					attendee.add_ons[addOn.name] = {
						selected: false,
						option: addOn.options ? addOn.options[0] || null : null,
					};
				}
			}
		}
	}
);

// Watch for changes in filtered add-ons and clean up orphaned selections
watch(
	() => filteredAddOns.value,
	(newAddOns) => {
		const availableAddOnNames = new Set(newAddOns.map((a) => a.name));

		// Clean up attendees' add-ons to only include currently available ones
		for (const attendee of attendees.value) {
			const currentAddOns = { ...attendee.add_ons };
			attendee.add_ons = {};

			// Re-add only available add-ons, preserving selections if they exist
			for (const addOn of newAddOns) {
				attendee.add_ons[addOn.name] = currentAddOns[addOn.name] || {
					selected: false,
					option: addOn.options ? addOn.options[0] || null : null,
				};
			}
		}
	}
);

const processBooking = createResource({
	url: "events.api.process_booking",
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
		coupon_code: props.couponInfo?.valid ? localCouponCode.value : null,
	};

	processBooking.submit(final_payload, {
		onSuccess: (data) => {
			// Clear stored data after successful booking
			clearStoredData();

			if (data.payment_link) {
				window.location.href = data.payment_link;
			} else {
				router.replace(`/bookings/${data.booking_name}`);
			}
		},
	});
}
</script>
