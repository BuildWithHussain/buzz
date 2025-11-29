<template>
	<ProfileView />
	<Tabs as="div" v-model="tabIndex" :tabs="tabs" @change="handleTabChange">
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
import { useRoute, useRouter } from "vue-router";
import ProfileView from "@/components/ProfileView.vue";

const route = useRoute();
const router = useRouter();

const tabs = [
	{ label: __("My Bookings"), name: "bookings-list" },
	{ label: __("My Tickets"), name: "tickets-list" },
	{ label: __("Sponsorships"), name: "sponsorships-list" },
];

// Find the tab index based on current route path
const getTabIndexFromRoute = () => {
	const currentPath = route.path;

	// Check path patterns for each tab
	if (currentPath.startsWith("/account/bookings")) {
		return tabs.findIndex((tab) => tab.name === "bookings-list");
	}
	if (currentPath.startsWith("/account/tickets")) {
		return tabs.findIndex((tab) => tab.name === "tickets-list");
	}
	if (currentPath.startsWith("/account/sponsorships")) {
		return tabs.findIndex((tab) => tab.name === "sponsorships-list");
	}
	if (currentPath.startsWith("/account/profile")) {
		return tabs.findIndex((tab) => tab.name === "profile");
	}

	// Default to first tab
	return 0;
};

const tabIndex = ref(getTabIndexFromRoute());

// Watch for route changes and update tab index
watch(
	() => route.path,
	() => {
		tabIndex.value = getTabIndexFromRoute();
	}
);

// Handle tab change and navigate to corresponding route
const handleTabChange = (newTabIndex) => {
	const selectedTab = tabs[newTabIndex];
	if (selectedTab && selectedTab.name !== route.name) {
		router.push({ name: selectedTab.name });
	}
};
</script>
