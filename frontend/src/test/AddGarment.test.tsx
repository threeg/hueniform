/**
 * AddGarment visual-fidelity tests — HUE-117.
 *
 * Checks:
 *   - Upload icon present in default state
 *   - Icon toggles on drag-over
 *   - Detecting state shows three dots (not skeleton bars)
 *   - Error banner contains icon element
 *   - jest-axe accessibility gate
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import type { ReactNode } from 'react'
import { describe, it, expect } from 'vitest'
import { http, HttpResponse } from 'msw'
import { server } from './server'

import Banner from '../components/Banner'
import { expectNoAxeViolations } from './a11y'

const DETECT_URL = 'http://127.0.0.1:8000/api/detections'

function makeWrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false }, mutations: { retry: false } } })
  return function Wrapper({ children }: { children: ReactNode }) {
    return (
      <QueryClientProvider client={qc}>
        <MemoryRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
          {children}
        </MemoryRouter>
      </QueryClientProvider>
    )
  }
}

async function renderAddGarment() {
  const { default: AddGarment } = await import('../routes/AddGarment')
  return render(<AddGarment />, { wrapper: makeWrapper() })
}

// ── Default state ─────────────────────────────────────────────────────────────

describe('AddGarment — default state', () => {
  it('renders the drop zone', async () => {
    await renderAddGarment()
    expect(screen.getByLabelText('File drop zone')).toBeInTheDocument()
  })

  it('renders the upload icon element', async () => {
    const { container } = await renderAddGarment()
    const icon = container.querySelector('[class*="uploadIcon"]') as HTMLElement
    expect(icon).not.toBeNull()
    expect(icon.textContent).toContain('↑')
  })

  it('shows the serif headline text', async () => {
    await renderAddGarment()
    expect(screen.getByText('Drag a garment photograph here')).toBeInTheDocument()
  })

  it('shows the Choose a file button', async () => {
    await renderAddGarment()
    expect(screen.getByRole('button', { name: /choose a file/i })).toBeInTheDocument()
  })

  it('has no axe violations in default state', async () => {
    const { container } = await renderAddGarment()
    await expectNoAxeViolations(container)
  })
})

// ── Drag-over state ───────────────────────────────────────────────────────────

describe('AddGarment — drag-over state', () => {
  it('shows the down arrow icon on drag-over', async () => {
    const { container } = await renderAddGarment()
    const zone = screen.getByLabelText('File drop zone')
    fireEvent.dragOver(zone)

    const icon = container.querySelector('[class*="uploadIcon"]') as HTMLElement
    expect(icon).not.toBeNull()
    expect(icon.textContent).toContain('↓')
  })

  it('changes headline to "Drop to upload" on drag-over', async () => {
    await renderAddGarment()
    const zone = screen.getByLabelText('File drop zone')
    fireEvent.dragOver(zone)
    expect(screen.getByText('Drop to upload')).toBeInTheDocument()
  })

  it('hides the Choose a file button on drag-over', async () => {
    await renderAddGarment()
    const zone = screen.getByLabelText('File drop zone')
    fireEvent.dragOver(zone)
    expect(screen.queryByRole('button', { name: /choose a file/i })).not.toBeInTheDocument()
  })
})

// ── Detecting state ───────────────────────────────────────────────────────────

describe('AddGarment — detecting state', () => {
  it('shows three dots (not skeleton bars) while detecting', async () => {
    server.use(
      http.post(DETECT_URL, () => new Promise(() => {})),
    )

    const user = userEvent.setup()
    const { container } = await renderAddGarment()
    const input = screen.getByTestId('file-input')
    await user.upload(input, new File(['x'], 'shirt.jpg', { type: 'image/jpeg' }))

    await waitFor(() => {
      const dots = container.querySelectorAll('[class*="dot"]')
      expect(dots.length).toBe(3)
    })

    expect(container.querySelector('[class*="skeleton"]')).toBeNull()
  })

  it('shows the detecting headline while in flight', async () => {
    server.use(
      http.post(DETECT_URL, () => new Promise(() => {})),
    )

    const user = userEvent.setup()
    await renderAddGarment()
    const input = screen.getByTestId('file-input')
    await user.upload(input, new File(['x'], 'jacket.png', { type: 'image/png' }))

    await waitFor(() =>
      expect(screen.getByText(/Detecting colours/i)).toBeInTheDocument()
    )
  })
})

// ── Error banner ──────────────────────────────────────────────────────────────

describe('Banner error variant', () => {
  it('contains the circle icon element', () => {
    const { container } = render(
      <Banner variant="error" message="Unsupported file format." />,
    )
    const icon = container.querySelector('[class*="icon"]')
    expect(icon).not.toBeNull()
    expect(icon?.textContent).toBe('!')
  })

  it('renders the message text', () => {
    render(<Banner variant="error" message="Something went wrong." />)
    expect(screen.getByText('Something went wrong.')).toBeInTheDocument()
  })

  it('warning variant shows an icon', () => {
    const { container } = render(
      <Banner variant="warning" message="Detection fell back to defaults." />,
    )
    expect(container.querySelector('[class*="icon"]')).not.toBeNull()
  })

  it('error banner has no axe violations', async () => {
    const { container } = render(
      <Banner variant="error" message="Something went wrong." />,
    )
    await expectNoAxeViolations(container)
  })

  it('warning banner has no axe violations', async () => {
    const { container } = render(
      <Banner variant="warning" message="Colour detection fell back." />,
    )
    await expectNoAxeViolations(container)
  })
})
