import { test, expect } from "@playwright/test";
import { BookingPage } from "../pages";
import { updateDoc, getList } from "../helpers/frappe";

interface NamedDoc {
	name: string;
}

test.describe("Tax Inclusive Pricing", () => {
	const testEventRoute = "test-event-e2e";

	test("should show tax as inclusive with correct amounts", async ({ page, request }) => {
		// Find the test event
		const events = await getList<NamedDoc>(request, "Buzz Event", {
			filters: { route: ["=", testEventRoute] },
		});
		expect(events.length).toBeGreaterThan(0);
		const eventName = events[0].name;

		// Enable tax-inclusive pricing on the event
		await updateDoc(request, "Buzz Event", eventName, {
			apply_tax: 1,
			tax_inclusive: 1,
			tax_label: "GST",
			tax_percentage: 18,
		});

		const bookingPage = new BookingPage(page);
		await bookingPage.goto(testEventRoute);
		await bookingPage.waitForFormLoad();

		// Fill attendee details to trigger summary
		await bookingPage.fillAttendeeDetails("Tax Test User", "taxtest@example.com");

		// Wait for the booking summary to render
		const summarySection = page.locator("text=Booking Summary");
		await expect(summarySection).toBeVisible({ timeout: 10000 });

		// Verify tax label shows "Incl."
		const taxLine = page.locator("text=/GST.*18.*%.*Incl/");
		await expect(taxLine).toBeVisible({ timeout: 5000 });

		// Verify Total (the h3 element) equals subtotal — tax is included
		const totalHeading = page.locator("h3:has-text('Total')");
		const totalContainer = totalHeading.locator("..");
		const totalText = await totalContainer.textContent();

		const subtotalContainer = page.locator("span:text-is('Subtotal')").locator("..");
		const subtotalText = await subtotalContainer.textContent();

		// Extract numeric values
		const subtotalMatch = subtotalText?.match(/[\d,]+/);
		const totalMatch = totalText?.match(/[\d,]+/);

		expect(subtotalMatch).toBeTruthy();
		expect(totalMatch).toBeTruthy();
		// Subtotal and Total should be equal for tax-inclusive
		expect(subtotalMatch![0]).toBe(totalMatch![0]);

		console.log(`Tax inclusive test passed: Subtotal=${subtotalMatch![0]}, Total=${totalMatch![0]}`);
	});

	test("should show tax as exclusive with increased total", async ({ page, request }) => {
		// Find the test event
		const events = await getList<NamedDoc>(request, "Buzz Event", {
			filters: { route: ["=", testEventRoute] },
		});
		expect(events.length).toBeGreaterThan(0);
		const eventName = events[0].name;

		// Enable tax-exclusive pricing on the event
		await updateDoc(request, "Buzz Event", eventName, {
			apply_tax: 1,
			tax_inclusive: 0,
			tax_label: "GST",
			tax_percentage: 18,
		});

		const bookingPage = new BookingPage(page);
		await bookingPage.goto(testEventRoute);
		await bookingPage.waitForFormLoad();

		// Fill attendee details to trigger summary
		await bookingPage.fillAttendeeDetails("Tax Test User", "taxtest@example.com");

		// Wait for the booking summary to render
		const summarySection = page.locator("text=Booking Summary");
		await expect(summarySection).toBeVisible({ timeout: 10000 });

		// Verify tax label does NOT show "Incl."
		const taxLineInclusive = page.locator("text=/GST.*18.*%.*Incl/");
		await expect(taxLineInclusive).not.toBeVisible();

		// Verify tax line exists without "Incl."
		const taxLine = page.locator("text=/GST.*18.*%/");
		await expect(taxLine).toBeVisible({ timeout: 5000 });

		// For exclusive tax: total should be greater than subtotal
		const totalHeading = page.locator("h3:has-text('Total')");
		const totalContainer = totalHeading.locator("..");
		const totalText = await totalContainer.textContent();

		const subtotalContainer = page.locator("span:text-is('Subtotal')").locator("..");
		const subtotalText = await subtotalContainer.textContent();

		const subtotalMatch = subtotalText?.match(/[\d,]+/);
		const totalMatch = totalText?.match(/[\d,]+/);

		expect(subtotalMatch).toBeTruthy();
		expect(totalMatch).toBeTruthy();

		const subtotalNum = parseInt(subtotalMatch![0].replace(/,/g, ""));
		const totalNum = parseInt(totalMatch![0].replace(/,/g, ""));

		// Total should be greater than subtotal for exclusive tax
		expect(totalNum).toBeGreaterThan(subtotalNum);

		console.log(`Tax exclusive test passed: Subtotal=${subtotalNum}, Total=${totalNum}`);
	});

	// Clean up: disable tax after tests
	test.afterAll(async ({ request }) => {
		const events = await getList<NamedDoc>(request, "Buzz Event", {
			filters: { route: ["=", testEventRoute] },
		});
		if (events.length > 0) {
			await updateDoc(request, "Buzz Event", events[0].name, {
				apply_tax: 0,
				tax_inclusive: 0,
			});
		}
	});
});
