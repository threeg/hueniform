---
id: HUE-050
title: Shared frontend test utilities (renderRoute, createTestQueryClient)
type: task
status: todo
milestone: 8
batch: cleanup
layer: tooling
depends_on: [HUE-032, HUE-033, HUE-034, HUE-035, HUE-036, HUE-037]
implements: []
tests_required: true
estimate: 2
---

## Background

`/verify` of the frontend batch identified ~130 lines of duplicated test
boilerplate across five route test files. Every file independently creates an
identical `QueryClient` (retry: false for queries and mutations), a
`createMemoryRouter` with the same future flags, and a local `renderScreen()`
helper function.

## Technical requirements

1. **Create `frontend/src/test/test-utils.ts`** with:
   - `createTestQueryClient()` — factory returning a `QueryClient` with retry
     disabled on both queries and mutations.
   - `renderRoute(routes, initialEntries, opts?)` — creates a memory router with
     the standard future flags, wraps in `QueryClientProvider`, and calls
     `render()`.

2. **Refactor consumers** — replace the local boilerplate in:
   - `UploadDetect.test.tsx`
   - `ConfirmCorrect.test.tsx`
   - `Inventory.test.tsx`
   - `GarmentDetail.test.tsx`
   - `OutfitSuggest.test.tsx`

3. Each file's `renderScreen()` function may still exist as a thin wrapper that
   calls `renderRoute()` with the route-specific arguments — but the QueryClient
   and router creation must come from the shared utility.

## Definition of done (acceptance criteria)

- [ ] `createTestQueryClient` and `renderRoute` exported from `test-utils.ts`
- [ ] All five route test files import and use the shared utilities
- [ ] No duplicate `new QueryClient(...)` or future-flag objects in test files
- [ ] All 132 frontend tests still pass unchanged
- [ ] `make test-frontend` passes with zero warnings
- [ ] Ticket status + notes updated in the same commit

## Tests / verification

No new tests required — pure refactor. Existing tests cover all paths.

`cd frontend && npx vitest run`

## Notes

- 2026-06-17 — created by `/verify` review of frontend batch (HUE-032–037).
