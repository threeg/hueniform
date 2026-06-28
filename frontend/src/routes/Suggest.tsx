import { useState, useMemo } from 'react'
import { Link } from 'react-router-dom'
import { useSuggest, useTaxonomy } from '../api/queries'
import { ApiRequestError, TaxonomySlot } from '../api/types'
import PaletteStrip from '../components/PaletteStrip'
import Banner from '../components/Banner'
import LoadingState from '../components/LoadingState'
import { hslToHex } from '../utils/colour'
import { typeLabel } from '../utils/typeLabel'
import styles from './Suggest.module.css'

// FR-51: slots that are on by default
const DEFAULT_SELECTED = new Set(['base', 'lower_body', 'socks', 'shoes'])
// FR-51.2: slot that can never be deselected
const MANDATORY = 'lower_body'
// FR-50.2: categories that cover the base layer
const ONE_PIECE_CATS = new Set(['dress', 'jumpsuit'])
// Display-label overrides for upper-body layer slots (HANDOFF-05)
const SLOT_DISPLAY_LABELS: Record<string, string> = {
  mid:   'Mid-layer',
  outer: 'Outer layer',
}
const REGION_LABELS: Record<string, string> = {
  head:       'Head',
  upper_body: 'Upper body',
  lower_body: 'Lower body',
  feet:       'Feet',
}

// Fixed wearing order for result slot tiles (wireframe §6)
const SLOT_ORDER = [
  'base', 'shirt', 'mid', 'outer',
  'lower_body', 'belt',
  'socks', 'shoes',
  'hat', 'glasses', 'earrings',
  'tie', 'scarf', 'necklace', 'watch', 'ring', 'bracelet',
]

const SCHEME_LABELS: Record<string, string> = {
  analogous:        'Analogous',
  complementary:    'Complementary',
  triadic:          'Triadic',
  monochromatic:    'Monochromatic',
  'neutral-based':  'Neutral-based',
}

// SlotOverride: boolean = explicit on/off; string[] = category constraint (implies on)
type SlotOverride = boolean | string[]

export default function Suggest() {
  const [slotOverrides, setSlotOverrides] = useState<Record<string, SlotOverride>>({})
  const [expandedSlot, setExpandedSlot] = useState<string | null>(null)

  const { data: taxonomy } = useTaxonomy()
  const { mutate: suggest, isPending, data, error } = useSuggest()

  const err = error as ApiRequestError | null
  const emptySlots: string[] = err?.code === 'empty_slots'
    ? ((err.details?.empty_slots as string[]) ?? [])
    : []

  // FR-50.2: is lower_body constrained exclusively to one-piece categories?
  const lbOverride = slotOverrides['lower_body']
  const isOnePieceOnly = Array.isArray(lbOverride) && lbOverride.length > 0
    && lbOverride.every(c => ONE_PIECE_CATS.has(c))

  function isEffectivelySelected(slotKey: string): boolean {
    if (slotKey === 'base' && isOnePieceOnly) return false
    const ov = slotOverrides[slotKey]
    if (ov === undefined) return DEFAULT_SELECTED.has(slotKey)
    if (typeof ov === 'boolean') return ov
    return true  // string[] = constrained but selected
  }

  function toggleSlot(slotKey: string) {
    if (slotKey === MANDATORY) return
    setSlotOverrides(prev => {
      const next = { ...prev }
      const ov = prev[slotKey]
      const currentlyOn = Array.isArray(ov) ? true : (ov ?? DEFAULT_SELECTED.has(slotKey))
      if (currentlyOn) {
        if (DEFAULT_SELECTED.has(slotKey)) next[slotKey] = false
        else delete next[slotKey]
      } else {
        if (DEFAULT_SELECTED.has(slotKey)) delete next[slotKey]
        else next[slotKey] = true
      }
      return next
    })
    setExpandedSlot(null)
  }

  function isChecked(slotKey: string, cat: string): boolean {
    const ov = slotOverrides[slotKey]
    return !Array.isArray(ov) || ov.includes(cat)
  }

  function toggleCategory(slotKey: string, cat: string, allCats: string[]) {
    setSlotOverrides(prev => {
      const ov = prev[slotKey]
      const current = Array.isArray(ov) ? ov : allCats
      const next = current.includes(cat)
        ? current.filter(c => c !== cat)
        : [...current, cat]
      const updated = { ...prev }
      if (next.length === 0) {
        // Last unticked — revert to "any" (FR-52)
        if (DEFAULT_SELECTED.has(slotKey)) delete updated[slotKey]
        else updated[slotKey] = true
      } else {
        updated[slotKey] = next
      }
      return updated
    })
  }

  function buildSlotsRequest(): Record<string, boolean | { categories: string[] }> {
    const req: Record<string, boolean | { categories: string[] }> = {}
    // FR-50.2: auto-deselect base when lower_body is one-piece only
    if (isOnePieceOnly) req['base'] = false
    for (const [key, ov] of Object.entries(slotOverrides)) {
      if (key === 'base' && isOnePieceOnly) continue  // already handled above
      if (Array.isArray(ov)) {
        req[key] = { categories: ov }
      } else {
        const defaultOn = DEFAULT_SELECTED.has(key)
        if (ov !== defaultOn) req[key] = ov
      }
    }
    return req
  }

  function handleSuggest() {
    const slotsOverride = buildSlotsRequest()
    suggest(Object.keys(slotsOverride).length > 0 ? { slots: slotsOverride } : {})
  }

  const familyHexMap = useMemo(() => {
    const map = new Map<string, string>()
    taxonomy?.families.forEach(f => {
      map.set(f.name, hslToHex(f.canonical.h, f.canonical.s, f.canonical.l))
    })
    return map
  }, [taxonomy])

  function renderSlotChip(slot: TaxonomySlot) {
    const key = slot.slot
    const isLocked = key === MANDATORY
    const isAutoOff = key === 'base' && isOnePieceOnly
    const isOn = isEffectivelySelected(key)
    const isEmpty = emptySlots.includes(key)
    const multiCat = slot.categories.length > 1
    const ov = slotOverrides[key]
    const isExpanded = expandedSlot === key
    const label = SLOT_DISPLAY_LABELS[key] ?? slot.label

    const chipEl = isLocked ? (
      <span
        className={`${styles.slotChip} ${styles.slotChipOn} ${styles.slotChipLocked}`}
        data-testid={`slot-${key}`}
        aria-label={`${label} (required)`}
      >
        🔒 {label}
      </span>
    ) : (
      <button
        type="button"
        className={[
          styles.slotChip,
          isOn ? styles.slotChipOn : '',
          isEmpty && isOn ? styles.slotChipEmpty : '',
        ].filter(Boolean).join(' ')}
        aria-pressed={isOn}
        onClick={() => toggleSlot(key)}
        disabled={isPending || isAutoOff}
        data-testid={`slot-${key}`}
      >
        {label}
        {isEmpty && isOn && (
          <span className={styles.emptyMarker}> — none in wardrobe</span>
        )}
      </button>
    )

    return (
      <div key={key} className={styles.slotWithConstraint}>
        {chipEl}
        {multiCat && isOn && (
          <>
            <button
              type="button"
              className={styles.constraintBtn}
              onClick={() => setExpandedSlot(prev => prev === key ? null : key)}
              aria-expanded={isExpanded}
              data-testid={`constraint-${key}`}
            >
              {Array.isArray(ov)
                ? ov.map(c => typeLabel(c)).join(', ') + ' ▾'
                : 'any ▾'}
            </button>
            {isExpanded && (
              <div
                role="group"
                aria-label={`${label} categories`}
                className={styles.checklist}
              >
                {slot.categories.map(cat => (
                  <label key={cat} className={styles.checklistItem}>
                    <input
                      type="checkbox"
                      checked={isChecked(key, cat)}
                      onChange={() => toggleCategory(key, cat, slot.categories)}
                    />
                    {typeLabel(cat)}
                  </label>
                ))}
              </div>
            )}
          </>
        )}
      </div>
    )
  }

  return (
    <main className={styles.page}>

      {/* ── Request panel (screen 5) ──────────────────────────────────────── */}
      <section className={styles.panel} aria-label="Outfit request">
        <h1 className={styles.heading}>Suggest an outfit</h1>

        {taxonomy?.regions?.map(region => {
          const anchors = region.slots.filter(s => s.role === 'anchor')
          const accessories = region.slots.filter(s => s.role !== 'anchor')
          return (
            <div key={region.region} className={styles.slotGroup}>
              <p className={styles.slotLabel}>
                {REGION_LABELS[region.region] ?? region.region}
              </p>
              <div className={styles.chips}>
                {anchors.map(slot => renderSlotChip(slot))}
              </div>
              {accessories.length > 0 && (
                <>
                  {anchors.length > 0 && (
                    <p className={styles.accessoriesLabel}>Accessories</p>
                  )}
                  <div className={styles.chips}>
                    {accessories.map(slot => renderSlotChip(slot))}
                  </div>
                </>
              )}
            </div>
          )
        })}

        {isOnePieceOnly && (
          <p className={styles.onePieceNote} data-testid="one-piece-note">
            A dress covers the base layer, so Base has been switched off for this request.
          </p>
        )}

        {err && <Banner variant="error" message={err.message} />}

        <div className={styles.panelFooter}>
          <p className={styles.hint}>
            The lower-body slot is always included; everything else is up to you.
          </p>
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
                        const hex = familyHexMap.get(echo.family)
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
