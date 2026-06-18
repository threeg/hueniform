import {
  useQuery,
  useMutation,
  useQueryClient,
} from '@tanstack/react-query'
import type { UseQueryResult, UseMutationResult } from '@tanstack/react-query'
import {
  getHealth,
  getTaxonomy,
  postDetection,
  postGarment,
  getGarments,
  getGarment,
  postGarmentRegenerate,
  putGarment,
  deleteGarment,
  postSuggestions,
} from './endpoints'
import type {
  TaxonomyResponse,
  DetectionResponse,
  Garment,
  GarmentCreateRequest,
  GarmentUpdateRequest,
  InventoryParams,
  InventoryResponse,
  RegenerationProposalResponse,
  SuggestionRequest,
  SuggestionResponse,
} from './types'

// ── §2.2 Taxonomy ─────────────────────────────────────────────────────────────

export function useTaxonomy(): UseQueryResult<TaxonomyResponse> {
  return useQuery({
    queryKey: ['taxonomy'],
    queryFn: getTaxonomy,
    staleTime: 300_000,
  })
}

// ── §2.6 Inventory list ───────────────────────────────────────────────────────

export function useGarments(
  params?: InventoryParams,
): UseQueryResult<InventoryResponse> {
  return useQuery({
    queryKey: ['garments', params],
    queryFn: () => getGarments(params),
    staleTime: 30_000,
  })
}

// ── §2.7 Garment detail ───────────────────────────────────────────────────────

export function useGarment(id: string): UseQueryResult<Garment> {
  return useQuery({
    queryKey: ['garment', id],
    queryFn: () => getGarment(id),
    enabled: Boolean(id),
  })
}

// ── §2.1 Health ───────────────────────────────────────────────────────────────

export function useHealth(): UseQueryResult<{ status: string; version: string }> {
  return useQuery({
    queryKey: ['health'],
    queryFn: getHealth,
    staleTime: 30_000,
  })
}

// ── §2.3 Upload and detect ────────────────────────────────────────────────────

export function useDetect(): UseMutationResult<DetectionResponse, Error, File> {
  return useMutation({
    mutationFn: postDetection,
  })
}

// ── §2.5 Confirm and save ─────────────────────────────────────────────────────

export function useCreateGarment(): UseMutationResult<
  Garment,
  Error,
  GarmentCreateRequest
> {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: postGarment,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['garments'] })
    },
  })
}

// ── §2.9 Regenerate ───────────────────────────────────────────────────────────

export function useRegenerateGarment(): UseMutationResult<
  RegenerationProposalResponse,
  Error,
  string
> {
  return useMutation({
    mutationFn: postGarmentRegenerate,
  })
}

// ── §2.10 Confirm regeneration ────────────────────────────────────────────────

export function useUpdateGarment(): UseMutationResult<
  Garment,
  Error,
  { id: string; body: GarmentUpdateRequest }
> {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ id, body }) => putGarment(id, body),
    onSuccess: (data) => {
      qc.invalidateQueries({ queryKey: ['garments'] })
      qc.setQueryData(['garment', data.id], data)
    },
  })
}

// ── §2.11 Delete ──────────────────────────────────────────────────────────────

export function useDeleteGarment(): UseMutationResult<void, Error, string> {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: deleteGarment,
    onSuccess: (_data, id) => {
      qc.invalidateQueries({ queryKey: ['garments'] })
      qc.removeQueries({ queryKey: ['garment', id] })
    },
  })
}

// ── §2.12 Suggest outfit ──────────────────────────────────────────────────────

export function useSuggest(): UseMutationResult<
  SuggestionResponse,
  Error,
  SuggestionRequest | undefined
> {
  return useMutation({
    mutationFn: (body) => postSuggestions(body),
  })
}
