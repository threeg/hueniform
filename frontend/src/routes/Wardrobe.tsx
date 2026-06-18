import { useMemo } from 'react'
import { Link, useSearchParams, useLocation } from 'react-router-dom'
import { useGarments, useTaxonomy } from '../api/queries'
import GarmentCard from '../components/GarmentCard'
import ErrorBanner from '../components/ErrorBanner'
import LoadingState from '../components/LoadingState'
import { hslToHex } from '../utils/colour'
import { typeLabel, GARMENT_TYPES } from '../utils/typeLabel'
import styles from './Wardrobe.module.css'


export default function Wardrobe() {
  const [searchParams, setSearchParams] = useSearchParams()
  const location = useLocation()

  const typeFilter   = searchParams.get('type')   ?? undefined
  const familyFilter = searchParams.get('family') ?? undefined
  const hasFilters   = !!(typeFilter || familyFilter)

  const { data, isLoading, isError, error, refetch } = useGarments({
    ...(typeFilter   && { type: typeFilter }),
    ...(familyFilter && { family: familyFilter }),
    limit: 500,
  })

  const { data: taxonomy } = useTaxonomy()

  function setFilter(key: 'type' | 'family', value: string) {
    setSearchParams(prev => {
      const next = new URLSearchParams(prev)
      if (value) next.set(key, value)
      else next.delete(key)
      return next
    })
  }

  function clearFilters() {
    setSearchParams({})
  }

  const garments = data?.garments ?? []
  const total    = data?.total ?? 0

  const familySwatchHex = useMemo(() => {
    const f = taxonomy?.families.find(fam => fam.name === familyFilter)
    return f ? hslToHex(f.canonical.h, f.canonical.s, f.canonical.l) : null
  }, [taxonomy, familyFilter])

  return (
    <main className={styles.page}>
      <div className={styles.filterBar} role="search" aria-label="Filter garments">
        <div className={styles.filterGroup}>
          <label htmlFor="type-filter" className={styles.filterLabel}>Type</label>
          <select
            id="type-filter"
            aria-label="Filter by type"
            value={typeFilter ?? ''}
            onChange={e => setFilter('type', e.target.value)}
            className={styles.filterSelect}
          >
            <option value="">All types</option>
            {GARMENT_TYPES.map(t => (
              <option key={t} value={t}>{typeLabel(t)}</option>
            ))}
          </select>
        </div>

        <div className={styles.filterGroup}>
          <label htmlFor="family-filter" className={styles.filterLabel}>Colour</label>
          <div className={styles.familyControl}>
            {familySwatchHex && (
              <span
                className={styles.familySwatch}
                style={{ backgroundColor: familySwatchHex }}
                aria-hidden="true"
              />
            )}
            <select
              id="family-filter"
              aria-label="Filter by colour family"
              value={familyFilter ?? ''}
              onChange={e => setFilter('family', e.target.value)}
              className={styles.filterSelect}
            >
              <option value="">All colours</option>
              {taxonomy?.families.map(f => (
                <option key={f.name} value={f.name}>{f.name}</option>
              ))}
            </select>
          </div>
        </div>

        {hasFilters && (
          <button
            className={styles.clearBtn}
            onClick={clearFilters}
            data-testid="clear-filters"
          >
            Clear filters
          </button>
        )}

        {data && (
          <span className={styles.count} data-testid="result-count">
            {total} {total === 1 ? 'garment' : 'garments'}
          </span>
        )}
      </div>

      {isLoading && <LoadingState label="Loading wardrobe…" />}

      {isError && (
        <div className={styles.errorBlock}>
          <ErrorBanner message={(error as Error).message} />
          <button className={styles.retryBtn} onClick={() => refetch()}>Retry</button>
        </div>
      )}

      {!isLoading && !isError && total === 0 && !hasFilters && (
        <div className={styles.emptyState} data-testid="empty-wardrobe">
          <p>Your wardrobe is empty.</p>
          <Link to="/add" className={styles.addLink}>Add your first garment</Link>
        </div>
      )}

      {!isLoading && !isError && total === 0 && hasFilters && (
        <div className={styles.emptyState} data-testid="empty-filter">
          <p>No garments match these filters.</p>
          <button className={styles.clearBtn} onClick={clearFilters}>Clear filters</button>
        </div>
      )}

      {!isLoading && !isError && garments.length > 0 && (
        <ul className={styles.grid} aria-label="Garment grid">
          {garments.map(g => (
            <li key={g.id} className={styles.gridItem}>
              <Link
                to={`/garments/${g.id}`}
                state={{ from: location.search.replace(/^\?/, '') }}
                className={styles.cardLink}
                aria-label={`${typeLabel(g.type)} garment detail`}
              >
                <GarmentCard garment={g} />
              </Link>
            </li>
          ))}
        </ul>
      )}
    </main>
  )
}
