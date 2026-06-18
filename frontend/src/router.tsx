import { lazy, Suspense } from 'react'
import { createBrowserRouter } from 'react-router-dom'
import App from './App'
import LoadingState from './components/LoadingState'

const Wardrobe = lazy(() => import('./routes/Wardrobe'))
const AddGarment = lazy(() => import('./routes/AddGarment'))
const AddConfirm = lazy(() => import('./routes/AddConfirm'))
const GarmentDetail = lazy(() => import('./routes/GarmentDetail'))
const Suggest = lazy(() => import('./routes/Suggest'))

const fallback = <LoadingState label="Loading…" />

export const router = createBrowserRouter([
  {
    path: '/',
    element: <App />,
    children: [
      { index: true, element: <Suspense fallback={fallback}><Wardrobe /></Suspense> },
      { path: 'add', element: <Suspense fallback={fallback}><AddGarment /></Suspense> },
      { path: 'add/confirm', element: <Suspense fallback={fallback}><AddConfirm /></Suspense> },
      { path: 'garments/:id', element: <Suspense fallback={fallback}><GarmentDetail /></Suspense> },
      { path: 'suggest', element: <Suspense fallback={fallback}><Suggest /></Suspense> },
    ],
  },
])
