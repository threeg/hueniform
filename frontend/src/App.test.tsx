import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import App from './App'

it('renders the sidebar shell', () => {
  render(
    <MemoryRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <App />
    </MemoryRouter>,
  )

  expect(screen.getByText('Hueniform')).toBeInTheDocument()
  expect(screen.getByText('Wardrobe')).toBeInTheDocument()
  expect(screen.getByText('Add garment')).toBeInTheDocument()
  expect(screen.getByText('Suggest outfit')).toBeInTheDocument()
})
