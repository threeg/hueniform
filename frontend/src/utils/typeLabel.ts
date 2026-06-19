// FR-16 identifiers → display labels (contract §1.2)
const LABELS: Record<string, string> = {
  t_shirt:     'T-shirt',
  long_sleeve: 'Long sleeve',
  track_top:   'Track top',
}

export const GARMENT_TYPES = [
  // base (upper body, layer 0)
  't_shirt', 'vest', 'long_sleeve',
  // shirt (upper body, layer 1)
  'shirt', 'blouse', 'polo',
  // mid (upper body, layer 2)
  'jumper', 'hoodie', 'cardigan', 'sweatshirt', 'track_top', 'waistcoat',
  // outer (upper body, layer 3)
  'jacket', 'blazer', 'coat',
  // head
  'hat', 'cap', 'beanie',
  'glasses', 'sunglasses', 'earrings',
  // upper body accessories
  'tie', 'scarf', 'necklace', 'watch', 'ring', 'bracelet',
  // lower body
  'trousers', 'jeans', 'chinos', 'shorts', 'skirt', 'dress', 'jumpsuit', 'belt',
  // feet
  'socks', 'shoes', 'boots', 'trainers', 'sandals',
] as const

export function typeLabel(type: string): string {
  return LABELS[type] ?? type.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())
}
