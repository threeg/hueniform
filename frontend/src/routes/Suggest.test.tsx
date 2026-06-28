/**
 * Tests for HUE-071: outfit-request slot selector and category-constraint checklist.
 * (FR-36, FR-49, FR-50, FR-51, FR-52)
 */
import { screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect } from 'vitest'
import { http, HttpResponse } from 'msw'
import { server } from '../test/server'
import { renderRoute } from '../test/test-utils'

import Suggest from './Suggest'
import { SUGGESTION_RESPONSE, ERR_EMPTY_SLOTS } from '../test/contract-examples'

const BASE = 'http://127.0.0.1:8000'

function renderScreen() {
  return renderRoute(
    [
      { path: '/suggest', element: <Suggest /> },
      { path: '/garments/:id', element: <div data-testid="detail-screen" /> },
      { path: '/add', element: <div data-testid="add-screen" /> },
    ],
    ['/suggest'],
  )
}

// Wait for taxonomy-driven content to appear (async fetch)
async function waitForPanel() {
  // lower_body chip is always rendered once taxonomy loads (it's default-selected)
  return screen.findByTestId('slot-lower_body')
}

// ── FR-51: default slot selection ─────────────────────────────────────────────

describe('Suggest — default slot selection (FR-51)', () => {
  it('default-selected slots have aria-pressed="true"', async () => {
    renderScreen()
    await waitForPanel()
    expect(screen.getByTestId('slot-base')).toHaveAttribute('aria-pressed', 'true')
    expect(screen.getByTestId('slot-socks')).toHaveAttribute('aria-pressed', 'true')
    expect(screen.getByTestId('slot-shoes')).toHaveAttribute('aria-pressed', 'true')
  })

  it('non-default slots have aria-pressed="false"', async () => {
    renderScreen()
    await waitForPanel()
    expect(screen.getByTestId('slot-hat')).toHaveAttribute('aria-pressed', 'false')
    expect(screen.getByTestId('slot-outer')).toHaveAttribute('aria-pressed', 'false')
  })

  it('lower_body chip is rendered as locked (non-button, required label) (FR-51.2)', async () => {
    renderScreen()
    const chip = await screen.findByTestId('slot-lower_body')
    expect(chip.tagName).not.toBe('BUTTON')
    expect(chip).toHaveAttribute('aria-label', 'Lower body (required)')
  })

  it('region headings appear (Head, Upper body, Lower body, Feet)', async () => {
    renderScreen()
    await waitForPanel()
    const panel = screen.getByRole('region', { name: 'Outfit request' })
    await within(panel).findByText('Upper body')
    expect(within(panel).getByText('Head')).toBeInTheDocument()
    expect(within(panel).getByText('Lower body')).toBeInTheDocument()
    expect(within(panel).getByText('Feet')).toBeInTheDocument()
  })

  it('panel hint text updated to lower-body focus (FR-51)', async () => {
    renderScreen()
    await waitForPanel()
    expect(
      screen.getByText('The lower-body slot is always included; everything else is up to you.'),
    ).toBeInTheDocument()
  })
})

// ── Slot toggle ───────────────────────────────────────────────────────────────

describe('Suggest — slot toggles', () => {
  const user = userEvent.setup

  it('toggling a non-default slot on sets aria-pressed="true"', async () => {
    renderScreen()
    await waitForPanel()
    const outer = screen.getByTestId('slot-outer')
    expect(outer).toHaveAttribute('aria-pressed', 'false')
    await user().click(outer)
    expect(outer).toHaveAttribute('aria-pressed', 'true')
  })

  it('toggling a default-on slot off sets aria-pressed="false"', async () => {
    renderScreen()
    await waitForPanel()
    const base = screen.getByTestId('slot-base')
    await user().click(base)
    expect(base).toHaveAttribute('aria-pressed', 'false')
  })

  it('toggling lower_body chip has no effect (locked)', async () => {
    renderScreen()
    const chip = await screen.findByTestId('slot-lower_body')
    // Locked chip is a span (not a button) — it stays locked
    expect(chip.tagName).not.toBe('BUTTON')
    expect(chip).toHaveAttribute('aria-label', 'Lower body (required)')
  })

  it('sends partial slots override — only non-defaults in request (FR-51)', async () => {
    let captured: unknown = null
    server.use(
      http.post(`${BASE}/api/suggestions`, async ({ request }) => {
        captured = await request.json()
        return HttpResponse.json(SUGGESTION_RESPONSE)
      }),
    )
    renderScreen()
    await waitForPanel()

    // Toggle outer on (non-default) and base off (default-on)
    await user().click(screen.getByTestId('slot-outer'))
    await user().click(screen.getByTestId('slot-base'))
    await user().click(screen.getByTestId('suggest-button'))

    await waitFor(() => expect(captured).not.toBeNull())
    const body = captured as { slots?: Record<string, unknown> }
    expect(body.slots?.outer).toBe(true)
    expect(body.slots?.base).toBe(false)
    // Default-on slots not overridden are absent from the slots map
    expect(body.slots?.socks).toBeUndefined()
    expect(body.slots?.shoes).toBeUndefined()
    expect(body.slots?.lower_body).toBeUndefined()
  })

  it('sends empty body when all defaults unchanged', async () => {
    let captured: unknown = null
    server.use(
      http.post(`${BASE}/api/suggestions`, async ({ request }) => {
        captured = await request.json()
        return HttpResponse.json(SUGGESTION_RESPONSE)
      }),
    )
    renderScreen()
    await waitForPanel()
    await user().click(screen.getByTestId('suggest-button'))

    await waitFor(() => expect(captured).not.toBeNull())
    // No slots key when everything is at default
    expect(captured as object).not.toHaveProperty('slots')
  })
})

// ── FR-52: category constraint checklist ─────────────────────────────────────

describe('Suggest — category constraint (FR-52)', () => {
  const user = userEvent.setup

  it('multi-category selected slot shows "any ▾" control', async () => {
    renderScreen()
    await waitForPanel()
    // lower_body is always selected (locked) and has many categories
    // base is default-selected and multi-category
    expect(screen.getByTestId('constraint-base')).toHaveTextContent('any ▾')
  })

  it('clicking "any ▾" expands the category checklist', async () => {
    renderScreen()
    await waitForPanel()
    await user().click(screen.getByTestId('constraint-base'))
    // Base has categories: t_shirt, vest, long_sleeve
    expect(screen.getByRole('group', { name: 'Base categories' })).toBeInTheDocument()
    const group = screen.getByRole('group', { name: 'Base categories' })
    const checkboxes = within(group).getAllByRole('checkbox')
    expect(checkboxes).toHaveLength(3)
    checkboxes.forEach(cb => expect(cb).toBeChecked())  // all checked = "any"
  })

  it('unchecking a category updates the constraint button label', async () => {
    renderScreen()
    await waitForPanel()
    await user().click(screen.getByTestId('constraint-base'))
    const group = screen.getByRole('group', { name: 'Base categories' })
    // Uncheck t_shirt
    await user().click(within(group).getByRole('checkbox', { name: /t.shirt/i }))
    // Constraint button now shows remaining categories (not "any")
    const btn = screen.getByTestId('constraint-base')
    expect(btn.textContent).not.toBe('any ▾')
    expect(btn.textContent).toContain('▾')
  })

  it('unchecking a category sends {categories:[...]} in the request (FR-52)', async () => {
    let captured: unknown = null
    server.use(
      http.post(`${BASE}/api/suggestions`, async ({ request }) => {
        captured = await request.json()
        return HttpResponse.json(SUGGESTION_RESPONSE)
      }),
    )
    renderScreen()
    await waitForPanel()

    // Open lower_body constraint (it's locked-on, has many categories)
    await user().click(screen.getByTestId('constraint-lower_body'))
    const group = screen.getByRole('group', { name: 'Lower body categories' })
    // Uncheck trousers
    await user().click(within(group).getByRole('checkbox', { name: /trousers/i }))
    await user().click(screen.getByTestId('suggest-button'))

    await waitFor(() => expect(captured).not.toBeNull())
    const body = captured as { slots?: Record<string, unknown> }
    expect(body.slots?.lower_body).toEqual({
      categories: expect.arrayContaining(['jeans', 'chinos', 'shorts', 'skirt', 'dress', 'jumpsuit']),
    })
    expect((body.slots?.lower_body as { categories: string[] }).categories).not.toContain('trousers')
  })

  it('un-ticking the last category reverts to "any" (FR-52 guard)', async () => {
    renderScreen()
    await waitForPanel()

    // Toggle hat on (3 categories: hat, cap, beanie)
    await user().click(screen.getByTestId('slot-hat'))
    await user().click(screen.getByTestId('constraint-hat'))
    const group = screen.getByRole('group', { name: 'Hat categories' })

    // Uncheck hat and cap → only beanie remains
    await user().click(within(group).getByRole('checkbox', { name: /^Hat/i }))
    await user().click(within(group).getByRole('checkbox', { name: /cap/i }))
    // Uncheck the last one (beanie)
    await user().click(within(group).getByRole('checkbox', { name: /beanie/i }))

    // Constraint button reverts to "any ▾" and all checkboxes are re-checked
    expect(screen.getByTestId('constraint-hat')).toHaveTextContent('any ▾')
    const checkboxes = within(group).getAllByRole('checkbox')
    checkboxes.forEach(cb => expect(cb).toBeChecked())
  })

  it('single-category slot has no constraint button', async () => {
    renderScreen()
    await waitForPanel()
    // socks has only one category
    expect(screen.queryByTestId('constraint-socks')).not.toBeInTheDocument()
  })
})

// ── FR-50.2: one-piece auto-deselects base ────────────────────────────────────

describe('Suggest — one-piece constraint auto-deselects base (FR-50.2)', () => {
  const user = userEvent.setup

  async function constrainLowerBodyToOnePiece() {
    // Open lower_body constraint
    await user().click(screen.getByTestId('constraint-lower_body'))
    const group = screen.getByRole('group', { name: 'Lower body categories' })
    // Uncheck all non-one-piece categories
    for (const name of [/trousers/i, /jeans/i, /chinos/i, /shorts/i, /skirt/i]) {
      await user().click(within(group).getByRole('checkbox', { name }))
    }
    // Only dress and jumpsuit remain → one-piece only
  }

  it('constraining lower_body to one-piece disables base chip', async () => {
    renderScreen()
    await waitForPanel()
    await constrainLowerBodyToOnePiece()
    expect(screen.getByTestId('slot-base')).toBeDisabled()
  })

  it('constraining lower_body to one-piece shows the note', async () => {
    renderScreen()
    await waitForPanel()
    await constrainLowerBodyToOnePiece()
    expect(screen.getByTestId('one-piece-note')).toHaveTextContent(
      'A dress covers the base layer, so Base has been switched off for this request.',
    )
  })

  it('one-piece sends base:false in the request', async () => {
    let captured: unknown = null
    server.use(
      http.post(`${BASE}/api/suggestions`, async ({ request }) => {
        captured = await request.json()
        return HttpResponse.json(SUGGESTION_RESPONSE)
      }),
    )
    renderScreen()
    await waitForPanel()
    await constrainLowerBodyToOnePiece()
    await user().click(screen.getByTestId('suggest-button'))

    await waitFor(() => expect(captured).not.toBeNull())
    const body = captured as { slots?: Record<string, unknown> }
    expect(body.slots?.base).toBe(false)
  })

  it('note disappears when lower_body constraint is relaxed back to non-one-piece', async () => {
    renderScreen()
    await waitForPanel()
    await constrainLowerBodyToOnePiece()
    expect(screen.getByTestId('one-piece-note')).toBeInTheDocument()

    // Checklist is still open — re-check trousers to make it non-one-piece-only
    const group = screen.getByRole('group', { name: 'Lower body categories' })
    await user().click(within(group).getByRole('checkbox', { name: /trousers/i }))

    expect(screen.queryByTestId('one-piece-note')).not.toBeInTheDocument()
  })
})

// ── FR-36: 409 empty_slots ────────────────────────────────────────────────────

describe('Suggest — 409 empty_slots (FR-36)', () => {
  const user = userEvent.setup

  it('renders the error message verbatim', async () => {
    server.use(
      http.post(`${BASE}/api/suggestions`, () =>
        HttpResponse.json(ERR_EMPTY_SLOTS, { status: 409 }),
      ),
    )
    renderScreen()
    await waitForPanel()
    await user().click(screen.getByTestId('suggest-button'))
    await screen.findByText(ERR_EMPTY_SLOTS.error.message)
  })

  it('flags the named slot chip with "none in wardrobe"', async () => {
    server.use(
      http.post(`${BASE}/api/suggestions`, () =>
        HttpResponse.json(ERR_EMPTY_SLOTS, { status: 409 }),
      ),
    )
    renderScreen()
    await waitForPanel()

    // Toggle hat on so it becomes a named slot in the 409 response
    await user().click(screen.getByTestId('slot-hat'))
    await user().click(screen.getByTestId('suggest-button'))

    // ERR_EMPTY_SLOTS.error.details.empty_slots = ['hat']
    const hatChip = await screen.findByTestId('slot-hat')
    expect(hatChip).toHaveTextContent('none in wardrobe')
  })
})
