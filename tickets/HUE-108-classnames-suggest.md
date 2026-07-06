---
id: HUE-108
title: Use classNames utility in Suggest.tsx
type: task
status: done
milestone: 20
batch: cleanup
layer: frontend
depends_on: [HUE-106]
implements: []
tests_required: true
estimate: 1
---

## In plain English

The Suggest screen still builds CSS class strings by hand in three places instead of using the shared helper that was created for exactly this purpose. This ticket finishes the job.

## Background

HUE-106 created `frontend/src/utils/classNames.ts` and refactored Button, Chip, TextInput and Wardrobe to use it, but missed three instances in `Suggest.tsx` (lines 234, 378, 422) that still inline the `.filter(Boolean).join(' ')` pattern. Identified by `/verify` post-batch review of the screen batch.

## Technical requirements

1. Import `classNames` from `../utils/classNames` in `Suggest.tsx`.
2. Replace the three inline `[…].filter(Boolean).join(' ')` expressions (slot chip, family chip, scheme option) with `classNames(…)` calls.
3. Existing tests must continue to pass with no changes to test files.

## Definition of done (acceptance criteria)

- [x] All `.filter(Boolean).join(' ')` instances removed from `Suggest.tsx`
- [x] `classNames` imported and used instead
- [x] `make test` passes with zero warnings
- [x] Ticket status + notes updated in the same commit

## Tests / verification

No new tests required — the utility is exercised transitively through existing Suggest component tests. `make test` (frontend component gate) confirms no regressions.

## Notes

- 2026-07-06 — created from `/verify` review of screen batch (HUE-098–105)
- 2026-07-06 — done. Imported `classNames` in `Suggest.tsx` and replaced all three inline `.filter(Boolean).join(' ')` expressions (slot chip, family chip, scheme option) with `classNames(…)` calls. No test files changed. `make test-frontend` green: 273 passed (13 suites), zero warnings. Sanity test: `cd frontend && npx vitest run --reporter=verbose src/routes/Suggest.test.tsx 2>&1 | tail -5`.
