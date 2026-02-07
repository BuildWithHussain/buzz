<template>
	<div>
		<ListView
			v-if="bookings.data"
			:columns="columns"
			:rows="bookings.data"
			row-key="name"
			:options="{
				selectable: false,
				getRowRoute: (row) => ({
					name: 'booking-details',
					params: { bookingId: row.name },
				}),
				emptyState: {
					title: __('No bookings found'),
					description: __('You haven\'t made any bookings yet.'),
				},
			}"
		>
			<template #cell="{ item, row, column }">
				<Badge
					v-if="column.key === 'status'"
					:theme="row.status === 'Confirmed' ? 'green' : 'red'"
					variant="subtle"
					size="sm"
				>
					{{ item }}
				</Badge>
				<span v-else>{{ item }}</span>
			</template>
		</ListView>
	</div>
</template>

<script setup>
import { ListView, useList, Badge } from "frappe-ui";
import { session } from "../data/session";
import { formatCurrency } from "@/utils/currency";
import { dayjsLocal } from "frappe-ui";
import { pluralize } from "@/utils/pluralize";

const columns = [
	{ label: __("Event"), key: "event_title" },
	{ label: "", key: "ticket_count" },
	{ label: __("Start Date"), key: "start_date" },
	{ label: __("Venue"), key: "venue" },
	{ label: __("Amount Paid"), key: "formatted_amount" },
	{ label: __("Status"), key: "status" },
];

const bookings = useList({
	doctype: "Event Booking",
	fields: [
		"name",
		"event",
		"event.title as event_title",
		"event.start_date",
		"event.venue",
		"docstatus",
		"total_amount",
		"currency",
		"creation",
		{ attendees: ["ticket_type"] },
	],
	filters: { user: session.user, docstatus: ["!=", "0"] },
	orderBy: "creation desc",
	realtime: true,
	auto: true,
	cacheKey: "bookings-list",
	onError: console.error,
	transform(data) {
		return data.map((booking) => ({
			...booking,
			formatted_amount:
				booking.total_amount !== 0
					? formatCurrency(booking.total_amount, booking.currency)
					: __("FREE"),
			status: booking.docstatus === 1 ? __("Confirmed") : __("Cancelled"),
			start_date: dayjsLocal(booking.start_date).format("MMM DD, YYYY"),
			ticket_count: pluralize(
				booking.attendees ? booking.attendees.length : 0,
				__("Ticket")
			),
		}));
	},
});
</script>
