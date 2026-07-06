import type { ButtonHTMLAttributes } from 'react'
import styles from './Chip.module.css'

interface Props extends ButtonHTMLAttributes<HTMLButtonElement> {
  selected?: boolean
}

export default function Chip({ selected = false, className, children, ...rest }: Props) {
  return (
    <button
      className={[styles.chip, selected ? styles.selected : '', className].filter(Boolean).join(' ')}
      aria-pressed={selected}
      {...rest}
    >
      {children}
    </button>
  )
}
