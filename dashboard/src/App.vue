<script setup lang="ts">
import { FrappeUIProvider, setConfig } from "frappe-ui";
import { computed } from "vue";
import { useRoute } from "vue-router";
import Layout from "./layouts/Layout.vue";
import MobileLayout from "./layouts/MobileLayout.vue";

const route = useRoute();

const isMobileRoute = computed(() => {
	return route.name === "checkin-scanner";
});

interface WindowWithTimezone extends Window {
	timezone?: {
		system?: string;
		user?: string;
	};
}

const windowWithTimezone = window as WindowWithTimezone;
setConfig("systemTimezone", windowWithTimezone.timezone?.system || null);
setConfig("localTimezone", windowWithTimezone.timezone?.user || null);
</script>

<template>
	<FrappeUIProvider>
		<MobileLayout v-if="isMobileRoute">
			<router-view />
		</MobileLayout>
		<Layout v-else>
			<router-view />
		</Layout>
	</FrappeUIProvider>
</template>
