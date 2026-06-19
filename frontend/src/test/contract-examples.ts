/**
 * Typed constants mirroring every documented response body in
 * docs/03-api-contract.md.  This is the single frontend location to update
 * when the contract changes (test strategy §11.4).
 *
 * Import from this module in MSW handlers and in test assertions so that
 * handler stubs and expected values always agree.
 */

// ── §1.1 ColourOut ────────────────────────────────────────────────────────────

export interface ColourOut {
  h: number
  s: number
  l: number
  family: string
  neutral: boolean
  hex: string
  proportion: number
}

// ── §1.2 GarmentSummary / Garment ─────────────────────────────────────────────

export interface GarmentSummary {
  id: string
  category: string
  colours: ColourOut[]
  thumbnail_url: string
}

export interface Garment extends GarmentSummary {
  image_url: string
  created_at: string
  regenerated_at: string | null
}

// ── §1.3 Error envelope ───────────────────────────────────────────────────────

export interface ApiError {
  error: {
    code: string
    message: string
    details: Record<string, unknown>
  }
}

// ── §2.1 GET /api/health ──────────────────────────────────────────────────────

export const HEALTH_OK = {
  status: 'ok',
  version: '0.1.0',
} as const

// ── §2.2 GET /api/taxonomy ────────────────────────────────────────────────────

export interface TaxonomyFamily {
  name: string
  neutral: boolean
  canonical: { h: number; s: number; l: number }
  representative_hue?: number
  hue_arc?: [number, number]
}

export const TAXONOMY_RESPONSE: { families: TaxonomyFamily[]; regions: unknown[] } = {
  families: [
    // Neutrals — no representative_hue / hue_arc
    { name: 'Black',     neutral: true,  canonical: { h: 0,   s: 0,  l: 6  } },
    { name: 'White',     neutral: true,  canonical: { h: 0,   s: 0,  l: 96 } },
    { name: 'Grey',      neutral: true,  canonical: { h: 0,   s: 0,  l: 50 } },
    { name: 'Navy',      neutral: true,  canonical: { h: 230, s: 40, l: 18 } },
    { name: 'Denim',     neutral: true,  canonical: { h: 215, s: 30, l: 45 } },
    { name: 'Brown',     neutral: true,  canonical: { h: 25,  s: 40, l: 30 } },
    { name: 'Beige/Tan', neutral: true,  canonical: { h: 35,  s: 30, l: 72 } },
    { name: 'Cream',     neutral: true,  canonical: { h: 45,  s: 25, l: 90 } },
    // Chromatics
    { name: 'Red',        neutral: false, representative_hue: 0,   hue_arc: [345, 15],  canonical: { h: 0,   s: 80, l: 50 } },
    { name: 'Orange',     neutral: false, representative_hue: 30,  hue_arc: [15,  45],  canonical: { h: 30,  s: 90, l: 55 } },
    { name: 'Yellow',     neutral: false, representative_hue: 60,  hue_arc: [45,  75],  canonical: { h: 60,  s: 90, l: 50 } },
    { name: 'Chartreuse', neutral: false, representative_hue: 90,  hue_arc: [75,  105], canonical: { h: 90,  s: 70, l: 40 } },
    { name: 'Green',      neutral: false, representative_hue: 120, hue_arc: [105, 135], canonical: { h: 120, s: 60, l: 40 } },
    { name: 'Mint',       neutral: false, representative_hue: 150, hue_arc: [135, 165], canonical: { h: 150, s: 60, l: 45 } },
    { name: 'Teal',       neutral: false, representative_hue: 180, hue_arc: [165, 195], canonical: { h: 180, s: 70, l: 50 } },
    { name: 'Azure',      neutral: false, representative_hue: 210, hue_arc: [195, 225], canonical: { h: 210, s: 70, l: 50 } },
    { name: 'Blue',       neutral: false, representative_hue: 240, hue_arc: [225, 255], canonical: { h: 240, s: 70, l: 50 } },
    { name: 'Violet',     neutral: false, representative_hue: 270, hue_arc: [255, 285], canonical: { h: 270, s: 60, l: 45 } },
    { name: 'Magenta',    neutral: false, representative_hue: 300, hue_arc: [285, 315], canonical: { h: 300, s: 70, l: 45 } },
    { name: 'Pink',       neutral: false, representative_hue: 330, hue_arc: [315, 345], canonical: { h: 330, s: 70, l: 65 } },
  ],
  regions: [
    {
      region: 'head',
      slots: [
        { slot: 'hat',      label: 'Hat',      categories: ['hat', 'cap', 'beanie'],   role: 'statement', default_selected: false },
        { slot: 'glasses',  label: 'Glasses',  categories: ['glasses', 'sunglasses'], role: 'minor',     default_selected: false },
        { slot: 'earrings', label: 'Earrings', categories: ['earrings'],              role: 'minor',     default_selected: false },
      ],
    },
    {
      region: 'upper_body',
      slots: [
        { slot: 'base',  label: 'Base',  categories: ['t_shirt', 'vest', 'long_sleeve'],                              role: 'anchor', default_selected: true,  layer_order: 0 },
        { slot: 'shirt', label: 'Shirt', categories: ['shirt', 'blouse', 'polo'],                                     role: 'anchor', default_selected: false, layer_order: 1 },
        { slot: 'mid',   label: 'Mid',   categories: ['jumper', 'hoodie', 'cardigan', 'sweatshirt', 'track_top', 'waistcoat'], role: 'anchor', default_selected: false, layer_order: 2 },
        { slot: 'outer', label: 'Outer', categories: ['jacket', 'blazer', 'coat'],                                    role: 'anchor', default_selected: false, layer_order: 3 },
        { slot: 'tie',      label: 'Tie',      categories: ['tie'],       role: 'minor', default_selected: false },
        { slot: 'scarf',    label: 'Scarf',    categories: ['scarf'],     role: 'minor', default_selected: false },
        { slot: 'necklace', label: 'Necklace', categories: ['necklace'],  role: 'minor', default_selected: false },
        { slot: 'watch',    label: 'Watch',    categories: ['watch'],     role: 'minor', default_selected: false },
        { slot: 'ring',     label: 'Ring',     categories: ['ring'],      role: 'minor', default_selected: false },
        { slot: 'bracelet', label: 'Bracelet', categories: ['bracelet'],  role: 'minor', default_selected: false },
      ],
    },
    {
      region: 'lower_body',
      slots: [
        { slot: 'lower_body', label: 'Lower body', categories: ['trousers', 'jeans', 'chinos', 'shorts', 'skirt', 'dress', 'jumpsuit'], role: 'anchor', default_selected: true,  mandatory: true, one_piece_categories: ['dress', 'jumpsuit'], one_piece_also_occupies: ['base'] },
        { slot: 'belt',       label: 'Belt',       categories: ['belt'],                                                                role: 'minor',  default_selected: false },
      ],
    },
    {
      region: 'feet',
      slots: [
        { slot: 'socks', label: 'Socks', categories: ['socks'],                             role: 'anchor', default_selected: true },
        { slot: 'shoes', label: 'Shoes', categories: ['shoes', 'boots', 'trainers', 'sandals'], role: 'anchor', default_selected: true },
      ],
    },
  ],
}

// ── §2.3 POST /api/detections — 201 success ───────────────────────────────────

export const DETECTION_RESPONSE = {
  token: '3f9d2c8e-1b4a-4c6d-8e2f-7a9b0c1d2e3f',
  expires_at: '2026-06-12T15:03:00Z',
  fallback_used: false,
  image: {
    url: '/api/detections/3f9d2c8e-1b4a-4c6d-8e2f-7a9b0c1d2e3f/image',
    width: 400,
    height: 500,
  },
  colours: [
    { h: 174, s: 58, l: 41, family: 'Teal',   neutral: false, hex: '#2CADA0', proportion: 80 },
    { h: 28,  s: 85, l: 55, family: 'Orange', neutral: false, hex: '#EE8225', proportion: 20 },
  ] as ColourOut[],
}

export const DETECTION_FALLBACK_RESPONSE = {
  ...DETECTION_RESPONSE,
  token: 'fallback-token-0000-0000-000000000000',
  fallback_used: true,
}

// ── §2.3 errors ───────────────────────────────────────────────────────────────

export const ERR_UNSUPPORTED_FORMAT: ApiError = {
  error: { code: 'unsupported_format', message: 'Only JPEG, PNG and WebP photographs are accepted.', details: {} },
}
export const ERR_UNREADABLE_IMAGE: ApiError = {
  error: { code: 'unreadable_image', message: 'The uploaded file could not be read as an image.', details: {} },
}
export const ERR_FILE_TOO_LARGE: ApiError = {
  error: { code: 'file_too_large', message: 'Uploads must not exceed 20 MB.', details: {} },
}

// ── §2.5 POST /api/garments — 201 success ────────────────────────────────────

export const GARMENT_ID = '0b6c4d1e-7a2f-4f7e-9d2a-1c3e5f7a9b0c'

export const GARMENT_DETAIL: Garment = {
  id: GARMENT_ID,
  category: 'jumper',
  colours: [
    { h: 174, s: 58, l: 41, family: 'Teal',   neutral: false, hex: '#2CADA0', proportion: 80 },
    { h: 28,  s: 85, l: 55, family: 'Orange', neutral: false, hex: '#EE8225', proportion: 20 },
  ],
  thumbnail_url: `/api/garments/${GARMENT_ID}/thumbnail`,
  image_url:     `/api/garments/${GARMENT_ID}/image`,
  created_at:    '2026-06-12T14:03:00Z',
  regenerated_at: null,
}

export const GARMENT_SUMMARY: GarmentSummary = {
  id:            GARMENT_DETAIL.id,
  category:      GARMENT_DETAIL.category,
  colours:       GARMENT_DETAIL.colours,
  thumbnail_url: GARMENT_DETAIL.thumbnail_url,
}

// ── §2.5 / §2.10 errors ──────────────────────────────────────────────────────

export const ERR_DETECTION_NOT_FOUND: ApiError = {
  error: { code: 'detection_not_found', message: 'Detection token not found or has expired.', details: {} },
}
export const ERR_GARMENT_NOT_FOUND: ApiError = {
  error: { code: 'garment_not_found', message: 'Garment not found.', details: {} },
}
export const ERR_INVALID_PALETTE: ApiError = {
  error: { code: 'invalid_palette', message: 'Palette must contain 1–4 colours with proportions summing to exactly 100.', details: {} },
}
export const ERR_INVALID_TYPE: ApiError = {
  error: { code: 'invalid_type', message: 'Unknown garment type.', details: {} },
}
export const ERR_INVALID_REGENERATION_TOKEN: ApiError = {
  error: { code: 'invalid_regeneration_token', message: 'Regeneration token is absent, expired, consumed, or bound to a different garment.', details: {} },
}

// ── §2.6 GET /api/garments ────────────────────────────────────────────────────

export const INVENTORY_RESPONSE = {
  garments: [GARMENT_SUMMARY],
  total: 1,
}

export const ERR_INVALID_FILTER: ApiError = {
  error: { code: 'invalid_filter', message: 'Unknown type or family filter value.', details: {} },
}

// ── §2.12 POST /api/suggestions — 200 combinations found ─────────────────────

export const SUGGESTION_RESPONSE = {
  combinations: [
    {
      rank: 1,
      scheme: 'analogous',
      fallback: false,
      slots: {
        base:       { ...GARMENT_SUMMARY, id: 'base-0000-0000-0000-000000000001',  category: 't_shirt' },
        lower_body: { ...GARMENT_SUMMARY, id: 'lower-0000-0000-0000-000000000002', category: 'trousers' },
        socks:      { ...GARMENT_SUMMARY, id: 'socks-0000-0000-0000-000000000003', category: 'socks' },
        shoes:      { ...GARMENT_SUMMARY, id: 'shoes-0000-0000-0000-000000000004', category: 'shoes' },
      },
      echoes: [{ family: 'Orange', from_slot: 'hat', to_slot: 'socks' }],
      explanation:
        'Analogous scheme: teal t-shirt and azure trousers sit side by side on the wheel; navy shoes and grey socks are neutrals; the orange cap echoes the stripe in the socks.',
    },
  ],
}

// ── §2.12 POST /api/suggestions — 200 no combination possible (FR-43b) ────────

export const SUGGESTION_EMPTY_RESPONSE = {
  combinations: [],
  explanation:
    'No harmonious outfit was found: no mid-layer garment in the wardrobe is compatible with any lower_body under any scheme.',
  hint: 'The mid slot most constrained the search — try the request without it, or add a neutral jumper.',
}

// ── §2.12 errors ──────────────────────────────────────────────────────────────

export const ERR_EMPTY_SLOTS: ApiError = {
  error: {
    code: 'empty_slots',
    message: 'You have no garments for the requested slot(s): hat.',
    details: { empty_slots: ['hat'] },
  },
}
export const ERR_INVALID_REQUEST: ApiError = {
  error: { code: 'invalid_request', message: 'Unknown slot key in request.', details: {} },
}
