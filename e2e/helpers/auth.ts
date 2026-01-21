import { APIRequestContext, BrowserContext, Page } from "@playwright/test";

const STORAGE_STATE_PATH = "e2e/.auth/user.json";

/**
 * Login via Frappe API (faster than UI login).
 * Sets cookies on the request context for subsequent API calls.
 */
export async function loginViaAPI(
	request: APIRequestContext,
	email = "Administrator",
	password = "admin",
): Promise<void> {
	const response = await request.post("/api/method/login", {
		form: {
			usr: email,
			pwd: password,
		},
	});

	if (!response.ok()) {
		throw new Error(`Login failed: ${response.status()} ${await response.text()}`);
	}
}

/**
 * Login via UI (for testing the login flow itself).
 */
export async function loginViaUI(
	page: Page,
	email = "Administrator",
	password = "admin",
): Promise<void> {
	await page.goto("/login");
	await page.waitForLoadState("networkidle");

	await page.fill('input[data-fieldname="email"]', email);
	await page.fill('input[data-fieldname="password"]', password);
	await page.click('button[type="submit"]');

	// Wait for redirect to desk/app
	await page.waitForURL(/\/(app|desk)/, { timeout: 30000 });
}

/**
 * Logout the current user.
 */
export async function logout(page: Page): Promise<void> {
	await page.goto("/api/method/logout");
	await page.waitForLoadState("networkidle");
}

/**
 * Save authentication state for reuse across tests.
 */
export async function saveAuthState(context: BrowserContext): Promise<void> {
	await context.storageState({ path: STORAGE_STATE_PATH });
}

/**
 * Get the storage state path for authenticated sessions.
 */
export function getStorageStatePath() {
	return STORAGE_STATE_PATH;
}

/**
 * Check if user is logged in by verifying session.
 */
export async function isLoggedIn(request: APIRequestContext): Promise<boolean> {
	try {
		const response = await request.get("/api/method/frappe.auth.get_logged_user");
		if (!response.ok()) return false;

		const data = (await response.json()) as { message?: string };
		return Boolean(data.message && data.message !== "Guest");
	} catch {
		return false;
	}
}
