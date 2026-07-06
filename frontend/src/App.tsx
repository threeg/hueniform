import { NavLink, Outlet } from 'react-router-dom'
import styles from './App.module.css'

// NavLink className helpers — one per navigation tier.
function sideClass({ isActive }: { isActive: boolean }) {
  return isActive ? `${styles.sideLink} ${styles.sideLinkActive}` : styles.sideLink
}
function topClass({ isActive }: { isActive: boolean }) {
  return isActive ? `${styles.topLink} ${styles.topLinkActive}` : styles.topLink
}
function tabClass({ isActive }: { isActive: boolean }) {
  return isActive ? `${styles.tabLink} ${styles.tabLinkActive}` : styles.tabLink
}

export default function App() {
  return (
    <div className={styles.frame}>
      {/* Top bar — wordmark on mobile, wordmark + nav on tablet; hidden on desktop */}
      <header className={styles.topBar}>
        <span className={styles.topWordmark}>Hueniform</span>
        <nav className={styles.topNav} aria-label="Top navigation">
          <NavLink to="/" end className={topClass}>Wardrobe</NavLink>
          <NavLink to="/add" className={topClass}>Add garment</NavLink>
          <NavLink to="/suggest" className={topClass}>Suggest outfit</NavLink>
        </nav>
      </header>

      {/* Fixed sidebar — desktop only */}
      <aside className={styles.sidebar}>
        <span className={styles.sideWordmark}>Hueniform</span>
        <nav aria-label="Sidebar">
          <NavLink to="/" end className={sideClass}>Wardrobe</NavLink>
          <NavLink to="/add" className={sideClass}>Add garment</NavLink>
          <NavLink to="/suggest" className={sideClass}>Suggest outfit</NavLink>
        </nav>
      </aside>

      <main className={styles.main}>
        <Outlet />
      </main>

      {/* Bottom tab bar — mobile only */}
      <nav className={styles.bottomBar} aria-label="Tab bar">
        <NavLink to="/" end className={tabClass} aria-label="Wardrobe">Wardrobe</NavLink>
        <NavLink to="/add" className={tabClass} aria-label="Add garment">Add</NavLink>
        <NavLink to="/suggest" className={tabClass} aria-label="Suggest outfit">Suggest</NavLink>
      </nav>
    </div>
  )
}
