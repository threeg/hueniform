import type { ButtonHTMLAttributes } from 'react'
import styles from './Button.module.css'
import { classNames } from '../utils/classNames'

export type ButtonVariant = 'primary' | 'secondary' | 'ghost' | 'destructive'

interface Props extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant
}

export default function Button({ variant = 'primary', className, children, ...rest }: Props) {
  return (
    <button
      className={classNames(styles.button, styles[variant], className)}
      {...rest}
    >
      {children}
    </button>
  )
}
