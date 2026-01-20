// @ts-check
import { defineConfig, devices } from "@playwright/test";

// Auth state file path
const authFile = "e2e/.auth/user.json";

/**
 * Read environment variables from file.
 * https://github.com/motdotla/dotenv
 */
// import dotenv from 'dotenv';
// import path from 'path';
// dotenv.config({ path: path.resolve(__dirname, '.env') });

/**
 * @see https://playwright.dev/docs/test-configuration
 */
export default defineConfig({
	testDir: "./e2e/tests",
	/* Run tests in files in parallel */
	fullyParallel: true,
	/* Fail the build on CI if you accidentally left test.only in the source code. */
	forbidOnly: !!process.env.CI,
	/* Retry on CI only */
	retries: process.env.CI ? 2 : 0,
	/* Opt out of parallel tests on CI. */
	workers: process.env.CI ? 1 : undefined,
	/* Reporter to use. See https://playwright.dev/docs/test-reporters */
	reporter: process.env.CI ? [["github"], ["html", { open: "never" }]] : "html",

	timeout: 60000,
	expect: {
		timeout: 10000,
	},

	/* Shared settings for all the projects below. See https://playwright.dev/docs/api/class-testoptions. */
	use: {
		baseURL: process.env.BASE_URL || "http://buzz.test:8000",
		trace: "on-first-retry",
		video: "retain-on-failure",
		screenshot: "only-on-failure",
		actionTimeout: 15000,
		navigationTimeout: 30000,
	},

	/* Configure projects for major browsers */
	projects: [
		{
			name: "setup",
			testMatch: /auth\.setup\.js/,
		},
		{
			name: "event-setup",
			testMatch: /event\.setup\.js/,
			use: {
				storageState: authFile,
			},
			dependencies: ["setup"],
		},
		{
			name: "chromium",
			use: {
				...devices["Desktop Chrome"],
				storageState: authFile,
			},
			dependencies: ["setup", "event-setup"],
		},

		// {
		// 	name: "firefox",
		// 	use: { ...devices["Desktop Firefox"] },
		// },

		// {
		// 	name: "webkit",
		// 	use: { ...devices["Desktop Safari"] },
		// },

		/* Test against mobile viewports. */
		// {
		//   name: 'Mobile Chrome',
		//   use: { ...devices['Pixel 5'] },
		// },
		// {
		//   name: 'Mobile Safari',
		//   use: { ...devices['iPhone 12'] },
		// },

		/* Test against branded browsers. */
		// {
		//   name: 'Microsoft Edge',
		//   use: { ...devices['Desktop Edge'], channel: 'msedge' },
		// },
		// {
		//   name: 'Google Chrome',
		//   use: { ...devices['Desktop Chrome'], channel: 'chrome' },
		// },
	],

	/* Run your local dev server before starting the tests */
	// webServer: {
	//   command: 'npm run start',
	//   url: 'http://localhost:3000',
	//   reuseExistingServer: !process.env.CI,
	// },
});
