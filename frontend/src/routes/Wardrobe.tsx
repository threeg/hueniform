import { useMemo } from 'react'
import { Link, useSearchParams, useLocation } from 'react-router-dom'
import { useGarments, useTaxonomy } from '../api/queries'
import Banner from '../components/Banner'
import Button from '../components/Button'
import GarmentCard from '../components/GarmentCard'
import LoadingState from '../components/LoadingState'
import { classNames } from '../utils/classNames'
import { hslToHex } from '../utils/colour'
import { typeLabel } from '../utils/typeLabel'
import styles from './Wardrobe.module.css'

// Static region grouping for the category dropdown — mirrors the taxonomy structure.
const REGION_GROUPS = [
  { label: 'Head',       categories: ['hat', 'cap', 'beanie', 'glasses', 'sunglasses', 'earrings'] },
  { label: 'Upper body', categories: ['t_shirt', 'vest', 'long_sleeve', 'shirt', 'blouse', 'polo', 'jumper', 'hoodie', 'cardigan', 'sweatshirt', 'track_top', 'waistcoat', 'jacket', 'blazer', 'coat', 'tie', 'scarf', 'necklace', 'watch', 'ring', 'bracelet'] },
  { label: 'Lower body', categories: ['trousers', 'jeans', 'chinos', 'shorts', 'skirt', 'dress', 'jumpsuit', 'belt'] },
  { label: 'Feet',       categories: ['socks', 'shoes', 'boots', 'trainers', 'sandals'] },
]

const ORDER_OPTIONS = [
  { value: 'hue',  label: 'Hue' },
  { value: 'date', label: 'Date added' },
] as const

export default function Wardrobe() {
  const [searchParams, setSearchParams] = useSearchParams()
  const location = useLocation()

  const typeFilter   = searchParams.get('category') ?? undefined
  const familyFilter = searchParams.get('family')   ?? undefined
  const orderFilter  = searchParams.get('order')    ?? 'hue'
  const hasFilters   = !!(typeFilter || familyFilter)

  const { data, isLoading, isError, error, refetch } = useGarments({
    ...(typeFilter   && { category: typeFilter }),
    ...(familyFilter && { family: familyFilter }),
    order: orderFilter,
    limit: 500,
  })

  const { data: taxonomy } = useTaxonomy()

  function setFilter(key: 'category' | 'family', value: string) {
    setSearchParams(prev => {
      const next = new URLSearchParams(prev)
      if (value) next.set(key, value)
      else next.delete(key)
      return next
    })
  }

  function setOrder(value: string) {
    setSearchParams(prev => {
      const next = new URLSearchParams(prev)
      next.set('order', value)
      return next
    })
  }

  function clearFilters() {
    setSearchParams(prev => {
      const next = new URLSearchParams(prev)
      next.delete('category')
      next.delete('family')
      return next
    })
  }

  const garments = data?.garments ?? []
  const total    = data?.total ?? 0

  const familySwatchHex = useMemo(() => {
    const f = taxonomy?.families.find(fam => fam.name === familyFilter)
    return f ? hslToHex(f.canonical.h, f.canonical.s, f.canonical.l) : null
  }, [taxonomy, familyFilter])

  // Group the flat ordered list by walking it — consecutive same-category items form a group.
  const groups = useMemo(() => {
    const result: Array<{ category: string; items: typeof garments }> = []
    for (const g of garments) {
      const last = result[result.length - 1]
      if (last && last.category === g.category) {
        last.items.push(g)
      } else {
        result.push({ category: g.category, items: [g] })
      }
    }
    return result
  }, [garments])

  return (
    <main className={styles.page}>
      <div className={styles.filterBar} role="search" aria-label="Filter garments">
        <div className={styles.filterGroup}>
          <label htmlFor="type-filter" className={styles.filterLabel}>Type</label>
          <select
            id="type-filter"
            aria-label="Filter by type"
            value={typeFilter ?? ''}
            onChange={e => setFilter('category', e.target.value)}
            className={styles.filterSelect}
          >
            <option value="">All types</option>
            {REGION_GROUPS.map(rg => (
              <optgroup key={rg.label} label={rg.label}>
                {rg.categories.map(cat => (
                  <option key={cat} value={cat}>{typeLabel(cat)}</option>
                ))}
              </optgroup>
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

        <div className={styles.orderToggle} role="group" aria-label="Sort order">
          {ORDER_OPTIONS.map(({ value, label }) => (
            <button
              key={value}
              type="button"
              className={classNames(styles.orderBtn, orderFilter === value && styles.orderBtnActive)}
              aria-pressed={orderFilter === value}
              data-testid={`order-${value}`}
              onClick={() => setOrder(value)}
            >
              {label}
            </button>
          ))}
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
          <Banner variant="error" message={(error as Error).message} />
          <Button variant="secondary" onClick={() => refetch()}>Retry</Button>
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

      {!isLoading && !isError && groups.length > 0 && groups.map(group => (
        <section key={group.category} className={styles.group}>
          <h2
            className={styles.groupHeader}
            data-testid={`group-header-${group.category}`}
          >
            {typeLabel(group.category)} · {group.items.length}
          </h2>
          <ul className={styles.grid} aria-label={`${typeLabel(group.category)} garments`}>
            {group.items.map(g => (
              <li key={g.id} className={styles.gridItem}>
                <Link
                  to={`/garments/${g.id}`}
                  state={{ from: location.search.replace(/^\?/, '') }}
                  className={styles.cardLink}
                  aria-label={`${typeLabel(g.category)} garment detail`}
                >
                  <GarmentCard garment={g} />
                </Link>
              </li>
            ))}
          </ul>
        </section>
      ))}
    </main>
  )
}
