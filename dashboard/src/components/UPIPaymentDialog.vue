<template>
	<Dialog v-model:open="isOpen" :options="{ size: 'md' }">
		<template #body>
			<div class="p-4">
				<h3 class="text-lg font-semibold mb-4">{{ __("UPI Payment") }}</h3>

				<div class="space-y-4">
					<!-- Amount -->
					<div class="text-center p-3 bg-gray-50 rounded">
						<div class="text-xl font-bold">{{ formatCurrency(amount, currency) }}</div>
					</div>

					<!-- Payment Methods -->
					<div v-if="offlineSettings.upi_id">
						<div class="flex items-center gap-2 p-2 bg-gray-50 rounded">
							<code class="flex-1 text-sm">{{ offlineSettings.upi_id }}</code>
							<Button size="sm" @click="copyToClipboard(offlineSettings.upi_id)">
								<LucideCopy class="w-4 h-4" />
							</Button>
						</div>
					</div>

					<div v-if="offlineSettings.qr_code" class="text-center">
						<div class="p-4 bg-white border-2 border-gray-200 rounded-lg w-full">
							<img :src="offlineSettings.qr_code" class="w-full h-auto object-contain" />
						</div>
					</div>

					<!-- Upload Proof -->
					<div>
						<label class="text-sm font-medium">{{ __("Payment Screenshot") }} *</label>
						<FileUploader 
							v-model="paymentProof" 
							:file-types="['image/*']"
							@success="onFileUpload"
						/>
						<div v-if="paymentProof" class="mt-2 text-sm text-green-600">
							✓ File uploaded: {{ paymentProof.name || 'Screenshot' }}
						</div>
					</div>
				</div>

				<div class="flex gap-2 mt-4">
					<Button variant="outline" class="flex-1" @click="$emit('cancel')">
						{{ __("Cancel") }}
					</Button>
					<Button variant="solid" class="flex-1" @click="submitOfflinePayment" :loading="loading" :disabled="!paymentProof">
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
	}
})

const emit = defineEmits(['update:open', 'submit', 'cancel'])

const isOpen = computed({
	get: () => props.open,
	set: (value) => emit('update:open', value)
})

const paymentProof = ref(null)

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
	if (!paymentProof.value) {
		toast.error(__('Please upload payment screenshot'))
		return
	}
	
	emit('submit', paymentProof.value)
}
</script>