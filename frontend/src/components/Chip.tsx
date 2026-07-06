import type { ButtonHTMLAttributes } from 'react'
import styles from './Chip.module.css'
import { classNames } from '../utils/classNames'

interface Props extends ButtonHTMLAttributes<HTMLButtonElement> {
  selected?: boolean
}

export default function Chip({ selected = false, className, children, ...rest }: Props) {
  return (
    <button
      className={classNames(styles.chip, selected && styles.selected, className)}
      aria-pressed={selected}
      {...rest}
    >
      {children}
    </button>
  )
}
