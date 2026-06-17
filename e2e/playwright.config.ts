import { defineConfig, devices } from '@playwright/test'
import { writeFileSync } from 'fs'
import { join, resolve } from 'path'
import { tmpdir } from 'os'

const REPO_ROOT = resolve(__dirname, '..')

// Fixed path so the spec file can read it without re-importing this module
// (which would re-run side-effects inside each Playwright worker).
// rembg finds its model at ~/.u2net/ (set by make setup); this dir is only
// for the SQLite database and staging uploads.
const E2E_DATA_DIR = join(tmpdir(), 'hueniform-e2e-data')

// Persist the path once at config evaluation time.  This file is read by
// smoke.spec.ts at worker startup.
writeFileSync(join(__dirname, '.e2e-data-dir'), E2E_DATA_DIR)

export default defineConfig({
  testDir: '.',
  // 120 s per test — rembg inference can be slow on first load.
  timeout: 120_000,
  use: {
    baseURL: 'http://127.0.0.1:8000',
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
    { name: 'firefox', use: { ...devices['Desktop Firefox'] } },
  ],
  webServer: {
    // Clean and recreate the data dir as part of server startup so this
    // side-effect runs exactly once (not on every config evaluation).
    // Always start a fresh server so Journey 3 sees an empty wardrobe.
    // Stop any running make run / make dev before executing make test-e2e.
    command: `rm -rf "${E2E_DATA_DIR}" && mkdir -p "${E2E_DATA_DIR}" && HUENIFORM_DATA_DIR="${E2E_DATA_DIR}" make run`,
    url: 'http://127.0.0.1:8000',
    reuseExistingServer: false,
    cwd: '..', // project root
    timeout: 60_000,
  },
})
