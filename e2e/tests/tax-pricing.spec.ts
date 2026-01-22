import { test, expect, Page, APIRequestContext } from "@playwright/test";
import { createDoc, deleteDoc, docExists, getList, updateDoc } from "../helpers/frappe";
import { BookingPage } from "../pages";

interface NamedDoc {
	name: string;
}

interface TaxEventFixture {
	name: string;
	route: string;
	standardTicket: string;
	vipTicket: string;
	addOnTitle: string;
}

const TEST_CATEGORY = "E2E Tax Category";
const TEST_HOST = "E2E Tax Host";

const formatCurrency = (amount: number, currency = "INR") =>
	new Intl.NumberFormat("en-US", { style: "currency", currency }).format(amount);

const getSummarySection = (page: Page) =>
	page.locator("h2:has-text('Booking Summary')").locator("..");

const expectSummaryValues = async ({
	page,
	subtotal,
	taxLabel,
	taxPercentage,
	taxAmount,
	total,
	currency = "INR",
}: {
	page: Page;
	subtotal: number;
	taxLabel: string;
	taxPercentage: number;
	taxAmount: number;
	total: number;
	currency?: string;
}) => {
	const summary = getSummarySection(page);
	await expect(summary).toBeVisible();

	const subtotalRow = summary.getByText("Subtotal").locator("..");
	await expect(subtotalRow).toContainText(formatCurrency(subtotal, currency));

	const taxRow = summary.getByText(`${taxLabel} (${taxPercentage}%)`).locator("..");
	await expect(taxRow).toContainText(formatCurrency(taxAmount, currency));

	const totalRow = summary.getByRole("heading", { name: "Total" }).locator("..");
	await expect(totalRow).toContainText(formatCurrency(total, currency));
};

const cleanupEvent = async (request: APIRequestContext, eventName: string) => {
	const tiers = await getList<NamedDoc>(request, "Sponsorship Tier", {
		filters: { event: ["=", eventName] },
	});
	for (const tier of tiers) {
		await deleteDoc(request, "Sponsorship Tier", tier.name).catch(() => {});
	}

	const ticketTypes = await getList<NamedDoc>(request, "Event Ticket Type", {
		filters: { event: ["=", eventName] },
	});
	for (const ticketType of ticketTypes) {
		await deleteDoc(request, "Event Ticket Type", ticketType.name).catch(() => {});
	}

	const addOns = await getList<NamedDoc>(request, "Ticket Add-on", {
		filters: { event: ["=", eventName] },
	});
	for (const addOn of addOns) {
		await deleteDoc(request, "Ticket Add-on", addOn.name).catch(() => {});
	}

	await deleteDoc(request, "Buzz Event", eventName).catch(() => {});
};

const createTaxEvent = async (
	request: APIRequestContext,
	options: {
		title: string;
		route: string;
		taxPercentage: number;
		totalIncludesTaxes: boolean;
		standardPrice: number;
		vipPrice: number;
		addOnPrice: number;
	},
) => {
	const {
		title,
		route,
		taxPercentage,
		totalIncludesTaxes,
		standardPrice,
		vipPrice,
		addOnPrice,
	} = options;

	if (!(await docExists(request, "Event Category", TEST_CATEGORY))) {
		await createDoc(request, "Event Category", {
			name: TEST_CATEGORY,
			enabled: 1,
			slug: "e2e-tax-category",
		});
	}

	if (!(await docExists(request, "Event Host", TEST_HOST))) {
		await createDoc(request, "Event Host", {
			name: TEST_HOST,
		});
	}

	const futureDate = new Date();
	futureDate.setMonth(futureDate.getMonth() + 1);
	const startDate = futureDate.toISOString().split("T")[0];

	const event = await createDoc<NamedDoc>(request, "Buzz Event", {
		title,
		category: TEST_CATEGORY,
		host: TEST_HOST,
		start_date: startDate,
		route,
		is_published: 1,
		medium: "In Person",
	});

	await updateDoc(request, "Buzz Event", event.name, {
		apply_tax: 1,
		tax_label: "GST",
		tax_percentage: taxPercentage,
		total_includes_taxes: totalIncludesTaxes ? 1 : 0,
	});

	const standardTicket = await createDoc<NamedDoc>(request, "Event Ticket Type", {
		event: event.name,
		title: "Standard Ticket",
		price: standardPrice,
		currency: "INR",
		is_published: 1,
	});

	const vipTicket = await createDoc<NamedDoc>(request, "Event Ticket Type", {
		event: event.name,
		title: "VIP Ticket",
		price: vipPrice,
		currency: "INR",
		is_published: 1,
	});

	await updateDoc(request, "Buzz Event", event.name, {
		default_ticket_type: standardTicket.name,
	});

	const addOn = await createDoc<NamedDoc>(request, "Ticket Add-on", {
		event: event.name,
		title: "Event T-Shirt",
		price: addOnPrice,
		currency: "INR",
		enabled: 1,
	});

	return {
		name: event.name,
		route,
		standardTicket: standardTicket.name,
		vipTicket: vipTicket.name,
		addOnTitle: "Event T-Shirt",
	} satisfies TaxEventFixture;
};

const selectTicketType = async (page: Page, ticketTitle: string) => {
	const ticketTypeField = page.getByText("Ticket Type").locator("..");
	const combo = ticketTypeField.getByRole("combobox").first();
	await combo.click();
	await page.getByRole("option", { name: new RegExp(ticketTitle, "i") }).click();
};

test.describe("Tax-inclusive vs tax-exclusive pricing", () => {
	const fixtures: { exclusive?: TaxEventFixture; inclusive?: TaxEventFixture } = {};

	test.beforeAll(async ({ request }) => {
		const suffix = Date.now();

		fixtures.exclusive = await createTaxEvent(request, {
			title: `E2E Tax Exclusive ${suffix}`,
			route: `e2e-tax-exclusive-${suffix}`,
			taxPercentage: 10,
			totalIncludesTaxes: false,
			standardPrice: 100,
			vipPrice: 200,
			addOnPrice: 50,
		});

		fixtures.inclusive = await createTaxEvent(request, {
			title: `E2E Tax Inclusive ${suffix}`,
			route: `e2e-tax-inclusive-${suffix}`,
			taxPercentage: 25,
			totalIncludesTaxes: true,
			standardPrice: 100,
			vipPrice: 125,
			addOnPrice: 25,
		});
	});

	test.afterAll(async ({ request }) => {
		if (fixtures.exclusive?.name) {
			await cleanupEvent(request, fixtures.exclusive.name);
		}
		if (fixtures.inclusive?.name) {
			await cleanupEvent(request, fixtures.inclusive.name);
		}
	});

	test("exclusive tax adds tax on top of subtotal", async ({ page }) => {
		const bookingPage = new BookingPage(page);
		const fixture = fixtures.exclusive!;

		await bookingPage.goto(fixture.route);
		await bookingPage.waitForFormLoad();

		await expectSummaryValues({
			page,
			subtotal: 100,
			taxLabel: "GST",
			taxPercentage: 10,
			taxAmount: 10,
			total: 110,
		});

		await page.getByLabel(fixture.addOnTitle).check();
		await expectSummaryValues({
			page,
			subtotal: 150,
			taxLabel: "GST",
			taxPercentage: 10,
			taxAmount: 15,
			total: 165,
		});

		await selectTicketType(page, "VIP Ticket");
		await expectSummaryValues({
			page,
			subtotal: 250,
			taxLabel: "GST",
			taxPercentage: 10,
			taxAmount: 25,
			total: 275,
		});
	});

	test("inclusive tax extracts tax from ticket + add-on totals", async ({ page }) => {
		const bookingPage = new BookingPage(page);
		const fixture = fixtures.inclusive!;

		await bookingPage.goto(fixture.route);
		await bookingPage.waitForFormLoad();

		await expectSummaryValues({
			page,
			subtotal: 80,
			taxLabel: "GST",
			taxPercentage: 25,
			taxAmount: 20,
			total: 100,
		});

		await page.getByLabel(fixture.addOnTitle).check();
		await expectSummaryValues({
			page,
			subtotal: 100,
			taxLabel: "GST",
			taxPercentage: 25,
			taxAmount: 25,
			total: 125,
		});

		await selectTicketType(page, "VIP Ticket");
		await expectSummaryValues({
			page,
			subtotal: 120,
			taxLabel: "GST",
			taxPercentage: 25,
			taxAmount: 30,
			total: 150,
		});
	});
});
