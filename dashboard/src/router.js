import { userResource } from "@/data/user";
import { createRouter, createWebHistory } from "vue-router";
import { session } from "./data/session";

const routes = [
	{
		path: "/",
		name: "dashboard",
		component: () => import("@/pages/Dashboard.vue"),
	},
	{
		path: "/book-tickets/:eventRoute",
		props: true,
		name: "event-booking",
		component: () => import("@/pages/BookTickets.vue"),
	},
	{
		path: "/bookings",
		redirect: "/account/bookings",
	},
	{
		path: "/bookings/:bookingId",
		redirect: (to) => ({
			name: "booking-details",
			params: { bookingId: to.params.bookingId },
		}),
		props: true,
	},
	{
		path: "/account",
		component: () => import("@/pages/Account.vue"),
		redirect: { name: "profile" },
		children: [
			{
				path: "",
				name: "profile",
				component: () => import("@/pages/Profile.vue"),
			},
			{
				path: "bookings",
				name: "bookings-list",
				component: () => import("@/pages/BookingsList.vue"),
				default: true,
			},
			{
				path: "bookings/:bookingId",
				props: true,
				name: "booking-details",
				component: () => import("@/pages/BookingDetails.vue"),
			},
			{
				path: "sponsorships",
				name: "sponsorships-list",
				component: () => import("@/pages/SponsorshipsList.vue"),
			},
			{
				path: "sponsorships/:enquiryId",
				props: true,
				name: "sponsorship-details",
				component: () => import("@/pages/SponsorshipDetails.vue"),
			},
		],
	},
];

const router = createRouter({
	history: createWebHistory("/dashboard"),
	routes,
});

router.beforeEach(async (to, from, next) => {
	let isLoggedIn = session.isLoggedIn;
	try {
		await userResource.promise;
	} catch (error) {
		isLoggedIn = false;
	}

	if (to.name === "Login" && isLoggedIn) {
		next({ name: "Home" });
	} else if (to.name !== "Login" && !isLoggedIn) {
		window.location.href = `/login?redirect-to=${encodeURIComponent(to.fullPath)}`;
	} else {
		next();
	}
});

export default router;
