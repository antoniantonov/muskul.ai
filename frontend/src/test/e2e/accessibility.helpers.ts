import { test as base, expect } from '@playwright/test';
import { injectAxe, checkA11y } from 'axe-playwright';

// Extend base test with accessibility testing
export const test = base.extend({
  // Automatically inject axe-core into every page
  page: async ({ page }, use) => {
    await use(page);
  },
});

export { expect };

// Helper function to test accessibility
export async function testAccessibility(
  page: Parameters<typeof injectAxe>[0],
  url?: string
): Promise<void> {
  if (url) {
    await page.goto(url);
  }
  await injectAxe(page);
  await checkA11y(page, undefined, {
    detailedReport: true,
    detailedReportOptions: {
      html: true,
    },
  });
}
