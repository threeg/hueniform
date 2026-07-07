import { memo } from 'react'
import type { GarmentSummary } from '../api/types'
import { typeLabel } from '../utils/typeLabel'
import PaletteStrip from './PaletteStrip'
import styles from './GarmentCard.module.css'

interface Props {
  garment: GarmentSummary
  /** Slot caption shown above the card in suggestion results. */
  slot?: string
  /** Date-order label ("newest" or "oldest") shown when wardrobe is sorted by date. */
  dateLabel?: string
}

function GarmentCard({ garment, slot, dateLabel }: Props) {
  return (
    <div className={styles.card}>
      {slot && <span className={styles.slot}>{slot}</span>}
      <img
        className={styles.thumbnail}
        src={garment.thumbnail_url}
        alt={`${typeLabel(garment.category)} thumbnail`}
      />
      <div className={styles.meta}>
        <div className={styles.metaRow}>
          <span className={styles.typeLabel}>{typeLabel(garment.category)}</span>
          {dateLabel && <span className={styles.dateLabel}>{dateLabel}</span>}
        </div>
        <PaletteStrip colours={garment.colours} height={8} />
      </div>
    </div>
  )
}

export default memo(GarmentCard)
