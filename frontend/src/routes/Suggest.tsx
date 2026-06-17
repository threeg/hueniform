import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useSuggest, useTaxonomy } from '../api/queries'
import { ApiRequestError } from '../api/types'
import PaletteStrip from '../components/PaletteStrip'
import ErrorBanner from '../components/ErrorBanner'
import LoadingState from '../components/LoadingState'
import { hslToHex } from '../utils/colour'
import { typeLabel } from '../utils/typeLabel'
import styles from './Suggest.module.css'

// FR-17: required slots always included, never interactive
const REQUIRED_SLOTS = ['top', 'bottom', 'socks', 'shoes'] as const

// FR-36: optional slots the user may toggle
const OPTIONAL_SLOTS = ['jersey', 'jacket', 'hat', 'accessory'] as const
type OptionalSlot = typeof OPTIONAL_SLOTS[number]

// Fixed wearing order for slot tiles (wireframe §6)
const SLOT_ORDER = ['top', 'jersey', 'jacket', 'bottom', 'socks', 'shoes', 'hat', 'accessory']

const SCHEME_LABELS: Record<string, string> = {
  analogous:            'Analogous',
  complementary:        'Complementary',
  triadic:              'Triadic',
  split_complementary:  'Split-complementary',
  monochromatic:        'Monochromatic',
  neutral:              'Neutral',
}

export default function Suggest() {
  const [selected, setSelected] = useState<Set<OptionalSlot>>(new Set())

  const { data: taxonomy } = useTaxonomy()
  const { mutate: suggest, isPending, data, error } = useSuggest()

  const err = error as ApiRequestError | null
  const emptySlots: string[] = err?.code === 'empty_slots'
    ? ((err.details?.empty_slots as string[]) ?? [])
    : []

  function toggle(slot: OptionalSlot) {
    setSelected(prev => {
      const next = new Set(prev)
      if (next.has(slot)) next.delete(slot)
      else next.add(slot)
      return next
    })
  }

  function handleSuggest() {
    suggest({
      include: Object.fromEntries(OPTIONAL_SLOTS.map(s => [s, selected.has(s)])),
    })
  }

  function familyHex(family: string): string | undefined {
    const f = taxonomy?.families.find(t => t.name === family)
    return f ? hslToHex(f.canonical.h, f.canonical.s, f.canonical.l) : undefined
  }

  return (
    <main className={styles.page}>

      {/* ── Request panel (screen 5) ──────────────────────────────────────── */}
      <section className={styles.panel} aria-label="Outfit request">
        <h1 className={styles.heading}>Suggest an outfit</h1>

        <div className={styles.slotGroup}>
          <p className={styles.slotLabel}>Always included</p>
          <div className={styles.chips} aria-label="Required slots">
            {REQUIRED_SLOTS.map(s => (
              <span
                key={s}
                className={styles.requiredChip}
                data-testid={`required-${s}`}
              >
                🔒 {typeLabel(s)}
              </span>
            ))}
          </div>
        </div>

        <div className={styles.slotGroup}>
          <p className={styles.slotLabel}>Optional slots</p>
          <div className={styles.chips}>
            {OPTIONAL_SLOTS.map(s => {
              const isEmpty = emptySlots.includes(s)
              return (
                <button
                  key={s}
                  className={[
                    styles.optionalChip,
                    selected.has(s) ? styles.chipOn : '',
                    isEmpty ? styles.chipEmpty : '',
                  ].join(' ')}
                  aria-pressed={selected.has(s)}
                  onClick={() => toggle(s)}
                  disabled={isPending}
                  data-testid={`slot-${s}`}
                >
                  {typeLabel(s)}
                  {isEmpty && (
                    <span className={styles.emptyMarker}> — none in wardrobe</span>
                  )}
                </button>
              )
            })}
          </div>
        </div>

        {err && <ErrorBanner message={err.message} />}

        <div className={styles.panelFooter}>
          <p className={styles.hint}>Top, bottom, socks and shoes are always included.</p>
          <button
            className={styles.suggestBtn}
            onClick={handleSuggest}
            disabled={isPending}
            aria-busy={isPending}
            data-testid="suggest-button"
          >
            {isPending ? 'Searching…' : 'Suggest outfits'}
          </button>
        </div>
      </section>

      {/* ── Results area (screen 6) ───────────────────────────────────────── */}
      {isPending && <LoadingState label="Finding harmonious outfits…" />}

      {!isPending && data && data.combinations.length === 0 && (
        <div className={styles.zeroResults} data-testid="zero-results">
          <p className={styles.zeroExplanation} data-testid="zero-explanation">
            {data.explanation}
          </p>
          {data.hint && (
            <p className={styles.zeroHint} data-testid="zero-hint">{data.hint}</p>
          )}
          <Link to="/add" className={styles.addLink}>Add a garment</Link>
        </div>
      )}

      {!isPending && data && data.combinations.length > 0 && (
        <section aria-label="Outfit suggestions">
          <ol className={styles.resultList}>
            {data.combinations.map((combo, i) => {
              const schemeLabel = combo.scheme
                ? `${SCHEME_LABELS[combo.scheme] ?? combo.scheme} scheme`
                : null
              const slotEntries = SLOT_ORDER
                .filter(slot => slot in combo.slots)
                .map(slot => [slot, combo.slots[slot]] as const)

              return (
                <li key={i} className={styles.resultCard} data-testid="result-card">
                  <div className={styles.cardHeader}>
                    <span className={styles.rank}>Suggestion {combo.rank}</span>
                    {schemeLabel && (
                      <span className={styles.schemeChip} data-testid="scheme-chip">
                        {schemeLabel}
                      </span>
                    )}
                    {combo.fallback && (
                      <span className={styles.fallbackChip} data-testid="fallback-label">
                        Neutral-based fallback
                      </span>
                    )}
                  </div>

                  <div className={styles.slotTiles}>
                    {slotEntries.map(([slot, garment]) => (
                      <Link
                        key={slot}
                        to={`/garments/${garment.id}`}
                        className={styles.slotTile}
                        data-testid="slot-tile"
                      >
                        <span className={styles.slotCaption}>{typeLabel(slot)}</span>
                        <img
                          src={garment.thumbnail_url}
                          alt={`${typeLabel(slot)} thumbnail`}
                          className={styles.slotThumb}
                        />
                        <PaletteStrip colours={garment.colours} height={8} />
                      </Link>
                    ))}
                  </div>

                  <p className={styles.explanation} data-testid="explanation">
                    {combo.explanation}
                  </p>

                  {combo.echoes.length > 0 && (
                    <ul className={styles.echoes}>
                      {combo.echoes.map((echo, j) => {
                        const hex = familyHex(echo.family)
                        return (
                          <li key={j} className={styles.echoLine} data-testid="echo-line">
                            {hex && (
                              <span
                                className={styles.echoSwatch}
                                style={{ backgroundColor: hex }}
                                aria-hidden="true"
                              />
                            )}
                            Echo: {echo.family} — {echo.from_slot} ↔ {echo.to_slot}
                          </li>
                        )
                      })}
                    </ul>
                  )}
                </li>
              )
            })}
          </ol>

          <div className={styles.suggestAgain}>
            <button
              className={styles.suggestAgainBtn}
              onClick={handleSuggest}
              disabled={isPending}
              data-testid="suggest-again"
            >
              Suggest again
            </button>
          </div>
        </section>
      )}
    </main>
  )
}
