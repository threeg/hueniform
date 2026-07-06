/**
 * Responsive navigation smoke — test strategy §10.3, NFR-7.
 *
 * Runs in three Playwright projects (mobile / tablet / desktop), each with
 * the matching viewport preset.  Asserts that the correct navigation tier
 * (bottom tab bar / top nav / sidebar) is visible, and that all three
 * destinations are reachable from it.
 *
 * See: docs/04-wireframes/07-responsive.md §2
 *       e2e/viewports.ts  (VIEWPORTS constants + forEachViewport helper)
 */

import { test, expect } from '@playwright/test'
import { tierFromPage } from './viewports'

test('correct navigation tier is visible for viewport', async ({ page }) => {
  await page.goto('/')

  const tier = tierFromPage(page)

  const sidebar = page.locator('aside:has(nav[aria-label="Sidebar"])')
  const topNav  = page.locator('nav[aria-label="Top navigation"]')
  const tabBar  = page.locator('nav[aria-label="Tab bar"]')

  if (tier === 'mobile') {
    await expect(sidebar).not.toBeVisible()
    await expect(topNav).not.toBeVisible()
    await expect(tabBar).toBeVisible()
  } else if (tier === 'tablet') {
    await expect(sidebar).not.toBeVisible()
    await expect(topNav).toBeVisible()
    await expect(tabBar).not.toBeVisible()
  } else {
    await expect(sidebar).toBeVisible()
    await expect(topNav).not.toBeVisible()
    await expect(tabBar).not.toBeVisible()
  }
})

test('all three destinations are reachable from the active nav', async ({ page }) => {
  const tier = tierFromPage(page)

  const nav =
    tier === 'mobile'  ? page.locator('nav[aria-label="Tab bar"]') :
    tier === 'tablet'  ? page.locator('nav[aria-label="Top navigation"]') :
    page.locator('nav[aria-label="Sidebar"]')

  // Navigate to each destination via the active nav tier.
  await page.goto('/')
  await nav.locator('a[href="/add"]').click()
  await expect(page).toHaveURL(/\/add$/, { timeout: 10_000 })

  await nav.locator('a[href="/suggest"]').click()
  await expect(page).toHaveURL(/\/suggest$/, { timeout: 10_000 })

  await nav.locator('a[href="/"]').first().click()
  await expect(page).toHaveURL(/\/$/, { timeout: 10_000 })
})
