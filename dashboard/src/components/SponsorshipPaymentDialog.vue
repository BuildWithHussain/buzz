<template>
	<Dialog
		v-model="isOpen"
		:options="{
			title:
				currentStep === 'tier'
					? __('Select Sponsorship Tier')
					: __('Select Payment Method'),
			size: 'xl',
			description:
				currentStep === 'tier'
					? __('Choose your preferred sponsorship tier and proceed to payment')
					: __('Choose your preferred payment method'),
		}"
	>
		<template #body-content>
			<!-- Step 1: Tier Selection -->
			<div v-if="currentStep === 'tier'">
				<div v-if="!props.eventId" class="text-center py-8">
					<p class="text-ink-gray-5">{{ __("Loading event information...") }}</p>
				</div>

				<div v-else-if="tiers.loading" class="flex justify-center py-8">
					<Spinner />
				</div>

				<div v-else-if="tiers.data && tiers.data.length > 0" class="space-y-4">
					<p class="text-ink-gray-7 mb-6">
						{{ __("Select a sponsorship tier for") }}
						<strong>{{ eventTitle || __("this event") }}</strong>
						{{ __("and proceed to payment.") }}
					</p>

					<div class="space-y-3">
						<div
							v-for="tier in tiers.data"
							:key="tier.name"
							class="border border-outline-gray-2 rounded-lg p-4 cursor-pointer transition-all hover:border-outline-gray-3 hover:bg-surface-gray-1"
							:class="{
								'border-outline-gray-4 bg-surface-gray-2':
									selectedTier?.name === tier.name,
							}"
							@click="selectedTier = tier"
						>
							<div class="flex items-center justify-between">
								<div class="flex items-center space-x-3">
									<input
										type="radio"
										:checked="selectedTier?.name === tier.name"
										@change="selectedTier = tier"
										class="text-ink-gray-6"
									/>
									<div>
										<h3 class="font-semibold text-ink-gray-9">
											{{ tier.title }}
										</h3>
									</div>
								</div>
								<div class="text-right">
									<p class="font-bold text-lg text-ink-gray-9">
										{{ formatCurrency(tier.price, tier.currency) }}
									</p>
								</div>
							</div>
						</div>
					</div>

					<div
						v-if="selectedTier"
						class="mt-6 p-4 bg-surface-green-1 border border-outline-green-1 rounded-lg"
					>
						<div class="flex items-center justify-between">
							<div>
								<h4 class="font-semibold text-ink-green-2">
									{{ __("Selected Tier") }}
								</h4>
								<p class="text-ink-green-2">{{ selectedTier.title }}</p>
							</div>
							<div class="text-right">
								<p class="text-sm text-ink-green-2">{{ __("Total Amount") }}</p>
								<p class="font-bold text-xl text-ink-green-2">
									{{ formatCurrency(selectedTier.price, selectedTier.currency) }}
								</p>
							</div>
						</div>
					</div>
				</div>

				<div v-else-if="tiers.error" class="text-center py-8">
					<p class="text-ink-red-2">{{ __("Error loading sponsorship tiers") }}</p>
					<p class="text-ink-gray-5 text-sm">{{ tiers.error }}</p>
				</div>

				<div v-else class="text-center py-8">
					<p class="text-ink-gray-5">
						{{ __("No sponsorship tiers available for this event") }}
					</p>
				</div>
			</div>

			<!-- Step 2: Payment Gateway Selection -->
			<div v-else-if="currentStep === 'gateway'" class="space-y-4">
				<p class="text-ink-gray-7 mb-6">
					{{ __("Select a payment method for your") }}
					<strong>{{ selectedTier?.title }}</strong> {{ __("sponsorship.") }}
				</p>

				<div class="space-y-3">
					<div
						v-for="gateway in paymentGateways"
						:key="gateway"
						class="border border-outline-gray-2 rounded-lg p-4 cursor-pointer transition-all hover:border-outline-gray-3 hover:bg-surface-gray-1"
						:class="{
							'border-outline-gray-4 bg-surface-gray-2': selectedGateway === gateway,
						}"
						@click="selectedGateway = gateway"
					>
						<div class="flex items-center space-x-3">
							<input
								type="radio"
								:checked="selectedGateway === gateway"
								@change="selectedGateway = gateway"
								class="text-ink-gray-6"
							/>
							<div>
								<h3 class="font-semibold text-ink-gray-9">{{ gateway }}</h3>
							</div>
						</div>
					</div>
				</div>
			</div>
		</template>

		<template #actions>
			<div class="flex justify-end space-x-3">
				<Button
					v-if="currentStep === 'gateway'"
					variant="ghost"
					@click="goBackToTierSelection"
				>
					{{ __("Back") }}
				</Button>
				<Button variant="ghost" @click="closeDialog">{{ __("Cancel") }}</Button>
				<Button
					variant="solid"
					:disabled="!canProceed || paymentLink.loading"
					:loading="paymentLink.loading"
					@click="proceedToPayment"
				>
					{{ __("Proceed to Pay") }}
				</Button>
			</div>
		</template>
	</Dialog>
</template>

<script setup>
import { ref, watch, computed } from "vue";
import { Dialog, Button, Spinner, createResource, useList } from "frappe-ui";
import { formatCurrency } from "../utils/currency";

const props = defineProps({
	open: {
		type: Boolean,
		default: false,
	},
	enquiryId: {
		type: String,
		required: true,
	},
	eventId: {
		type: String,
		required: true,
	},
	eventTitle: {
		type: String,
		required: false,
	},
});

const emit = defineEmits(["update:open", "payment-started"]);

const isOpen = ref(props.open);
const selectedTier = ref(null);
const selectedGateway = ref(null);
const currentStep = ref("tier"); // 'tier' or 'gateway'
const paymentGateways = ref([]);

const canProceed = computed(() => {
	if (currentStep.value === "tier") {
		return selectedTier.value !== null;
	}
	return selectedGateway.value !== null;
});

// Watch for prop changes
watch(
	() => props.open,
	(newVal) => {
		isOpen.value = newVal;
		if (newVal && props.eventId) {
			// Reset selection when dialog opens
			selectedTier.value = null;
			selectedGateway.value = null;
			currentStep.value = "tier";
			tiers.fetch();
			fetchPaymentGateways();
		}
	}
);

watch(isOpen, (newVal) => {
	emit("update:open", newVal);
});

// Resource to fetch sponsorship tiers
const tiers = useList({
	doctype: "Sponsorship Tier",
	filters: { event: props.eventId },
	fields: ["name", "title", "price", "currency"],
	orderBy: "price asc",
	onError: console.error,
	auto: false, // Don't auto-fetch, we'll fetch manually when dialog opens
});

// Fetch payment gateways for the event
const paymentGatewaysResource = createResource({
	url: "buzz.api.get_event_payment_gateways",
	onSuccess: (data) => {
		paymentGateways.value = data || [];
	},
	onError: console.error,
});

function fetchPaymentGateways() {
	paymentGatewaysResource.submit({
		event: props.eventId,
	});
}

// Resource to create payment link
const paymentLink = createResource({
	url: "buzz.api.create_sponsorship_payment_link",
	onSuccess: (paymentUrl) => {
		emit("payment-started");
		closeDialog();
		// Redirect to payment page
		window.location.href = paymentUrl;
	},
	onError: (error) => {
		console.error("Payment link creation failed:", error);
		// TODO: Show error toast
	},
});

const closeDialog = () => {
	isOpen.value = false;
	selectedTier.value = null;
	selectedGateway.value = null;
	currentStep.value = "tier";
};

const goBackToTierSelection = () => {
	currentStep.value = "tier";
	selectedGateway.value = null;
};

const proceedToPayment = () => {
	if (currentStep.value === "tier") {
		if (!selectedTier.value) return;

		// Check if we need to show gateway selection
		if (paymentGateways.value.length > 1) {
			currentStep.value = "gateway";
			return;
		}

		// Single gateway or no gateways - submit directly
		submitPayment(paymentGateways.value[0] || null);
	} else {
		// Gateway step
		if (!selectedGateway.value) return;
		submitPayment(selectedGateway.value);
	}
};

function submitPayment(gateway) {
	paymentLink.submit({
		enquiry_id: props.enquiryId,
		tier_id: selectedTier.value.name,
		payment_gateway: gateway,
	});
}
</script>
