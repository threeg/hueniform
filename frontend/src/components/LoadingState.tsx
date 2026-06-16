import styles from './LoadingState.module.css'

interface Props {
  label?: string
}

export default function LoadingState({ label }: Props) {
  return (
    <div className={styles.loading} aria-busy="true">
      {label ? (
        <span className={styles.label}>{label}</span>
      ) : (
        <>
          <div className={styles.skeleton} />
          <div className={styles.skeleton} style={{ width: '75%' }} />
          <div className={styles.skeleton} style={{ width: '50%' }} />
        </>
      )}
    </div>
  )
}
