<template>
	<div class="flex items-center justify-center min-h-[75vh] w-full">
		<div
			class="w-full max-w-md space-y-6 rounded-xl bg-surface-white border border-outline-gray-3 p-6 shadow-sm sm:p-8"
		>
			<div v-if="pageState === 'loading'" class="flex justify-center py-12">
				<LoadingIndicator class="h-8 w-8 text-ink-gray-4" />
			</div>

			<div v-else-if="pageState === 'error'" class="text-center">
				<div
					class="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-surface-red-2"
				>
					<FeatherIcon name="alert-circle" class="h-6 w-6 text-ink-red-3" />
				</div>
				<h2 class="mt-4 text-lg font-semibold text-ink-gray-9">
					{{ __("Unable to Load") }}
				</h2>
				<p class="mt-2 text-base text-ink-gray-5">{{ __(errorMessage) }}</p>
			</div>

			<div
				v-else-if="pageState === 'success' || pageState === 'submitted'"
				class="text-center"
			>
				<div
					class="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-surface-blue-2"
				>
					<FeatherIcon name="check" class="h-6 w-6 text-ink-blue-3" />
				</div>

				<h2 class="mt-4 text-lg font-semibold text-ink-gray-9">
					{{ __("Feedback Received") }}
				</h2>
				<p class="mt-2 text-base text-ink-gray-5">
					{{ __("Thanks {0} for reviewing {1}!", [attendeeName, eventName]) }}
				</p>

				<div class="mt-6 rounded-lg bg-surface-gray-2 p-4 border border-outline-gray-2">
					<div class="mb-2 flex flex-col items-center justify-center">
						<Rating :modelValue="form.rating" readonly size="lg" />
						<div class="mt-2 flex items-center space-x-1.5" v-if="form.rating > 0">
							<span class="text-lg">{{ ratingLevels[form.rating - 1].icon }}</span>
							<span class="text-sm font-medium text-ink-gray-7">
								{{ ratingLevels[form.rating - 1].label }}
							</span>
						</div>
					</div>
					<p v-if="existingComment" class="text-base italic text-ink-gray-7 text-center">
						"{{ existingComment }}"
					</p>
				</div>
			</div>

			<div v-else>
				<div class="text-center mb-4">
					<p class="text-lg font-medium text-ink-gray-5">
						{{ __("Hi {0}!", [attendeeName]) }}
					</p>
					<h2 class="mt-1 text-2xl font-bold text-ink-gray-9">
						{{ __("How was {0}?", [eventName]) }}
					</h2>
				</div>

				<div class="space-y-6">
					<div class="flex flex-col items-center justify-center py-2">
						<p class="text-sm font-medium text-ink-gray-5 mb-1">
							{{ __("Rate your experience") }} <span class="text-red-500">*</span>
						</p>

						<Rating v-model="form.rating" size="xl" :rating_from="5" />
						<div
							class="mt-1 h-8 flex items-center justify-center space-x-2 transition-all"
							v-if="form.rating > 0"
						>
							<span class="text-lg">
								{{ ratingLevels[form.rating - 1].icon }}
							</span>
							<span class="text-sm text-ink-gray-9">
								{{ ratingLevels[form.rating - 1].label }}
							</span>
						</div>
					</div>

					<FormControl
						type="textarea"
						v-model="form.comment"
						:placeholder="__('Share your experience...')"
						:rows="4"
					/>

					<div
						v-if="submitError"
						class="text-center bg-surface-red-1 p-2 rounded border border-outline-red-2"
					>
						<p class="text-sm font-medium text-ink-red-3">
							{{ submitError }}
						</p>
					</div>

					<Button
						variant="solid"
						size="md"
						class="w-full justify-center"
						:loading="submitFeedback.loading"
						@click="submitFeedback.submit()"
					>
						{{ __("Submit Feedback") }}
					</Button>
				</div>
			</div>
		</div>
	</div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from "vue";
import { useRoute } from "vue-router";
import {
	createResource,
	FormControl,
	Button,
	LoadingIndicator,
	Rating,
	FeatherIcon,
} from "frappe-ui";

const route = useRoute();

// Reactive States
const pageState = ref("loading");
const errorMessage = ref("");
const attendeeName = ref("");
const eventName = ref("");
const existingComment = ref("");
const submitError = ref("");

const form = reactive({
	ticket: route.query.ticket,
	comment: "",
	rating: 0,
});

const ratingLevels = computed(() => [
	{ icon: "😡", label: __("Terrible") },
	{ icon: "☹️", label: __("Bad") },
	{ icon: "😐", label: __("Average") },
	{ icon: "🙂", label: __("Good") },
	{ icon: "😍", label: __("Excellent") },
]);

const getFeedback = createResource({
	url: "buzz.api.get_feedback",
	params: {
		ticket: route.query.ticket,
	},
	auto: false,
	onSuccess(data) {
		if (data.attendee_name) attendeeName.value = data.attendee_name;
		if (data.event_title) eventName.value = data.event_title;

		if (data.status === "submitted") {
			existingComment.value = data.comment;
			form.rating = data.rating;
		}
		pageState.value = data.status;
	},
	onError(error) {
		pageState.value = "error";
		const msg = (errorMessage.value = error?.messages?.[0] || "Something went wrong");
		errorMessage.value = msg;
	},
});

const submitFeedback = createResource({
	url: "buzz.api.submit_feedback",
	makeParams() {
		return {
			ticket: form.ticket,
			comment: form.comment,
			rating: form.rating,
		};
	},
	validate() {
		submitError.value = "";
		if (form.rating === 0) {
			const msg = __("Please provide a rating.");
			submitError.value = msg;
			return msg;
		}
	},
	onSuccess() {
		pageState.value = "success";
		existingComment.value = form.comment;
	},
	onError(error) {
		const msg = (errorMessage.value =
			error?.messages?.[0] || error?.message || "Something went wrong");
		submitError.value = msg;
	},
});

onMounted(() => {
	if (!form.ticket) {
		pageState.value = "error";
		errorMessage.value = __("Invalid Link.");
	} else {
		getFeedback.submit();
	}
});
</script>
