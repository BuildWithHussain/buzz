<template>
	<Dialog v-model="isOpen" :options="{ title: __('QR Code'), size: 'lg' }">
		<template #body-content>
			<div class="flex justify-center">
				<img :src="qrCodeSrc" :alt="altText" class="w-full max-w-sm" />
			</div>
		</template>
	</Dialog>
</template>

<script setup>
import { computed } from "vue";
import { Dialog } from "frappe-ui";

const props = defineProps({
	modelValue: {
		type: Boolean,
		default: false,
	},
	qrCodeSrc: {
		type: String,
		required: true,
	},
	altText: {
		type: String,
		default: "QR Code",
	},
});

const emit = defineEmits(["update:modelValue"]);

const isOpen = computed({
	get: () => props.modelValue,
	set: (value) => emit("update:modelValue", value),
});
</script>
