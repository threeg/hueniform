import { useState, useMemo } from 'react'
import { useLocation, useNavigate, Navigate } from 'react-router-dom'
import type { DetectionResponse, RegenerationProposalResponse } from '../api/types'
import { useTaxonomy, useCreateGarment, useUpdateGarment } from '../api/queries'
import { typeLabel } from '../utils/typeLabel'
import { hslToHex, normaliseProportions } from '../utils/colour'
import Banner from '../components/Banner'
import Button from '../components/Button'
import Chip from '../components/Chip'
import Swatch from '../components/Swatch'
import styles from './AddConfirm.module.css'


const REGION_LABELS: Record<string, string> = {
  head:       'Head',
  upper_body: 'Upper body',
  lower_body: 'Lower body',
  feet:       'Feet',
}

interface EditableColour {
  h: number
  s: number
  l: number
  hex: string
  family: string
  proportion: number
}

export default function AddConfirm() {
  const location = useLocation()
  const navigate = useNavigate()

  const detection = location.state?.detection as DetectionResponse | undefined
  const garmentId = (detection as RegenerationProposalResponse | undefined)
    ?.garment_id
  const isRegeneration = Boolean(garmentId)

  const [colours, setColours] = useState<EditableColour[]>(() =>
    detection?.colours.map(c => ({
      h: c.h, s: c.s, l: c.l, hex: c.hex, family: c.family,
      proportion: c.proportion,
    })) ?? [],
  )
  const [selectedType, setSelectedType] = useState<string | null>(null)
  const [addOpen, setAddOpen] = useState(false)
  const [newFamily, setNewFamily] = useState('')
  const [newProportion, setNewProportion] = useState(20)

  const { data: taxonomy } = useTaxonomy()

  const {
    mutate: createGarment, isPending: creating, error: createError,
  } = useCreateGarment()
  const {
    mutate: updateGarment, isPending: updating, error: updateError,
  } = useUpdateGarment()

  if (!detection) {
    return <Navigate to="/add" replace />
  }

  const isPending = creating || updating
  const saveError = createError ?? updateError
  const total = colours.reduce((sum, c) => sum + c.proportion, 0)
  const canSave = selectedType !== null && colours.length > 0 && !isPending

  function setProportion(idx: number, value: number) {
    const v = Math.max(1, Math.min(100, value))
    setColours(prev => prev.map((c, i) => i === idx ? { ...c, proportion: v } : c))
  }

  function removeColour(idx: number) {
    setColours(prev => prev.filter((_, i) => i !== idx))
  }

  function handleAddColour() {
    if (!newFamily) return
    const family = taxonomy?.families.find(f => f.name === newFamily)
    if (!family) return
    const { h, s, l } = family.canonical
    setColours(prev => [
      ...prev,
      { h, s, l, hex: hslToHex(h, s, l), family: family.name, proportion: newProportion },
    ])
    setAddOpen(false)
    setNewFamily('')
    setNewProportion(20)
  }

  function handleSave() {
    if (!selectedType) return
    const normProportions = normaliseProportions(colours.map(c => c.proportion))
    const normColours = colours.map((c, i) => ({
      h: c.h, s: c.s, l: c.l, proportion: normProportions[i],
    }))
    const onSuccess = () => navigate('/')

    if (isRegeneration && garmentId) {
      updateGarment({
        id: garmentId,
        body: { regeneration_token: detection!.token, category: selectedType, colours: normColours },
      }, { onSuccess })
    } else {
      createGarment({
        detection_token: detection!.token, category: selectedType, colours: normColours,
      }, { onSuccess })
    }
  }

  return (
    <div className={styles.page}>
      <h1 className={styles.title}>
        {isRegeneration ? 'Confirm regeneration' : 'Confirm garment'}
      </h1>

      <div className={styles.layout}>
        {/* Left: image preview */}
        <div className={styles.preview}>
          <img
            className={styles.previewImage}
            src={detection.image.url}
            alt="Garment photograph"
          />
          <p className={styles.dimensions}>
            {detection.image.width} × {detection.image.height} px
          </p>
        </div>

        {/* Right: palette editor + controls */}
        <div className={styles.editor}>
          {detection.fallback_used && (
            <Banner variant="warning" message="Colour detection fell back to the whole image — background colours may be included." />
          )}

          {saveError && <Banner variant="error" message={saveError.message} />}

          {/* Colour rows (FR-28, FR-29) */}
          <section aria-label="Palette colours">
            <p className={styles.paletteLabel}>Detected palette</p>
            {colours.map((c, idx) => (
              <div key={idx} className={styles.colourRow} data-testid="colour-row">
                <Swatch hex={c.hex} family={c.family} size={28} />
                <div className={styles.stepperPill}>
                  <button
                    type="button"
                    className={styles.stepperBtn}
                    aria-label={`Decrease ${c.family} proportion`}
                    onClick={() => setProportion(idx, c.proportion - 1)}
                    disabled={isPending}
                  >
                    −
                  </button>
                  <span className={styles.stepperValue} aria-hidden="true">
                    {c.proportion}
                  </span>
                  <button
                    type="button"
                    className={styles.stepperBtn}
                    aria-label={`Increase ${c.family} proportion`}
                    onClick={() => setProportion(idx, c.proportion + 1)}
                    disabled={isPending}
                  >
                    +
                  </button>
                </div>
                <span className={styles.percentLabel}>%</span>
                <button
                  type="button"
                  aria-label={`Remove ${c.family}`}
                  className={styles.removeLink}
                  onClick={() => removeColour(idx)}
                  disabled={colours.length <= 1 || isPending}
                >
                  Remove
                </button>
              </div>
            ))}
          </section>

          {/* Proportion preview bar */}
          {total > 0 && (
            <div className={styles.bar} aria-hidden="true">
              {colours.map((c, idx) => (
                <span
                  key={idx}
                  className={styles.barSegment}
                  style={{
                    backgroundColor: c.hex,
                    width: `${(c.proportion / total) * 100}%`,
                  }}
                />
              ))}
            </div>
          )}

          {/* Live total (FR-29) */}
          <p className={styles.totalLine} aria-live="polite" data-testid="total-line">
            Total: <strong>{total}%</strong>
            {total !== 100 && ' — will be normalised to 100% on save'}
          </p>

          {/* Add a colour (FR-29) */}
          {colours.length < 4 && (
            <div className={styles.addSection}>
              {!addOpen ? (
                <button
                  type="button"
                  className={styles.addButton}
                  onClick={() => setAddOpen(true)}
                  disabled={isPending}
                >
                  + Add a colour
                </button>
              ) : (
                <div className={styles.addPanel} data-testid="add-panel">
                  <p className={styles.addPanelHeader}>Add a colour</p>
                  <div className={styles.familyList}>
                    {taxonomy?.families.map(f => {
                      const hex = hslToHex(f.canonical.h, f.canonical.s, f.canonical.l)
                      return (
                        <button
                          key={f.name}
                          type="button"
                          className={[
                            styles.familyRow,
                            newFamily === f.name ? styles.familyRowSelected : '',
                          ].filter(Boolean).join(' ')}
                          onClick={() => setNewFamily(f.name)}
                        >
                          <span
                            className={styles.familyDot}
                            style={{ backgroundColor: hex }}
                            aria-hidden="true"
                          />
                          {f.name}
                        </button>
                      )
                    })}
                  </div>
                  <div className={styles.addPanelFooter}>
                    <label className={styles.addProportionLabel}>
                      Proportion
                      <input
                        type="number"
                        aria-label="New colour proportion"
                        min={1}
                        max={100}
                        value={newProportion}
                        onChange={e => {
                          const v = parseInt(e.target.value, 10)
                          if (!isNaN(v)) setNewProportion(v)
                        }}
                        className={styles.addProportionInput}
                      />
                      <span>%</span>
                    </label>
                    <Button
                      variant="primary"
                      type="button"
                      onClick={handleAddColour}
                      disabled={!newFamily}
                      data-testid="add-confirm"
                    >
                      Add
                    </Button>
                    <Button
                      variant="secondary"
                      type="button"
                      onClick={() => { setAddOpen(false); setNewFamily('') }}
                    >
                      Cancel
                    </Button>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Category picker (FR-31) */}
          <p className={styles.categoryLabel}>Garment category — required</p>
          <section aria-label="Garment category" className={styles.typePicker}>
            <div className={styles.categoryContainer}>
              {taxonomy?.regions?.map(region => (
                <div key={region.region} className={styles.regionGroup}>
                  <h3 className={styles.regionHeading}>
                    {REGION_LABELS[region.region] ?? region.region}
                  </h3>
                  {region.slots.flatMap(slot => slot.categories).map(cat => (
                    <Chip
                      key={cat}
                      selected={selectedType === cat}
                      onClick={() => setSelectedType(cat)}
                      disabled={isPending}
                      className={styles.categoryChip}
                    >
                      {typeLabel(cat)}
                    </Chip>
                  ))}
                </div>
              ))}
            </div>
          </section>

          {/* Save / Cancel (FR-30) */}
          <div className={styles.actions}>
            <Button
              variant="primary"
              onClick={handleSave}
              disabled={!canSave}
              data-testid="save-button"
            >
              {isPending ? 'Saving…' : 'Save garment'}
            </Button>
            <Button
              variant="secondary"
              onClick={() =>
                navigate(isRegeneration && garmentId ? `/garments/${garmentId}` : '/add')
              }
            >
              Cancel
            </Button>
            {!canSave && !isPending && (
              <p className={styles.saveHint}>Save enables once a category is chosen</p>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
