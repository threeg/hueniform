import { useState } from 'react'
import { useLocation, useNavigate, Navigate } from 'react-router-dom'
import type { DetectionResponse, RegenerationProposalResponse } from '../api/types'
import { useTaxonomy, useCreateGarment, useUpdateGarment } from '../api/queries'
import { typeLabel } from '../utils/typeLabel'
import { hslToHex, normaliseProportions } from '../utils/colour'
import Swatch from '../components/Swatch'
import WarningBanner from '../components/WarningBanner'
import ErrorBanner from '../components/ErrorBanner'
import styles from './AddConfirm.module.css'

const GARMENT_TYPES = [
  'top', 'bottom', 'jersey', 'jacket',
  'socks', 'shoes', 'hat', 'accessory',
] as const

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

  // All hooks must run before any conditional return
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
        body: { regeneration_token: detection!.token, type: selectedType, colours: normColours },
      }, { onSuccess })
    } else {
      createGarment({
        detection_token: detection!.token, type: selectedType, colours: normColours,
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
            <WarningBanner message="Colour detection fell back to the whole image — background colours may be included." />
          )}

          {saveError && <ErrorBanner message={saveError.message} />}

          {/* Colour rows (FR-28, FR-29) */}
          <section aria-label="Palette colours">
            {colours.map((c, idx) => (
              <div key={idx} className={styles.colourRow} data-testid="colour-row">
                <Swatch hex={c.hex} family={c.family} proportion={c.proportion} size={28} />
                <div className={styles.stepper}>
                  <button
                    type="button"
                    aria-label={`Decrease ${c.family} proportion`}
                    onClick={() => setProportion(idx, c.proportion - 1)}
                    disabled={isPending}
                  >
                    −
                  </button>
                  <input
                    type="number"
                    aria-label={`${c.family} proportion`}
                    min={1}
                    max={100}
                    value={c.proportion}
                    onChange={e => {
                      const v = parseInt(e.target.value, 10)
                      if (!isNaN(v)) setProportion(idx, v)
                    }}
                    disabled={isPending}
                    className={styles.proportionInput}
                  />
                  <button
                    type="button"
                    aria-label={`Increase ${c.family} proportion`}
                    onClick={() => setProportion(idx, c.proportion + 1)}
                    disabled={isPending}
                  >
                    +
                  </button>
                </div>
                <button
                  type="button"
                  aria-label={`Remove ${c.family}`}
                  className={styles.removeButton}
                  onClick={() => removeColour(idx)}
                  disabled={colours.length <= 1 || isPending}
                >
                  Remove
                </button>
              </div>
            ))}
          </section>

          {/* Stacked preview bar */}
          {total > 0 && (
            <div className={styles.bar} aria-label="Proportion preview">
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
            Total: {total}%
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
                  <select
                    aria-label="Colour family"
                    value={newFamily}
                    onChange={e => setNewFamily(e.target.value)}
                  >
                    <option value="">Select a family…</option>
                    {taxonomy?.families.map(f => (
                      <option key={f.name} value={f.name}>{f.name}</option>
                    ))}
                  </select>
                  {newFamily && taxonomy && (() => {
                    const fam = taxonomy.families.find(f => f.name === newFamily)!
                    return (
                      <Swatch
                        hex={hslToHex(fam.canonical.h, fam.canonical.s, fam.canonical.l)}
                        family={fam.name}
                      />
                    )
                  })()}
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
                  />
                  <button
                    type="button"
                    onClick={handleAddColour}
                    disabled={!newFamily}
                    data-testid="add-confirm"
                  >
                    Add
                  </button>
                  <button
                    type="button"
                    onClick={() => { setAddOpen(false); setNewFamily('') }}
                  >
                    Cancel
                  </button>
                </div>
              )}
            </div>
          )}

          {/* Type picker (FR-31) */}
          <section aria-label="Garment type" className={styles.typePicker}>
            {GARMENT_TYPES.map(t => (
              <button
                key={t}
                type="button"
                aria-pressed={selectedType === t}
                className={[
                  styles.typeButton,
                  selectedType === t ? styles.typeSelected : '',
                ]
                  .filter(Boolean)
                  .join(' ')}
                onClick={() => setSelectedType(t)}
                disabled={isPending}
              >
                {typeLabel(t)}
              </button>
            ))}
          </section>

          {/* Save / Cancel (FR-30) */}
          <div className={styles.actions}>
            <button
              type="button"
              className={styles.saveButton}
              onClick={handleSave}
              disabled={!canSave}
              data-testid="save-button"
            >
              {isPending ? 'Saving…' : 'Save garment'}
            </button>
            <button
              type="button"
              className={styles.cancelButton}
              onClick={() =>
                navigate(isRegeneration && garmentId ? `/garments/${garmentId}` : '/add')
              }
            >
              Cancel
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
