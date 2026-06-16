// FR-16 identifiers → display labels (contract §1.3)
const LABELS: Record<string, string> = {
  top:       'Top',
  bottom:    'Bottom',
  jersey:    'Jersey',
  jacket:    'Jacket',
  socks:     'Socks',
  shoes:     'Shoes',
  hat:       'Hat',
  accessory: 'Accessory',
}

export function typeLabel(type: string): string {
  return LABELS[type] ?? type
}
