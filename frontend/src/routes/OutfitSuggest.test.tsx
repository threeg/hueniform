/**
 * Tests for HUE-037: outfit-suggestion result display.
 * Request-panel and slot-selector behaviour covered by Suggest.test.tsx (HUE-071).
 */
import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect } from 'vitest'
import { http, HttpResponse } from 'msw'
import { server } from '../test/server'
import { renderRoute } from '../test/test-utils'

import Suggest from './Suggest'
import {
  SUGGESTION_RESPONSE,
  SUGGESTION_EMPTY_RESPONSE,
  ERR_EMPTY_SLOTS,
} from '../test/contract-examples'

// A fallback combination for FR-43a tests
const FALLBACK_RESPONSE = {
  combinations: [{ ...SUGGESTION_RESPONSE.combinations[0], fallback: true }],
}

// A neutral-based scheme response for SCHEME_LABELS coverage
const NEUTRAL_BASED_RESPONSE = {
  combinations: [{ ...SUGGESTION_RESPONSE.combinations[0], scheme: 'neutral-based' }],
}

// ── Helpers ───────────────────────────────────────────────────────────────────

function renderScreen() {
  return renderRoute(
    [
      { path: '/suggest', element: <Suggest /> },
      { path: '/add', element: <div data-testid="add-screen" /> },
      { path: '/garments/:id', element: <div data-testid="detail-screen" /> },
    ],
    ['/suggest'],
  )
}

const user = userEvent.setup

// ── Result cards (FR-37, FR-38, FR-39, FR-41) ─────────────────────────────────

describe('Suggest — result cards (FR-37/38/39/41)', () => {
  it('renders one result card per combination (FR-39)', async () => {
    renderScreen()
    await user().click(screen.getByTestId('suggest-button'))
    await waitFor(() => screen.getAllByTestId('result-card'))
    expect(screen.getAllByTestId('result-card')).toHaveLength(
      SUGGESTION_RESPONSE.combinations.length,
    )
  })

  it('shows the scheme chip (FR-37)', async () => {
    renderScreen()
    await user().click(screen.getByTestId('suggest-button'))
    await waitFor(() => screen.getByTestId('scheme-chip'))
    expect(screen.getByTestId('scheme-chip')).toHaveTextContent('Analogous scheme')
  })

  it('shows neutral-based scheme label correctly', async () => {
    server.use(
      http.post('http://127.0.0.1:8000/api/suggestions', () =>
        HttpResponse.json(NEUTRAL_BASED_RESPONSE),
      ),
    )
    renderScreen()
    await user().click(screen.getByTestId('suggest-button'))
    await waitFor(() => screen.getByTestId('scheme-chip'))
    expect(screen.getByTestId('scheme-chip')).toHaveTextContent('Neutral-based scheme')
  })

  it('renders slot tiles for each slot in the combination (FR-37)', async () => {
    renderScreen()
    await user().click(screen.getByTestId('suggest-button'))
    await waitFor(() => screen.getAllByTestId('slot-tile'))
    const tiles = screen.getAllByTestId('slot-tile')
    const combo = SUGGESTION_RESPONSE.combinations[0]
    expect(tiles).toHaveLength(Object.keys(combo.slots).length)
  })

  it('renders the explanation verbatim (FR-38)', async () => {
    renderScreen()
    await user().click(screen.getByTestId('suggest-button'))
    await waitFor(() => screen.getByTestId('explanation'))
    expect(screen.getByTestId('explanation')).toHaveTextContent(
      SUGGESTION_RESPONSE.combinations[0].explanation,
    )
  })

  it('renders echo lines from the echoes array', async () => {
    renderScreen()
    await user().click(screen.getByTestId('suggest-button'))
    await waitFor(() => screen.getAllByTestId('echo-line'))
    const echoLines = screen.getAllByTestId('echo-line')
    expect(echoLines).toHaveLength(SUGGESTION_RESPONSE.combinations[0].echoes.length)
    expect(echoLines[0]).toHaveTextContent('Echo: Orange — hat ↔ socks')
  })

  it('shows "Suggest again" button after results (FR-42)', async () => {
    renderScreen()
    await user().click(screen.getByTestId('suggest-button'))
    await waitFor(() => screen.getByTestId('suggest-again'))
    expect(screen.getByTestId('suggest-again')).toBeInTheDocument()
  })

  it('slot tiles link to garment detail', async () => {
    renderScreen()
    await user().click(screen.getByTestId('suggest-button'))
    await waitFor(() => screen.getAllByTestId('slot-tile'))
    const tiles = screen.getAllByTestId('slot-tile')
    tiles.forEach(tile => {
      expect(tile).toHaveAttribute('href', expect.stringContaining('/garments/'))
    })
  })
})

// ── Fallback label (FR-43a) ───────────────────────────────────────────────────

describe('Suggest — fallback label (FR-43a)', () => {
  it('shows "Neutral-based fallback" label when fallback is true', async () => {
    server.use(
      http.post('http://127.0.0.1:8000/api/suggestions', () =>
        HttpResponse.json(FALLBACK_RESPONSE),
      ),
    )
    renderScreen()
    await user().click(screen.getByTestId('suggest-button'))
    await waitFor(() => screen.getByTestId('fallback-label'))
    expect(screen.getByTestId('fallback-label')).toHaveTextContent('Neutral-based fallback')
  })

  it('does not show fallback label when fallback is false', async () => {
    renderScreen()
    await user().click(screen.getByTestId('suggest-button'))
    await waitFor(() => screen.getByTestId('result-card'))
    expect(screen.queryByTestId('fallback-label')).not.toBeInTheDocument()
  })
})

// ── Zero results (FR-43b) ─────────────────────────────────────────────────────

describe('Suggest — zero results (FR-43b)', () => {
  it('renders explanation and hint verbatim when combinations is empty', async () => {
    server.use(
      http.post('http://127.0.0.1:8000/api/suggestions', () =>
        HttpResponse.json(SUGGESTION_EMPTY_RESPONSE),
      ),
    )
    renderScreen()
    await user().click(screen.getByTestId('suggest-button'))
    await waitFor(() => screen.getByTestId('zero-results'))
    expect(screen.getByTestId('zero-explanation')).toHaveTextContent(
      SUGGESTION_EMPTY_RESPONSE.explanation,
    )
    expect(screen.getByTestId('zero-hint')).toHaveTextContent(
      SUGGESTION_EMPTY_RESPONSE.hint,
    )
  })
})

// ── 409 empty_slots (FR-36) ───────────────────────────────────────────────────

describe('Suggest — 409 empty_slots (FR-36)', () => {
  it('shows the error banner with the envelope message on 409', async () => {
    server.use(
      http.post('http://127.0.0.1:8000/api/suggestions', () =>
        HttpResponse.json(ERR_EMPTY_SLOTS, { status: 409 }),
      ),
    )
    renderScreen()
    // Wait for taxonomy before clicking the hat chip
    const hat = await screen.findByTestId('slot-hat')
    await user().click(hat)
    await user().click(screen.getByTestId('suggest-button'))
    await waitFor(() => screen.getByRole('alert'))
    expect(screen.getByRole('alert')).toHaveTextContent(ERR_EMPTY_SLOTS.error.message)
  })

  it('marks the offending slot chip with an empty-slot indicator', async () => {
    server.use(
      http.post('http://127.0.0.1:8000/api/suggestions', () =>
        HttpResponse.json(ERR_EMPTY_SLOTS, { status: 409 }),
      ),
    )
    renderScreen()
    const hat = await screen.findByTestId('slot-hat')
    await user().click(hat)
    await user().click(screen.getByTestId('suggest-button'))
    await waitFor(() => screen.getByRole('alert'))
    expect(screen.getByTestId('slot-hat')).toHaveTextContent('none in wardrobe')
  })
})

// ── Loading state ─────────────────────────────────────────────────────────────

describe('Suggest — loading state', () => {
  it('shows searching indicator while request is in flight', async () => {
    server.use(
      http.post('http://127.0.0.1:8000/api/suggestions', async () => {
        await new Promise(resolve => setTimeout(resolve, 80))
        return HttpResponse.json(SUGGESTION_RESPONSE)
      }),
    )
    renderScreen()
    await user().click(screen.getByTestId('suggest-button'))
    expect(screen.getByText('Searching…')).toBeInTheDocument()
    await waitFor(() => screen.getByTestId('result-card'))
  })
})
