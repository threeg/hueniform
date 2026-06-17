import { useState } from 'react'
import { useParams, useLocation, useNavigate, Link } from 'react-router-dom'
import { useGarment, useRegenerateGarment, useDeleteGarment } from '../api/queries'
import { ApiRequestError } from '../api/types'
import PaletteStrip from '../components/PaletteStrip'
import Swatch from '../components/Swatch'
import ErrorBanner from '../components/ErrorBanner'
import LoadingState from '../components/LoadingState'
import { typeLabel } from '../utils/typeLabel'
import styles from './GarmentDetail.module.css'

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString('en-GB', {
    day: 'numeric', month: 'long', year: 'numeric',
  })
}

export default function GarmentDetail() {
  const { id } = useParams<{ id: string }>()
  const location = useLocation()
  const navigate = useNavigate()

  const from = (location.state as { from?: string } | null)?.from
  const backHref = from ? `/?${from}` : '/'

  const { data: garment, isLoading, isError, error } = useGarment(id!)
  const { mutate: regenerate, isPending: regenPending, error: regenError } = useRegenerateGarment()
  const { mutate: remove,     isPending: deletePending, error: deleteError } = useDeleteGarment()

  const [showConfirm, setShowConfirm] = useState(false)

  function handleRegenerate() {
    regenerate(id!, {
      onSuccess: data => navigate('/add/confirm', { state: { detection: data } }),
    })
  }

  function handleDelete() {
    remove(id!, {
      onSuccess: () => navigate('/'),
    })
  }

  if (isLoading) return <LoadingState label="Loading garment…" />

  if (isError) {
    const err = error as ApiRequestError
    if (err?.code === 'garment_not_found') {
      return (
        <main className={styles.page} data-testid="not-found">
          <p>Garment not found.</p>
          <Link to="/">← Wardrobe</Link>
        </main>
      )
    }
    return (
      <main className={styles.page}>
        <ErrorBanner message={err?.message ?? 'Failed to load garment.'} />
      </main>
    )
  }

  if (!garment) return null

  const actionError = regenError ?? deleteError

  return (
    <main className={styles.page}>
      <Link to={backHref} className={styles.backLink} data-testid="back-link">
        ← Wardrobe
      </Link>

      <div className={styles.layout}>
        {/* Left column — photograph */}
        <div className={styles.imageCol}>
          <img
            src={garment.image_url}
            alt="Garment photograph"
            className={styles.photo}
          />
        </div>

        {/* Right column — detail and actions */}
        <div className={styles.detailCol}>
          <h1 className={styles.typeHeading}>{typeLabel(garment.type)}</h1>

          <PaletteStrip colours={garment.colours} height={16} />

          <ul className={styles.paletteList} aria-label="Colour palette">
            {garment.colours.map((c, i) => (
              <li key={i} className={styles.paletteRow} data-testid="palette-row">
                <Swatch hex={c.hex} family={c.family} proportion={c.proportion} />
              </li>
            ))}
          </ul>

          <div className={styles.dates}>
            <p>Added {formatDate(garment.created_at)}</p>
            {garment.regenerated_at && (
              <p data-testid="regen-date">
                Colours regenerated {formatDate(garment.regenerated_at)}
              </p>
            )}
          </div>

          <div className={styles.actions}>
            {actionError && <ErrorBanner message={(actionError as Error).message} />}

            <p className={styles.actionHint}>
              Wrong colours? Regenerate re-detects them from the photograph.
            </p>

            <button
              className={styles.regenBtn}
              onClick={handleRegenerate}
              disabled={regenPending || deletePending}
              aria-busy={regenPending}
              data-testid="regen-button"
            >
              {regenPending ? 'Detecting…' : 'Regenerate colours'}
            </button>

            <button
              className={styles.deleteBtn}
              onClick={() => setShowConfirm(true)}
              disabled={regenPending || deletePending}
              data-testid="delete-button"
            >
              Delete garment
            </button>
          </div>
        </div>
      </div>

      {/* Delete confirmation dialogue (FR-34) */}
      {showConfirm && (
        <div
          className={styles.backdrop}
          role="dialog"
          aria-modal="true"
          aria-label="Confirm deletion"
          data-testid="delete-dialog"
        >
          <div className={styles.dialog}>
            <p className={styles.dialogQuestion}>
              Delete this {typeLabel(garment.type).toLowerCase()}?
            </p>
            <img
              src={garment.thumbnail_url}
              alt="Garment thumbnail"
              className={styles.dialogThumb}
            />
            <p className={styles.dialogWarning}>
              This removes the photograph and all colour data. This cannot be undone.
            </p>
            <div className={styles.dialogActions}>
              {/* Cancel is first in DOM — receives default focus (FR-34) */}
              <button
                className={styles.cancelBtn}
                onClick={() => setShowConfirm(false)}
                disabled={deletePending}
                data-testid="cancel-delete"
                autoFocus
              >
                Cancel
              </button>
              <button
                className={styles.confirmDeleteBtn}
                onClick={handleDelete}
                disabled={deletePending}
                aria-busy={deletePending}
                data-testid="confirm-delete"
              >
                {deletePending ? 'Deleting…' : 'Delete'}
              </button>
            </div>
          </div>
        </div>
      )}
    </main>
  )
}
