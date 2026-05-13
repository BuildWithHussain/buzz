<template>
	<div>
		<div class="w-8 mx-auto" v-if="form_data_resource.loading">
			<Spinner />
		</div>

		<div v-else-if="submitted" class="text-center">
			<div class="bg-surface-green-1 border border-outline-green-1 rounded-lg p-8">
				<LucideCheckCircle class="w-16 h-16 text-ink-green-2 mx-auto mb-4" />
				<h2 class="text-ink-green-3 font-semibold text-xl mb-2">
					{{ form_data.success_title }}
				</h2>
				<div
					v-if="rendered_success_message"
					class="prose prose-sm max-w-none text-ink-green-2"
					v-html="rendered_success_message"
				></div>
				<p v-else class="text-ink-green-2">
					{{ __("Your proposal has been received.") }}
				</p>
			</div>
		</div>

		<LoginRequired
			v-else-if="login_required"
			:message="__('Please log in to submit a proposal.')"
		/>

		<div v-else-if="form_data">
			<form
				class="bg-surface-white border border-outline-gray-1 rounded-lg"
				@submit.prevent="handleSubmit"
			>
				<div class="px-6 py-5 border-b border-outline-gray-1">
					<h1 class="text-ink-gray-9 font-bold text-2xl">
						{{ form_data.banner_title }}
					</h1>
				</div>

				<div class="p-6 space-y-6">
					<div
						v-for="(section, section_index) in field_sections"
						:key="section_index"
						class="grid gap-4"
						:style="{
							gridTemplateColumns: `repeat(${section.length}, minmax(0, 1fr))`,
						}"
					>
						<div
							v-for="(column, column_index) in section"
							:key="column_index"
							class="space-y-4"
						>
							<CustomFieldInput
								v-for="field in column"
								:key="field.fieldname"
								:field="{ ...field, mandatory: field.reqd }"
								:model-value="form_values[field.fieldname]"
								@update:model-value="form_values[field.fieldname] = $event"
							/>
						</div>
					</div>
				</div>

				<div class="px-6 pb-6">
					<Button
						variant="solid"
						size="lg"
						class="w-full"
						:loading="submit_resource.loading"
						type="submit"
					>
						{{ __("Submit") }}
					</Button>
				</div>
			</form>
		</div>

		<div v-else-if="load_error" class="text-center">
			<div class="bg-surface-amber-1 border border-outline-amber-1 rounded-lg p-8">
				<LucideAlertCircle class="w-16 h-16 text-ink-amber-3 mx-auto mb-4" />
				<h2 class="text-ink-amber-3 font-semibold text-xl mb-2">
					{{ __("Not Found") }}
				</h2>
				<p class="text-ink-amber-2">
					{{ load_error }}
				</p>
			</div>
		</div>
	</div>
</template>

<script setup>
import CustomFieldInput from "@/components/CustomFieldInput.vue";
import LoginRequired from "@/components/LoginRequired.vue";
import { Button, Spinner, createResource, toast } from "frappe-ui";
import { marked } from "marked";
import { computed, reactive, ref } from "vue";
import LucideAlertCircle from "~icons/lucide/alert-circle";
import LucideCheckCircle from "~icons/lucide/check-circle";

const form_data = ref(null);
const form_values = reactive({});
const submitted = ref(false);
const login_required = ref(false);
const load_error = ref(null);

const rendered_success_message = computed(() => {
	const msg = form_data.value?.success_message;
	if (!msg) return "";
	return marked(msg);
});

const field_sections = computed(() => {
	const fields = form_data.value?.form_fields || [];
	const sections = [];
	let current_section = [[]];
	for (const field of fields) {
		if (field.fieldtype === "Section Break") {
			if (current_section.some((col) => col.length)) {
				sections.push(current_section);
			}
			current_section = [[]];
			continue;
		}
		if (field.fieldtype === "Column Break") {
			current_section.push([]);
			continue;
		}
		current_section[current_section.length - 1].push(field);
	}
	if (current_section.some((col) => col.length)) {
		sections.push(current_section);
	}
	return sections;
});

const form_data_resource = createResource({
	url: "buzz.api.forms.get_event_proposal_form_data",
	auto: true,
	onSuccess: (data) => {
		form_data.value = data;
		for (const field of data.form_fields || []) {
			if (field.default) {
				form_values[field.fieldname] = field.default;
			}
		}
	},
	onError: (err) => {
		if (err.exc_type === "AuthenticationError") {
			login_required.value = true;
			return;
		}
		load_error.value = err.messages?.[0] || __("Form not found");
	},
});

const submit_resource = createResource({
	url: "buzz.api.forms.submit_event_proposal",
	onSuccess: () => {
		submitted.value = true;
	},
	onError: (err) => {
		const messages = err.messages || [];
		const msg = messages.find((m) => typeof m === "string" && m.trim());
		toast.error(msg || __("Failed to submit proposal"));
	},
});

function handleSubmit() {
	submit_resource.submit({ data: { ...form_values } });
}
</script>
