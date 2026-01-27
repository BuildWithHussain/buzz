import { test, expect } from "@playwright/test";
import { BookingPage } from "../pages";

// Unique suffix per run to avoid rate limits (5/hour per email/phone)
const uid = Date.now();

test.describe("Guest Booking", () => {
	test("guest booking without OTP", async ({ page }) => {
		const email = `guest-no-otp-${uid}@test.com`;
		const bookingPage = new BookingPage(page);
		await bookingPage.goto("guest-no-otp-e2e");
		await bookingPage.waitForFormLoad();

		// Fill guest details (exact placeholders to avoid matching attendee fields)
		await page.locator('input[placeholder="Enter your name"]').fill("Test Guest");
		await page.locator('input[placeholder="Enter your email"]').fill(email);

		// Fill attendee details (exact placeholders to avoid matching guest fields)
		await page.locator('input[placeholder="Enter full name"]').first().fill("Test Guest");
		await page.locator('input[placeholder="Enter email address"]').first().fill(email);

		// Submit
		await bookingPage.submit();

		// Assert booking confirmed
		await expect(page.getByText("Booking Confirmed!")).toBeVisible({ timeout: 30000 });
	});

	test("guest booking with Email OTP", async ({ page }) => {
		const email = `guest-email-otp-${uid}@test.com`;
		const bookingPage = new BookingPage(page);
		await bookingPage.goto("guest-email-otp-e2e");
		await bookingPage.waitForFormLoad();

		// Fill guest details
		await page.locator('input[placeholder="Enter your name"]').fill("Test Guest Email");
		await page.locator('input[placeholder="Enter your email"]').fill(email);

		// Fill attendee details
		await page.locator('input[placeholder="Enter full name"]').first().fill("Test Guest Email");
		await page.locator('input[placeholder="Enter email address"]').first().fill(email);

		// Intercept OTP response before clicking submit
		const otpResponsePromise = page.waitForResponse(
			(resp) =>
				resp.url().includes("send_guest_booking_otp") &&
				!resp.url().includes("sms") &&
				resp.status() === 200,
		);

		await bookingPage.submit();

		// Extract OTP from API response (e2e_test_mode returns it)
		const otpResponse = await otpResponsePromise;
		const otpData = (await otpResponse.json()) as { message?: { otp?: string } };
		const otp = otpData.message?.otp;
		expect(otp).toBeTruthy();

		// OTP modal should appear
		await expect(page.getByText("Verify Your Email")).toBeVisible({ timeout: 10000 });

		// Enter OTP and verify
		await page.locator('input[placeholder="123456"]').fill(otp!);
		await page.getByRole("button", { name: "Verify & Book" }).click();

		// Assert booking confirmed
		await expect(page.getByText("Booking Confirmed!")).toBeVisible({ timeout: 30000 });
	});

	test("guest booking with Phone OTP", async ({ page }) => {
		const email = `guest-phone-otp-${uid}@test.com`;
		const phone = `9${uid.toString().slice(-9)}`;
		const bookingPage = new BookingPage(page);
		await bookingPage.goto("guest-phone-otp-e2e");
		await bookingPage.waitForFormLoad();

		// Fill guest details (phone field appears for Phone OTP)
		await page.locator('input[placeholder="Enter your name"]').fill("Test Guest Phone");
		await page.locator('input[placeholder="Enter your email"]').fill(email);
		await page.locator('input[placeholder="Enter your phone number"]').fill(phone);

		// Fill attendee details
		await page.locator('input[placeholder="Enter full name"]').first().fill("Test Guest Phone");
		await page.locator('input[placeholder="Enter email address"]').first().fill(email);

		// Intercept OTP SMS response before clicking submit
		const otpResponsePromise = page.waitForResponse(
			(resp) => resp.url().includes("send_guest_booking_otp_sms") && resp.status() === 200,
		);

		await bookingPage.submit();

		// Extract OTP from API response (e2e_test_mode returns it)
		const otpResponse = await otpResponsePromise;
		const otpData = (await otpResponse.json()) as { message?: { otp?: string } };
		const otp = otpData.message?.otp;
		expect(otp).toBeTruthy();

		// OTP modal should appear
		await expect(page.getByText("Verify Your Phone")).toBeVisible({ timeout: 10000 });

		// Enter OTP and verify
		await page.locator('input[placeholder="123456"]').fill(otp!);
		await page.getByRole("button", { name: "Verify & Book" }).click();

		// Assert booking confirmed
		await expect(page.getByText("Booking Confirmed!")).toBeVisible({ timeout: 30000 });
	});
});
