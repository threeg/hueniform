import { render } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { createMemoryRouter, RouterProvider } from 'react-router-dom'
import type { RouteObject, InitialEntry } from 'react-router-dom'

export function createTestQueryClient(): QueryClient {
  return new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  })
}

export function renderRoute(
  routes: RouteObject[],
  initialEntries: InitialEntry[],
) {
  const qc = createTestQueryClient()
  const router = createMemoryRouter(routes, {
    initialEntries,
    future: { v7_startTransition: true, v7_relativeSplatPath: true },
  })
  return render(
    <QueryClientProvider client={qc}>
      <RouterProvider router={router} future={{ v7_startTransition: true }} />
    </QueryClientProvider>,
  )
}
