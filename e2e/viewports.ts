/**
 * Viewport presets and per-tier journey helper — test strategy §10.3, NFR-7.
 *
 * Import from e2e tests to run assertions across mobile / tablet / desktop
 * without duplicating the viewport constants.
 */

import type { Page } from '@playwright/test'

/** Viewport dimensions for the three responsive tiers (07-responsive §1). */
export const VIEWPORTS = {
  mobile:  { width: 390,  height: 844  },
  tablet:  { width: 834,  height: 1194 },
  desktop: { width: 1280, height: 800  },
} as const

export type ViewportTier = keyof typeof VIEWPORTS

/**
 * Run `fn` at each viewport tier in sequence, resizing the page in-place.
 * Use when a single test should assert behaviour at all three tiers.
 *
 * @example
 * test('nav works at every tier', async ({ page }) => {
 *   await page.goto('/')
 *   await forEachViewport(page, async (tier) => {
 *     await expect(page.locator('aside')).toBeVisible()  // or not, by tier
 *   })
 * })
 */
/**
 * Return the responsive tier for the current page viewport.
 * Breakpoints match `07-responsive §1`: < 640 mobile, < 1024 tablet, else desktop.
 */
export function tierFromPage(page: Page): ViewportTier {
  const vp = page.viewportSize()
  if (!vp) throw new Error('no viewport')
  return vp.width < 640 ? 'mobile' : vp.width < 1024 ? 'tablet' : 'desktop'
}

export async function forEachViewport(
  page: Page,
  fn: (tier: ViewportTier) => Promise<void>,
): Promise<void> {
  for (const tier of Object.keys(VIEWPORTS) as ViewportTier[]) {
    await page.setViewportSize(VIEWPORTS[tier])
    await fn(tier)
  }
}
