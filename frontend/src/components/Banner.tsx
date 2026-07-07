import styles from './Banner.module.css'

interface Props {
  message: string
  variant: 'error' | 'warning'
  action?: { label: string; onClick: () => void }
}

export default function Banner({ message, variant, action }: Props) {
  return (
    <div
      className={`${styles.banner} ${styles[variant]}`}
      role={variant === 'error' ? 'alert' : 'status'}
    >
      <span className={styles.icon} aria-hidden="true">!</span>
      <span className={styles.text}>{message}</span>
      {action && (
        <button type="button" className={styles.action} onClick={action.onClick}>
          {action.label}
        </button>
      )}
    </div>
  )
}
