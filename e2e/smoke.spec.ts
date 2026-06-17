/**
 * Smoke suite (HUE-040 / NFR-7): three end-to-end journeys against the fully
 * assembled production-style application.
 *
 * Skip guard: if the rembg model is absent (make setup not yet run), all tests
 * skip with an explicit message.  If Playwright browsers are absent, Playwright
 * itself will report a clear install error before tests begin.
 *
 * Run order is serial and intentional:
 *   Journey 3 — empty-slot rejection (fresh empty wardrobe)
 *   Journey 1 — add a garment (upload → confirm → save → inventory)
 *   Journey 2 — request an outfit (500-garment seed → suggest → results)
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
// rembg also caches it at ~/.u2net/; we check the project copy as the
// canonical indicator that make setup has been run.
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

  // ── Journey 3 — empty-slot rejection ──────────────────────────────────────
  // Runs first while the wardrobe is guaranteed empty.  Requesting outfits
  // returns 409 empty_slots; the UI renders the error on the request panel.
  test('journey 3 — empty-slot rejection', async ({ page }) => {
    await page.goto('/suggest')

    // Request with default required slots only (top, bottom, socks, shoes —
    // none present in a fresh wardrobe).
    await page.getByTestId('suggest-button').click()

    // ErrorBanner renders with role="alert" for 409 empty_slots
    await expect(page.getByRole('alert')).toBeVisible({ timeout: 15_000 })
  })

  // ── Journey 1 — add a garment ─────────────────────────────────────────────
  // Upload a synthetic fixture → confirm-and-correct (select type) → save →
  // garment appears in inventory and survives a type filter.
  test('journey 1 — add a garment', async ({ page }) => {
    await page.goto('/add')

    // Trigger upload via the hidden file input (data-testid="file-input").
    // setInputFiles bypasses the drag-and-drop zone without needing drag events.
    await page.getByTestId('file-input').setInputFiles(FIXTURE_IMAGE)

    // Wait for rembg inference + navigation to /add/confirm.
    // First invocation loads the ONNX model; allow generous time.
    await page.waitForURL('**/add/confirm', { timeout: 90_000 })

    // Select garment type — save is disabled until a type is chosen (FR-31)
    await page.getByLabel('Garment type').getByRole('button', { name: 'Top' }).click()
    await expect(page.getByTestId('save-button')).toBeEnabled()

    // Save → redirect to inventory
    await page.getByTestId('save-button').click()
    await page.waitForURL('/', { timeout: 15_000 })

    // Garment visible in inventory (both browsers share the server, so count ≥ 1)
    await expect(page.getByTestId('result-count')).toContainText(/[1-9]/)

    // Survives a type=top filter
    await page.getByLabel('Filter by type').selectOption('top')
    await expect(page.getByTestId('result-count')).toContainText(/[1-9]/)
  })

  // ── Journey 2 — request an outfit ─────────────────────────────────────────
  // Seeds 500 garments via materialise_wardrobe (bypasses detection), then
  // exercises the suggest screen: ranked cards, scheme chip, slot tiles,
  // explanation text, and 'Suggest again'.
  test.describe('with seeded wardrobe', () => {
    test.beforeAll(() => {
      // Inserts 500 synthetic garments directly into the running server's DB.
      execSync(`"${PYTHON}" "${SEED_SCRIPT}"`, {
        env: { ...process.env, HUENIFORM_DATA_DIR: E2E_DATA_DIR },
        cwd: REPO_ROOT,
        stdio: 'pipe',
      })
    })

    test('journey 2 — request an outfit', async ({ page }) => {
      await page.goto('/suggest')

      // Toggle one optional slot (jersey) — required slots always included
      await page.getByTestId('slot-jersey').click()
      await expect(page.getByTestId('slot-jersey')).toHaveAttribute('aria-pressed', 'true')

      await page.getByTestId('suggest-button').click()

      // Ranked result cards appear
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

      // 'Suggest again' returns a fresh valid response
      await page.getByTestId('suggest-again').click()
      await expect(page.getByTestId('result-card').first()).toBeVisible({ timeout: 15_000 })
    })
  })
})
