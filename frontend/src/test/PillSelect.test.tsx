/**
 * PillSelect component tests — HUE-114.
 *
 * Covers: closed state rendering, open/close behaviour, option selection,
 * outside-click close, keyboard navigation, ARIA listbox pattern, axe clean.
 */

import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, vi } from 'vitest'
import { expectNoAxeViolations } from './a11y'

import PillSelect from '../components/PillSelect'
import type { PillSelectOption, PillSelectGroup } from '../components/PillSelect'

const FLAT_OPTIONS: PillSelectOption[] = [
  { value: 'teal',   label: 'Teal'   },
  { value: 'navy',   label: 'Navy'   },
  { value: 'red',    label: 'Red'    },
  { value: 'orange', label: 'Orange' },
]

const GROUPED_OPTIONS: PillSelectGroup[] = [
  { groupLabel: 'Head',       options: [{ value: 'hat', label: 'Hat' }, { value: 'cap', label: 'Cap' }] },
  { groupLabel: 'Upper body', options: [{ value: 't_shirt', label: 'T-shirt' }, { value: 'jumper', label: 'Jumper' }] },
]

const user = userEvent.setup

// ── Closed state ──────────────────────────────────────────────────────────────

describe('PillSelect — closed state', () => {
  it('renders the trigger button with label, placeholder value, and caret', () => {
    render(<PillSelect label="Colour" value="" placeholder="All colours" options={FLAT_OPTIONS} onChange={() => {}} />)
    const btn = screen.getByRole('button')
    expect(btn).toBeInTheDocument()
    expect(btn).toHaveAttribute('aria-haspopup', 'listbox')
    expect(btn).toHaveAttribute('aria-expanded', 'false')
    expect(btn).toHaveAttribute('aria-label', 'Colour: All colours')
  })

  it('reflects selected value in aria-label when an option is chosen', () => {
    render(<PillSelect label="Colour" value="teal" placeholder="All colours" options={FLAT_OPTIONS} onChange={() => {}} />)
    expect(screen.getByRole('button')).toHaveAttribute('aria-label', 'Colour: Teal')
  })

  it('does not render the listbox when closed', () => {
    render(<PillSelect label="Colour" value="" placeholder="All colours" options={FLAT_OPTIONS} onChange={() => {}} />)
    expect(screen.queryByRole('listbox')).not.toBeInTheDocument()
  })
})

// ── Open / close ──────────────────────────────────────────────────────────────

describe('PillSelect — open/close', () => {
  it('opens the listbox panel on trigger click', async () => {
    render(<PillSelect label="Colour" value="" placeholder="All colours" options={FLAT_OPTIONS} onChange={() => {}} />)
    await user().click(screen.getByRole('button'))
    expect(screen.getByRole('listbox')).toBeInTheDocument()
    expect(screen.getByRole('button')).toHaveAttribute('aria-expanded', 'true')
  })

  it('closes the panel on a second click', async () => {
    render(<PillSelect label="Colour" value="" placeholder="All colours" options={FLAT_OPTIONS} onChange={() => {}} />)
    const btn = screen.getByRole('button')
    await user().click(btn)
    await user().click(btn)
    expect(screen.queryByRole('listbox')).not.toBeInTheDocument()
  })

  it('closes the panel when clicking outside', async () => {
    const { container } = render(
      <div>
        <PillSelect label="Colour" value="" placeholder="All colours" options={FLAT_OPTIONS} onChange={() => {}} />
        <button type="button" data-testid="outside">Outside</button>
      </div>,
    )
    await user().click(container.querySelector('button[aria-haspopup]')!)
    expect(screen.getByRole('listbox')).toBeInTheDocument()
    await user().click(screen.getByTestId('outside'))
    await waitFor(() => expect(screen.queryByRole('listbox')).not.toBeInTheDocument())
  })
})

// ── Option selection ──────────────────────────────────────────────────────────

describe('PillSelect — option selection', () => {
  it('calls onChange with the option value when an option is clicked', async () => {
    const onChange = vi.fn()
    render(<PillSelect label="Colour" value="" placeholder="All colours" options={FLAT_OPTIONS} onChange={onChange} />)
    await user().click(screen.getByRole('button'))
    await user().click(screen.getByRole('option', { name: 'Teal' }))
    expect(onChange).toHaveBeenCalledWith('teal')
  })

  it('calls onChange with "" when the placeholder option is clicked', async () => {
    const onChange = vi.fn()
    render(<PillSelect label="Colour" value="teal" placeholder="All colours" options={FLAT_OPTIONS} onChange={onChange} />)
    await user().click(screen.getByRole('button'))
    await user().click(screen.getByRole('option', { name: 'All colours' }))
    expect(onChange).toHaveBeenCalledWith('')
  })

  it('closes the panel after selecting an option', async () => {
    render(<PillSelect label="Colour" value="" placeholder="All colours" options={FLAT_OPTIONS} onChange={() => {}} />)
    await user().click(screen.getByRole('button'))
    await user().click(screen.getByRole('option', { name: 'Teal' }))
    await waitFor(() => expect(screen.queryByRole('listbox')).not.toBeInTheDocument())
  })

  it('marks the currently selected option as aria-selected=true', async () => {
    render(<PillSelect label="Colour" value="navy" placeholder="All colours" options={FLAT_OPTIONS} onChange={() => {}} />)
    await user().click(screen.getByRole('button'))
    expect(screen.getByRole('option', { name: 'Navy' })).toHaveAttribute('aria-selected', 'true')
    expect(screen.getByRole('option', { name: 'Teal' })).toHaveAttribute('aria-selected', 'false')
  })
})

// ── Grouped options ───────────────────────────────────────────────────────────

describe('PillSelect — grouped options', () => {
  it('renders options from all groups when open', async () => {
    render(<PillSelect label="Category" value="" placeholder="All categories" groups={GROUPED_OPTIONS} onChange={() => {}} />)
    await user().click(screen.getByRole('button'))
    expect(screen.getByRole('option', { name: 'Hat' })).toBeInTheDocument()
    expect(screen.getByRole('option', { name: 'T-shirt' })).toBeInTheDocument()
  })

  it('renders group separators with group labels', async () => {
    const { container } = render(
      <PillSelect label="Category" value="" placeholder="All categories" groups={GROUPED_OPTIONS} onChange={() => {}} />,
    )
    await user().click(screen.getByRole('button'))
    const seps = container.querySelectorAll('[class*="groupSep"]')
    const texts = Array.from(seps).map(el => el.textContent)
    expect(texts).toContain('Head')
    expect(texts).toContain('Upper body')
  })

  it('calls onChange with correct value for grouped option', async () => {
    const onChange = vi.fn()
    render(<PillSelect label="Category" value="" placeholder="All categories" groups={GROUPED_OPTIONS} onChange={onChange} />)
    await user().click(screen.getByRole('button'))
    await user().click(screen.getByRole('option', { name: 'Jumper' }))
    expect(onChange).toHaveBeenCalledWith('jumper')
  })
})

// ── Keyboard navigation ───────────────────────────────────────────────────────

describe('PillSelect — keyboard navigation', () => {
  it('opens on Enter', async () => {
    render(<PillSelect label="Colour" value="" placeholder="All colours" options={FLAT_OPTIONS} onChange={() => {}} />)
    screen.getByRole('button').focus()
    await user().keyboard('{Enter}')
    expect(screen.getByRole('listbox')).toBeInTheDocument()
  })

  it('opens on Space', async () => {
    render(<PillSelect label="Colour" value="" placeholder="All colours" options={FLAT_OPTIONS} onChange={() => {}} />)
    screen.getByRole('button').focus()
    await user().keyboard(' ')
    expect(screen.getByRole('listbox')).toBeInTheDocument()
  })

  it('closes on Escape', async () => {
    render(<PillSelect label="Colour" value="" placeholder="All colours" options={FLAT_OPTIONS} onChange={() => {}} />)
    await user().click(screen.getByRole('button'))
    await user().keyboard('{Escape}')
    await waitFor(() => expect(screen.queryByRole('listbox')).not.toBeInTheDocument())
  })

  it('moves focused option down with ArrowDown', async () => {
    render(<PillSelect label="Colour" value="" placeholder="All colours" options={FLAT_OPTIONS} onChange={() => {}} data-testid="pill" />)
    screen.getByRole('button').focus()
    await user().keyboard('{Enter}')
    // Index 0 = "All colours"; ArrowDown → index 1 = "Teal"
    await user().keyboard('{ArrowDown}')
    // With roving tabindex, browser focus moves to the option element
    expect(document.activeElement?.textContent?.trim()).toBe('Teal')
  })

  it('selects the focused option with Enter while open', async () => {
    const onChange = vi.fn()
    render(<PillSelect label="Colour" value="" placeholder="All colours" options={FLAT_OPTIONS} onChange={onChange} />)
    screen.getByRole('button').focus()
    await user().keyboard('{Enter}')       // open
    await user().keyboard('{ArrowDown}')   // focus "Teal" (index 1)
    await user().keyboard('{Enter}')       // select
    expect(onChange).toHaveBeenCalledWith('teal')
  })
})

// ── Custom renderOption ───────────────────────────────────────────────────────

describe('PillSelect — renderOption', () => {
  it('uses renderOption to render custom option content', async () => {
    render(
      <PillSelect
        label="Colour"
        value=""
        placeholder="All colours"
        options={FLAT_OPTIONS}
        onChange={() => {}}
        renderOption={opt => <><span data-testid={`swatch-${opt.value}`} /> {opt.label}</>}
      />,
    )
    await user().click(screen.getByRole('button'))
    expect(screen.getByTestId('swatch-teal')).toBeInTheDocument()
  })
})

// ── Accessibility ─────────────────────────────────────────────────────────────

describe('PillSelect — accessibility (NFR-11)', () => {
  it('closed state has no axe violations', async () => {
    const { container } = render(
      <PillSelect label="Colour" value="" placeholder="All colours" options={FLAT_OPTIONS} onChange={() => {}} />,
    )
    await expectNoAxeViolations(container)
  })

  it('open state has no axe violations', async () => {
    const { container } = render(
      <PillSelect label="Colour" value="" placeholder="All colours" options={FLAT_OPTIONS} onChange={() => {}} />,
    )
    await user().click(container.querySelector('button')!)
    await expectNoAxeViolations(container)
  })

  it('open grouped state has no axe violations', async () => {
    const { container } = render(
      <PillSelect label="Category" value="" placeholder="All categories" groups={GROUPED_OPTIONS} onChange={() => {}} />,
    )
    await user().click(container.querySelector('button')!)
    await expectNoAxeViolations(container)
  })
})
