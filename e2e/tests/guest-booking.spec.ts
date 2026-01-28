import { test, expect } from "@playwright/test";
import { BookingPage } from "../pages";

// Unique suffix per run to avoid rate limits
const uid = Date.now();

test.describe("Guest Booking", () => {
	test("guest booking without OTP", async ({ page }) => {
		const email = `guest-no-otp-${uid}@test.com`;
		const bookingPage = new BookingPage(page);
		await bookingPage.goto("guest-no-otp-e2e");
		await bookingPage.waitForFormLoad();

		await page.locator('input[placeholder="Enter your name"]').fill("Test Guest");
		await page.locator('input[placeholder="Enter your email"]').fill(email);

		await page.locator('input[placeholder="Enter full name"]').first().fill("Test Guest");
		await page.locator('input[placeholder="Enter email address"]').first().fill(email);

		await bookingPage.submit();

		await expect(page.getByText("Booking Confirmed!")).toBeVisible({ timeout: 30000 });
	});

	test("guest booking with Email OTP", async ({ page }) => {
		const email = `guest-email-otp-${uid}@test.com`;
		const bookingPage = new BookingPage(page);
		await bookingPage.goto("guest-email-otp-e2e");
		await bookingPage.waitForFormLoad();

		await page.locator('input[placeholder="Enter your name"]').fill("Test Guest Email");
		await page.locator('input[placeholder="Enter your email"]').fill(email);

		await page.locator('input[placeholder="Enter full name"]').first().fill("Test Guest Email");
		await page.locator('input[placeholder="Enter email address"]').first().fill(email);

		const otpResponsePromise = page.waitForResponse(
			(resp) =>
				resp.url().includes("send_guest_booking_otp") &&
				!resp.url().includes("sms") &&
				resp.status() === 200,
		);

		await bookingPage.submit();

		const otpResponse = await otpResponsePromise;
		const otpData = (await otpResponse.json()) as { message?: { otp?: string } };
		const otp = otpData.message?.otp;
		expect(otp).toBeTruthy();

		await expect(page.getByText("Verify Your Email")).toBeVisible({ timeout: 10000 });

		await page.locator('input[placeholder="123456"]').fill(otp!);
		await page.getByRole("button", { name: "Verify & Book" }).click();

		await expect(page.getByText("Booking Confirmed!")).toBeVisible({ timeout: 30000 });
	});

	test("guest booking with Phone OTP", async ({ page }) => {
		const email = `guest-phone-otp-${uid}@test.com`;
		const phone = `9${uid.toString().slice(-9)}`;
		const bookingPage = new BookingPage(page);
		await bookingPage.goto("guest-phone-otp-e2e");
		await bookingPage.waitForFormLoad();

		await page.locator('input[placeholder="Enter your name"]').fill("Test Guest Phone");
		await page.locator('input[placeholder="Enter your email"]').fill(email);
		await page.locator('input[placeholder="Enter your phone number"]').fill(phone);

		await page.locator('input[placeholder="Enter full name"]').first().fill("Test Guest Phone");
		await page.locator('input[placeholder="Enter email address"]').first().fill(email);

		const otpResponsePromise = page.waitForResponse(
			(resp) => resp.url().includes("send_guest_booking_otp_sms") && resp.status() === 200,
		);

		await bookingPage.submit();

		const otpResponse = await otpResponsePromise;
		const otpData = (await otpResponse.json()) as { message?: { otp?: string } };
		const otp = otpData.message?.otp;
		expect(otp).toBeTruthy();

		await expect(page.getByText("Verify Your Phone")).toBeVisible({ timeout: 10000 });

		await page.locator('input[placeholder="123456"]').fill(otp!);
		await page.getByRole("button", { name: "Verify & Book" }).click();

		await expect(page.getByText("Booking Confirmed!")).toBeVisible({ timeout: 30000 });
	});
});
