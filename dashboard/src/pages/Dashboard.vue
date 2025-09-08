<template>
	<div class="space-y-4">
		<RouterLink
			:to="{ name: 'bookings-list' }"
			class="text-ink-blue-3 hover:underline mb-4 block"
		>
			My Bookings
		</RouterLink>
		<RouterLink
			:to="{ name: 'schedule-gantt-poc' }"
			class="text-ink-green-3 hover:underline mb-4 block"
		>
			📅 Schedule Gantt POC - Event Scheduling with Gantt Chart
		</RouterLink>
	</div>
</template>

<script setup></script>
