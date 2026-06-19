import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect } from 'vitest'
import { http, HttpResponse } from 'msw'
import { server } from '../test/server'
import { renderRoute } from '../test/test-utils'

import GarmentDetail from './GarmentDetail'
import {
  GARMENT_DETAIL,
  GARMENT_ID,
  DETECTION_RESPONSE,
  ERR_GARMENT_NOT_FOUND,
} from '../test/contract-examples'

// Regeneration response has a garment_id (FR-33)
const REGEN_RESPONSE = { ...DETECTION_RESPONSE, garment_id: GARMENT_ID }

// ── Helpers ───────────────────────────────────────────────────────────────────

function renderScreen(state?: Record<string, unknown>) {
  return renderRoute(
    [
      { path: '/garments/:id', element: <GarmentDetail /> },
      { path: '/', element: <div data-testid="wardrobe-screen" /> },
      { path: '/add/confirm', element: <div data-testid="confirm-screen" /> },
    ],
    [{ pathname: `/garments/${GARMENT_ID}`, state: state ?? null }],
  )
}

const user = userEvent.setup

// ── Default state ─────────────────────────────────────────────────────────────

describe('GarmentDetail — default state', () => {
  it('shows the garment photograph', async () => {
    renderScreen()
    const img = await screen.findByAltText('Garment photograph')
    expect(img).toHaveAttribute('src', GARMENT_DETAIL.image_url)
  })

  it('shows the type as the heading', async () => {
    renderScreen()
    expect(await screen.findByRole('heading', { name: 'Jumper' })).toBeInTheDocument()
  })

  it('renders one palette row per colour (FR-5)', async () => {
    renderScreen()
    await screen.findByRole('heading', { name: 'Jumper' })
    expect(screen.getAllByTestId('palette-row')).toHaveLength(GARMENT_DETAIL.colours.length)
  })

  it('shows the Added date', async () => {
    renderScreen()
    expect(await screen.findByText(/Added 12 June 2026/)).toBeInTheDocument()
  })

  it('does not show regenerated date when regenerated_at is null', async () => {
    renderScreen()
    await screen.findByRole('heading', { name: 'Jumper' })
    expect(screen.queryByTestId('regen-date')).not.toBeInTheDocument()
  })

  it('shows regenerated date when regenerated_at is set', async () => {
    server.use(
      http.get(`http://127.0.0.1:8000/api/garments/${GARMENT_ID}`, () =>
        HttpResponse.json({ ...GARMENT_DETAIL, regenerated_at: '2026-06-14T09:00:00Z' }),
      ),
    )
    renderScreen()
    expect(await screen.findByTestId('regen-date')).toHaveTextContent(
      'Colours regenerated 14 June 2026',
    )
  })

  it('has no text input or edit field (FR-32)', async () => {
    const { container } = renderScreen()
    await screen.findByRole('heading', { name: 'Jumper' })
    expect(container.querySelectorAll('input, textarea')).toHaveLength(0)
  })

  it('shows a ← Wardrobe back link', async () => {
    renderScreen()
    expect(await screen.findByTestId('back-link')).toBeInTheDocument()
  })

  it('back link points to / when no filter state', async () => {
    renderScreen()
    const link = await screen.findByTestId('back-link')
    expect(link).toHaveAttribute('href', '/')
  })

  it('back link preserves filter state passed from inventory', async () => {
    renderScreen({ from: 'category=jumper&family=Teal' })
    const link = await screen.findByTestId('back-link')
    expect(link).toHaveAttribute('href', '/?category=jumper&family=Teal')
  })
})

// ── Regenerate (FR-33) ────────────────────────────────────────────────────────

describe('GarmentDetail — regenerate (FR-33)', () => {
  it('calls POST /api/garments/:id/regenerate on click', async () => {
    let called = false
    server.use(
      http.post(`http://127.0.0.1:8000/api/garments/${GARMENT_ID}/regenerate`, () => {
        called = true
        return HttpResponse.json(REGEN_RESPONSE)
      }),
    )
    renderScreen()
    await user().click(await screen.findByTestId('regen-button'))
    await waitFor(() => expect(called).toBe(true))
  })

  it('navigates to /add/confirm with the regeneration token (FR-33)', async () => {
    renderScreen()
    await user().click(await screen.findByTestId('regen-button'))
    await waitFor(() =>
      expect(screen.getByTestId('confirm-screen')).toBeInTheDocument(),
    )
  })

  it('shows pending state while regeneration is in flight', async () => {
    server.use(
      http.post(`http://127.0.0.1:8000/api/garments/${GARMENT_ID}/regenerate`, async () => {
        await new Promise(resolve => setTimeout(resolve, 80))
        return HttpResponse.json(REGEN_RESPONSE)
      }),
    )
    renderScreen()
    await user().click(await screen.findByTestId('regen-button'))
    expect(screen.getByText('Detecting…')).toBeInTheDocument()
    await waitFor(() =>
      expect(screen.getByTestId('confirm-screen')).toBeInTheDocument(),
    )
  })
})

// ── Delete with confirmation (FR-34) ──────────────────────────────────────────

describe('GarmentDetail — delete (FR-34)', () => {
  it('shows the confirmation dialogue when Delete garment is clicked', async () => {
    renderScreen()
    await user().click(await screen.findByTestId('delete-button'))
    expect(screen.getByTestId('delete-dialog')).toBeInTheDocument()
  })

  it('names the garment type in the dialogue', async () => {
    renderScreen()
    await user().click(await screen.findByTestId('delete-button'))
    expect(screen.getByText(/Delete this jumper/i)).toBeInTheDocument()
  })

  it('Cancel dismisses the dialogue without calling DELETE', async () => {
    let called = false
    server.use(
      http.delete(`http://127.0.0.1:8000/api/garments/${GARMENT_ID}`, () => {
        called = true
        return new HttpResponse(null, { status: 204 })
      }),
    )
    renderScreen()
    await user().click(await screen.findByTestId('delete-button'))
    await user().click(screen.getByTestId('cancel-delete'))
    expect(screen.queryByTestId('delete-dialog')).not.toBeInTheDocument()
    expect(called).toBe(false)
  })

  it('calls DELETE /api/garments/:id on confirm (FR-34)', async () => {
    let called = false
    server.use(
      http.delete(`http://127.0.0.1:8000/api/garments/${GARMENT_ID}`, () => {
        called = true
        return new HttpResponse(null, { status: 204 })
      }),
    )
    renderScreen()
    await user().click(await screen.findByTestId('delete-button'))
    await user().click(screen.getByTestId('confirm-delete'))
    await waitFor(() => expect(called).toBe(true))
  })

  it('navigates to / after successful delete (FR-34)', async () => {
    renderScreen()
    await user().click(await screen.findByTestId('delete-button'))
    await user().click(screen.getByTestId('confirm-delete'))
    await waitFor(() =>
      expect(screen.getByTestId('wardrobe-screen')).toBeInTheDocument(),
    )
  })
})

// ── 404 not-found state ───────────────────────────────────────────────────────

describe('GarmentDetail — not found', () => {
  it('shows a not-found message with a Wardrobe link on 404', async () => {
    server.use(
      http.get(`http://127.0.0.1:8000/api/garments/${GARMENT_ID}`, () =>
        HttpResponse.json(ERR_GARMENT_NOT_FOUND, { status: 404 }),
      ),
    )
    renderScreen()
    await waitFor(() =>
      expect(screen.getByTestId('not-found')).toBeInTheDocument(),
    )
    expect(screen.getByRole('link', { name: /Wardrobe/i })).toBeInTheDocument()
  })
})
