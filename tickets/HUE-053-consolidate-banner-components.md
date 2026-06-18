---
id: HUE-053
title: Consolidate ErrorBanner and WarningBanner into Banner component
type: task
status: todo
milestone: 8
batch: cleanup
layer: frontend
depends_on: [HUE-032]
implements: []
tests_required: true
estimate: 1
---

## Background

`/verify` of the frontend batch identified that `ErrorBanner.tsx` and
`WarningBanner.tsx` are near-identical components differing only in ARIA role
(`alert` vs `status`). Consolidating into a single component with a `variant`
prop reduces duplication and simplifies maintenance.

## Technical requirements

1. **Create `frontend/src/components/Banner.tsx`** with:
   - Props: `{ message: string; variant: 'error' | 'warning' }`
   - ARIA role: `alert` for error, `status` for warning
   - CSS class: existing shared styles (or variant-specific if styling differs)

2. **Update consumers** — replace all `<ErrorBanner message={…} />` with
   `<Banner variant="error" message={…} />` and all `<WarningBanner message={…} />`
   with `<Banner variant="warning" message={…} />`.

3. **Remove** `ErrorBanner.tsx` and `WarningBanner.tsx`.

4. **Update component tests** in `frontend/src/test/components.test.tsx` to test
   the unified `Banner` component with both variants.

## Definition of done (acceptance criteria)

- [ ] Single `Banner` component handles both error and warning variants
- [ ] `ErrorBanner.tsx` and `WarningBanner.tsx` removed
- [ ] All consumers updated to use `Banner`
- [ ] Component tests updated and passing
- [ ] `make test-frontend` passes with zero warnings
- [ ] Ticket status + notes updated in the same commit

## Tests / verification

`cd frontend && npx vitest run`

## Notes

- 2026-06-17 — created by `/verify` review of frontend batch (HUE-032–037).
