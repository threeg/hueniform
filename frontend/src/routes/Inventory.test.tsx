import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect } from 'vitest'
import { http, HttpResponse } from 'msw'
import { server } from '../test/server'
import { renderRoute } from '../test/test-utils'
import { expectNoAxeViolations } from '../test/a11y'

import Wardrobe from './Wardrobe'
import {
  GARMENT_SUMMARY,
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
  it('populates the Colour dropdown with taxonomy families', async () => {
    renderScreen()
    await user().click(screen.getByTestId('pill-select-family'))
    await waitFor(() =>
      expect(screen.getByRole('option', { name: 'Teal' })).toBeInTheDocument(),
    )
    expect(screen.getByRole('option', { name: 'Navy' })).toBeInTheDocument()
    expect(screen.getByRole('option', { name: 'Red' })).toBeInTheDocument()
  })

  it('Category dropdown contains all 40 garment categories', async () => {
    renderScreen()
    await user().click(screen.getByTestId('pill-select-category'))
    await screen.findByRole('option', { name: 'T-shirt' })
    const opts = screen.getAllByRole('option')
    // +1 for "All categories" placeholder option
    expect(opts.length).toBeGreaterThanOrEqual(41)
    const labels = opts.map(o => o.textContent?.trim())
    expect(labels).toContain('T-shirt')
    expect(labels).toContain('Trousers')
    expect(labels).toContain('Jumper')
    expect(labels).toContain('Jacket')
    expect(labels).toContain('Socks')
    expect(labels).toContain('Shoes')
    expect(labels).toContain('Hat')
    expect(labels).toContain('Dress')
  })
})

// ── Filtering — query parameters (FR-35) ─────────────────────────────────────

describe('Wardrobe — filtering (FR-35)', () => {
  it('sends category param when type filter is selected', async () => {
    let capturedUrl: string | undefined
    server.use(
      http.get('http://127.0.0.1:8000/api/garments', ({ request }) => {
        capturedUrl = request.url
        return HttpResponse.json(INVENTORY_RESPONSE)
      }),
    )
    renderScreen()
    await user().click(screen.getByTestId('pill-select-category'))
    await user().click(await screen.findByRole('option', { name: 'Jumper' }))
    await waitFor(() => {
      expect(capturedUrl).toBeDefined()
      expect(capturedUrl).toContain('category=jumper')
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
    await user().click(screen.getByTestId('pill-select-family'))
    await user().click(await screen.findByRole('option', { name: 'Teal' }))
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
    await user().click(screen.getByTestId('pill-select-category'))
    await user().click(await screen.findByRole('option', { name: 'Jumper' }))
    await user().click(screen.getByTestId('pill-select-family'))
    await user().click(await screen.findByRole('option', { name: 'Teal' }))
    await waitFor(() => {
      expect(capturedUrl).toContain('category=jumper')
      expect(capturedUrl).toContain('family=Teal')
    })
  })

  it('shows the clear-filters button when a filter is active', async () => {
    renderScreen()
    await user().click(screen.getByTestId('pill-select-category'))
    await user().click(await screen.findByRole('option', { name: 'T-shirt' }))
    await waitFor(() =>
      expect(screen.getByTestId('clear-filters')).toBeInTheDocument(),
    )
  })

  it('hides the clear-filters button when no filter is active', () => {
    renderScreen()
    expect(screen.queryByTestId('clear-filters')).not.toBeInTheDocument()
  })

  it('clears filters and resets the pills when Clear is clicked', async () => {
    renderScreen()
    await user().click(screen.getByTestId('pill-select-category'))
    await user().click(await screen.findByRole('option', { name: 'T-shirt' }))
    await waitFor(() =>
      expect(screen.getByTestId('clear-filters')).toBeInTheDocument(),
    )
    await user().click(screen.getByTestId('clear-filters'))
    await waitFor(() =>
      expect(screen.queryByTestId('clear-filters')).not.toBeInTheDocument(),
    )
    expect(screen.getByTestId('pill-select-category')).toHaveAttribute(
      'aria-label', 'Category: All categories',
    )
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
    renderScreen({ initialSearch: 'category=jumper' })
    await waitFor(() =>
      expect(screen.getByTestId('empty-filter')).toBeInTheDocument(),
    )
    expect(screen.queryByTestId('empty-wardrobe')).not.toBeInTheDocument()
    const clearBtn = screen.getAllByTestId('clear-filters')
    expect(clearBtn.length).toBeGreaterThan(0)
  })
})

// ── Loading state ─────────────────────────────────────────────────────────────

describe('Wardrobe — loading state', () => {
  it('shows skeleton cards while the inventory is fetching', async () => {
    server.use(
      http.get('http://127.0.0.1:8000/api/garments', async () => {
        await new Promise(resolve => setTimeout(resolve, 80))
        return HttpResponse.json(INVENTORY_RESPONSE)
      }),
    )
    renderScreen()
    expect(screen.getByTestId('loading-skeleton')).toBeInTheDocument()
    await waitFor(() =>
      expect(screen.queryByTestId('loading-skeleton')).not.toBeInTheDocument(),
    )
  })

  it('shows "…" in the count while loading', async () => {
    server.use(
      http.get('http://127.0.0.1:8000/api/garments', async () => {
        await new Promise(resolve => setTimeout(resolve, 80))
        return HttpResponse.json(INVENTORY_RESPONSE)
      }),
    )
    renderScreen()
    expect(screen.getByTestId('result-count')).toHaveTextContent('…')
    await waitFor(() =>
      expect(screen.queryByTestId('result-count')).not.toHaveTextContent('…'),
    )
  })
})

// ── Error state ───────────────────────────────────────────────────────────────

describe('Wardrobe — error state', () => {
  it('shows an error banner with inline Retry on load failure', async () => {
    server.use(
      http.get('http://127.0.0.1:8000/api/garments', () =>
        HttpResponse.json(ERR_INVALID_FILTER, { status: 422 }),
      ),
    )
    renderScreen()
    await waitFor(() =>
      expect(screen.getByRole('alert')).toBeInTheDocument(),
    )
    const alert = screen.getByRole('alert')
    expect(alert).toContainElement(screen.getByRole('button', { name: 'Retry' }))
  })
})

// ── URL state preservation ─────────────────────────────────────────────────────

describe('Wardrobe — URL filter state', () => {
  it('pre-selects category from URL search params on mount', async () => {
    renderScreen({ initialSearch: 'category=jumper' })
    await waitFor(() =>
      expect(screen.getByTestId('pill-select-category')).toHaveAttribute(
        'aria-label', 'Category: Jumper',
      ),
    )
  })
})

// ── FR-47: order toggle ────────────────────────────────────────────────────────

describe('Wardrobe — order toggle (FR-47)', () => {
  it('renders Hue and Date added order buttons', async () => {
    renderScreen()
    await waitFor(() => expect(screen.getByTestId('order-hue')).toBeInTheDocument())
    expect(screen.getByTestId('order-date')).toBeInTheDocument()
  })

  it('Hue is pressed by default', async () => {
    renderScreen()
    await waitFor(() =>
      expect(screen.getByTestId('order-hue')).toHaveAttribute('aria-pressed', 'true'),
    )
    expect(screen.getByTestId('order-date')).toHaveAttribute('aria-pressed', 'false')
  })

  it('switching to Date sends order=date in the API request', async () => {
    let capturedUrl: string | undefined
    server.use(
      http.get('http://127.0.0.1:8000/api/garments', ({ request }) => {
        capturedUrl = request.url
        return HttpResponse.json(INVENTORY_RESPONSE)
      }),
    )
    renderScreen()
    await waitFor(() => expect(screen.getByTestId('order-date')).toBeInTheDocument())
    await user().click(screen.getByTestId('order-date'))
    await waitFor(() => {
      expect(capturedUrl).toBeDefined()
      expect(capturedUrl).toContain('order=date')
    })
  })

  it('order=date in URL pre-selects Date button', async () => {
    renderScreen({ initialSearch: 'order=date' })
    await waitFor(() =>
      expect(screen.getByTestId('order-date')).toHaveAttribute('aria-pressed', 'true'),
    )
  })
})

// ── FR-47: category grouping ──────────────────────────────────────────────────

describe('Wardrobe — category grouping (FR-47)', () => {
  it('renders a group header for each distinct category', async () => {
    server.use(
      http.get('http://127.0.0.1:8000/api/garments', () =>
        HttpResponse.json({
          garments: [
            { ...GARMENT_SUMMARY, id: 'aaa', category: 'jumper' },
            { ...GARMENT_SUMMARY, id: 'bbb', category: 'jumper' },
            { ...GARMENT_SUMMARY, id: 'ccc', category: 't_shirt' },
          ],
          total: 3,
        }),
      ),
    )
    renderScreen()
    await screen.findByTestId('group-header-jumper')
    expect(screen.getByTestId('group-header-t_shirt')).toBeInTheDocument()
  })

  it('group header shows category label and item count', async () => {
    server.use(
      http.get('http://127.0.0.1:8000/api/garments', () =>
        HttpResponse.json({
          garments: [
            { ...GARMENT_SUMMARY, id: 'aaa', category: 'jumper' },
            { ...GARMENT_SUMMARY, id: 'bbb', category: 'jumper' },
          ],
          total: 2,
        }),
      ),
    )
    renderScreen()
    const header = await screen.findByTestId('group-header-jumper')
    expect(header).toHaveTextContent('Jumper')
    expect(header).toHaveTextContent('2')
  })
})

// ── FR-47: region-grouped category dropdown ───────────────────────────────────

describe('Wardrobe — region-grouped category dropdown (FR-47)', () => {
  it('Category dropdown has group separators for all four body regions', async () => {
    const { container } = renderScreen()
    await user().click(screen.getByTestId('pill-select-category'))
    await screen.findByRole('option', { name: 'T-shirt' })
    const seps = container.querySelectorAll('[class*="groupSep"]')
    const labels = Array.from(seps).map(el => el.textContent)
    expect(labels).toContain('Head')
    expect(labels).toContain('Upper body')
    expect(labels).toContain('Lower body')
    expect(labels).toContain('Feet')
  })
})

// ── Visual structure (HUE-113) ────────────────────────────────────────────────

describe('Wardrobe — visual structure (HUE-113)', () => {
  it('result count is inside the title row, not the filter bar', async () => {
    const { container } = renderScreen()
    await waitFor(() =>
      expect(screen.getByTestId('result-count')).toBeInTheDocument(),
    )
    const titleRow = container.querySelector('[class*="titleRow"]')
    expect(titleRow).toBeInTheDocument()
    expect(titleRow).toContainElement(screen.getByTestId('result-count'))
  })

  it('group header has pill-badge class', async () => {
    server.use(
      http.get('http://127.0.0.1:8000/api/garments', () =>
        HttpResponse.json({
          garments: [{ ...GARMENT_SUMMARY, id: 'aaa', category: 'jumper' }],
          total: 1,
        }),
      ),
    )
    const { container } = renderScreen()
    await screen.findByTestId('group-header-jumper')
    expect(container.querySelector('[class*="groupBadge"]')).toBeInTheDocument()
  })

  it('group header contains count sub-pill', async () => {
    server.use(
      http.get('http://127.0.0.1:8000/api/garments', () =>
        HttpResponse.json({
          garments: [
            { ...GARMENT_SUMMARY, id: 'aaa', category: 'jumper' },
            { ...GARMENT_SUMMARY, id: 'bbb', category: 'jumper' },
          ],
          total: 2,
        }),
      ),
    )
    const { container } = renderScreen()
    await screen.findByTestId('group-header-jumper')
    const badge = container.querySelector('[class*="groupBadge"]')
    expect(badge?.querySelector('[class*="groupCount"]')).toBeInTheDocument()
    expect(badge?.querySelector('[class*="groupCount"]')?.textContent).toBe('2')
  })
})

// ── Visual structure — HUE-119 ────────────────────────────────────────────────

describe('Wardrobe — empty state visual structure (HUE-119)', () => {
  it('empty wardrobe shows diamond icon', async () => {
    server.use(
      http.get('http://127.0.0.1:8000/api/garments', () =>
        HttpResponse.json({ garments: [], total: 0 }),
      ),
    )
    const { container } = renderScreen()
    await waitFor(() =>
      expect(screen.getByTestId('empty-wardrobe')).toBeInTheDocument(),
    )
    expect(container.querySelector('[class*="emptyIcon"]')).toBeInTheDocument()
  })

  it('empty wardrobe shows serif heading', async () => {
    server.use(
      http.get('http://127.0.0.1:8000/api/garments', () =>
        HttpResponse.json({ garments: [], total: 0 }),
      ),
    )
    renderScreen()
    await waitFor(() =>
      expect(screen.getByRole('heading', { name: 'Your wardrobe is empty' })).toBeInTheDocument(),
    )
  })

  it('filter-empty state shows dashed card and inline clear link', async () => {
    server.use(
      http.get('http://127.0.0.1:8000/api/garments', () =>
        HttpResponse.json({ garments: [], total: 0 }),
      ),
    )
    const { container } = renderScreen({ initialSearch: 'category=jumper' })
    await waitFor(() =>
      expect(screen.getByTestId('empty-filter')).toBeInTheDocument(),
    )
    expect(container.querySelector('[class*="emptyCard"]')).toBeInTheDocument()
    expect(screen.getByText(/No garments match/i)).toBeInTheDocument()
    expect(screen.getByText(/Clear the filters/i)).toBeInTheDocument()
  })

  it('date-order: first card gets "newest" label, last card gets "oldest" label', async () => {
    server.use(
      http.get('http://127.0.0.1:8000/api/garments', () =>
        HttpResponse.json({
          garments: [
            { ...GARMENT_SUMMARY, id: 'aaa', category: 'jumper' },
            { ...GARMENT_SUMMARY, id: 'bbb', category: 'jumper' },
            { ...GARMENT_SUMMARY, id: 'ccc', category: 't_shirt' },
          ],
          total: 3,
        }),
      ),
    )
    renderScreen({ initialSearch: 'order=date' })
    await waitFor(() =>
      expect(screen.queryByTestId('loading-skeleton')).not.toBeInTheDocument(),
    )
    expect(screen.getByText('newest')).toBeInTheDocument()
    expect(screen.getByText('oldest')).toBeInTheDocument()
  })

  it('hue-order: no "newest"/"oldest" labels shown', async () => {
    renderScreen()
    await waitFor(() =>
      expect(screen.queryByTestId('loading-skeleton')).not.toBeInTheDocument(),
    )
    expect(screen.queryByText('newest')).not.toBeInTheDocument()
    expect(screen.queryByText('oldest')).not.toBeInTheDocument()
  })
})

// ── Accessibility (NFR-11) ────────────────────────────────────────────────────

describe('Wardrobe — accessibility (NFR-11)', () => {
  it('loaded grid state has no axe violations', async () => {
    const { container } = renderScreen()
    await waitFor(() =>
      expect(screen.getAllByRole('listitem').length).toBeGreaterThan(0),
    )
    await expectNoAxeViolations(container)
  })

  it('empty wardrobe state has no axe violations', async () => {
    server.use(
      http.get('http://127.0.0.1:8000/api/garments', () =>
        HttpResponse.json({ garments: [], total: 0 }),
      ),
    )
    const { container } = renderScreen()
    await waitFor(() =>
      expect(screen.getByTestId('empty-wardrobe')).toBeInTheDocument(),
    )
    await expectNoAxeViolations(container)
  })
})
