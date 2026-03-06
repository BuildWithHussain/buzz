<template>
	<ProfileView />
	<Tabs as="div" v-model="tabIndex" :tabs="tabs">
		<template #tab-panel>
			<div class="py-5">
				<router-view></router-view>
			</div>
		</template>
	</Tabs>
</template>

<script setup>
import { Tabs } from "frappe-ui";
import { ref, watch } from "vue";
import { useRoute } from "vue-router";
import ProfileView from "@/components/ProfileView.vue";
import LucideCalendarDays from "~icons/lucide/calendar-days";
import LucideTicket from "~icons/lucide/ticket";
import LucideMegaphone from "~icons/lucide/megaphone";
import LucideCircleDollarSign from "~icons/lucide/circle-dollar-sign";

const route = useRoute();

const tabs = [
	{ label: __("My Bookings"), route: "/account/bookings", icon: LucideCalendarDays },
	{ label: __("My Tickets"), route: "/account/tickets", icon: LucideTicket },
	{ label: __("Talk Proposals"), route: "/account/proposals", icon: LucideMegaphone },
	{ label: __("Sponsorships"), route: "/account/sponsorships", icon: LucideCircleDollarSign },
];

// Find the tab index based on current route path
const getTabIndexFromRoute = () => {
	const currentPath = route.path;
	const index = tabs.findIndex((tab) => currentPath.startsWith(tab.route));
	return index >= 0 ? index : 0;
};

const tabIndex = ref(getTabIndexFromRoute());

// Watch for route changes and update tab index
watch(
	() => route.path,
	() => {
		tabIndex.value = getTabIndexFromRoute();
	}
);
</script>
