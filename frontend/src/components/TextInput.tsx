import type { InputHTMLAttributes } from 'react'
import styles from './TextInput.module.css'
import { classNames } from '../utils/classNames'

interface Props extends InputHTMLAttributes<HTMLInputElement> {
  label?: string
}

export default function TextInput({ label, id, className, ...rest }: Props) {
  return (
    <div>
      {label && (
        <label
          htmlFor={id}
          style={{
            display: 'block',
            marginBottom: 'var(--space-1)',
            fontSize: 'var(--text-sm)',
            color: 'var(--color-ink-secondary)',
          }}
        >
          {label}
        </label>
      )}
      <input
        id={id}
        className={classNames(styles.input, className)}
        {...rest}
      />
    </div>
  )
}
