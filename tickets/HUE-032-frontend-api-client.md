---
id: HUE-032
title: Frontend API client, query layer and shared components
type: task
status: done
milestone: 8
batch: frontend
layer: frontend
depends_on: [HUE-003, HUE-005, HUE-006]
implements: [FR-5]
tests_required: true
estimate: 5
---

## Background
Every screen needs a typed API client, TanStack Query hooks and the shared visual components (wireframes §3) before it can be built. Per the contract the frontend is built against the contract and MSW independently of the backend.

## Technical requirements
- A typed client + TanStack Query hooks for every endpoint, derived from the contract (`contract-examples.ts`, HUE-006)
- Error-envelope handling surfacing the plain-language `message` (never the `code`) (contract §1.3)
- Shared components (wireframes §3): Swatch (renders `hex`, FR-5), Palette strip (position order, width ∝ proportion), Garment card, Error banner, Warning banner, Loading state
- Type-label capitalisation helper (the eight FR-16 identifiers); built against MSW handlers (HUE-006)

## Definition of done (acceptance criteria)
- [x] Typed client + query hooks cover every contract endpoint; errors surface the `message` only
- [x] Shared components render swatches from `hex` (FR-5), palette strips in position order, cards, banners, loading states
- [x] Components tested against MSW with the contract example bodies
- [x] Tests added/updated per test strategy §12.2 (or exemption stated below) and passing in `make test`
- [x] Relevant extra gate green where applicable ((none — default gate only))
- [x] Ticket status + notes updated in the same commit

## Tests / verification
Vitest + RTL + MSW (§10.1): swatch renders the `hex`; palette strip orders by position with proportional widths; error banner shows `message` not `code`; query hooks consume the contract-shaped handlers.

## Notes
- 2026-06-15 — created
- 2026-06-16 — done: `api/types.ts` — TypeScript interfaces mirroring every contract shape
  (ColourOut, GarmentSummary, Garment, ApiRequestError class, TaxonomyResponse,
  DetectionResponse, GarmentCreate/UpdateRequest, InventoryParams/Response,
  RegenerationProposalResponse, SuggestionRequest/Combination/Response);
  `api/client.ts` — `apiFetch` base wrapper (error envelope → ApiRequestError, 204 body-less,
  blob for non-JSON content types); `api/endpoints.ts` — one typed function per contract
  endpoint (§2.1–§2.12); `api/queries.ts` — TanStack Query hooks (useQuery for reads:
  useHealth, useTaxonomy, useGarments, useGarment; useMutation for writes: useDetect,
  useCreateGarment, useRegenerateGarment, useUpdateGarment, useDeleteGarment, useSuggest;
  cache invalidation on mutations); `utils/typeLabel.ts` — FR-16 eight-identifier map;
  `components/Swatch` — hex fill + 1 px outline + family + optional proportion;
  `components/PaletteStrip` — proportional width segments in position order;
  `components/GarmentCard` — thumbnail, palette strip, capitalised type label, optional slot caption;
  `components/ErrorBanner` — role=alert, message-only (never code);
  `components/WarningBanner` — amber-tinted status banner;
  `components/LoadingState` — skeleton blocks or labelled inline row; plus CSS Modules for each.
  `test/components.test.tsx` — 35 tests: 8 typeLabel checks, 4 Swatch, 3 PaletteStrip,
  5 GarmentCard, 3 ErrorBanner, 1 WarningBanner, 3 LoadingState, 2 useTaxonomy, 2 useGarments,
  2 useDetect (inc. error-path), 2 useSuggest (inc. include-flag forwarding).
  All 36 tests pass (36 total inc. App.test); 0 warnings.
- Sanity: `cd frontend && npm run test`
