import styles from './Banner.module.css'

interface Props {
  message: string
  variant: 'error' | 'warning'
}

export default function Banner({ message, variant }: Props) {
  return (
    <div
      className={`${styles.banner} ${styles[variant]}`}
      role={variant === 'error' ? 'alert' : 'status'}
    >
      {message}
    </div>
  )
}
