/**
 * App shell and responsive navigation tests — HUE-097, NFR-7, NFR-11.
 *
 * jsdom does not execute CSS media queries, so all three nav tiers
 * (sidebar, top nav, bottom tab bar) are in the DOM simultaneously.
 * Tests assert on DOM structure and accessibility; responsive visual
 * behaviour is verified via QA steps.
 */

import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { axe, toHaveNoViolations } from 'jest-axe'
import { describe, it, expect } from 'vitest'

import App from '../App'

expect.extend(toHaveNoViolations)

function renderShell(initialPath = '/') {
  return render(
    <MemoryRouter
      initialEntries={[initialPath]}
      future={{ v7_startTransition: true, v7_relativeSplatPath: true }}
    >
      <App />
    </MemoryRouter>,
  )
}

// ── Sidebar nav (desktop tier) ────────────────────────────────────────────

describe('sidebar (desktop nav)', () => {
  it('is present in the DOM as an aside element', () => {
    renderShell()
    expect(document.querySelector('aside')).toBeInTheDocument()
  })

  it('contains a navigation landmark labelled "Sidebar"', () => {
    renderShell()
    expect(screen.getByRole('navigation', { name: 'Sidebar' })).toBeInTheDocument()
  })

  it('sidebar nav contains Wardrobe link to /', () => {
    renderShell()
    const nav = screen.getByRole('navigation', { name: 'Sidebar' })
    const link = nav.querySelector('a[href="/"]')
    expect(link).toBeInTheDocument()
    expect(link).toHaveTextContent('Wardrobe')
  })

  it('sidebar nav contains Add garment link to /add', () => {
    renderShell()
    const nav = screen.getByRole('navigation', { name: 'Sidebar' })
    const link = nav.querySelector('a[href="/add"]')
    expect(link).toBeInTheDocument()
    expect(link).toHaveTextContent('Add garment')
  })

  it('sidebar nav contains Suggest outfit link to /suggest', () => {
    renderShell()
    const nav = screen.getByRole('navigation', { name: 'Sidebar' })
    const link = nav.querySelector('a[href="/suggest"]')
    expect(link).toBeInTheDocument()
    expect(link).toHaveTextContent('Suggest outfit')
  })
})

// ── Top nav (tablet tier) ─────────────────────────────────────────────────

describe('top nav (tablet nav)', () => {
  it('is present in the DOM labelled "Top navigation"', () => {
    renderShell()
    expect(screen.getByRole('navigation', { name: 'Top navigation' })).toBeInTheDocument()
  })

  it('top nav carries all three destinations', () => {
    renderShell()
    const nav = screen.getByRole('navigation', { name: 'Top navigation' })
    expect(nav.querySelector('a[href="/"]')).toBeInTheDocument()
    expect(nav.querySelector('a[href="/add"]')).toBeInTheDocument()
    expect(nav.querySelector('a[href="/suggest"]')).toBeInTheDocument()
  })
})

// ── Bottom tab bar (mobile tier) ──────────────────────────────────────────

describe('bottom tab bar (mobile nav)', () => {
  it('is present in the DOM labelled "Tab bar"', () => {
    renderShell()
    expect(screen.getByRole('navigation', { name: 'Tab bar' })).toBeInTheDocument()
  })

  it('tab bar carries all three destinations', () => {
    renderShell()
    const nav = screen.getByRole('navigation', { name: 'Tab bar' })
    expect(nav.querySelector('a[href="/"]')).toBeInTheDocument()
    expect(nav.querySelector('a[href="/add"]')).toBeInTheDocument()
    expect(nav.querySelector('a[href="/suggest"]')).toBeInTheDocument()
  })

  it('Add tab has accessible name "Add garment" (aria-label extends visible "Add")', () => {
    renderShell()
    const nav = screen.getByRole('navigation', { name: 'Tab bar' })
    const addLink = nav.querySelector('a[href="/add"]') as HTMLAnchorElement
    expect(addLink.getAttribute('aria-label')).toBe('Add garment')
  })

  it('Suggest tab has accessible name "Suggest outfit"', () => {
    renderShell()
    const nav = screen.getByRole('navigation', { name: 'Tab bar' })
    const suggestLink = nav.querySelector('a[href="/suggest"]') as HTMLAnchorElement
    expect(suggestLink.getAttribute('aria-label')).toBe('Suggest outfit')
  })

  it('tab links meet 44 px touch target (min-height style token)', () => {
    renderShell()
    const nav = screen.getByRole('navigation', { name: 'Tab bar' })
    const links = nav.querySelectorAll('a')
    expect(links.length).toBe(3)
    // Each link carries the tabLink class which sets min-height: 44px via token.
    // We verify the class is applied (CSS itself is trusted, per §10.1).
    links.forEach(link => expect(link.className).toMatch(/tabLink/))
  })
})

// ── Wordmark ──────────────────────────────────────────────────────────────

describe('wordmark', () => {
  it('is present (topBar and/or sidebar)', () => {
    renderShell()
    const wordmarks = screen.getAllByText('Hueniform')
    expect(wordmarks.length).toBeGreaterThanOrEqual(1)
  })
})

// ── Active state ──────────────────────────────────────────────────────────

describe('active state', () => {
  it('marks the Wardrobe sidebar link active at /', () => {
    renderShell('/')
    const nav = screen.getByRole('navigation', { name: 'Sidebar' })
    const wardrobeLink = nav.querySelector('a[href="/"]') as HTMLAnchorElement
    // React Router adds aria-current="page" to active NavLinks.
    expect(wardrobeLink.getAttribute('aria-current')).toBe('page')
  })

  it('marks the Add garment sidebar link active at /add', () => {
    renderShell('/add')
    const nav = screen.getByRole('navigation', { name: 'Sidebar' })
    const addLink = nav.querySelector('a[href="/add"]') as HTMLAnchorElement
    expect(addLink.getAttribute('aria-current')).toBe('page')
  })
})

// ── Main landmark ─────────────────────────────────────────────────────────

describe('main landmark', () => {
  it('has exactly one main element', () => {
    renderShell()
    expect(screen.getAllByRole('main').length).toBe(1)
  })
})

// ── Accessibility ─────────────────────────────────────────────────────────

describe('accessibility (jest-axe)', () => {
  it('shell at / has no axe violations', async () => {
    const { container } = renderShell('/')
    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })

  it('shell at /add has no axe violations', async () => {
    const { container } = renderShell('/add')
    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })

  it('shell at /suggest has no axe violations', async () => {
    const { container } = renderShell('/suggest')
    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })
})
