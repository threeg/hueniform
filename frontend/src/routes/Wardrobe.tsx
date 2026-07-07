import { useMemo } from 'react'
import { Link, useSearchParams, useLocation } from 'react-router-dom'
import { useGarments, useTaxonomy } from '../api/queries'
import Banner from '../components/Banner'
import GarmentCard from '../components/GarmentCard'
import PillSelect from '../components/PillSelect'
import type { PillSelectGroup, PillSelectOption } from '../components/PillSelect'
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

// Derived once — REGION_GROUPS is module-level constant so this is stable.
const CATEGORY_GROUPS: PillSelectGroup[] = REGION_GROUPS.map(rg => ({
  groupLabel: rg.label,
  options: rg.categories.map(cat => ({ value: cat, label: typeLabel(cat) })),
}))

const ORDER_OPTIONS = [
  { value: 'hue',  label: 'Hue' },
  { value: 'date', label: 'Date added' },
] as const

const SKELETON_COUNT = 4

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

  // Map family name → hex for swatch rendering in the Colour dropdown panel
  const familyHexes = useMemo(() => {
    const m: Record<string, string> = {}
    taxonomy?.families.forEach(f => {
      m[f.name] = hslToHex(f.canonical.h, f.canonical.s, f.canonical.l)
    })
    return m
  }, [taxonomy])

  const familyOptions = useMemo<PillSelectOption[]>(() =>
    (taxonomy?.families ?? []).map(f => ({ value: f.name, label: f.name })),
  [taxonomy],
  )

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

  // First and last garment IDs for "newest"/"oldest" date labels.
  const firstGarmentId = garments[0]?.id
  const lastGarmentId  = garments[garments.length - 1]?.id

  return (
    <main className={styles.page}>
      <div className={styles.titleRow}>
        <h1 className={styles.title}>Wardrobe</h1>
        <span
          className={classNames(styles.count, isLoading && styles.countLoading)}
          data-testid="result-count"
        >
          {isLoading ? '…' : `${total} ${total === 1 ? 'garment' : 'garments'}`}
        </span>
      </div>

      <div className={styles.filterBar} role="search" aria-label="Filter garments">
        <PillSelect
          label="Category"
          value={typeFilter ?? ''}
          placeholder="All categories"
          groups={CATEGORY_GROUPS}
          onChange={val => setFilter('category', val)}
          data-testid="pill-select-category"
        />

        <PillSelect
          label="Colour"
          value={familyFilter ?? ''}
          placeholder="All colours"
          options={familyOptions}
          onChange={val => setFilter('family', val)}
          renderOption={opt => (
            <>
              {familyHexes[opt.value] && (
                <span
                  className={styles.familySwatch}
                  style={{ backgroundColor: familyHexes[opt.value] }}
                  aria-hidden="true"
                />
              )}
              {opt.label}
            </>
          )}
          data-testid="pill-select-family"
        />

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
      </div>

      {isLoading && (
        <div className={styles.skeletonSection} aria-busy="true" data-testid="loading-skeleton">
          <div className={styles.skeletonBadge} />
          <div className={styles.skeletonGrid} aria-hidden="true">
            {Array.from({ length: SKELETON_COUNT }, (_, i) => (
              <div key={i} className={styles.skeletonCard}>
                <div className={styles.skeletonPhoto} />
                <div className={styles.skeletonMeta}>
                  <div className={styles.skeletonLabel} />
                  <div className={styles.skeletonStrip} />
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {isError && (
        <Banner
          variant="error"
          message={(error as Error).message}
          action={{ label: 'Retry', onClick: () => refetch() }}
        />
      )}

      {!isLoading && !isError && total === 0 && !hasFilters && (
        <div className={styles.emptyCard} data-testid="empty-wardrobe">
          <div className={styles.emptyIcon} aria-hidden="true">◇</div>
          <h2 className={styles.emptyHeading}>Your wardrobe is empty</h2>
          <p className={styles.emptySubtext}>
            Photograph a garment and Hueniform will detect its colours.
          </p>
          <Link to="/add" className={styles.emptyCta}>Add your first garment</Link>
        </div>
      )}

      {!isLoading && !isError && total === 0 && hasFilters && (
        <div className={styles.emptyCard} data-testid="empty-filter">
          <p className={styles.emptyHeadingFilter}>No garments match</p>
          <p className={styles.emptySubtext}>
            <button className={styles.clearLink} onClick={clearFilters} data-testid="clear-filters">
              Clear the filters
            </button>
            {' '}to see everything.
          </p>
        </div>
      )}

      {!isLoading && !isError && groups.length > 0 && groups.map(group => (
        <section key={group.category} className={styles.group}>
          <h2
            className={styles.groupBadge}
            data-testid={`group-header-${group.category}`}
          >
            {typeLabel(group.category)}
            <span className={styles.groupCount}>{group.items.length}</span>
          </h2>
          <ul className={styles.grid} aria-label={`${typeLabel(group.category)} garments`}>
            {group.items.map(g => {
              const dateLabel = orderFilter === 'date'
                ? (g.id === firstGarmentId ? 'newest' : g.id === lastGarmentId ? 'oldest' : undefined)
                : undefined
              return (
                <li key={g.id} className={styles.gridItem}>
                  <Link
                    to={`/garments/${g.id}`}
                    state={{ from: location.search.replace(/^\?/, '') }}
                    className={styles.cardLink}
                    aria-label={`${typeLabel(g.category)} garment detail`}
                  >
                    <GarmentCard garment={g} dateLabel={dateLabel} />
                  </Link>
                </li>
              )
            })}
          </ul>
        </section>
      ))}
    </main>
  )
}
