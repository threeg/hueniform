import { apiFetch } from './client'
import type {
  TaxonomyResponse,
  DetectionResponse,
  Garment,
  GarmentCreateRequest,
  GarmentUpdateRequest,
  PatchGarmentRequest,
  InventoryParams,
  InventoryResponse,
  RegenerationProposalResponse,
  SuggestionRequest,
  SuggestionResponse,
} from './types'

// ── §2.1 Health ───────────────────────────────────────────────────────────────

export function getHealth(): Promise<{ status: string; version: string }> {
  return apiFetch('/api/health')
}

// ── §2.2 Taxonomy ─────────────────────────────────────────────────────────────

export function getTaxonomy(): Promise<TaxonomyResponse> {
  return apiFetch('/api/taxonomy')
}

// ── §2.3 Upload and detect ────────────────────────────────────────────────────

export function postDetection(file: File): Promise<DetectionResponse> {
  const body = new FormData()
  body.append('file', file)
  return apiFetch('/api/detections', { method: 'POST', body })
}

// ── §2.4 Staged image preview ─────────────────────────────────────────────────

export function getDetectionImage(token: string): Promise<Blob> {
  return apiFetch(`/api/detections/${token}/image`)
}

// ── §2.5 Confirm and save ─────────────────────────────────────────────────────

export function postGarment(body: GarmentCreateRequest): Promise<Garment> {
  return apiFetch('/api/garments', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
}

// ── §2.6 Inventory list ───────────────────────────────────────────────────────

export function getGarments(params?: InventoryParams): Promise<InventoryResponse> {
  const qs = new URLSearchParams()
  if (params?.category) qs.set('category', params.category)
  if (params?.family)   qs.set('family', params.family)
  if (params?.order)    qs.set('order', params.order)
  if (params?.limit  != null) qs.set('limit',  String(params.limit))
  if (params?.offset != null) qs.set('offset', String(params.offset))
  const suffix = qs.size > 0 ? `?${qs}` : ''
  return apiFetch(`/api/garments${suffix}`)
}

// ── §2.7 Garment detail ───────────────────────────────────────────────────────

export function getGarment(id: string): Promise<Garment> {
  return apiFetch(`/api/garments/${id}`)
}

// ── §2.8 Garment images ───────────────────────────────────────────────────────

export function getGarmentImage(id: string): Promise<Blob> {
  return apiFetch(`/api/garments/${id}/image`)
}

export function getGarmentThumbnail(id: string): Promise<Blob> {
  return apiFetch(`/api/garments/${id}/thumbnail`)
}

// ── §2.9 Regenerate ───────────────────────────────────────────────────────────

export function postGarmentRegenerate(id: string): Promise<RegenerationProposalResponse> {
  return apiFetch(`/api/garments/${id}/regenerate`, { method: 'POST' })
}

// ── §2.10 Confirm regeneration ────────────────────────────────────────────────

export function putGarment(
  id: string,
  body: GarmentUpdateRequest,
): Promise<Garment> {
  return apiFetch(`/api/garments/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
}

// ── §2.10a Direct category edit ──────────────────────────────────────────────

export function patchGarment(
  id: string,
  body: PatchGarmentRequest,
): Promise<Garment> {
  return apiFetch(`/api/garments/${id}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
}

// ── §2.11 Delete ──────────────────────────────────────────────────────────────

export function deleteGarment(id: string): Promise<void> {
  return apiFetch(`/api/garments/${id}`, { method: 'DELETE' })
}

// ── §2.12 Suggest outfit ──────────────────────────────────────────────────────

export function postSuggestions(body?: SuggestionRequest): Promise<SuggestionResponse> {
  return apiFetch('/api/suggestions', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body ?? {}),
  })
}
