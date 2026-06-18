---
id: HUE-052
title: Configure staleTime for taxonomy and garments queries
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

`/verify` of the frontend batch identified that `useTaxonomy()` and
`useGarments()` in `frontend/src/api/queries.ts` both default to
`staleTime: 0`. This causes re-fetches on every window focus or component
remount. Taxonomy is immutable within a session, so a long stale time is
appropriate. Garments change only on explicit user actions, so a moderate stale
time avoids redundant network round-trips while keeping data reasonably fresh.

## Technical requirements

1. **`useTaxonomy()`** — add `staleTime: 5 * 60 * 1000` (5 minutes). Taxonomy
   families and canonical colours do not change at runtime.

2. **`useGarments()`** — add `staleTime: 30_000` (30 seconds). Mutations already
   call `invalidateQueries` on the `['garments']` key, so explicit user actions
   still trigger immediate re-fetches.

## Definition of done (acceptance criteria)

- [ ] `useTaxonomy` has `staleTime: 300_000`
- [ ] `useGarments` has `staleTime: 30_000`
- [ ] All existing frontend tests still pass unchanged
- [ ] `make test-frontend` passes with zero warnings
- [ ] Ticket status + notes updated in the same commit

## Tests / verification

No new tests required — behavioural change is limited to cache timing; existing
tests mock at the MSW level and are unaffected.

`cd frontend && npx vitest run`

## Notes

- 2026-06-17 — created by `/verify` review of frontend batch (HUE-032–037).
