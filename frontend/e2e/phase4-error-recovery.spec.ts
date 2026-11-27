import { expect, test } from '@playwright/test';
import { installMockApi } from './mock-api';

/**
 * Phase 4A acceptance scenarios.
 *
 * The browser suite uses a deterministic mocked API so frontend recovery behavior
 * can be validated without requiring a running backend or staging database.
 */

test.describe('Phase 4A error handling and token recovery', () => {
  test('redirects once with a session-expired notice after dashboard 401', async ({ page }) => {
    await installMockApi(page);
    await page.route('**/api/assessments', async (route) => {
      await route.fulfill({ status: 401, contentType: 'application/json', body: JSON.stringify({ detail: 'Token expired' }) });
    });
    await page.addInitScript(() => {
      localStorage.setItem('auth_token', 'expired-token');
      localStorage.setItem('auth_email', 'expired@example.com');
    });
    await page.goto('/dashboard');
    await expect(page).toHaveURL(/\/login$/);
    await expect(page.getByRole('alert')).toContainText('session expired');
  });

  test('preserves assessment answers after a failed answer submission', async ({ page }) => {
    await installMockApi(page);
    await page.goto('/assessment/1');
    await page.locator('fieldset').first().locator('input[type="radio"]').last().check();
    await page.route('**/api/assessments/1/answers', async (route) => {
      await route.fulfill({ status: 503, contentType: 'application/json', body: JSON.stringify({ detail: 'temporary failure' }) });
    });
    await page.getByRole('button', { name: /Save and continue/ }).click();
    await expect(page.getByRole('alert')).toContainText('answers are still here');
    await expect(page.locator('fieldset').first().locator('input[type="radio"]').last()).toBeChecked();
  });

  test('shows a retryable error for a network failure during submission', async ({ page }) => {
    await installMockApi(page);
    await page.goto('/assessment/1');
    await page.locator('fieldset').first().locator('input[type="radio"]').last().check();
    await page.route('**/api/assessments/1/answers', (route) => route.abort('failed'));
    await page.getByRole('button', { name: /Save and continue/ }).click();
    await expect(page.getByRole('alert')).toContainText('could not reach the service');
    await expect(page.getByRole('button', { name: /Save and continue/ })).toBeEnabled();
  });

  test('does not render an empty state when dashboard loading fails', async ({ page }) => {
    await installMockApi(page);
    await page.route('**/api/assessments', async (route) => {
      await route.fulfill({ status: 500, contentType: 'application/json', body: JSON.stringify({ detail: 'server error' }) });
    });
    await page.goto('/dashboard');
    await expect(page.getByRole('alert')).toBeVisible();
    await expect(page.getByText('Start with a governance baseline')).not.toBeVisible();
    await expect(page.getByRole('button', { name: /Retry/ })).toBeVisible();
  });

  test('shows export failure without losing the loaded report', async ({ page }) => {
    await installMockApi(page);
    await page.goto('/report/1');
    await page.route('**/api/assessments/1/export/csv', async (route) => {
      await route.fulfill({ status: 503, contentType: 'application/json', body: JSON.stringify({ detail: 'export unavailable' }) });
    });
    await page.getByRole('button', { name: 'Export CSV' }).click();
    await expect(page.getByText('Assessment Report', { exact: true })).toBeVisible();
    await expect(page.getByRole('alert')).toContainText('export the CSV');
    await expect(page.getByRole('button', { name: 'Export CSV' })).toBeEnabled();
  });

  test('recovers after refreshing an assessment with two completed categories', async ({ page }) => {
    await installMockApi(page, { seedCompletedCategories: 2 });
    await page.goto('/assessment/1');
    await expect(page.getByText('2 of 4 sections complete')).toBeVisible();
    await page.reload();
    await expect(page.getByText('2 of 4 sections complete')).toBeVisible();
    await expect(page.getByRole('progressbar', { name: 'Assessment progress' })).toHaveAttribute('aria-valuenow', '2');
  });

  test('does not create duplicate submissions on double-click', async ({ page }) => {
    await installMockApi(page);
    let answerRequests = 0;
    await page.route('**/api/assessments/1/answers', async (route) => {
      answerRequests += 1;
      await route.continue();
    });
    await page.goto('/assessment/1');
    await page.locator('fieldset').first().locator('input[type="radio"]').last().check();
    await page.getByRole('button', { name: /Save and continue/ }).dblclick();
    await expect.poll(() => answerRequests).toBe(1);
  });

  test('supports keyboard completion on a mobile viewport', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 812 });
    await installMockApi(page);
    await page.goto('/assessment/1');
    await page.locator('fieldset').first().locator('input[type="radio"]').last().focus();
    await page.keyboard.press('Space');
    await expect(page.locator('fieldset').first().locator('input[type="radio"]').last()).toBeChecked();
  });
});
