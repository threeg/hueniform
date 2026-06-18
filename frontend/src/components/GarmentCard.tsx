import { memo } from 'react'
import type { GarmentSummary } from '../api/types'
import { typeLabel } from '../utils/typeLabel'
import PaletteStrip from './PaletteStrip'
import styles from './GarmentCard.module.css'

interface Props {
  garment: GarmentSummary
  /** Slot caption shown above the card in suggestion results. */
  slot?: string
}

function GarmentCard({ garment, slot }: Props) {
  return (
    <div className={styles.card}>
      {slot && <span className={styles.slot}>{slot}</span>}
      <img
        className={styles.thumbnail}
        src={garment.thumbnail_url}
        alt={`${typeLabel(garment.type)} thumbnail`}
      />
      <div className={styles.meta}>
        <span className={styles.typeLabel}>{typeLabel(garment.type)}</span>
        <PaletteStrip colours={garment.colours} />
      </div>
    </div>
  )
}

export default memo(GarmentCard)
