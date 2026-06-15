import { NavLink, Outlet } from 'react-router-dom'
import styles from './App.module.css'

export default function App() {
  return (
    <div className={styles.frame}>
      <aside className={styles.sidebar}>
        <div className={styles.wordmark}>Hueniform</div>
        <nav className={styles.nav}>
          <NavLink
            to="/"
            end
            className={({ isActive }) =>
              isActive ? styles.linkActive : styles.link
            }
          >
            Wardrobe
          </NavLink>
          <NavLink
            to="/add"
            className={({ isActive }) =>
              isActive ? styles.linkActive : styles.link
            }
          >
            Add garment
          </NavLink>
          <NavLink
            to="/suggest"
            className={({ isActive }) =>
              isActive ? styles.linkActive : styles.link
            }
          >
            Suggest outfit
          </NavLink>
        </nav>
      </aside>
      <main className={styles.main}>
        <Outlet />
      </main>
    </div>
  )
}
