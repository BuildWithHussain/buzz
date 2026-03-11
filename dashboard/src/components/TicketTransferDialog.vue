<template>
	<Dialog v-model="isOpen">
		<template #body-title>
			<h3 class="text-xl font-semibold text-ink-gray-9">{{ __("Transfer Ticket") }}</h3>
		</template>
		<template #body-content>
			<div class="space-y-4">
				<p class="text-ink-gray-7">
					{{
						__(
							"Transfer this ticket to a new attendee. The new attendee will receive the updated ticket information."
						)
					}}
				</p>

				<FormControl
					type="text"
					:label="__('New Attendee Name')"
					:placeholder="__('Enter full name')"
					v-model="transferForm.name"
					:required="true"
				/>

				<FormControl
					type="email"
					:label="__('New Attendee Email')"
					:placeholder="__('Enter email address')"
					v-model="transferForm.email"
					:required="true"
				/>
			</div>
		</template>
		<template #actions="{ close }">
			<div class="flex gap-2">
				<Button
					variant="solid"
					@click="handleTransferTicket"
					:loading="transferResource.loading"
					:disabled="!transferForm.name || !transferForm.email"
				>
					{{ __("Transfer Ticket") }}
				</Button>
				<Button variant="outline" @click="close"> {{ __("Cancel") }} </Button>
			</div>
		</template>
	</Dialog>
</template>

<script setup lang="ts">
import { ref, watch, computed } from "vue";
import { createResource, Dialog, FormControl, Button, toast } from "frappe-ui";
import type { EventTicket } from "@/types/Ticketing/EventTicket";
import { FrappeError } from "@/types/Frappe/FrappeError";

const props = withDefaults(
	defineProps<{
		modelValue?: boolean;
		ticket?: EventTicket | null;
	}>(),
	{
		modelValue: false,
		ticket: null,
	}
);

const emit = defineEmits<{
	"update:modelValue": [value: boolean];
	success: [];
}>();

const isOpen = computed({
	get: () => props.modelValue,
	set: (value: boolean) => emit("update:modelValue", value),
});

const transferForm = ref({
	name: "",
	email: "",
});

// Transfer ticket resource
const transferResource = createResource({
	url: "buzz.api.transfer_ticket",
	onSuccess: () => {
		toast.success(__("Ticket transferred successfully!"));
		isOpen.value = false;
		resetTransferForm();
		emit("success");
	},
	onError: (error: FrappeError) => {
		toast.error(`${__("Failed to transfer ticket")}: ${error.message}`);
	},
});

const handleTransferTicket = () => {
	if (!props.ticket || !transferForm.value.name || !transferForm.value.email) {
		toast.error(__("Please fill in all required fields"));
		return;
	}

	transferResource.submit({
		ticket_id: props.ticket.name,
		new_name: transferForm.value.name,
		new_email: transferForm.value.email,
	});
};

const resetTransferForm = () => {
	transferForm.value = {
		name: "",
		email: "",
	};
};

// Reset form when dialog is closed
watch(isOpen, (newValue: boolean) => {
	if (!newValue) {
		resetTransferForm();
	}
});
</script>
