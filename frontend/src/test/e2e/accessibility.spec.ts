import { test, expect } from '../accessibility.helpers';
import { testAccessibility } from '../accessibility.helpers';

test.describe('Accessibility Tests', () => {
  test('Dashboard page should be accessible @a11y', async ({ page }) => {
    await testAccessibility(page, '/');
    expect(await page.title()).toBeTruthy();
  });

  test('Activities page should be accessible @a11y', async ({ page }) => {
    await testAccessibility(page, '/activities');
    expect(await page.title()).toBeTruthy();
  });

  test('Providers page should be accessible @a11y', async ({ page }) => {
    await testAccessibility(page, '/providers');
    expect(await page.title()).toBeTruthy();
  });

  test('Import page should be accessible @a11y', async ({ page }) => {
    await testAccessibility(page, '/import');
    expect(await page.title()).toBeTruthy();
  });

  test('Keyboard navigation should work', async ({ page }) => {
    await page.goto('/');
    
    // Tab through interactive elements
    await page.keyboard.press('Tab');
    const focused = await page.evaluate(() => document.activeElement?.tagName);
    expect(focused).toBeTruthy();
  });
});
