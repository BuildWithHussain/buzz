<template>
	<div>
		<ListView
			v-if="proposals.data"
			:columns="columns"
			:rows="proposals.data"
			row-key="name"
			:options="{
				selectable: false,
				getRowRoute: (row) => ({
					name: 'proposal-details',
					params: { proposalId: row.name },
				}),
				emptyState: {
					title: __('No proposals yet'),
					description: __('Your talk proposals will appear here'),
				},
			}"
		>
			<template #cell="{ item, row, column }">
				<Badge
					v-if="column.key === 'status'"
					:theme="getStatusTheme(row.status)"
					variant="subtle"
					size="sm"
				>
					{{ item }}
				</Badge>
				<span v-else>{{ item }}</span>
			</template>
		</ListView>

		<div v-else-if="proposals.loading" class="w-4">
			<Spinner />
		</div>

		<div v-else-if="proposals.data && proposals.data.length === 0" class="text-center py-8">
			<div class="text-ink-gray-5 text-lg mb-2">
				{{ __("No proposals yet") }}
			</div>
			<div class="text-ink-gray-4 text-sm">
				{{ __("Your talk proposals will appear here") }}
			</div>
		</div>
	</div>
</template>

<script setup>
import { ListView, Badge, Spinner, useList, dayjsLocal } from "frappe-ui";
import { session } from "@/data/session";

const columns = [
	{ label: __("Title"), key: "title" },
	{ label: __("Event"), key: "event_title" },
	{ label: __("Status"), key: "status" },
	{ label: __("Submitted"), key: "formatted_creation" },
];

const proposals = useList({
	doctype: "Talk Proposal",
	fields: ["name", "title", "event.title as event_title", "status", "creation"],
	filters: {
		submitted_by: session.user,
	},
	orderBy: "creation desc",
	auto: true,
	cacheKey: ["proposals-list", session.user],
	transform(data) {
		return data.map((proposal) => ({
			...proposal,
			formatted_creation: dayjsLocal(proposal.creation).format("MMM DD, YYYY"),
		}));
	},
});

const getStatusTheme = (status) => {
	switch (status) {
		case "Accepted":
			return "green";
		case "Shortlisted":
			return "blue";
		case "Review Pending":
			return "orange";
		case "Rejected":
			return "red";
		default:
			return "gray";
	}
};
</script>
