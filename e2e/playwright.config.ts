import { defineConfig, devices } from '@playwright/test'

// Full webServer config and smoke journeys arrive in HUE-038 / HUE-040.
// This config establishes the Chromium + Firefox projects (NFR-7, test strategy §9).
export default defineConfig({
  testDir: '.',
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
    { name: 'firefox', use: { ...devices['Desktop Firefox'] } },
  ],
  webServer: {
    command: 'make run',
    url: 'http://127.0.0.1:8000',
    reuseExistingServer: !process.env['CI'],
    cwd: '..', // project root
  },
})
