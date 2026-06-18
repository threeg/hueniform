---
id: HUE-048
title: Fix SCHEME_LABELS map and add neutral-based test coverage
type: task
status: todo
milestone: 8
batch: cleanup
layer: frontend
depends_on: [HUE-037]
implements: []
tests_required: true
estimate: 1
---

## Background

`/verify` of the frontend batch identified that `SCHEME_LABELS` in `Suggest.tsx`
has two issues: the key `neutral` should be `neutral-based` (the value the backend
actually returns), and the extraneous `split_complementary` key is never returned
by the backend. The `?? combo.scheme` fallback prevents breakage, but neutral-based
fallback combinations display `"neutral-based scheme"` instead of the properly
capitalised `"Neutral-based scheme"`.

## Technical requirements

1. **Fix `SCHEME_LABELS` keys** in `frontend/src/routes/Suggest.tsx:22-29`:
   - Replace `neutral: 'Neutral'` with `'neutral-based': 'Neutral-based'`.
   - Remove `split_complementary: 'Split-complementary'`.

2. **Add test for neutral-based scheme rendering** in
   `frontend/src/routes/OutfitSuggest.test.tsx` — a test case that returns a
   combination with `scheme: 'neutral-based'` and verifies the chip reads
   `"Neutral-based scheme"`.

## Definition of done (acceptance criteria)

- [ ] `SCHEME_LABELS` keys match the backend's actual scheme values exactly
- [ ] Test verifies neutral-based scheme label renders correctly
- [ ] `make test-frontend` passes with zero warnings
- [ ] Ticket status + notes updated in the same commit

## Tests / verification

`cd frontend && npx vitest run src/routes/OutfitSuggest.test.tsx`

## Notes

- 2026-06-17 — created by `/verify` review of frontend batch (HUE-032–037).
