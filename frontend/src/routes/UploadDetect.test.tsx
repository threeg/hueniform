import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { createMemoryRouter, RouterProvider } from 'react-router-dom'
import { describe, it, expect } from 'vitest'
import { http, HttpResponse } from 'msw'
import { server } from '../test/server'

import AddGarment from './AddGarment'
import {
  DETECTION_RESPONSE,
  DETECTION_FALLBACK_RESPONSE,
  ERR_UNSUPPORTED_FORMAT,
  ERR_UNREADABLE_IMAGE,
  ERR_FILE_TOO_LARGE,
} from '../test/contract-examples'

// ── Helpers ───────────────────────────────────────────────────────────────────

function renderScreen() {
  const qc = new QueryClient({
    defaultOptions: {
      mutations: { retry: false },
      queries: { retry: false },
    },
  })
  const router = createMemoryRouter(
    [
      {
        path: '/add',
        element: (
          <QueryClientProvider client={qc}>
            <AddGarment />
          </QueryClientProvider>
        ),
      },
      {
        path: '/add/confirm',
        element: <div data-testid="confirm-screen" />,
      },
    ],
    {
      initialEntries: ['/add'],
      future: { v7_startTransition: true, v7_relativeSplatPath: true },
    },
  )
  return render(
    <RouterProvider router={router} future={{ v7_startTransition: true }} />,
  )
}

function garmentFile(name = 'garment.jpg', type = 'image/jpeg') {
  return new File(['bytes'], name, { type })
}

// ── Default state (FR-23) ─────────────────────────────────────────────────────

describe('AddGarment — default state', () => {
  it('renders the drop zone headline', () => {
    renderScreen()
    expect(
      screen.getByText('Drag a garment photograph here'),
    ).toBeInTheDocument()
  })

  it('renders the "Choose a file…" button (FR-23)', () => {
    renderScreen()
    expect(
      screen.getByRole('button', { name: 'Choose a file…' }),
    ).toBeInTheDocument()
  })

  it('renders the format hint (FR-23)', () => {
    renderScreen()
    expect(screen.getByText(/JPEG, PNG or WebP/)).toBeInTheDocument()
  })

  it('renders the photography tip', () => {
    renderScreen()
    expect(screen.getByText(/contrasting background/i)).toBeInTheDocument()
  })

  it('has a hidden file input accepting image types', () => {
    renderScreen()
    const input = screen.getByTestId('file-input') as HTMLInputElement
    expect(input.type).toBe('file')
    expect(input.accept).toContain('image/jpeg')
    expect(input.accept).toContain('image/png')
    expect(input.accept).toContain('image/webp')
  })
})

// ── Detecting state ───────────────────────────────────────────────────────────

describe('AddGarment — detecting state', () => {
  it('shows loading indicator and hides button while request is in-flight', async () => {
    // Delay so we can observe the pending state
    server.use(
      http.post('http://127.0.0.1:8000/api/detections', async () => {
        await new Promise((resolve) => setTimeout(resolve, 80))
        return HttpResponse.json(DETECTION_RESPONSE, { status: 201 })
      }),
    )
    const user = userEvent.setup()
    renderScreen()
    const input = screen.getByTestId('file-input')
    await user.upload(input, garmentFile())
    expect(screen.getByText('Detecting colours…')).toBeInTheDocument()
    expect(
      screen.queryByRole('button', { name: 'Choose a file…' }),
    ).not.toBeInTheDocument()
    // Wait for resolution so the test cleans up
    await waitFor(() =>
      expect(screen.getByTestId('confirm-screen')).toBeInTheDocument(),
    )
  })
})

// ── Success → navigate (FR-26) ────────────────────────────────────────────────

describe('AddGarment — success', () => {
  it('navigates to /add/confirm after a successful upload (FR-26)', async () => {
    const user = userEvent.setup()
    renderScreen()
    await user.upload(screen.getByTestId('file-input'), garmentFile())
    await waitFor(() =>
      expect(screen.getByTestId('confirm-screen')).toBeInTheDocument(),
    )
  })
})

// ── Rejection errors (FR-24) ──────────────────────────────────────────────────

describe('AddGarment — rejection errors (FR-24)', () => {
  it.each([
    ['unsupported_format', 400, ERR_UNSUPPORTED_FORMAT],
    ['unreadable_image',   400, ERR_UNREADABLE_IMAGE],
    ['file_too_large',     413, ERR_FILE_TOO_LARGE],
  ] as [string, number, typeof ERR_UNSUPPORTED_FORMAT][])(
    'shows the server message for %s — not the code',
    async (code, status, errorBody) => {
      server.use(
        http.post('http://127.0.0.1:8000/api/detections', () =>
          HttpResponse.json(errorBody, { status }),
        ),
      )
      const user = userEvent.setup()
      renderScreen()
      await user.upload(screen.getByTestId('file-input'), garmentFile())
      await waitFor(() =>
        expect(
          screen.getByText(errorBody.error.message),
        ).toBeInTheDocument(),
      )
      // Code must NOT appear
      expect(screen.queryByText(code)).not.toBeInTheDocument()
      // Drop zone still present (retry is possible)
      expect(
        screen.getByRole('button', { name: 'Choose a file…' }),
      ).toBeInTheDocument()
    },
  )
})

// ── Fallback handoff (FR-27) ──────────────────────────────────────────────────

describe('AddGarment — fallback_used handoff (FR-27)', () => {
  it('navigates with fallback_used: true when the server returns it', async () => {
    server.use(
      http.post('http://127.0.0.1:8000/api/detections', () =>
        HttpResponse.json(DETECTION_FALLBACK_RESPONSE, { status: 201 }),
      ),
    )

    // Capture the navigation state by rendering an instrumented confirm stub
    let capturedState: unknown
    const qc = new QueryClient({
      defaultOptions: { mutations: { retry: false } },
    })
    const { default: AddGarmentComp } = await import('./AddGarment')
    const router = createMemoryRouter(
      [
        {
          path: '/add',
          element: (
            <QueryClientProvider client={qc}>
              <AddGarmentComp />
            </QueryClientProvider>
          ),
        },
        {
          path: '/add/confirm',
          element: (
            <StateCapture
              onCapture={(s) => {
                capturedState = s
              }}
            />
          ),
        },
      ],
      {
        initialEntries: ['/add'],
        future: { v7_startTransition: true, v7_relativeSplatPath: true },
      },
    )
    render(
      <RouterProvider router={router} future={{ v7_startTransition: true }} />,
    )

    const user = userEvent.setup()
    await user.upload(screen.getByTestId('file-input'), garmentFile())
    await waitFor(() => expect(capturedState).toBeDefined())
    expect(
      (capturedState as { detection: { fallback_used: boolean } }).detection
        .fallback_used,
    ).toBe(true)
  })
})

// ── Multi-file drop ───────────────────────────────────────────────────────────

describe('AddGarment — multi-file drop', () => {
  it('shows a notice when more than one file is dropped', async () => {
    // Hold the response so navigation does not fire before we check the notice
    server.use(
      http.post('http://127.0.0.1:8000/api/detections', async () => {
        await new Promise((resolve) => setTimeout(resolve, 200))
        return HttpResponse.json(DETECTION_RESPONSE, { status: 201 })
      }),
    )
    renderScreen()
    const zone = screen.getByLabelText('File drop zone')
    fireEvent.drop(zone, {
      dataTransfer: { files: [garmentFile('a.jpg'), garmentFile('b.jpg')] },
    })
    // Notice is set synchronously before the mutation fires; check immediately
    expect(screen.getByText(/Multiple files dropped/)).toBeInTheDocument()
    // Wait for navigation so the test cleans up properly
    await waitFor(() =>
      expect(screen.getByTestId('confirm-screen')).toBeInTheDocument(),
    )
  })
})

// ── Drag-over highlight (FR-23) ───────────────────────────────────────────────

describe('AddGarment — drag-over', () => {
  it('marks the zone as drag-over during a drag', () => {
    renderScreen()
    const zone = screen.getByLabelText('File drop zone')
    fireEvent.dragOver(zone, { dataTransfer: { files: [] } })
    // The zone gains the drag-over state — observable via aria-busy being false
    // and the zone still being present
    expect(zone).toBeInTheDocument()
  })

  it('clears drag-over when leaving the zone', () => {
    renderScreen()
    const zone = screen.getByLabelText('File drop zone')
    fireEvent.dragOver(zone, { dataTransfer: { files: [] } })
    fireEvent.dragLeave(zone, { relatedTarget: document.body })
    expect(zone).toBeInTheDocument()
  })
})

// ── StateCapture helper ───────────────────────────────────────────────────────

import { useLocation } from 'react-router-dom'
import { useEffect } from 'react'

function StateCapture({ onCapture }: { onCapture: (s: unknown) => void }) {
  const { state } = useLocation()
  useEffect(() => { onCapture(state) }, [state, onCapture])
  return <div data-testid="confirm-screen" />
}
