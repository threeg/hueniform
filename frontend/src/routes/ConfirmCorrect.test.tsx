import { render, screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { createMemoryRouter, RouterProvider } from 'react-router-dom'
import { describe, it, expect } from 'vitest'
import { http, HttpResponse } from 'msw'
import type { ReactNode } from 'react'
import { server } from '../test/server'

import AddConfirm from './AddConfirm'
import {
  DETECTION_RESPONSE,
  DETECTION_FALLBACK_RESPONSE,
  GARMENT_DETAIL,
  GARMENT_ID,
  ERR_DETECTION_NOT_FOUND,
  ERR_INVALID_REGENERATION_TOKEN,
} from '../test/contract-examples'

// Regeneration detection state — same shape as DETECTION_RESPONSE + garment_id
const REGEN_DETECTION = { ...DETECTION_RESPONSE, garment_id: GARMENT_ID }

// ── Helpers ───────────────────────────────────────────────────────────────────

function makeWrapper() {
  return ({ children }: { children: ReactNode }) => (
    <QueryClientProvider
      client={new QueryClient({ defaultOptions: { mutations: { retry: false }, queries: { retry: false } } })}
    >
      {children}
    </QueryClientProvider>
  )
}

function renderScreen(
  state: Record<string, unknown> = { detection: DETECTION_RESPONSE },
) {
  const qc = new QueryClient({
    defaultOptions: { mutations: { retry: false }, queries: { retry: false } },
  })
  const Wrapper = ({ children }: { children: ReactNode }) => (
    <QueryClientProvider client={qc}>{children}</QueryClientProvider>
  )
  const router = createMemoryRouter(
    [
      {
        path: '/add/confirm',
        element: <Wrapper><AddConfirm /></Wrapper>,
      },
      { path: '/add', element: <div data-testid="add-screen" /> },
      { path: '/', element: <div data-testid="wardrobe-screen" /> },
      { path: '/garments/:id', element: <div data-testid="detail-screen" /> },
    ],
    { initialEntries: [{ pathname: '/add/confirm', state }] },
  )
  return render(<RouterProvider router={router} />)
}

const user = userEvent.setup

// ── Redirect when no state ────────────────────────────────────────────────────

describe('AddConfirm — no state', () => {
  it('redirects to /add when no detection state is present', () => {
    renderScreen({})
    expect(screen.getByTestId('add-screen')).toBeInTheDocument()
  })
})

// ── Default state (FR-28) ─────────────────────────────────────────────────────

describe('AddConfirm — default state', () => {
  it('shows the page heading', () => {
    renderScreen()
    expect(screen.getByRole('heading', { name: 'Confirm garment' })).toBeInTheDocument()
  })

  it('renders a colour row for each detected colour (FR-28)', () => {
    renderScreen()
    const rows = screen.getAllByTestId('colour-row')
    expect(rows).toHaveLength(DETECTION_RESPONSE.colours.length)
  })

  it('shows family names from the detection response (FR-5)', () => {
    renderScreen()
    expect(screen.getByText('Teal')).toBeInTheDocument()
    expect(screen.getByText('Orange')).toBeInTheDocument()
  })

  it('renders the detection photograph', () => {
    renderScreen()
    const img = screen.getByAltText('Garment photograph')
    expect(img).toHaveAttribute('src', DETECTION_RESPONSE.image.url)
  })

  it('shows all eight type buttons (FR-31)', () => {
    renderScreen()
    const section = screen.getByRole('region', { name: 'Garment type' })
    expect(within(section).getAllByRole('button')).toHaveLength(8)
  })
})

// ── Fallback warning (FR-27) ──────────────────────────────────────────────────

describe('AddConfirm — fallback warning (FR-27)', () => {
  it('shows the warning banner when fallback_used is true', () => {
    renderScreen({ detection: DETECTION_FALLBACK_RESPONSE })
    expect(screen.getByRole('status')).toBeInTheDocument()
    expect(screen.getByText(/Colour detection fell back/)).toBeInTheDocument()
  })

  it('does not show the warning banner when fallback_used is false', () => {
    renderScreen()
    expect(screen.queryByRole('status')).not.toBeInTheDocument()
  })
})

// ── Type picker — save disabled (FR-30, FR-31) ─────────────────────────────────

describe('AddConfirm — type picker', () => {
  it('save button is disabled when no type is selected (FR-30, FR-31)', () => {
    renderScreen()
    expect(screen.getByTestId('save-button')).toBeDisabled()
  })

  it('save button is enabled after selecting a type', async () => {
    renderScreen()
    await user().click(screen.getByRole('button', { name: 'Top' }))
    expect(screen.getByTestId('save-button')).not.toBeDisabled()
  })

  it('marks the selected type as pressed', async () => {
    renderScreen()
    const bottomBtn = screen.getByRole('button', { name: 'Bottom' })
    await user().click(bottomBtn)
    expect(bottomBtn).toHaveAttribute('aria-pressed', 'true')
  })
})

// ── Proportion stepper and live total (FR-29) ──────────────────────────────────

describe('AddConfirm — proportion editor (FR-29)', () => {
  it('shows the initial total', () => {
    renderScreen()
    expect(screen.getByTestId('total-line')).toHaveTextContent('Total: 100%')
  })

  it('updates the live total when a proportion changes', async () => {
    renderScreen()
    // Teal starts at 80; decrease by 1
    await user().click(
      screen.getByRole('button', { name: 'Decrease Teal proportion' }),
    )
    expect(screen.getByTestId('total-line')).toHaveTextContent('Total: 99%')
  })

  it('shows normalisation notice when total ≠ 100', async () => {
    renderScreen()
    await user().click(
      screen.getByRole('button', { name: 'Decrease Teal proportion' }),
    )
    expect(screen.getByTestId('total-line')).toHaveTextContent(
      'will be normalised to 100% on save',
    )
  })

  it('does not show normalisation notice when total = 100', () => {
    renderScreen()
    expect(screen.getByTestId('total-line')).not.toHaveTextContent(
      'will be normalised',
    )
  })
})

// ── Colour removal ────────────────────────────────────────────────────────────

describe('AddConfirm — colour removal', () => {
  it('removes the colour row when Remove is clicked', async () => {
    renderScreen()
    expect(screen.getAllByTestId('colour-row')).toHaveLength(2)
    await user().click(screen.getByRole('button', { name: 'Remove Teal' }))
    expect(screen.getAllByTestId('colour-row')).toHaveLength(1)
  })

  it('disables Remove when only one colour remains', async () => {
    renderScreen()
    await user().click(screen.getByRole('button', { name: 'Remove Teal' }))
    expect(
      screen.getByRole('button', { name: 'Remove Orange' }),
    ).toBeDisabled()
  })
})

// ── Manual add colour (FR-29) ─────────────────────────────────────────────────

describe('AddConfirm — add a colour (FR-29)', () => {
  it('opens the add panel when "Add a colour" is clicked', async () => {
    renderScreen()
    await user().click(screen.getByRole('button', { name: '+ Add a colour' }))
    expect(screen.getByTestId('add-panel')).toBeInTheDocument()
  })

  it('adds a new colour row with canonical HSL when family is chosen and Add clicked', async () => {
    renderScreen()
    // Wait for taxonomy to load
    await waitFor(() => screen.getByRole('button', { name: '+ Add a colour' }))
    await user().click(screen.getByRole('button', { name: '+ Add a colour' }))

    const select = await screen.findByRole('combobox', { name: 'Colour family' })
    await user().selectOptions(select, 'Red')

    // Set proportion
    await user().clear(screen.getByRole('spinbutton', { name: 'New colour proportion' }))
    await user().type(screen.getByRole('spinbutton', { name: 'New colour proportion' }), '10')

    await user().click(screen.getByTestId('add-confirm'))

    // The panel closes and a new row is added
    expect(screen.queryByTestId('add-panel')).not.toBeInTheDocument()
    expect(screen.getAllByTestId('colour-row')).toHaveLength(3)
    expect(screen.getByText('Red')).toBeInTheDocument()
  })
})

// ── Save — POST /api/garments (FR-30) ─────────────────────────────────────────

describe('AddConfirm — save (FR-30)', () => {
  it('sends POST /api/garments with detection_token, type and colours', async () => {
    let captured: unknown
    server.use(
      http.post('http://127.0.0.1:8000/api/garments', async ({ request }) => {
        captured = await request.json()
        return HttpResponse.json(GARMENT_DETAIL, { status: 201 })
      }),
    )
    renderScreen()
    await user().click(screen.getByRole('button', { name: 'Jersey' }))
    await user().click(screen.getByTestId('save-button'))
    await waitFor(() => expect(captured).toBeDefined())
    const body = captured as Record<string, unknown>
    expect(body.detection_token).toBe(DETECTION_RESPONSE.token)
    expect(body.type).toBe('jersey')
    expect(Array.isArray(body.colours)).toBe(true)
  })

  it('normalises proportions to sum to 100 on save (FR-29)', async () => {
    let captured: unknown
    server.use(
      http.post('http://127.0.0.1:8000/api/garments', async ({ request }) => {
        captured = await request.json()
        return HttpResponse.json(GARMENT_DETAIL, { status: 201 })
      }),
    )
    renderScreen()
    // Decrease Teal so total ≠ 100
    await user().click(
      screen.getByRole('button', { name: 'Decrease Teal proportion' }),
    )
    expect(screen.getByTestId('total-line')).toHaveTextContent('Total: 99%')

    await user().click(screen.getByRole('button', { name: 'Jersey' }))
    await user().click(screen.getByTestId('save-button'))
    await waitFor(() => expect(captured).toBeDefined())

    const colours = (captured as { colours: { proportion: number }[] }).colours
    const sum = colours.reduce((a, c) => a + c.proportion, 0)
    expect(sum).toBe(100)
  })

  it('navigates to / after a successful save', async () => {
    renderScreen()
    await user().click(screen.getByRole('button', { name: 'Top' }))
    await user().click(screen.getByTestId('save-button'))
    await waitFor(() =>
      expect(screen.getByTestId('wardrobe-screen')).toBeInTheDocument(),
    )
  })

  it('shows an error banner on save failure (expired token)', async () => {
    server.use(
      http.post('http://127.0.0.1:8000/api/garments', () =>
        HttpResponse.json(ERR_DETECTION_NOT_FOUND, { status: 404 }),
      ),
    )
    renderScreen()
    await user().click(screen.getByRole('button', { name: 'Top' }))
    await user().click(screen.getByTestId('save-button'))
    await waitFor(() =>
      expect(
        screen.getByText(ERR_DETECTION_NOT_FOUND.error.message),
      ).toBeInTheDocument(),
    )
  })
})

// ── Regeneration variant (FR-33) ──────────────────────────────────────────────

describe('AddConfirm — regeneration variant (FR-33)', () => {
  it('shows "Confirm regeneration" heading', () => {
    renderScreen({ detection: REGEN_DETECTION })
    expect(
      screen.getByRole('heading', { name: 'Confirm regeneration' }),
    ).toBeInTheDocument()
  })

  it('sends PUT /api/garments/:id with regeneration_token (FR-33)', async () => {
    let captured: unknown
    let capturedId: string | undefined
    server.use(
      http.put('http://127.0.0.1:8000/api/garments/:id', async ({ request, params }) => {
        captured = await request.json()
        capturedId = params.id as string
        return HttpResponse.json(GARMENT_DETAIL)
      }),
    )
    renderScreen({ detection: REGEN_DETECTION })
    await user().click(screen.getByRole('button', { name: 'Jersey' }))
    await user().click(screen.getByTestId('save-button'))
    await waitFor(() => expect(captured).toBeDefined())
    const body = captured as Record<string, unknown>
    expect(capturedId).toBe(GARMENT_ID)
    expect(body.regeneration_token).toBe(REGEN_DETECTION.token)
    expect(body.type).toBe('jersey')
  })

  it('shows error banner on invalid regeneration token', async () => {
    server.use(
      http.put('http://127.0.0.1:8000/api/garments/:id', () =>
        HttpResponse.json(ERR_INVALID_REGENERATION_TOKEN, { status: 409 }),
      ),
    )
    renderScreen({ detection: REGEN_DETECTION })
    await user().click(screen.getByRole('button', { name: 'Top' }))
    await user().click(screen.getByTestId('save-button'))
    await waitFor(() =>
      expect(
        screen.getByText(ERR_INVALID_REGENERATION_TOKEN.error.message),
      ).toBeInTheDocument(),
    )
  })
})
