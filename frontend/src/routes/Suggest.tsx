import { useState, useMemo } from 'react'
import { Link } from 'react-router-dom'
import { useSuggest, useTaxonomy, useGarments } from '../api/queries'
import { ApiRequestError, GarmentSummary, TaxonomySlot } from '../api/types'
import Banner from '../components/Banner'
import Button from '../components/Button'
import LoadingState from '../components/LoadingState'
import PaletteStrip from '../components/PaletteStrip'
import { classNames } from '../utils/classNames'
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
  const [count, setCount] = useState(3)
  const [pins, setPins] = useState<Record<string, GarmentSummary>>({})
  const [pickerOpen, setPickerOpen] = useState(false)
  const [anchorFamily, setAnchorFamily] = useState<string | null>(null)
  const [anchorScheme, setAnchorScheme] = useState<string | null>(null)

  const { data: taxonomy } = useTaxonomy()
  const { data: inventory } = useGarments()
  const { mutate: suggest, isPending, data, error } = useSuggest()

  const err = error as ApiRequestError | null
  const emptySlots: string[] = err?.code === 'empty_slots'
    ? ((err.details?.empty_slots as string[]) ?? [])
    : []

  // FR-50.2: is lower_body constrained exclusively to one-piece categories,
  // or is a one-piece garment pinned to lower_body?
  const lbOverride = slotOverrides['lower_body']
  const lbPin = pins['lower_body']
  const isOnePieceOnly =
    (Array.isArray(lbOverride) && lbOverride.length > 0
      && lbOverride.every(c => ONE_PIECE_CATS.has(c)))
    || (lbPin != null && ONE_PIECE_CATS.has(lbPin.category))

  function isEffectivelySelected(slotKey: string): boolean {
    if (slotKey === 'base' && isOnePieceOnly) return false
    if (slotKey in pins) return true  // pinned slot is always selected
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

  function categoryToSlot(category: string): string | null {
    if (!taxonomy?.regions) return null
    for (const region of taxonomy.regions) {
      for (const slot of region.slots) {
        if (slot.categories.includes(category)) return slot.slot
      }
    }
    return null
  }

  function buildRequest(pinsOverride?: Record<string, GarmentSummary>) {
    const allPins = pinsOverride ?? pins
    const slotsOverride = buildSlotsRequest()
    // Pin-based one-piece: if lower_body pin is a one-piece, also exclude base
    const lbPinGarment = allPins['lower_body']
    if (lbPinGarment && ONE_PIECE_CATS.has(lbPinGarment.category)) {
      slotsOverride['base'] = false
    }
    const req: Record<string, unknown> = { count }
    if (Object.keys(slotsOverride).length > 0) req.slots = slotsOverride
    if (Object.keys(allPins).length > 0) {
      req.pins = Object.fromEntries(
        Object.entries(allPins).map(([s, g]) => [s, g.id]),
      )
    }
    if (anchorFamily || anchorScheme) {
      const anchor: { family?: string; scheme?: string } = {}
      if (anchorFamily) anchor.family = anchorFamily
      if (anchorScheme) anchor.scheme = anchorScheme
      req.anchor = anchor
    }
    return req
  }

  function handleSuggest() {
    suggest(buildRequest())
  }

  function handlePinGarment(garment: GarmentSummary) {
    const slot = categoryToSlot(garment.category)
    if (!slot) return
    setPins(prev => ({ ...prev, [slot]: garment }))
    setPickerOpen(false)
  }

  function handleSuggestAround(garment: GarmentSummary) {
    const slot = categoryToSlot(garment.category)
    if (!slot) return
    const newPins = { ...pins, [slot]: garment }
    setPins(newPins)
    setPickerOpen(false)
    suggest(buildRequest(newPins))
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
        role="note"
        className={`${styles.slotChip} ${styles.slotChipOn} ${styles.slotChipLocked}`}
        data-testid={`slot-${key}`}
        aria-label={`${label} (required)`}
      >
        🔒 {label}
      </span>
    ) : (
      <button
        type="button"
        className={classNames(
          styles.slotChip,
          isOn && styles.slotChipOn,
          isEmpty && isOn && styles.slotChipEmpty,
        )}
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

        {/* ── Build around a garment (FR-44) ─────────────────────────────── */}
        <div className={styles.pinSection}>
          <p className={styles.sectionHeading}>Build around a garment</p>
          {Object.keys(pins).length > 0 && (
            <div className={styles.pinChips}>
              {Object.entries(pins).map(([slot, garment]) => (
                <div key={slot} className={styles.pinChip} data-testid={`pin-chip-${slot}`}>
                  <img
                    src={garment.thumbnail_url}
                    alt={typeLabel(garment.category)}
                    className={styles.pinThumb}
                  />
                  <span className={styles.pinLabel}>{typeLabel(garment.category)}</span>
                  <button
                    type="button"
                    aria-label={`Remove ${slot} pin`}
                    data-testid="pin-chip-remove"
                    className={styles.pinRemove}
                    onClick={() => setPins(prev => {
                      const n = { ...prev }
                      delete n[slot]
                      return n
                    })}
                  >×</button>
                </div>
              ))}
            </div>
          )}
          <button
            type="button"
            data-testid="pin-button"
            className={styles.pinButton}
            onClick={() => setPickerOpen(true)}
          >
            Pin a garment
          </button>
        </div>

        {/* ── Build around a colour (FR-45) ──────────────────────────────── */}
        <div className={styles.anchorSection}>
          <p className={styles.sectionHeading}>Build around a colour</p>
          <div className={styles.anchorRow}>
            <span className={styles.anchorLabel}>Colour family</span>
            <div className={styles.familyChips}>
              {taxonomy?.families.map(family => {
                const hex = hslToHex(family.canonical.h, family.canonical.s, family.canonical.l)
                return (
                  <button
                    key={family.name}
                    type="button"
                    className={classNames(
                      styles.familyChip,
                      anchorFamily === family.name && styles.familyChipSelected,
                    )}
                    data-testid={`anchor-family-${family.name}`}
                    aria-pressed={anchorFamily === family.name}
                    onClick={() => setAnchorFamily(prev => prev === family.name ? null : family.name)}
                  >
                    <span
                      className={styles.familySwatch}
                      style={{ backgroundColor: hex }}
                      aria-hidden="true"
                    />
                    {family.name}
                  </button>
                )
              })}
              {anchorFamily && (
                <button
                  type="button"
                  data-testid="anchor-family-clear"
                  className={styles.anchorClearBtn}
                  onClick={() => setAnchorFamily(null)}
                >
                  Clear
                </button>
              )}
            </div>
          </div>
          <div className={styles.anchorRow}>
            <span className={styles.anchorLabel}>Scheme</span>
            <div className={styles.schemeRow}>
              {[
                { key: null,             label: 'Any',            testid: 'anchor-scheme-any' },
                { key: 'neutral-based',  label: 'Neutral-based',  testid: 'anchor-scheme-neutral-based' },
                { key: 'monochromatic',  label: 'Monochromatic',  testid: 'anchor-scheme-monochromatic' },
                { key: 'analogous',      label: 'Analogous',      testid: 'anchor-scheme-analogous' },
                { key: 'complementary',  label: 'Complementary',  testid: 'anchor-scheme-complementary' },
                { key: 'triadic',        label: 'Triadic',        testid: 'anchor-scheme-triadic' },
              ].map(({ key, label, testid }) => (
                <button
                  key={testid}
                  type="button"
                  data-testid={testid}
                  className={classNames(
                    styles.schemeOption,
                    anchorScheme === key && styles.schemeOptionSelected,
                  )}
                  aria-pressed={anchorScheme === key}
                  onClick={() => setAnchorScheme(key)}
                >
                  {label}
                </button>
              ))}
            </div>
          </div>
        </div>

        {err && <Banner variant="error" message={err.message} />}

        <div className={styles.countRow}>
          <span className={styles.countLabel}>How many outfits?</span>
          <span className={styles.countHint}>(1–25)</span>
          <div className={styles.countStepper}>
            <button
              type="button"
              className={styles.stepBtn}
              onClick={() => setCount(c => Math.max(1, c - 1))}
              disabled={count <= 1 || isPending}
              aria-label="Decrease count"
              data-testid="count-decrement"
            >−</button>
            <span className={styles.countDisplay} data-testid="count-display">{count}</span>
            <button
              type="button"
              className={styles.stepBtn}
              onClick={() => setCount(c => Math.min(25, c + 1))}
              disabled={count >= 25 || isPending}
              aria-label="Increase count"
              data-testid="count-increment"
            >+</button>
          </div>
        </div>

        <div className={styles.panelFooter}>
          <p className={styles.hint}>
            The lower-body slot is always included; everything else is up to you.
          </p>
          <Button
            variant="primary"
            onClick={handleSuggest}
            disabled={isPending}
            aria-busy={isPending}
            data-testid="suggest-button"
          >
            {isPending ? 'Searching…' : 'Suggest outfits'}
          </Button>
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

      {/* ── Pin picker modal ─────────────────────────────────────────────── */}
      {pickerOpen && (
        <div
          role="dialog"
          aria-modal="true"
          aria-label="Pick a garment to pin"
          className={styles.pickerOverlay}
          onClick={e => { if (e.target === e.currentTarget) setPickerOpen(false) }}
        >
          <div className={styles.pickerModal} data-testid="picker-modal">
            <div className={styles.pickerHeader}>
              <span className={styles.pickerTitle}>Pin a garment</span>
              <button
                type="button"
                aria-label="Close picker"
                className={styles.pickerClose}
                onClick={() => setPickerOpen(false)}
              >×</button>
            </div>
            <div className={styles.pickerList}>
              {inventory?.garments.map(garment => (
                <div key={garment.id} className={styles.pickerCard} data-testid="picker-garment">
                  <img
                    src={garment.thumbnail_url}
                    alt={typeLabel(garment.category)}
                    className={styles.pickerThumb}
                  />
                  <span className={styles.pickerCategory}>{typeLabel(garment.category)}</span>
                  <PaletteStrip colours={garment.colours} height={6} />
                  <div className={styles.pickerActions}>
                    <button
                      type="button"
                      data-testid="picker-pin-action"
                      className={styles.pickerPinBtn}
                      onClick={() => handlePinGarment(garment)}
                    >
                      Pin to request
                    </button>
                    <button
                      type="button"
                      data-testid="picker-suggest-around"
                      className={styles.pickerSuggestBtn}
                      onClick={() => handleSuggestAround(garment)}
                    >
                      Suggest outfits around this
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {!isPending && data && data.combinations.length > 0 && (
        <section aria-label="Outfit suggestions">
          <p className={styles.resultsHeader} data-testid="results-header">
            {data.requested_count && data.combinations.length < data.requested_count
              ? `Showing ${data.combinations.length} of ${data.requested_count} you asked for`
              : `${data.combinations.length} ${data.combinations.length === 1 ? 'outfit' : 'outfits'}`}
          </p>
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
            <Button
              variant="secondary"
              onClick={handleSuggest}
              disabled={isPending}
              data-testid="suggest-again"
            >
              Suggest again
            </Button>
          </div>
        </section>
      )}
    </main>
  )
}
