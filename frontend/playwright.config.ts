import { defineConfig, devices } from '@playwright/test';

const baseURL = process.env.BASE_URL || 'http://localhost/';
const evidenceMode = process.env.E2E_EVIDENCE === '1';
const executablePath = process.env.PLAYWRIGHT_EXECUTABLE_PATH || (process.platform === 'linux' ? '/usr/bin/chromium' : undefined);

export default defineConfig({
  testDir: './e2e',
  fullyParallel: false,
  forbidOnly: Boolean(process.env.CI),
  retries: process.env.CI ? 2 : 0,
  workers: 1,
  reporter: [
    ['list'],
    ['html', { outputFolder: 'playwright-report', open: 'never' }],
  ],
  outputDir: 'test-results',
  use: {
    ...devices['Desktop Chrome'],
    baseURL,
    headless: true,
    acceptDownloads: true,
    trace: 'retain-on-failure',
    screenshot: evidenceMode ? 'on' : 'only-on-failure',
    video: 'retain-on-failure',
    launchOptions: {
      ...(executablePath ? { executablePath } : {}),
      args: process.platform === 'linux' ? ['--no-sandbox'] : [],
    },
  },
});
