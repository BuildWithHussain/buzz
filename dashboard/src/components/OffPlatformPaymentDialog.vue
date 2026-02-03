<template>
	<Dialog v-model:open="isOpen" :options="{ size: 'md' }">
		<template #body>
			<div class="p-4">
				<!-- Title (shows custom label if set, otherwise default) -->
				<h3 class="text-lg font-semibold mb-4">
					{{ offlineSettings.label ? offlineSettings.label : __("Off-platform Payment") }}
				</h3>
				<!-- Instructions -->
				<div v-if="offlineSettings.instructions" class="mb-4 p-3 bg-blue-50 border border-blue-200 rounded">
					<p class="text-sm text-blue-800">{{ offlineSettings.instructions }}</p>
				</div>

				<div class="space-y-4">
					<!-- Amount -->
					<div class="text-center p-3 bg-gray-50 rounded">
						<div class="text-xl font-bold">{{ formatCurrency(amount, currency) }}</div>
					</div>

					<!-- Payment Methods -->
					<div v-if="offlineSettings.payment_id">
						<div class="flex items-center gap-2 p-2 bg-gray-50 rounded">
							<code class="flex-1 text-sm">{{ offlineSettings.payment_id }}</code>
							<Button size="sm" @click="copyToClipboard(offlineSettings.payment_id)">
								<LucideCopy class="w-4 h-4" />
							</Button>
						</div>
					</div>

					<div v-if="offlineSettings.qr_code" class="text-center">
						<div class="p-4 bg-white border-2 border-gray-200 rounded-lg w-full">
							<img :src="offlineSettings.qr_code" class="w-full h-auto object-contain" />
						</div>
					</div>

					<!-- Custom Fields -->
					<CustomFieldsSection
						v-if="offPlatformCustomFields.length > 0"
						:custom-fields="offPlatformCustomFields"
						v-model="customFieldsData"
						:show-title="false"
					/>

					<!-- Upload Proof -->
					<div v-if="offlineSettings.collect_payment_proof">
						<label class="text-sm font-medium">{{ __("Payment Proof") }} *</label>
						<FileUploader 
							v-model="paymentProof" 
							:file-types="['image/*']"
							@success="onFileUpload"
						/>
						<div v-if="paymentProof" class="mt-2 text-sm text-green-600">
							✓ File uploaded: {{ paymentProof.name || 'Payment Proof' }}
						</div>
					</div>
				</div>

				<div class="flex gap-2 mt-4">
					<Button variant="outline" class="flex-1" @click="$emit('cancel')">
						{{ __("Cancel") }}
					</Button>
					<Button variant="solid" class="flex-1" @click="submitOfflinePayment" :loading="loading" :disabled="isSubmitDisabled">
						{{ __("Submit") }}
					</Button>
				</div>
			</div>
		</template>
	</Dialog>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Dialog, Button, FileUploader, toast } from 'frappe-ui'
import { formatCurrency } from '../utils/currency.js'
import CustomFieldsSection from './CustomFieldsSection.vue'
import LucideCopy from '~icons/lucide/copy'

const props = defineProps({
	open: {
		type: Boolean,
		default: false
	},
	amount: {
		type: Number,
		required: true
	},
	currency: {
		type: String,
		default: 'INR'
	},
	offlineSettings: {
		type: Object,
		required: true
	},
	loading: {
		type: Boolean,
		default: false
	},
	customFields: {
		type: Array,
		default: () => []
	}
})

const emit = defineEmits(['update:open', 'submit', 'cancel'])

const isOpen = computed({
	get: () => props.open,
	set: (value) => emit('update:open', value)
})

const paymentProof = ref(null)
const customFieldsData = ref({})

// Filter custom fields for off-platform payment
const offPlatformCustomFields = computed(() => 
	props.customFields.filter(field => field.applied_to === 'Off-platform Payment')
)

// Check if submit should be disabled
const isSubmitDisabled = computed(() => {
	// Check payment proof requirement
	if (props.offlineSettings.collect_payment_proof && !paymentProof.value) {
		return true
	}
	
	// Check mandatory custom fields
	for (const field of offPlatformCustomFields.value) {
		if (field.mandatory && (!customFieldsData.value[field.fieldname] || customFieldsData.value[field.fieldname] === '')) {
			return true
		}
	}
	
	return false
})

const onFileUpload = (file) => {
	paymentProof.value = file
	console.log('File uploaded:', file)
}

const copyToClipboard = async (text) => {
	try {
		await navigator.clipboard.writeText(text)
		toast.success(__('Copied to clipboard'))
	} catch (err) {
		toast.error(__('Failed to copy'))
	}
}

const submitOfflinePayment = () => {
	if (isSubmitDisabled.value) {
		toast.error(__('Please fill all required fields'))
		return
	}
	
	emit('submit', {
		payment_proof: paymentProof.value,
		custom_fields: customFieldsData.value
	})
}
</script>