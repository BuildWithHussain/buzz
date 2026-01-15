import { test, expect } from "@playwright/test";

test("should login successfully with valid credentials", async ({ page }) => {
	await page.goto("/login");

	const username = process.env.FRAPPE_USER || "Administrator";
	const password = process.env.FRAPPE_PASSWORD || "admin";

	await page.getByLabel("Email").fill(username);
	await page.getByLabel("Password").fill(password);

	await page.getByRole("button", { name: "Login" }).click();

	await expect(page).not.toHaveURL(/.*login.*/);
	await page.waitForLoadState("networkidle");

	const loggedInUser = await page.evaluate(() => frappe.session.user);
	expect(loggedInUser).toBe(username);
});
