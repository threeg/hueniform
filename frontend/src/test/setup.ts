import '@testing-library/jest-dom/vitest'
import { afterAll, afterEach, beforeAll, expect } from 'vitest'
import { toHaveNoViolations } from 'jest-axe'
import { server } from './server'

// Register jest-axe matcher globally so individual test files don't each need
// expect.extend(toHaveNoViolations).  Tests still import axe/expectNoAxeViolations
// from ./a11y; this ensures the matcher is always available.
expect.extend(toHaveNoViolations)

// Intercept all HTTP requests in tests; unhandled requests are an error
// so missing handlers are caught immediately (test strategy §10.1).
beforeAll(() => server.listen({ onUnhandledRequest: 'error' }))
afterEach(() => server.resetHandlers())
afterAll(() => server.close())
