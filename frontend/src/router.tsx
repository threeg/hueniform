import { createBrowserRouter } from 'react-router-dom'
import App from './App'
import Wardrobe from './routes/Wardrobe'
import AddGarment from './routes/AddGarment'
import AddConfirm from './routes/AddConfirm'
import GarmentDetail from './routes/GarmentDetail'
import Suggest from './routes/Suggest'

export const router = createBrowserRouter([
  {
    path: '/',
    element: <App />,
    children: [
      { index: true, element: <Wardrobe /> },
      { path: 'add', element: <AddGarment /> },
      { path: 'add/confirm', element: <AddConfirm /> },
      { path: 'garments/:id', element: <GarmentDetail /> },
      { path: 'suggest', element: <Suggest /> },
    ],
  },
])
