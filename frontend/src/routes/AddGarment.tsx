import { useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useDetect } from '../api/queries'
import Banner from '../components/Banner'
import LoadingState from '../components/LoadingState'
import styles from './AddGarment.module.css'

export default function AddGarment() {
  const navigate = useNavigate()
  const { mutate: detect, isPending, error, reset } = useDetect()
  const inputRef = useRef<HTMLInputElement>(null)
  const [dragOver, setDragOver] = useState(false)
  const [multiNotice, setMultiNotice] = useState(false)

  function submit(file: File) {
    reset()
    detect(file, {
      onSuccess: (data) => {
        navigate('/add/confirm', { state: { detection: data } })
      },
    })
  }

  function handleFiles(files: FileList | null) {
    if (!files || files.length === 0) return
    setMultiNotice(files.length > 1)
    submit(files[0])
  }

  function handleDrop(e: React.DragEvent) {
    e.preventDefault()
    setDragOver(false)
    if (isPending) return
    handleFiles(e.dataTransfer.files)
  }

  function handleDragOver(e: React.DragEvent) {
    e.preventDefault()
    if (!isPending) setDragOver(true)
  }

  function handleDragLeave(e: React.DragEvent) {
    // Only clear when leaving the zone itself, not a child element
    if (!e.currentTarget.contains(e.relatedTarget as Node)) {
      setDragOver(false)
    }
  }

  function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
    handleFiles(e.target.files)
    e.target.value = ''
  }

  const zoneClass = [
    styles.zone,
    dragOver ? styles.dragOver : '',
    isPending ? styles.inert : '',
  ]
    .filter(Boolean)
    .join(' ')

  return (
    <div className={styles.page}>
      <h1 className={styles.title}>Add garment</h1>

      {error && <Banner variant="error" message={error.message} />}

      {multiNotice && (
        <p className={styles.notice} role="status">
          Multiple files dropped — using the first file only.
        </p>
      )}

      <div
        className={zoneClass}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        aria-label="File drop zone"
        aria-busy={isPending}
      >
        {isPending ? (
          <LoadingState label="Detecting colours…" />
        ) : (
          <>
            <p className={styles.headline}>Drag a garment photograph here</p>
            <p className={styles.or}>or</p>
            <button
              type="button"
              className={styles.pickButton}
              onClick={() => inputRef.current?.click()}
            >
              Choose a file…
            </button>
            <p className={styles.hint}>JPEG, PNG or WebP, up to 20 MB</p>
            <p className={styles.tip}>
              Tip: a plain, contrasting background helps the colour detector
              isolate the garment.
            </p>
          </>
        )}
      </div>

      <input
        ref={inputRef}
        type="file"
        accept="image/jpeg,image/png,image/webp"
        className={styles.hiddenInput}
        onChange={handleChange}
        data-testid="file-input"
        tabIndex={-1}
      />
    </div>
  )
}
