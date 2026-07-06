/**
 * Shared component tests — design system §5, NFR-11, test strategy §10.3.
 *
 * Covers new and restyled shared components:
 *   - Button (all variants + disabled)
 *   - Chip (default + selected + disabled)
 *   - TextInput (plain + labelled)
 *
 * Each interactive component is checked for:
 *   - Correct role / accessible text
 *   - jest-axe zero violations (NFR-11)
 *   - aria-pressed for selected Chip
 */

import { render, screen } from '@testing-library/react'
import { axe, toHaveNoViolations } from 'jest-axe'
import { describe, it, expect } from 'vitest'

import Button from '../components/Button'
import Chip from '../components/Chip'
import TextInput from '../components/TextInput'

expect.extend(toHaveNoViolations)

// ── Button ────────────────────────────────────────────────────────────────────

describe('Button', () => {
  it('renders as a button element', () => {
    render(<Button>Save</Button>)
    expect(screen.getByRole('button', { name: 'Save' })).toBeInTheDocument()
  })

  it('defaults to primary variant', () => {
    const { container } = render(<Button>Save</Button>)
    const btn = container.querySelector('button')
    expect(btn?.className).toMatch(/primary/)
  })

  it('renders secondary variant', () => {
    const { container } = render(<Button variant="secondary">Cancel</Button>)
    expect(container.querySelector('button')?.className).toMatch(/secondary/)
  })

  it('renders ghost variant', () => {
    const { container } = render(<Button variant="ghost">Skip</Button>)
    expect(container.querySelector('button')?.className).toMatch(/ghost/)
  })

  it('renders destructive variant', () => {
    const { container } = render(<Button variant="destructive">Delete</Button>)
    expect(container.querySelector('button')?.className).toMatch(/destructive/)
  })

  it('passes disabled attribute through', () => {
    render(<Button disabled>Save</Button>)
    expect(screen.getByRole('button', { name: 'Save' })).toBeDisabled()
  })

  it('passes onClick through', () => {
    let clicked = false
    render(<Button onClick={() => { clicked = true }}>Click</Button>)
    screen.getByRole('button').click()
    expect(clicked).toBe(true)
  })

  it('primary button has no axe violations', async () => {
    const { container } = render(<Button>Save</Button>)
    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })

  it('secondary button has no axe violations', async () => {
    const { container } = render(<Button variant="secondary">Cancel</Button>)
    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })

  it('ghost button has no axe violations', async () => {
    const { container } = render(<Button variant="ghost">Skip</Button>)
    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })

  it('destructive button has no axe violations', async () => {
    const { container } = render(<Button variant="destructive">Delete</Button>)
    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })

  it('disabled button has no axe violations', async () => {
    const { container } = render(<Button disabled>Save</Button>)
    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })
})

// ── Chip ──────────────────────────────────────────────────────────────────────

describe('Chip', () => {
  it('renders as a button element', () => {
    render(<Chip>Teal</Chip>)
    expect(screen.getByRole('button', { name: 'Teal' })).toBeInTheDocument()
  })

  it('has aria-pressed=false when not selected', () => {
    render(<Chip>Teal</Chip>)
    expect(screen.getByRole('button', { name: 'Teal' })).toHaveAttribute('aria-pressed', 'false')
  })

  it('has aria-pressed=true when selected', () => {
    render(<Chip selected>Navy</Chip>)
    expect(screen.getByRole('button', { name: 'Navy' })).toHaveAttribute('aria-pressed', 'true')
  })

  it('carries selected class when selected', () => {
    const { container } = render(<Chip selected>Navy</Chip>)
    expect(container.querySelector('button')?.className).toMatch(/selected/)
  })

  it('default chip has no axe violations', async () => {
    const { container } = render(<Chip>Teal</Chip>)
    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })

  it('selected chip has no axe violations', async () => {
    const { container } = render(<Chip selected>Navy</Chip>)
    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })

  it('disabled chip has no axe violations', async () => {
    const { container } = render(<Chip disabled>Muted</Chip>)
    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })
})

// ── TextInput ─────────────────────────────────────────────────────────────────

describe('TextInput', () => {
  it('renders an input element', () => {
    render(<TextInput />)
    expect(screen.getByRole('textbox')).toBeInTheDocument()
  })

  it('renders with a label associated via id', () => {
    render(<TextInput id="name" label="Full name" />)
    expect(screen.getByLabelText('Full name')).toBeInTheDocument()
  })

  it('passes placeholder through', () => {
    render(<TextInput placeholder="Search…" />)
    expect(screen.getByPlaceholderText('Search…')).toBeInTheDocument()
  })

  it('passes disabled attribute through', () => {
    render(<TextInput disabled />)
    expect(screen.getByRole('textbox')).toBeDisabled()
  })

  it('unlabelled input has no axe violations', async () => {
    const { container } = render(<TextInput aria-label="Search garments" />)
    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })

  it('labelled input has no axe violations', async () => {
    const { container } = render(<TextInput id="q" label="Search" />)
    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })

  it('disabled labelled input has no axe violations', async () => {
    const { container } = render(<TextInput id="q2" label="Search" disabled />)
    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })
})
