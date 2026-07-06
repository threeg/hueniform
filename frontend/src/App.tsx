import { NavLink, Outlet } from 'react-router-dom'
import styles from './App.module.css'
import { classNames } from './utils/classNames'

function createNavClass(base: string, active: string) {
  return ({ isActive }: { isActive: boolean }) => classNames(base, isActive && active)
}

const sideClass     = createNavClass(styles.sideLink,     styles.sideLinkActive)
const tabClass      = createNavClass(styles.tabLink,      styles.tabLinkActive)
const iconRailClass = createNavClass(styles.iconRailLink, styles.iconRailLinkActive)

export default function App() {
  return (
    <div className={styles.frame}>
      {/* Top bar — mobile only: wordmark; hidden at tablet+ */}
      <header className={styles.topBar}>
        <span className={styles.topWordmark}>
          Hueniform
          <span className={styles.wordmarkDot} aria-hidden="true" />
        </span>
      </header>

      {/* Icon rail — tablet only (640–1023 px) */}
      <aside className={styles.iconRail}>
        <span className={styles.iconRailWordmark} aria-hidden="true">
          H<span className={styles.iconRailDot}>.</span>
        </span>
        <nav aria-label="Top navigation">
          <NavLink to="/" end className={iconRailClass}>
            <span className={styles.navIconContainer}>
              <span className={styles.navIconWardrobe} aria-hidden="true" />
            </span>
            Wardrobe
          </NavLink>
          <NavLink to="/add" className={iconRailClass}>
            <span className={styles.navIconContainer}>
              <span className={styles.navIconAdd} aria-hidden="true" />
            </span>
            Add
          </NavLink>
          <NavLink to="/suggest" className={iconRailClass}>
            <span className={styles.navIconContainer}>
              <span className={styles.navIconSuggest} aria-hidden="true" />
            </span>
            Suggest
          </NavLink>
        </nav>
      </aside>

      {/* Fixed sidebar — desktop only (≥ 1024 px) */}
      <aside className={styles.sidebar}>
        <span className={styles.sideWordmark}>
          Hueniform
          <span className={styles.wordmarkDot} aria-hidden="true" />
        </span>
        <nav aria-label="Sidebar">
          <NavLink to="/" end className={sideClass}>
            <span className={styles.navIconWardrobe} aria-hidden="true" />
            Wardrobe
          </NavLink>
          <NavLink to="/add" className={sideClass}>
            <span className={styles.navIconAdd} aria-hidden="true" />
            Add garment
          </NavLink>
          <NavLink to="/suggest" className={sideClass}>
            <span className={styles.navIconSuggest} aria-hidden="true" />
            Suggest outfit
          </NavLink>
        </nav>
      </aside>

      <main className={styles.main}>
        <Outlet />
      </main>

      {/* Bottom tab bar — mobile only */}
      <nav className={styles.bottomBar} aria-label="Tab bar">
        <NavLink to="/" end className={tabClass} aria-label="Wardrobe">
          <span className={styles.navIconWardrobe} aria-hidden="true" />
          Wardrobe
        </NavLink>
        <NavLink to="/add" className={tabClass} aria-label="Add garment">
          <span className={styles.navIconAdd} aria-hidden="true" />
          Add
        </NavLink>
        <NavLink to="/suggest" className={tabClass} aria-label="Suggest outfit">
          <span className={styles.navIconSuggest} aria-hidden="true" />
          Suggest
        </NavLink>
      </nav>
    </div>
  )
}
