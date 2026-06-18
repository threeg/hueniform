import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect } from 'vitest'
import { http, HttpResponse } from 'msw'
import { server } from '../test/server'
import { renderRoute } from '../test/test-utils'

import Wardrobe from './Wardrobe'
import {
  GARMENT_SUMMARY,
  GARMENT_ID,
  TAXONOMY_RESPONSE,
  INVENTORY_RESPONSE,
  ERR_INVALID_FILTER,
} from '../test/contract-examples'

// ── Helpers ───────────────────────────────────────────────────────────────────

interface RenderOptions {
  initialSearch?: string
}

function renderScreen({ initialSearch = '' }: RenderOptions = {}) {
  return renderRoute(
    [
      { path: '/', element: <Wardrobe /> },
      { path: '/add', element: <div data-testid="add-screen" /> },
      { path: '/garments/:id', element: <div data-testid="detail-screen" /> },
    ],
    [initialSearch ? `/?${initialSearch}` : '/'],
  )
}

const user = userEvent.setup

// ── Default grid (FR-35) ──────────────────────────────────────────────────────

describe('Wardrobe — default grid (FR-35)', () => {
  it('shows a card for each garment in the inventory', async () => {
    renderScreen()
    await waitFor(() =>
      expect(screen.getAllByRole('listitem').length).toBeGreaterThan(0),
    )
    expect(screen.getAllByRole('listitem')).toHaveLength(INVENTORY_RESPONSE.garments.length)
  })

  it('shows the result count', async () => {
    renderScreen()
    await waitFor(() =>
      expect(screen.getByTestId('result-count')).toHaveTextContent(
        `${INVENTORY_RESPONSE.total} garment`,
      ),
    )
  })

  it('card link navigates to /garments/:id on click', async () => {
    renderScreen()
    const link = await screen.findByRole('link', { name: /garment detail/i })
    await user().click(link)
    await waitFor(() =>
      expect(screen.getByTestId('detail-screen')).toBeInTheDocument(),
    )
  })
})

// ── Filter bar — taxonomy (FR-35) ─────────────────────────────────────────────

describe('Wardrobe — filter bar taxonomy', () => {
  it('populates family dropdown with taxonomy families', async () => {
    renderScreen()
    const select = screen.getByRole('combobox', { name: 'Filter by colour family' })
    // Wait for taxonomy to load
    await waitFor(() => {
      const options = Array.from((select as HTMLSelectElement).options).map(o => o.value)
      expect(options).toContain('Teal')
    })
    const options = Array.from((select as HTMLSelectElement).options).map(o => o.value)
    expect(options).toContain('Navy')
    expect(options).toContain('Red')
  })

  it('includes all 8 garment types in the type dropdown', () => {
    renderScreen()
    const select = screen.getByRole('combobox', { name: 'Filter by type' })
    const values = Array.from((select as HTMLSelectElement).options).map(o => o.value)
    expect(values).toContain('top')
    expect(values).toContain('bottom')
    expect(values).toContain('jersey')
    expect(values).toContain('jacket')
    expect(values).toContain('socks')
    expect(values).toContain('shoes')
    expect(values).toContain('hat')
    expect(values).toContain('accessory')
  })
})

// ── Filtering — query parameters (FR-35) ─────────────────────────────────────

describe('Wardrobe — filtering (FR-35)', () => {
  it('sends type param when type filter is selected', async () => {
    let capturedUrl: string | undefined
    server.use(
      http.get('http://127.0.0.1:8000/api/garments', ({ request }) => {
        capturedUrl = request.url
        return HttpResponse.json(INVENTORY_RESPONSE)
      }),
    )
    renderScreen()
    const select = screen.getByRole('combobox', { name: 'Filter by type' })
    await user().selectOptions(select, 'jersey')
    await waitFor(() => {
      expect(capturedUrl).toBeDefined()
      expect(capturedUrl).toContain('type=jersey')
    })
  })

  it('sends family param when family filter is selected', async () => {
    let capturedUrl: string | undefined
    server.use(
      http.get('http://127.0.0.1:8000/api/garments', ({ request }) => {
        capturedUrl = request.url
        return HttpResponse.json(INVENTORY_RESPONSE)
      }),
    )
    renderScreen()
    const select = screen.getByRole('combobox', { name: 'Filter by colour family' })
    // Wait for taxonomy options to load
    await waitFor(() => {
      const options = Array.from((select as HTMLSelectElement).options).map(o => o.value)
      expect(options).toContain('Teal')
    })
    await user().selectOptions(select, 'Teal')
    await waitFor(() => {
      expect(capturedUrl).toBeDefined()
      expect(capturedUrl).toContain('family=Teal')
    })
  })

  it('sends both type and family when both filters are active (AND, FR-35)', async () => {
    let capturedUrl: string | undefined
    server.use(
      http.get('http://127.0.0.1:8000/api/garments', ({ request }) => {
        capturedUrl = request.url
        return HttpResponse.json(INVENTORY_RESPONSE)
      }),
    )
    renderScreen()
    const typeSelect   = screen.getByRole('combobox', { name: 'Filter by type' })
    const familySelect = screen.getByRole('combobox', { name: 'Filter by colour family' })
    // Wait for taxonomy
    await waitFor(() => {
      const opts = Array.from((familySelect as HTMLSelectElement).options).map(o => o.value)
      expect(opts).toContain('Teal')
    })
    await user().selectOptions(typeSelect,   'jersey')
    await user().selectOptions(familySelect, 'Teal')
    await waitFor(() => {
      expect(capturedUrl).toContain('type=jersey')
      expect(capturedUrl).toContain('family=Teal')
    })
  })

  it('shows the clear-filters button when a filter is active', async () => {
    renderScreen()
    const typeSelect = screen.getByRole('combobox', { name: 'Filter by type' })
    await user().selectOptions(typeSelect, 'top')
    await waitFor(() =>
      expect(screen.getByTestId('clear-filters')).toBeInTheDocument(),
    )
  })

  it('hides the clear-filters button when no filter is active', () => {
    renderScreen()
    expect(screen.queryByTestId('clear-filters')).not.toBeInTheDocument()
  })

  it('clears filters and resets the dropdowns when Clear is clicked', async () => {
    renderScreen()
    const typeSelect = screen.getByRole('combobox', { name: 'Filter by type' })
    await user().selectOptions(typeSelect, 'top')
    await waitFor(() =>
      expect(screen.getByTestId('clear-filters')).toBeInTheDocument(),
    )
    await user().click(screen.getByTestId('clear-filters'))
    await waitFor(() =>
      expect(screen.queryByTestId('clear-filters')).not.toBeInTheDocument(),
    )
    expect((typeSelect as HTMLSelectElement).value).toBe('')
  })
})

// ── Empty states (FR-35) ──────────────────────────────────────────────────────

describe('Wardrobe — empty wardrobe (FR-35)', () => {
  it('shows the empty-wardrobe state with a CTA link when total is 0 and no filters', async () => {
    server.use(
      http.get('http://127.0.0.1:8000/api/garments', () =>
        HttpResponse.json({ garments: [], total: 0 }),
      ),
    )
    renderScreen()
    await waitFor(() =>
      expect(screen.getByTestId('empty-wardrobe')).toBeInTheDocument(),
    )
    expect(screen.getByRole('link', { name: /Add your first garment/i })).toBeInTheDocument()
  })

  it('shows the empty-filter state with clear offer when total is 0 and filters are active', async () => {
    server.use(
      http.get('http://127.0.0.1:8000/api/garments', () =>
        HttpResponse.json({ garments: [], total: 0 }),
      ),
    )
    renderScreen({ initialSearch: 'type=jersey' })
    await waitFor(() =>
      expect(screen.getByTestId('empty-filter')).toBeInTheDocument(),
    )
    expect(screen.queryByTestId('empty-wardrobe')).not.toBeInTheDocument()
    // Offers to clear from within the empty-filter block
    const clearBtn = screen.getAllByTestId('clear-filters')
    expect(clearBtn.length).toBeGreaterThan(0)
  })
})

// ── Loading state ─────────────────────────────────────────────────────────────

describe('Wardrobe — loading state', () => {
  it('shows the loading indicator while the inventory is fetching', async () => {
    server.use(
      http.get('http://127.0.0.1:8000/api/garments', async () => {
        await new Promise(resolve => setTimeout(resolve, 80))
        return HttpResponse.json(INVENTORY_RESPONSE)
      }),
    )
    renderScreen()
    expect(screen.getByText('Loading wardrobe…')).toBeInTheDocument()
    await waitFor(() =>
      expect(screen.queryByText('Loading wardrobe…')).not.toBeInTheDocument(),
    )
  })
})

// ── Error state ───────────────────────────────────────────────────────────────

describe('Wardrobe — error state', () => {
  it('shows an error banner and retry button on load failure', async () => {
    server.use(
      http.get('http://127.0.0.1:8000/api/garments', () =>
        HttpResponse.json(ERR_INVALID_FILTER, { status: 422 }),
      ),
    )
    renderScreen()
    await waitFor(() =>
      expect(screen.getByRole('alert')).toBeInTheDocument(),
    )
    expect(screen.getByRole('button', { name: 'Retry' })).toBeInTheDocument()
  })
})

// ── URL state preservation ─────────────────────────────────────────────────────

describe('Wardrobe — URL filter state', () => {
  it('pre-selects type from URL search params on mount', async () => {
    renderScreen({ initialSearch: 'type=jersey' })
    const select = screen.getByRole('combobox', { name: 'Filter by type' }) as HTMLSelectElement
    // The select value is set from URL immediately
    await waitFor(() => expect(select.value).toBe('jersey'))
  })
})
