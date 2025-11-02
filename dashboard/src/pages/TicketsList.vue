<template>
	<div>
		<div v-if="tickets.loading" class="flex justify-center py-8">
			<div class="text-ink-gray-6">Loading tickets...</div>
		</div>

		<div
			v-else-if="tickets.error"
			class="bg-surface-red-1 border border-outline-red-1 rounded-lg p-4"
		>
			<p class="text-ink-red-3">Error loading tickets: {{ tickets.error.message }}</p>
		</div>

		<ListView
			v-else
			:columns="columns"
			:rows="tickets.data || []"
			row-key="name"
			:options="{
				selectable: false,
				getRowRoute: (row) => ({
					name: 'ticket-details',
					params: { ticketId: row.name },
				}),
				emptyState: {
					title: 'No tickets found',
					description: 'You haven\'t purchased any tickets yet.',
				},
			}"
		>
			<template #cell="{ item }">
				<span>{{ item }}</span>
			</template>
		</ListView>
	</div>
</template>

<script setup>
import { ListView, useList } from "frappe-ui";
import { session } from "../data/session";
import { dayjsLocal } from "frappe-ui";

const columns = [
	{ label: "Attendee Name", key: "attendee_name" },
	{ label: "Event", key: "event_title" },
	{ label: "Ticket Type", key: "ticket_type_display" },
	{ label: "Start Date", key: "start_date" },
];

const tickets = useList({
	doctype: "Event Ticket",
	fields: [
		"name",
		"attendee_name",
		"attendee_email",
		"ticket_type",
		"ticket_type.title as ticket_type_title",
		"event",
		"event.title as event_title",
		"event.start_date",
		"creation",
	],
	filters: {
		attendee_email: session.user,
		docstatus: ["!=", 0],
	},
	orderBy: "creation desc",
	realtime: true,
	auto: true,
	cacheKey: "tickets-list",
	onError: console.error,
	transform(data) {
		return data.map((ticket) => ({
			...ticket,
			start_date: dayjsLocal(ticket.start_date).format("MMM DD, YYYY"),
			ticket_type_display: ticket.ticket_type_title || ticket.ticket_type,
		}));
	},
});
</script>
