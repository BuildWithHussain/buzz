import { userResource } from "@/data/user";
import { createRouter, createWebHistory } from "vue-router";
import { session } from "./data/session";

const routes = [
	{
		path: "/",
		name: "dashboard",
		redirect: { name: "bookings-tab" },
	},
	{
		path: "/check-in",
		name: "check-in",
		component: () => import("@/pages/CheckInScanner.vue"),
	},
	{
		path: "/book-tickets/:eventRoute",
		props: true,
		name: "event-booking",
		meta: { isPublic: true },
		component: () => import("@/pages/BookTickets.vue"),
	},
	{
		path: "/register-interest/:campaign",
		props: true,
		name: "register-interest",
		component: () => import("@/pages/RegisterInterest.vue"),
	},
	{
		path: "/bookings",
		name: "bookings-tab",
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
		path: "/tickets",
		redirect: "/account/tickets",
	},
	{
		path: "/tickets/:ticketId",
		redirect: (to) => ({
			name: "ticket-details",
			params: { ticketId: to.params.ticketId },
		}),
		props: true,
	},
	{
		path: "/account",
		component: () => import("@/pages/Account.vue"),
		redirect: { name: "bookings-list" },
		children: [
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
				path: "tickets",
				name: "tickets-list",
				component: () => import("@/pages/TicketsList.vue"),
			},
			{
				path: "tickets/:ticketId",
				props: true,
				name: "ticket-details",
				component: () => import("@/pages/TicketDetails.vue"),
			},
			{
				path: "proposals",
				name: "proposals-list",
				component: () => import("@/pages/ProposalsList.vue"),
			},
			{
				path: "proposals/:proposalId",
				props: true,
				name: "proposal-details",
				component: () => import("@/pages/ProposalDetails.vue"),
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
		await userResource.fetch();
	} catch (error) {
		isLoggedIn = false;
	}

	if (to.meta?.isPublic) {
		next();
		return;
	}

	if (to.name === "Login" && isLoggedIn) {
		next({ name: "dashboard" });
	} else if (to.name !== "Login" && !isLoggedIn) {
		window.location.href = `/login?redirect-to=/dashboard${encodeURIComponent(to.fullPath)}`;
	} else {
		next();
	}
});

export default router;
