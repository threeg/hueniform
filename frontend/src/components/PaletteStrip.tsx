import { memo } from 'react'
import type { ColourOut } from '../api/types'
import { classNames } from '../utils/classNames'
import styles from './PaletteStrip.module.css'

interface Props {
  colours: ColourOut[]
  height?: number
  className?: string
}

function PaletteStrip({ colours, height = 12, className }: Props) {
  return (
    <div
      className={classNames(styles.strip, className)}
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
