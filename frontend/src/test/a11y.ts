/**
 * Shared accessibility testing helper — test strategy §10.3, NFR-11.
 *
 * Exports a pre-configured axe instance scoped to WCAG 2.1 A + AA rules and
 * an `expectNoAxeViolations` shorthand.  Import this module instead of
 * jest-axe directly so all component tests use the same ruleset.
 *
 * Colour-contrast checks rely on CSS computed values that jsdom does not
 * provide; axe returns those checks as "incomplete" (not violations).
 * AA-compliant contrast is verified separately at the token level in
 * tokens.test.ts (design system §2.6).
 */

import { configureAxe, toHaveNoViolations } from 'jest-axe'
import { expect } from 'vitest'

export { toHaveNoViolations }

/** Axe instance scoped to WCAG 2.1 A + AA tags (NFR-11). */
export const axe = configureAxe({
  runOnly: {
    type: 'tag',
    values: ['wcag2a', 'wcag2aa'],
  },
})

/** Assert zero axe violations (WCAG 2.1 AA) on the given container. */
export async function expectNoAxeViolations(
  container: Element | Document,
): Promise<void> {
  const results = await axe(container as Element)
  expect(results).toHaveNoViolations()
}
