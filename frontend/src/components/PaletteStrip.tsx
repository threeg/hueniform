import { memo } from 'react'
import type { ColourOut } from '../api/types'
import styles from './PaletteStrip.module.css'

interface Props {
  colours: ColourOut[]
  height?: number
}

function PaletteStrip({ colours, height = 12 }: Props) {
  return (
    <div
      className={styles.strip}
      style={{ height }}
      aria-label="Colour palette"
    >
      {colours.map((c, i) => (
        <span
          key={i}
          className={styles.segment}
          style={{ backgroundColor: c.hex, width: `${c.proportion}%` }}
          title={`${c.family} ${c.proportion}%`}
          data-testid="palette-segment"
          data-hex={c.hex}
          data-proportion={c.proportion}
        />
      ))}
    </div>
  )
}

export default memo(PaletteStrip)
