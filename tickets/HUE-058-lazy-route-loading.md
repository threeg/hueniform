---
id: HUE-058
title: Lazy route loading with React.lazy and Suspense
type: task
status: done
milestone: 8
batch: cleanup
layer: frontend
depends_on: [HUE-032]
implements: []
tests_required: true
estimate: 1
---

## In plain English
Loads each screen only when you actually visit it rather than all at once up front, so the app starts up faster.

## Background

`/verify` of the complete MVP identified that all 5 route components in
`frontend/src/router.tsx` are statically imported, meaning the full bundle
loads on initial page visit regardless of which screen the user navigates to.

## Technical requirements

1. **Convert route imports to `React.lazy()`** in `frontend/src/router.tsx`:
   - `const Wardrobe = React.lazy(() => import('./routes/Wardrobe'))`
   - `const AddGarment = React.lazy(() => import('./routes/AddGarment'))`
   - `const AddConfirm = React.lazy(() => import('./routes/AddConfirm'))`
   - `const GarmentDetail = React.lazy(() => import('./routes/GarmentDetail'))`
   - `const Suggest = React.lazy(() => import('./routes/Suggest'))`

2. **Wrap route elements** in `<Suspense fallback={<LoadingState label="Loading…" />}>`.

3. **Verify** that the App shell (`App.tsx`) and shared components remain in
   the main bundle (not lazy-loaded).

## Definition of done (acceptance criteria)

- [x] All 5 route components loaded via `React.lazy()`
- [x] `Suspense` fallback renders `LoadingState`
- [x] All existing frontend tests still pass
- [x] `make test-frontend` passes with zero warnings
- [x] Ticket status + notes updated in the same commit

## Tests / verification

`cd frontend && npx vitest run`

Note: route tests use `createMemoryRouter` which resolves lazy routes
synchronously in test — no special handling needed.

## Notes

- 2026-06-18 — created by `/verify` complete MVP review.
- 2026-06-18 — implemented: all 5 route imports in `router.tsx` converted to `React.lazy()`; each route element wrapped in `<Suspense fallback={<LoadingState label="Loading…" />}>`; shared `fallback` constant avoids repeating the JSX. App shell and shared components remain in the main bundle. 134 tests passed, zero warnings.
