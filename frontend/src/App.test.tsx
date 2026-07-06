import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import App from './App'

it('renders the app shell with all navigation destinations', () => {
  render(
    <MemoryRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <App />
    </MemoryRouter>,
  )

  // Wordmark appears in both topBar (mobile/tablet) and sidebar (desktop).
  expect(screen.getAllByText('Hueniform').length).toBeGreaterThanOrEqual(1)

  // Each destination label appears in the sidebar nav and the top nav.
  expect(screen.getAllByText('Wardrobe').length).toBeGreaterThanOrEqual(1)
  expect(screen.getAllByText('Add garment').length).toBeGreaterThanOrEqual(1)
  expect(screen.getAllByText('Suggest outfit').length).toBeGreaterThanOrEqual(1)
})
