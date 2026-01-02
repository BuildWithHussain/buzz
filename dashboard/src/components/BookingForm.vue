<!-- BookingForm.vue -->
<template>
	<div>
		<EventDetailsHeader :event-details="eventDetails" />

		<!-- Payment Gateway Selection Dialog -->
		<PaymentGatewayDialog
			v-model:open="showGatewayDialog"
			:payment-gateways="paymentGateways"
			@gateway-selected="onGatewaySelected"
		/>

		<form @submit.prevent="submit">
			<div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
				<!-- Left Side: Form Inputs -->
				<div class="lg:col-span-2">
					<!-- Booking-level Custom Fields -->
					<div
						v-if="bookingCustomFields.length > 0"
						class="bg-surface-white border border-outline-gray-3 rounded-xl p-4 md:p-6 mb-6 shadow-sm"
					>
						<CustomFieldsSection
							v-model="bookingCustomFieldsData"
							:custom-fields="bookingCustomFields"
							:title="__('Booking Information')"
						/>
					</div>

					<AttendeeFormControl
						v-for="(attendee, index) in attendees"
						:key="attendee.id"
						:attendee="attendee"
						:index="index"
						:available-ticket-types="availableTicketTypes"
						:available-add-ons="availableAddOns"
						:custom-fields="ticketCustomFields"
						:show-remove="attendees.length > 1"
						:eventDetails="eventDetails"
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
							+ {{ __("Add Another Attendee") }}
						</Button>
					</div>
				</div>

				<!-- Right Side: Coupon, Summary and Submit -->
				<div class="lg:col-span-1">
					<div class="sticky top-4 w-full">
						<!-- Coupon Code Section -->
						<div
							v-if="finalTotal > 0 || couponApplied"
							class="bg-surface-white border border-outline-gray-3 rounded-xl p-4 mb-4"
						>
							<h3 class="text-lg font-semibold text-ink-gray-8 mb-3">
								{{ __("Have a coupon?") }}
							</h3>

							<div v-if="!couponApplied" class="flex gap-2">
								<FormControl
									v-model="couponCode"
									:placeholder="__('Enter coupon code')"
									class="flex-1"
									@keyup.enter="applyCoupon"
								/>
								<Button
									variant="outline"
									@click="applyCoupon"
									:loading="validateCoupon.loading"
								>
									{{ __("Apply") }}
								</Button>
							</div>

							<!-- Applied coupon display -->
							<div
								v-else
								class="flex items-center justify-between bg-green-50 border border-green-200 rounded-lg p-3"
							>
								<div class="flex items-center gap-2">
									<span class="text-green-700 font-medium">{{
										couponCode
									}}</span>
									<span class="text-green-600 text-sm">
										<template v-if="couponData.coupon_type === 'Free Tickets'">
											({{ matchingAttendeesCount }} {{ __("eligible") }},
											{{
												Math.min(
													matchingAttendeesCount,
													couponData.remaining_tickets
												)
											}}
											{{ __("free") }})
										</template>
										<template v-else>
											({{
												couponData.discount_type === "Percentage"
													? couponData.discount_value + "% off"
													: formatPriceOrFree(
															couponData.discount_value,
															totalCurrency
													  ) + " off"
											}})
										</template>
									</span>
								</div>
								<Button variant="ghost" size="sm" @click="removeCoupon">
									✕
								</Button>
							</div>

							<!-- Error message -->
							<p v-if="couponError" class="text-red-500 text-sm mt-2">
								{{ couponError }}
							</p>
						</div>

						<BookingSummary
							class="mb-6"
							v-if="!eventDetails.free_webinar"
							:summary="summary"
							:net-amount="netAmount"
							:discount-amount="discountAmount"
							:coupon-applied="couponApplied"
							:coupon-type="couponData?.coupon_type || ''"
							:tax-amount="taxAmount"
							:tax-percentage="taxPercentage"
							:tax-label="taxLabel"
							:should-apply-tax="shouldApplyTax"
							:total="finalTotal"
							:total-currency="totalCurrency"
						/>

						<div class="w-full">
							<Button
								variant="solid"
								size="lg"
								class="w-full"
								type="submit"
								:loading="processBooking.loading"
							>
								{{ submitButtonText }}
							</Button>
						</div>
					</div>
				</div>
			</div>
		</form>
	</div>
</template>

<script setup>
import { computed, watch, ref } from "vue";
import AttendeeFormControl from "./AttendeeFormControl.vue";
import BookingSummary from "./BookingSummary.vue";
import EventDetailsHeader from "./EventDetailsHeader.vue";
import CustomFieldsSection from "./CustomFieldsSection.vue";
import PaymentGatewayDialog from "./PaymentGatewayDialog.vue";
import { createResource, toast, FormControl } from "frappe-ui";
import { formatPriceOrFree } from "../utils/currency.js";
import { useBookingFormStorage } from "../composables/useBookingFormStorage.js";
import { useRouter, useRoute } from "vue-router";
import { userResource } from "../data/user.js";

const router = useRouter();
const route = useRoute();

const getUtmParameters = () => {
	const utmParams = [];
	for (const [key, value] of Object.entries(route.query)) {
		if (key.toLowerCase().startsWith("utm_") && value) {
			utmParams.push({
				utm_name: key,
				value: String(value),
			});
		}
	}
	return utmParams;
};

const props = defineProps({
	availableAddOns: {
		type: Array,
		default: () => [],
	},
	availableTicketTypes: {
		type: Array,
		default: () => [],
	},
	taxSettings: {
		type: Object,
		default: () => ({
			apply_tax: false,
			tax_label: "Tax",
			tax_percentage: 0,
		}),
	},
	eventDetails: {
		type: Object,
		default: () => ({}),
	},
	customFields: {
		type: Array,
		default: () => [],
	},
	eventRoute: {
		type: String,
		required: true,
	},
	paymentGateways: {
		type: Array,
		default: () => [],
	},
});

// --- STATE ---
// Use the booking form storage composable with event-scoped keys
const {
	attendees,
	attendeeIdCounter,
	bookingCustomFields: storedBookingCustomFields,
} = useBookingFormStorage(props.eventRoute);

// Use stored booking custom fields data
const bookingCustomFieldsData = storedBookingCustomFields;

// Payment gateway dialog state
const showGatewayDialog = ref(false);
const pendingPayload = ref(null);

// Coupon state
const couponCode = ref("");
const couponApplied = ref(false);
const couponError = ref("");
const couponData = ref(null);

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

// Separate custom fields by applied_to
const bookingCustomFields = computed(() =>
	props.customFields.filter((field) => field.applied_to === "Booking")
);

const ticketCustomFields = computed(() =>
	props.customFields.filter((field) => field.applied_to === "Ticket")
);

const getDefaultTicketType = () => {
	// Use the default ticket type from event details if set
	const defaultTicketType = props.eventDetails?.default_ticket_type;
	if (defaultTicketType) {
		// Verify that the default ticket type is available
		const isAvailable = props.availableTicketTypes.some((tt) => tt.name == defaultTicketType);
		if (isAvailable) {
			return defaultTicketType;
		}
	}
	// Fall back to the first available ticket type
	return props.availableTicketTypes[0]?.name || "";
};

const createNewAttendee = () => {
	attendeeIdCounter.value++;
	const newAttendee = {
		id: attendeeIdCounter.value,
		full_name: "",
		email: "",
		// Use default ticket type from event details, or first available
		ticket_type: getDefaultTicketType(),
		add_ons: {},
		custom_fields: {},
	};
	for (const addOn of props.availableAddOns) {
		newAttendee.add_ons[addOn.name] = {
			selected: false,
			option: addOn.options ? addOn.options[0] || null : null,
		};
	}

	// Initialize custom fields with default values
	for (const field of ticketCustomFields.value) {
		if (field.default_value) {
			newAttendee.custom_fields[field.fieldname] = field.default_value;
		}
	}

	return newAttendee;
};

const addAttendee = () => {
	const newAttendee = createNewAttendee();
	attendees.value.push(newAttendee);
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
				// Skip if add-on no longer exists (e.g., was disabled)
				if (!addOnInfo) continue;

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
const shouldApplyTax = computed(() => {
	return props.taxSettings?.apply_tax;
});

const taxLabel = computed(() => {
	return props.taxSettings?.tax_label || "Tax";
});

const taxPercentage = computed(() => {
	return shouldApplyTax.value ? props.taxSettings?.tax_percentage || 0 : 0;
});

// Count of attendees matching the coupon's ticket type (for Free Tickets)
const matchingAttendeesCount = computed(() => {
	if (!couponData.value || couponData.value.coupon_type !== "Free Tickets") return 0;
	return attendees.value.filter((a) => a.ticket_type === couponData.value.ticket_type).length;
});

// Discount amount based on coupon
const discountAmount = computed(() => {
	if (!couponApplied.value || !couponData.value) return 0;

	// Free Tickets - only discount attendees with matching ticket type
	if (couponData.value.coupon_type === "Free Tickets") {
		const couponTicketType = couponData.value.ticket_type;
		const ticketInfo = ticketTypesMap.value[couponTicketType];
		if (!ticketInfo) return 0;

		// Count only attendees with matching ticket type
		const matchingAttendees = attendees.value.filter(
			(a) => a.ticket_type === couponTicketType
		);
		const freeTicketCount = Math.min(
			matchingAttendees.length,
			couponData.value.remaining_tickets
		);
		let discount = freeTicketCount * ticketInfo.price;

		// Add free add-ons discount for free ticket holders only
		if (couponData.value.free_add_ons && couponData.value.free_add_ons.length > 0) {
			for (let i = 0; i < freeTicketCount; i++) {
				const attendee = matchingAttendees[i];
				if (attendee) {
					for (const freeAddOnName of couponData.value.free_add_ons) {
						if (attendee.add_ons[freeAddOnName]?.selected) {
							const addOnInfo = addOnsMap.value[freeAddOnName];
							if (addOnInfo) {
								discount += addOnInfo.price;
							}
						}
					}
				}
			}
		}

		return discount;
	}

	// Discount coupon
	if (couponData.value.discount_type === "Percentage") {
		return netAmount.value * (couponData.value.discount_value / 100);
	}
	return Math.min(couponData.value.discount_value, netAmount.value);
});

// Amount after discount
const amountAfterDiscount = computed(() => {
	return netAmount.value - discountAmount.value;
});

const taxAmount = computed(() => {
	return shouldApplyTax.value ? (amountAfterDiscount.value * taxPercentage.value) / 100 : 0;
});

const finalTotal = computed(() => {
	return amountAfterDiscount.value + taxAmount.value;
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

// Auto-select ticket type based on event's default or if there's only one available
watch(
	() => props.availableTicketTypes,
	(newTicketTypes) => {
		if (newTicketTypes && newTicketTypes.length > 0) {
			const defaultTicketType = getDefaultTicketType();
			for (const attendee of attendees.value) {
				if (!attendee.ticket_type || attendee.ticket_type === "") {
					attendee.ticket_type = defaultTicketType;
				}
			}
		}
	},
	{ immediate: true }
);

// Initialize booking custom fields with default values
watch(
	() => bookingCustomFields.value,
	(fields) => {
		if (fields && fields.length > 0) {
			for (const field of fields) {
				// Only set default value if field doesn't already have a value
				if (field.default_value && !bookingCustomFieldsData.value[field.fieldname]) {
					bookingCustomFieldsData.value[field.fieldname] = field.default_value;
				}
			}
		}
	},
	{ immediate: true }
);

const processBooking = createResource({
	url: "buzz.api.process_booking",
});

const validateCoupon = createResource({
	url: "buzz.api.validate_coupon",
});

// --- COUPON FUNCTIONS ---
async function applyCoupon() {
	if (!couponCode.value.trim()) {
		couponError.value = __("Please enter a coupon code");
		return;
	}

	couponError.value = "";
	let result;
	try {
		result = await validateCoupon.submit({
			coupon_code: couponCode.value.trim(),
			event: eventId.value,
		});
	} catch (error) {
		couponError.value = error.message || __("Failed to validate coupon");
		return;
	}

	if (result.valid) {
		couponApplied.value = true;

		if (result.coupon_type === "Discount") {
			couponData.value = {
				coupon_type: "Discount",
				discount_type: result.discount_type,
				discount_value: result.discount_value,
			};
			toast.success(__("Coupon applied successfully!"));
		} else if (result.coupon_type === "Free Tickets") {
			couponData.value = {
				coupon_type: "Free Tickets",
				ticket_type: result.ticket_type,
				remaining_tickets: result.remaining_tickets,
				free_add_ons: result.free_add_ons || [],
			};

			// Note: Users can choose any ticket type - only matching types get free discount
			toast.success(
				__(
					`Free ticket coupon applied! Select "${
						ticketTypesMap.value[result.ticket_type]?.title || result.ticket_type
					}" to get free tickets (${result.remaining_tickets} available)`
				)
			);
		}
	} else {
		couponApplied.value = false;
		couponData.value = null;
		couponError.value = result.error;
	}
}

function removeCoupon() {
	couponCode.value = "";
	couponApplied.value = false;
	couponData.value = null;
	couponError.value = "";
}

// --- FORM VALIDATION ---
const validateForm = () => {
	const errors = [];

	// Validate booking-level mandatory fields
	for (const field of bookingCustomFields.value) {
		if (field.mandatory) {
			const value = bookingCustomFieldsData.value[field.fieldname];
			if (!value || !String(value).trim()) {
				errors.push(`${field.label} is required`);
			}
		}
	}

	// Validate ticket-level mandatory fields for each attendee
	attendees.value.forEach((attendee, index) => {
		for (const field of ticketCustomFields.value) {
			if (field.mandatory) {
				const value = attendee.custom_fields?.[field.fieldname];
				if (!value || !String(value).trim()) {
					errors.push(`${field.label} is required for Attendee #${index + 1}`);
				}
			}
		}
	});

	return errors;
};

// --- FORM SUBMISSION ---
async function submit() {
	if (processBooking.loading) return;

	// Validate mandatory fields
	const validationErrors = validateForm();
	if (validationErrors.length > 0) {
		// Show the first error as toast, or all errors if only a few
		if (validationErrors.length === 1) {
			toast.error(validationErrors[0]);
		} else if (validationErrors.length <= 3) {
			toast.error(`Please fill in the required fields:\n${validationErrors.join("\n")}`);
		} else {
			toast.error(`Please fill in ${validationErrors.length} required fields.`);
		}
		return;
	}

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

		// Clean custom fields - include all valid fields (mandatory fields are validated separately)
		if (cleanAttendee.custom_fields) {
			const cleanedCustomFields = {};
			for (const [fieldName, value] of Object.entries(cleanAttendee.custom_fields)) {
				// Check if this is a valid custom field for tickets
				const fieldDef = ticketCustomFields.value.find((cf) => cf.fieldname === fieldName);
				if (fieldDef) {
					// Include mandatory fields even if empty (validation already passed)
					// For non-mandatory fields, only include if they have values
					if (fieldDef.mandatory || (value != null && String(value).trim())) {
						cleanedCustomFields[fieldName] = value || "";
					}
				}
			}
			cleanAttendee.custom_fields =
				Object.keys(cleanedCustomFields).length > 0 ? cleanedCustomFields : null;
		}

		return cleanAttendee;
	});

	// Clean booking custom fields
	const cleanedBookingCustomFields = {};
	for (const [fieldName, value] of Object.entries(bookingCustomFieldsData.value)) {
		// Check if this is a valid custom field for bookings
		const fieldDef = bookingCustomFields.value.find((cf) => cf.fieldname === fieldName);
		if (fieldDef) {
			// Include mandatory fields even if empty (validation already passed)
			// For non-mandatory fields, only include if they have values
			if (fieldDef.mandatory || (value != null && String(value).trim())) {
				cleanedBookingCustomFields[fieldName] = value || "";
			}
		}
	}

	const utmParameters = getUtmParameters();

	const final_payload = {
		event: eventId.value,
		attendees: attendees_payload,
		coupon_code: couponApplied.value ? couponCode.value.trim() : null,
		booking_custom_fields:
			Object.keys(cleanedBookingCustomFields).length > 0 ? cleanedBookingCustomFields : null,
		utm_parameters: utmParameters.length > 0 ? utmParameters : null,
	};

	// Check if we need to show gateway selection dialog
	// Only show dialog if there's a payment (finalTotal > 0) and multiple gateways
	if (finalTotal.value > 0 && props.paymentGateways.length > 1) {
		pendingPayload.value = final_payload;
		showGatewayDialog.value = true;
		return;
	}

	// Single gateway or free event - submit directly
	submitBooking(final_payload, props.paymentGateways[0] || null);
}

function submitBooking(payload, paymentGateway) {
	processBooking.submit(
		{
			...payload,
			payment_gateway: paymentGateway,
		},
		{
			onSuccess: (data) => {
				if (data.payment_link) {
					window.location.href = data.payment_link;
				} else {
					// free event
					router.replace(`/bookings/${data.booking_name}?success=true`);
				}
			},
			onError: (error) => {
				const message = error.messages?.[0] || error.message || __("Booking failed");
				toast.error(message);
			},
		}
	);
}

function onGatewaySelected(gateway) {
	if (pendingPayload.value) {
		submitBooking(pendingPayload.value, gateway);
		pendingPayload.value = null;
	}
}

const submitButtonText = computed(() => {
	if (processBooking.loading) {
		return __("Processing...");
	}

	if (finalTotal.value > 0) {
		return __("Pay & Book");
	}

	if (props.eventDetails.category === "Webinars") {
		return __("Register");
	}

	return __("Book Tickets");
});
</script>
