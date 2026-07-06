import { useRef, useState, useEffect, useId } from 'react'
import type { ReactNode } from 'react'
import styles from './PillSelect.module.css'
import { classNames } from '../utils/classNames'

export interface PillSelectOption {
  value: string
  label: string
}

export interface PillSelectGroup {
  groupLabel: string
  options: PillSelectOption[]
}

interface Props {
  label: string
  value: string
  placeholder: string
  options?: PillSelectOption[]
  groups?: PillSelectGroup[]
  onChange: (value: string) => void
  renderOption?: (opt: PillSelectOption) => ReactNode
  'data-testid'?: string
}

export default function PillSelect({
  label, value, placeholder, options, groups, onChange, renderOption,
  'data-testid': testId,
}: Props) {
  const [isOpen, setIsOpen]               = useState(false)
  const [focusedIndex, setFocusedIndex]   = useState(0)
  const containerRef = useRef<HTMLDivElement>(null)
  const triggerRef   = useRef<HTMLButtonElement>(null)
  const optionRefs   = useRef<Map<number, HTMLDivElement>>(new Map())
  const uid          = useId()
  const listboxId    = `${uid}-listbox`

  // Flat navigable list: placeholder "All" entry + every real option in order
  const flatOptions: PillSelectOption[] = [
    { value: '', label: placeholder },
    ...(groups ? groups.flatMap(g => g.options) : (options ?? [])),
  ]

  const selectedLabel = flatOptions.find(o => o.value === value)?.label ?? placeholder

  function open() {
    setFocusedIndex(Math.max(0, flatOptions.findIndex(o => o.value === value)))
    setIsOpen(true)
  }

  function close() {
    setIsOpen(false)
    triggerRef.current?.focus()
  }

  function select(val: string) {
    onChange(val)
    close()
  }

  // Move browser focus to the active option whenever focusedIndex changes and the panel is open.
  // This is the roving-tabindex pattern: tabIndex=0 on the active option, -1 on all others.
  useEffect(() => {
    if (isOpen) {
      optionRefs.current.get(focusedIndex)?.focus()
    }
  }, [isOpen, focusedIndex])

  // Close on outside mousedown
  useEffect(() => {
    if (!isOpen) return
    function handleOutside(e: MouseEvent) {
      if (!containerRef.current?.contains(e.target as Node)) {
        setIsOpen(false)
      }
    }
    document.addEventListener('mousedown', handleOutside)
    return () => document.removeEventListener('mousedown', handleOutside)
  }, [isOpen])

  function handleTriggerKeyDown(e: React.KeyboardEvent<HTMLButtonElement>) {
    switch (e.key) {
      case 'Enter':
      case ' ':
        e.preventDefault()
        if (isOpen) close()
        else open()
        break
      case 'Escape':
        if (isOpen) { e.preventDefault(); close() }
        break
      case 'ArrowDown':
        e.preventDefault()
        open()
        break
      case 'Tab':
        if (isOpen) setIsOpen(false)
        break
    }
  }

  function handleOptionKeyDown(e: React.KeyboardEvent<HTMLDivElement>, idx: number) {
    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault()
        setFocusedIndex(Math.min(idx + 1, flatOptions.length - 1))
        break
      case 'ArrowUp':
        e.preventDefault()
        setFocusedIndex(Math.max(idx - 1, 0))
        break
      case 'Enter':
      case ' ':
        e.preventDefault()
        select(flatOptions[idx].value)
        break
      case 'Escape':
        e.preventDefault()
        close()
        break
      case 'Tab':
        close()
        break
    }
  }

  function setOptRef(idx: number) {
    return (el: HTMLDivElement | null) => {
      if (el) optionRefs.current.set(idx, el)
      else optionRefs.current.delete(idx)
    }
  }

  function renderOptionEl(opt: PillSelectOption, idx: number) {
    return (
      <div
        key={opt.value === '' ? '__all__' : opt.value}
        ref={setOptRef(idx)}
        role="option"
        aria-selected={value === opt.value}
        tabIndex={focusedIndex === idx ? 0 : -1}
        className={classNames(
          styles.option,
          value === opt.value && styles.optionSelected,
          focusedIndex === idx && styles.optionFocused,
        )}
        onMouseDown={e => { e.preventDefault(); select(opt.value) }}
        onKeyDown={e => handleOptionKeyDown(e, idx)}
      >
        {opt.value === '' || !renderOption ? opt.label : renderOption(opt)}
      </div>
    )
  }

  return (
    <div ref={containerRef} className={styles.container}>
      <button
        ref={triggerRef}
        type="button"
        className={classNames(styles.trigger, value !== '' && styles.triggerActive)}
        aria-haspopup="listbox"
        aria-expanded={isOpen}
        aria-controls={listboxId}
        aria-label={`${label}: ${selectedLabel}`}
        onClick={() => (isOpen ? close() : open())}
        onKeyDown={handleTriggerKeyDown}
        data-testid={testId}
      >
        <span aria-hidden="true" className={styles.triggerLabel}>{label}</span>
        <span aria-hidden="true" className={styles.triggerValue}>{selectedLabel}</span>
        <span aria-hidden="true" className={styles.caret}>▾</span>
      </button>

      {isOpen && (
        <div
          id={listboxId}
          role="listbox"
          aria-label={label}
          className={styles.panel}
        >
          {/* "All" option at index 0 */}
          {renderOptionEl(flatOptions[0], 0)}

          {/* Grouped options */}
          {groups?.map(group => (
            <div key={group.groupLabel} role="group" aria-label={group.groupLabel}>
              <span className={styles.groupSep} aria-hidden="true">{group.groupLabel}</span>
              {group.options.map(opt => {
                const idx = flatOptions.findIndex(o => o.value === opt.value)
                return renderOptionEl(opt, idx)
              })}
            </div>
          ))}

          {/* Flat options */}
          {!groups && options?.map(opt => {
            const idx = flatOptions.findIndex(o => o.value === opt.value)
            return renderOptionEl(opt, idx)
          })}
        </div>
      )}
    </div>
  )
}
