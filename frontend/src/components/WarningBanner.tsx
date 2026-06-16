import styles from './WarningBanner.module.css'

interface Props {
  message: string
}

export default function WarningBanner({ message }: Props) {
  return (
    <div className={styles.banner} role="status">
      {message}
    </div>
  )
}
