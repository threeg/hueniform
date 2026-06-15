import { useParams } from 'react-router-dom'

export default function GarmentDetail() {
  const { id } = useParams()
  return <h1>Garment {id}</h1>
}
