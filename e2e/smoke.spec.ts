/**
 * Smoke suite (HUE-085 / NFR-7): four end-to-end journeys for v0.2.0 against
 * the fully assembled production-style application.
 *
 * Skip guard: if the rembg model is absent (make setup not yet run), all tests
 * skip with an explicit message.  If Playwright browsers are absent, Playwright
 * itself will report a clear install error before tests begin.
 *
 * Run order is serial and intentional:
 *   Journey 4 — empty-slot rejection (fresh empty wardrobe)
 *   Journey 1 — add a garment & browse the grouped inventory
 *   Journey 2 — edit a garment's category directly (FR-46)
 *   Journey 3 — request an outfit (500-garment seeded wardrobe)
 */

import { test, expect } from '@playwright/test'
import { execSync } from 'child_process'
import { existsSync, readFileSync } from 'fs'
import { join, resolve } from 'path'

const REPO_ROOT = resolve(__dirname, '..')

// Path written by playwright.config.ts at evaluation time; reading it here
// avoids re-running the config side-effects inside each worker.
const E2E_DATA_DIR = readFileSync(join(__dirname, '.e2e-data-dir'), 'utf-8').trim()

// The model is stored at data/models/ in the project root (make setup).
const MODEL_PATH    = join(REPO_ROOT, 'data', 'models', 'u2net.onnx')
const FIXTURE_IMAGE = join(REPO_ROOT, 'backend', 'tests', 'fixtures', 'synthetic', 'flat_red.png')
const PYTHON        = join(REPO_ROOT, 'backend', '.venv', 'bin', 'python')
const SEED_SCRIPT   = join(REPO_ROOT, 'scripts', 'seed_test_wardrobe.py')

const modelPresent = existsSync(MODEL_PATH)

test.describe('smoke journeys', () => {
  test.describe.configure({ mode: 'serial' })

  test.beforeEach(() => {
    test.skip(
      !modelPresent,
      `rembg model absent — run make setup (expected: ${MODEL_PATH})`,
    )
  })

  // ── Journey 4 — empty-slot rejection ──────────────────────────────────────
  // Runs first while the wardrobe is guaranteed empty.  Requesting outfits with
  // the default required slots returns 409 empty_slots; the UI shows the error
  // banner and flags each empty slot "— none in wardrobe".
  test('journey 4 — empty-slot rejection', async ({ page }) => {
    await page.goto('/suggest')

    // Wait for taxonomy to load so slot chips are present before requesting.
    // Without this, a fast-fail 409 can return before taxonomy renders the chips,
    // leaving emptySlots populated but no DOM elements to attach the marker to.
    await expect(page.getByTestId('slot-base')).toBeVisible({ timeout: 10_000 })

    // Request with default required slots only (none present in a fresh wardrobe).
    await page.getByTestId('suggest-button').click()

    // ErrorBanner renders with role="alert" for 409 empty_slots
    await expect(page.getByRole('alert')).toBeVisible({ timeout: 15_000 })

    // At least one slot is flagged "none in wardrobe" within the slot selector
    await expect(page.getByText(/none in wardrobe/).first()).toBeVisible()
  })

  // ── Journey 1 — add a garment & browse grouped inventory ─────────────────
  // Upload a synthetic fixture → confirm-and-correct (select an FR-16 category)
  // → save → garment appears in the inventory grouped by category; the order
  // toggle works; a category filter narrows the results.
  test('journey 1 — add a garment & browse grouped inventory', async ({ page }) => {
    await page.goto('/add')

    // Trigger upload via the hidden file input.
    await page.getByTestId('file-input').setInputFiles(FIXTURE_IMAGE)

    // Wait for rembg inference + navigation to /add/confirm.
    // First invocation loads the ONNX model; allow generous time.
    await page.waitForURL('**/add/confirm', { timeout: 90_000 })

    // Select a category from the FR-16 picker (save disabled until chosen, FR-31).
    // The picker is an aria-region grouped by body region; click the T-shirt button.
    await page.getByRole('region', { name: 'Garment category' })
      .getByRole('button', { name: 'T-shirt' })
      .click()
    await expect(page.getByTestId('save-button')).toBeEnabled()

    // Save → redirect to inventory
    await page.getByTestId('save-button').click()
    await page.waitForURL('/', { timeout: 15_000 })

    // Garment appears in the T-shirt category group (FR-47 grouping)
    await expect(page.getByTestId('group-header-t_shirt')).toBeVisible()
    await expect(page.getByTestId('result-count')).toContainText(/[1-9]/)

    // Hue order toggle is active by default (FR-47)
    await expect(page.getByTestId('order-hue')).toHaveAttribute('aria-pressed', 'true')

    // Switching to Date added activates that button instead
    await page.getByTestId('order-date').click()
    await expect(page.getByTestId('order-date')).toHaveAttribute('aria-pressed', 'true')
    await expect(page.getByTestId('order-hue')).toHaveAttribute('aria-pressed', 'false')

    // Category filter narrows to the added garment
    await page.getByLabel('Filter by type').selectOption('t_shirt')
    await expect(page.getByTestId('result-count')).toContainText(/[1-9]/)
  })

  // ── Journey 2 — edit a garment's category (FR-46) ─────────────────────────
  // From the garment detail page, change the category directly (no re-detection)
  // → the garment moves to the new group in inventory; palette unchanged.
  test('journey 2 — edit a garment category (FR-46)', async ({ page }) => {
    await page.goto('/')

    // Navigate to the garment detail added in Journey 1
    await page.getByRole('link', { name: /T-shirt garment detail/i }).first().click()
    await page.waitForURL('**/garments/**', { timeout: 10_000 })

    // Open the inline category editor
    await page.getByTestId('edit-category-button').click()

    // Select Jumper and save.  On success the editor closes (category-save button
    // disappears); wait for that before navigating so the PATCH write commits first.
    await page.getByTestId('cat-jumper').click()
    await page.getByTestId('category-save').click()
    await expect(page.getByTestId('category-save')).not.toBeVisible({ timeout: 10_000 })

    // Return to inventory and verify the garment is now in the Jumper group
    await page.goto('/')
    await expect(page.getByTestId('group-header-jumper')).toBeVisible()
  })

  // ── Journey 3 — request an outfit (seeded wardrobe) ───────────────────────
  // Seeds 500 garments (all FR-16 categories) via materialise_wardrobe, then
  // exercises the rebuilt outfit-request screen: slot toggle, count control,
  // ranked cards with scheme chip, per-slot tiles, explanation; "Suggest again".
  test.describe('with seeded wardrobe', () => {
    test.beforeAll(() => {
      // Inserts 500 synthetic garments directly into the running server's DB.
      execSync(`"${PYTHON}" "${SEED_SCRIPT}"`, {
        env: { ...process.env, HUENIFORM_DATA_DIR: E2E_DATA_DIR },
        cwd: REPO_ROOT,
        stdio: 'pipe',
      })
    })

    test('journey 3 — request an outfit', async ({ page }) => {
      await page.goto('/suggest')

      // Toggle the mid-layer optional slot on (v0.2.0 slot key, was 'jersey')
      await page.getByTestId('slot-mid').click()
      await expect(page.getByTestId('slot-mid')).toHaveAttribute('aria-pressed', 'true')

      // Increment count from 3 to 5 (FR-48)
      await page.getByTestId('count-increment').click()
      await page.getByTestId('count-increment').click()
      await expect(page.getByTestId('count-display')).toHaveText('5')

      await page.getByTestId('suggest-button').click()

      // Ranked result cards appear (up to the requested count)
      const firstCard = page.getByTestId('result-card').first()
      await expect(firstCard).toBeVisible({ timeout: 15_000 })

      // Scheme chip present (FR-39)
      await expect(page.getByTestId('scheme-chip').first()).toBeVisible()

      // Per-slot thumbnail tiles present (at least one)
      await expect(page.getByTestId('slot-tile').first()).toBeVisible()

      // Non-empty explanation text (FR-37)
      const explanation = page.getByTestId('explanation').first()
      await expect(explanation).toBeVisible()
      await expect(explanation).not.toHaveText('')

      // 'Suggest again' returns a fresh valid response (FR-42)
      await page.getByTestId('suggest-again').click()
      await expect(page.getByTestId('result-card').first()).toBeVisible({ timeout: 15_000 })
    })
  })
})
