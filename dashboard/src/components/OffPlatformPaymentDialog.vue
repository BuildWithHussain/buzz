<template>
	<Dialog v-model:open="isOpen" :options="{ size: 'md' }">
		<template #body>
			<div class="p-4">
				<!-- Title (shows custom label if set, otherwise default) -->
				<h3 class="text-lg font-semibold mb-4 text-ink-gray-9">
					{{ offlineSettings.label }}
				</h3>

				<div class="space-y-4">
					<!-- Amount -->
					<div class="text-center p-3 bg-surface-gray-1 rounded">
						<div class="text-xl font-bold text-ink-gray-9">
							{{ formatCurrency(amount, currency) }}
						</div>
					</div>

					<!-- Payment Details (HTML Content) -->
					<div
						v-if="offlineSettings.payment_details"
						class="prose-sm bg-surface-gray-1 border border-outline-gray-1 rounded p-3 text-ink-gray-9"
						v-html="offlineSettings.payment_details"
					></div>

					<!-- Custom Fields -->
					<CustomFieldsSection
						v-if="offPlatformCustomFields.length > 0"
						:custom-fields="offPlatformCustomFields"
						v-model="customFieldsData"
						:show-title="false"
					/>

					<!-- Upload Proof -->
					<div v-if="offlineSettings.collect_payment_proof">
						<label class="block text-sm font-medium text-ink-gray-8 mb-2"
							>{{ __("Proof of Payment") }} *</label
						>
						<FileUploader
							v-model="paymentProof"
							:file-types="['image/*']"
							@success="onFileUpload"
						/>
						<div v-if="paymentProof" class="mt-2 text-sm text-ink-green-2">
							✓ File uploaded: {{ paymentProof.name || "Proof of Payment" }}
						</div>
					</div>
				</div>

				<div class="flex gap-2 mt-4">
					<Button variant="outline" class="flex-1" @click="$emit('cancel')">
						{{ __("Cancel") }}
					</Button>
					<Button
						variant="solid"
						class="flex-1"
						@click="submitOfflinePayment"
						:loading="loading"
						:disabled="isSubmitDisabled"
					>
						{{ __("Submit") }}
					</Button>
				</div>
			</div>
		</template>
	</Dialog>
</template>

<script setup>
import { ref, computed } from "vue";
import { Dialog, Button, FileUploader, toast } from "frappe-ui";
import { formatCurrency } from "../utils/currency";
import CustomFieldsSection from "./CustomFieldsSection.vue";

const props = defineProps({
	open: {
		type: Boolean,
		default: false,
	},
	amount: {
		type: Number,
		required: true,
	},
	currency: {
		type: String,
		default: "INR",
	},
	offlineSettings: {
		type: Object,
		required: true,
	},
	loading: {
		type: Boolean,
		default: false,
	},
	customFields: {
		type: Array,
		default: () => [],
	},
});

const emit = defineEmits(["update:open", "submit", "cancel"]);

const isOpen = computed({
	get: () => props.open,
	set: (value) => emit("update:open", value),
});

const paymentProof = ref(null);
const customFieldsData = ref({});

// Filter custom fields for off-platform payment
const offPlatformCustomFields = computed(() =>
	props.customFields.filter((field) => field.applied_to === "Off-platform Payment")
);

// Check if submit should be disabled
const isSubmitDisabled = computed(() => {
	// Check payment proof requirement
	if (props.offlineSettings.collect_payment_proof && !paymentProof.value) {
		return true;
	}

	// Check mandatory custom fields
	for (const field of offPlatformCustomFields.value) {
		if (
			field.mandatory &&
			(!customFieldsData.value[field.fieldname] ||
				customFieldsData.value[field.fieldname] === "")
		) {
			return true;
		}
	}

	return false;
});

const onFileUpload = (file) => {
	paymentProof.value = file;
};

const submitOfflinePayment = () => {
	if (isSubmitDisabled.value) {
		toast.error(__("Please fill all required fields"));
		return;
	}

	emit("submit", {
		payment_proof: paymentProof.value,
		custom_fields: customFieldsData.value,
	});
};
</script>
