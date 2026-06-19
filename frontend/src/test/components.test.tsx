import { render, screen, waitFor } from '@testing-library/react'
import { renderHook } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import type { ReactNode } from 'react'
import { describe, it, expect } from 'vitest'
import { http, HttpResponse } from 'msw'
import { server } from './server'

import Swatch from '../components/Swatch'
import PaletteStrip from '../components/PaletteStrip'
import GarmentCard from '../components/GarmentCard'
import Banner from '../components/Banner'
import LoadingState from '../components/LoadingState'
import { typeLabel } from '../utils/typeLabel'
import { useTaxonomy, useGarments, useDetect, useSuggest } from '../api/queries'
import { ApiRequestError } from '../api/types'

import {
  GARMENT_SUMMARY,
  DETECTION_RESPONSE,
  TAXONOMY_RESPONSE,
  INVENTORY_RESPONSE,
  SUGGESTION_RESPONSE,
  ERR_UNSUPPORTED_FORMAT,
} from './contract-examples'

// ── Helpers ───────────────────────────────────────────────────────────────────

function makeWrapper() {
  const qc = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  })
  return function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={qc}>{children}</QueryClientProvider>
  }
}

// ── typeLabel ─────────────────────────────────────────────────────────────────

describe('typeLabel', () => {
  it.each([
    ['top',       'Top'],
    ['bottom',    'Bottom'],
    ['jersey',    'Jersey'],
    ['jacket',    'Jacket'],
    ['socks',     'Socks'],
    ['shoes',     'Shoes'],
    ['hat',       'Hat'],
    ['accessory', 'Accessory'],
  ] as [string, string][])('typeLabel(%s) → %s', (type, expected) => {
    expect(typeLabel(type)).toBe(expected)
  })
})

// ── Swatch ────────────────────────────────────────────────────────────────────

describe('Swatch', () => {
  it('fills the square with the given hex (FR-5)', () => {
    const { container } = render(
      <Swatch hex="#2CADA0" family="Teal" proportion={80} />,
    )
    const square = container.querySelector('[data-testid="swatch-square"]') as HTMLElement
    expect(square).toHaveStyle({ backgroundColor: '#2CADA0' })
  })

  it('shows the family name', () => {
    render(<Swatch hex="#2CADA0" family="Teal" />)
    expect(screen.getByText('Teal')).toBeInTheDocument()
  })

  it('shows proportion when provided', () => {
    render(<Swatch hex="#2CADA0" family="Teal" proportion={80} />)
    expect(screen.getByText('80%')).toBeInTheDocument()
  })

  it('omits proportion when not provided', () => {
    render(<Swatch hex="#2CADA0" family="Teal" />)
    expect(screen.queryByText(/%/)).not.toBeInTheDocument()
  })
})

// ── PaletteStrip ──────────────────────────────────────────────────────────────

describe('PaletteStrip', () => {
  it('renders one segment per colour', () => {
    render(<PaletteStrip colours={DETECTION_RESPONSE.colours} />)
    const segments = screen.getAllByTestId('palette-segment')
    expect(segments).toHaveLength(DETECTION_RESPONSE.colours.length)
  })

  it('renders colours in position order (first = highest proportion)', () => {
    render(<PaletteStrip colours={DETECTION_RESPONSE.colours} />)
    const segments = screen.getAllByTestId('palette-segment')
    // DETECTION_RESPONSE.colours[0] is Teal 80%, colours[1] is Orange 20%
    expect(segments[0]).toHaveAttribute('data-hex', '#2CADA0')
    expect(segments[1]).toHaveAttribute('data-hex', '#EE8225')
  })

  it('sets width proportional to proportion', () => {
    render(<PaletteStrip colours={DETECTION_RESPONSE.colours} />)
    const segments = screen.getAllByTestId('palette-segment')
    expect(segments[0]).toHaveStyle({ width: '80%' })
    expect(segments[1]).toHaveStyle({ width: '20%' })
  })
})

// ── GarmentCard ───────────────────────────────────────────────────────────────

describe('GarmentCard', () => {
  it('shows the capitalised type label', () => {
    render(<GarmentCard garment={GARMENT_SUMMARY} />)
    expect(screen.getByText('Jumper')).toBeInTheDocument()
  })

  it('shows the thumbnail image with the thumbnail_url', () => {
    render(<GarmentCard garment={GARMENT_SUMMARY} />)
    const img = screen.getByRole('img')
    expect(img).toHaveAttribute('src', GARMENT_SUMMARY.thumbnail_url)
  })

  it('renders a palette strip', () => {
    render(<GarmentCard garment={GARMENT_SUMMARY} />)
    expect(screen.getAllByTestId('palette-segment').length).toBeGreaterThan(0)
  })

  it('shows slot caption when provided', () => {
    render(<GarmentCard garment={GARMENT_SUMMARY} slot="top" />)
    expect(screen.getByText('top')).toBeInTheDocument()
  })

  it('omits slot caption when not provided', () => {
    const { container } = render(<GarmentCard garment={GARMENT_SUMMARY} />)
    // No slot span rendered — palette strip is still present
    expect(container.querySelector('[class*="slot"]')).not.toBeInTheDocument()
  })
})

// ── Banner ────────────────────────────────────────────────────────────────────

describe('Banner', () => {
  it('renders the message verbatim (error variant)', () => {
    render(
      <Banner variant="error" message="Only JPEG, PNG and WebP photographs are accepted." />,
    )
    expect(
      screen.getByText('Only JPEG, PNG and WebP photographs are accepted.'),
    ).toBeInTheDocument()
  })

  it('does not show a machine code', () => {
    render(<Banner variant="error" message="Only JPEG, PNG and WebP photographs are accepted." />)
    expect(screen.queryByText('unsupported_format')).not.toBeInTheDocument()
  })

  it('has role=alert for error variant', () => {
    render(<Banner variant="error" message="Error." />)
    expect(screen.getByRole('alert')).toBeInTheDocument()
  })

  it('renders the message verbatim (warning variant)', () => {
    render(
      <Banner variant="warning" message="Colour detection fell back to a simpler method." />,
    )
    expect(
      screen.getByText('Colour detection fell back to a simpler method.'),
    ).toBeInTheDocument()
  })

  it('has role=status for warning variant', () => {
    render(<Banner variant="warning" message="Warning." />)
    expect(screen.getByRole('status')).toBeInTheDocument()
  })
})

// ── LoadingState ──────────────────────────────────────────────────────────────

describe('LoadingState', () => {
  it('renders without crashing', () => {
    const { container } = render(<LoadingState />)
    expect(container.firstChild).toBeInTheDocument()
  })

  it('shows an optional label', () => {
    render(<LoadingState label="Loading wardrobe…" />)
    expect(screen.getByText('Loading wardrobe…')).toBeInTheDocument()
  })

  it('has aria-busy when rendering', () => {
    const { container } = render(<LoadingState />)
    expect(container.querySelector('[aria-busy="true"]')).toBeInTheDocument()
  })
})

// ── Query hooks — useTaxonomy ─────────────────────────────────────────────────

describe('useTaxonomy', () => {
  it('fetches taxonomy families from the API', async () => {
    const { result } = renderHook(() => useTaxonomy(), {
      wrapper: makeWrapper(),
    })
    await waitFor(() => expect(result.current.isSuccess).toBe(true))
    expect(result.current.data?.families).toHaveLength(
      TAXONOMY_RESPONSE.families.length,
    )
  })

  it('returns each family name', async () => {
    const { result } = renderHook(() => useTaxonomy(), {
      wrapper: makeWrapper(),
    })
    await waitFor(() => expect(result.current.isSuccess).toBe(true))
    const names = result.current.data!.families.map((f) => f.name)
    expect(names).toContain('Teal')
    expect(names).toContain('Navy')
  })
})

// ── Query hooks — useGarments ─────────────────────────────────────────────────

describe('useGarments', () => {
  it('returns the inventory from the API', async () => {
    const { result } = renderHook(() => useGarments(), {
      wrapper: makeWrapper(),
    })
    await waitFor(() => expect(result.current.isSuccess).toBe(true))
    expect(result.current.data?.garments).toHaveLength(
      INVENTORY_RESPONSE.garments.length,
    )
    expect(result.current.data?.total).toBe(INVENTORY_RESPONSE.total)
  })

  it('exposes a garment with the contract shape', async () => {
    const { result } = renderHook(() => useGarments(), {
      wrapper: makeWrapper(),
    })
    await waitFor(() => expect(result.current.isSuccess).toBe(true))
    const g = result.current.data!.garments[0]
    expect(g).toHaveProperty('id')
    expect(g).toHaveProperty('category')
    expect(g).toHaveProperty('colours')
    expect(g).toHaveProperty('thumbnail_url')
  })
})

// ── Query hooks — useDetect (mutation) ────────────────────────────────────────

describe('useDetect', () => {
  it('posts a file and returns a detection response', async () => {
    const { result } = renderHook(() => useDetect(), {
      wrapper: makeWrapper(),
    })
    const file = new File(['bytes'], 'garment.jpg', { type: 'image/jpeg' })
    result.current.mutate(file)
    await waitFor(() => expect(result.current.isSuccess).toBe(true))
    expect(result.current.data?.token).toBe(DETECTION_RESPONSE.token)
    expect(result.current.data?.colours).toHaveLength(
      DETECTION_RESPONSE.colours.length,
    )
  })

  it('surfaces the error message on API failure', async () => {
    server.use(
      http.post('http://127.0.0.1:8000/api/detections', () =>
        HttpResponse.json(ERR_UNSUPPORTED_FORMAT, { status: 400 }),
      ),
    )
    const { result } = renderHook(() => useDetect(), {
      wrapper: makeWrapper(),
    })
    const file = new File(['bytes'], 'garment.jpg', { type: 'image/jpeg' })
    result.current.mutate(file)
    await waitFor(() => expect(result.current.isError).toBe(true))
    const err = result.current.error as ApiRequestError
    expect(err.message).toBe(ERR_UNSUPPORTED_FORMAT.error.message)
    expect(err.code).toBe(ERR_UNSUPPORTED_FORMAT.error.code)
  })
})

// ── Query hooks — useSuggest (mutation) ───────────────────────────────────────

describe('useSuggest', () => {
  it('posts a suggestions request and returns combinations', async () => {
    const { result } = renderHook(() => useSuggest(), {
      wrapper: makeWrapper(),
    })
    result.current.mutate(undefined)
    await waitFor(() => expect(result.current.isSuccess).toBe(true))
    expect(result.current.data?.combinations).toHaveLength(
      SUGGESTION_RESPONSE.combinations.length,
    )
  })

  it('passes include flags to the API', async () => {
    let capturedBody: unknown
    server.use(
      http.post('http://127.0.0.1:8000/api/suggestions', async ({ request }) => {
        capturedBody = await request.json()
        return HttpResponse.json(SUGGESTION_RESPONSE)
      }),
    )
    const { result } = renderHook(() => useSuggest(), {
      wrapper: makeWrapper(),
    })
    result.current.mutate({ include: { jersey: true } })
    await waitFor(() => expect(result.current.isSuccess).toBe(true))
    expect(capturedBody).toEqual({ include: { jersey: true } })
  })
})
