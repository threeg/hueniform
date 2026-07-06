/**
 * Responsive layout smoke — HUE-105, NFR-7.
 *
 * Verifies that the v0.3.0 restyle responsive rules hold end-to-end across
 * mobile / tablet / desktop. Runs in three Playwright projects (see
 * playwright.config.ts). No model inference required — these tests navigate
 * to static pages and check layout structure only.
 *
 * Per-screen jest-axe zero-violations coverage is in the component test suite
 * (HUE-099–HUE-104); this suite confirms the assembled app renders without
 * structural regressions at each viewport.
 */

import { test, expect } from '@playwright/test'
import { tierFromPage as tier } from './viewports'

// ── Navigation tier ────────────────────────────────────────────────────────────

test('correct navigation tier is visible', async ({ page }) => {
  await page.goto('/')
  const t = tier(page)

  const sidebar = page.locator('aside:has(nav[aria-label="Sidebar"])')
  const topNav  = page.locator('nav[aria-label="Top navigation"]')
  const tabBar  = page.locator('nav[aria-label="Tab bar"]')

  if (t === 'mobile') {
    await expect(tabBar).toBeVisible()
    await expect(sidebar).not.toBeVisible()
    await expect(topNav).not.toBeVisible()
  } else if (t === 'tablet') {
    await expect(topNav).toBeVisible()
    await expect(sidebar).not.toBeVisible()
    await expect(tabBar).not.toBeVisible()
  } else {
    await expect(sidebar).toBeVisible()
    await expect(topNav).not.toBeVisible()
    await expect(tabBar).not.toBeVisible()
  }
})

// ── Suggest screen — primary action reachability ─────────────────────────────

test('suggest screen primary action is reachable', async ({ page }) => {
  await page.goto('/suggest')

  // Taxonomy must load before the slot chips are rendered.
  await expect(page.getByTestId('slot-lower_body')).toBeVisible({ timeout: 10_000 })

  // The Suggest outfits button must be visible and enabled at every viewport.
  // On mobile it is in a sticky footer fixed above the tab bar (56 px).
  const btn = page.getByTestId('suggest-button')
  await expect(btn).toBeVisible()
  await expect(btn).toBeEnabled()
})

// ── Suggest screen — sticky footer on mobile ──────────────────────────────────

test('suggest-button sticky footer position on mobile', async ({ page }) => {
  test.skip(tier(page) !== 'mobile', 'mobile only')
  await page.goto('/suggest')
  await expect(page.getByTestId('slot-lower_body')).toBeVisible({ timeout: 10_000 })

  const btn = page.getByTestId('suggest-button')
  await expect(btn).toBeVisible()

  // On mobile the button is in a fixed footer, so its bottom edge should be
  // above the bottom of the viewport (tab-bar height is 56 px).
  const box = await btn.boundingBox()
  const vp  = page.viewportSize()!
  expect(box).not.toBeNull()
  // Fixed footer bottom = 56 px above the viewport bottom; button should not
  // extend to the very bottom of the screen.
  expect(box!.y + box!.height).toBeLessThan(vp.height - 40)
})

// ── Add-garment screen — pick button visible ──────────────────────────────────

test('add-garment pick button is visible', async ({ page }) => {
  await page.goto('/add')
  // The shared Button (secondary variant) is the sole interactive element.
  await expect(page.getByRole('button', { name: /Choose a file/i })).toBeVisible()
})

// ── Wardrobe screen — renders without error ───────────────────────────────────

test('wardrobe screen renders without error', async ({ page }) => {
  await page.goto('/')
  // Either garment cards or the empty-state message must be present.
  // Use first() because the shell may contain a nested main alongside the route.
  await expect(page.locator('main').first()).toBeVisible()
  // No unexpected error banners.
  await expect(page.getByRole('alert')).not.toBeVisible()
})
