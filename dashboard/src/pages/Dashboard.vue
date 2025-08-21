<template>
	<div class="space-y-6">
		<div>
			<h1 class="text-2xl font-bold text-gray-900 mb-2">Dashboard</h1>
			<p class="text-gray-600">Welcome to the Events Management Dashboard</p>
		</div>

		<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
			<!-- User Bookings -->
			<div class="bg-white rounded-lg shadow-sm border p-6">
				<h3 class="text-lg font-semibold text-gray-900 mb-2">My Bookings</h3>
				<p class="text-gray-600 text-sm mb-4">View and manage your event bookings</p>
				<RouterLink
					:to="{ name: 'bookings-list' }"
					class="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
				>
					View Bookings
				</RouterLink>
			</div>

			<!-- Check-in Scanner -->
			<div class="bg-white rounded-lg shadow-sm border p-6">
				<h3 class="text-lg font-semibold text-gray-900 mb-2">Check-in Scanner</h3>
				<p class="text-gray-600 text-sm mb-4">Scan QR codes to check in event attendees</p>
				<RouterLink
					:to="{ name: 'checkin-scanner' }"
					class="inline-flex items-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
				>
					<template #prefix>
						<LucideQrCode class="w-4 h-4 mr-2" />
					</template>
					Open Scanner
				</RouterLink>
			</div>

			<!-- My Tickets -->
			<div class="bg-white rounded-lg shadow-sm border p-6">
				<h3 class="text-lg font-semibold text-gray-900 mb-2">My Tickets</h3>
				<p class="text-gray-600 text-sm mb-4">View your purchased tickets</p>
				<RouterLink
					:to="{ name: 'tickets-list' }"
					class="inline-flex items-center px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
				>
					View Tickets
				</RouterLink>
			</div>
		</div>
	</div>
</template>

<script setup>
import LucideQrCode from "~icons/lucide/qr-code";
</script>
