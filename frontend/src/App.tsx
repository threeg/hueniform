import { NavLink, Outlet } from 'react-router-dom'
import styles from './App.module.css'
import { classNames } from './utils/classNames'

function createNavClass(base: string, active: string) {
  return ({ isActive }: { isActive: boolean }) => classNames(base, isActive && active)
}

const sideClass = createNavClass(styles.sideLink, styles.sideLinkActive)
const topClass  = createNavClass(styles.topLink,  styles.topLinkActive)
const tabClass  = createNavClass(styles.tabLink,  styles.tabLinkActive)

export default function App() {
  return (
    <div className={styles.frame}>
      {/* Top bar — wordmark on mobile, wordmark + nav on tablet; hidden on desktop */}
      <header className={styles.topBar}>
        <span className={styles.topWordmark}>
          Hueniform
          <span className={styles.wordmarkDot} aria-hidden="true" />
        </span>
        <nav className={styles.topNav} aria-label="Top navigation">
          <NavLink to="/" end className={topClass}>
            <span className={styles.navIconWardrobe} aria-hidden="true" />
            Wardrobe
          </NavLink>
          <NavLink to="/add" className={topClass}>
            <span className={styles.navIconAdd} aria-hidden="true" />
            Add garment
          </NavLink>
          <NavLink to="/suggest" className={topClass}>
            <span className={styles.navIconSuggest} aria-hidden="true" />
            Suggest outfit
          </NavLink>
        </nav>
      </header>

      {/* Fixed sidebar — desktop only */}
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
