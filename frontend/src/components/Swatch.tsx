import styles from './Swatch.module.css'

interface Props {
  hex: string
  family: string
  proportion?: number
  size?: number
}

export default function Swatch({ hex, family, proportion, size = 20 }: Props) {
  return (
    <span className={styles.swatch}>
      <span
        className={styles.square}
        style={{ backgroundColor: hex, width: size, height: size }}
        aria-hidden="true"
        data-testid="swatch-square"
      />
      <span className={styles.label}>
        {family}
        {proportion != null && (
          <span className={styles.proportion}>{proportion}%</span>
        )}
      </span>
    </span>
  )
}
