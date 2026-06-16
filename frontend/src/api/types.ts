/**
 * TypeScript interfaces mirroring the API contract (docs/03-api-contract.md).
 * These are the canonical frontend type definitions — screens and hooks import
 * from here, not from test fixtures.
 */

// ── §1.1 Colour objects ───────────────────────────────────────────────────────

export interface ColourOut {
  h: number
  s: number
  l: number
  family: string
  neutral: boolean
  hex: string
  proportion: number
}

export interface ColourIn {
  h: number
  s: number
  l: number
  proportion: number
}

// ── §1.2 Garment objects ──────────────────────────────────────────────────────

export interface GarmentSummary {
  id: string
  type: string
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

/** Thrown by the API client on any non-2xx response. */
export class ApiRequestError extends Error {
  constructor(
    public readonly status: number,
    public readonly code: string,
    message: string,
    public readonly details: Record<string, unknown>,
  ) {
    super(message)
    this.name = 'ApiRequestError'
  }
}

// ── §2.2 Taxonomy ─────────────────────────────────────────────────────────────

export interface TaxonomyFamily {
  name: string
  neutral: boolean
  canonical: { h: number; s: number; l: number }
  representative_hue?: number
  hue_arc?: [number, number]
}

export interface TaxonomyResponse {
  families: TaxonomyFamily[]
}

// ── §2.3 Detection ────────────────────────────────────────────────────────────

export interface DetectionResponse {
  token: string
  expires_at: string
  fallback_used: boolean
  image: { url: string; width: number; height: number }
  colours: ColourOut[]
}

// ── §2.5 / §2.7 / §2.10 Garment operations ───────────────────────────────────

export interface GarmentCreateRequest {
  detection_token: string
  type: string
  colours: ColourIn[]
}

export interface GarmentUpdateRequest {
  regeneration_token: string
  type: string
  colours: ColourIn[]
}

// ── §2.6 Inventory ────────────────────────────────────────────────────────────

export interface InventoryParams {
  type?: string
  family?: string
  limit?: number
  offset?: number
}

export interface InventoryResponse {
  garments: GarmentSummary[]
  total: number
}

// ── §2.9 Regeneration proposal ────────────────────────────────────────────────

export interface RegenerationProposalResponse extends DetectionResponse {
  garment_id: string
}

// ── §2.12 Suggestions ────────────────────────────────────────────────────────

export interface EchoRecord {
  family: string
  from_slot: string
  to_slot: string
}

export interface SuggestionCombination {
  rank: number
  scheme: string | null
  fallback: boolean
  slots: Record<string, GarmentSummary>
  echoes: EchoRecord[]
  explanation: string
}

export interface SuggestionRequest {
  include?: Record<string, boolean>
}

export interface SuggestionResponse {
  combinations: SuggestionCombination[]
  explanation?: string
  hint?: string
}
