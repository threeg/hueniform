/**
 * Axe harness smoke test — proves jest-axe wiring works end-to-end
 * (test strategy §10.3, NFR-11).  Run with:
 *   cd frontend && npm run test -- axe --run
 */

import { render } from '@testing-library/react'
import { describe, it } from 'vitest'
import Banner from '../components/Banner'
import LoadingState from '../components/LoadingState'
import { expectNoAxeViolations } from './a11y'

describe('axe harness smoke (§10.3)', () => {
  it('Banner error has no axe violations', async () => {
    const { container } = render(
      <Banner variant="error" message="Something went wrong." />,
    )
    await expectNoAxeViolations(container)
  })

  it('Banner warning has no axe violations', async () => {
    const { container } = render(
      <Banner variant="warning" message="Colour detection fell back." />,
    )
    await expectNoAxeViolations(container)
  })

  it('LoadingState has no axe violations', async () => {
    const { container } = render(<LoadingState label="Loading…" />)
    await expectNoAxeViolations(container)
  })
})
