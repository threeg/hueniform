---
id: HUE-116
title: Nav and secondary-button hover interaction fidelity
type: task
status: done
milestone: 20
batch: cleanup
layer: frontend
depends_on: [HUE-110, HUE-096]
implements: []
tests_required: false
---

## In plain English

The nav item hover and the secondary button hover both differ from the prototype's specified interaction states. This ticket brings them into fidelity.

## Background

Identified during QA of HUE-110 (nav visual fidelity). The prototype specifies hover states that were not included in HUE-110's acceptance criteria.

## Technical requirements

1. **Nav item hover** — prototype: `background: #f3e6d4; color: #3a3128`. Currently `background: var(--color-border-subtle)` (#ecdcc7) with a cooler grey tint. Fix to use `var(--color-ground)` (#eae0d0, closest token to the warm `#f3e6d4` without adding a new token) across `.sideLink:hover`, `.topLink:hover`, and `.tabLink:hover`.

2. **Secondary button hover** — prototype: `background: #f7efe3; border-color: #d8c3a6; color: #3a3128`. Currently missing the `color` change; text stays `--color-ink-secondary` on hover instead of darkening to `--color-ink`. Fix: add `color: var(--color-ink)` to `.secondary:hover:not(:disabled)` in `Button.module.css`.

## Definition of done (acceptance criteria)

- [x] Nav item hover uses a warm token background close to the prototype value
- [x] Secondary button hover darkens text to `var(--color-ink)`
- [x] `make test` passes with zero warnings
- [x] Ticket status + notes updated in the same commit

## Tests / verification

No new tests required — these are cosmetic hover changes. `make test` confirms no regressions. QA via browser: hover over nav items (warm tint visible) and secondary buttons (text darkens).

## Notes

- 2026-07-06 — created from QA of HUE-110; hover states identified against prototype
- 2026-07-06 — done. Three changes: (1) `.topLink:hover` and `.sideLink:hover` background changed from `var(--color-border-subtle)` to `var(--color-ground)` (warmer token, closer to prototype `#f3e6d4`); (2) added missing `.tabLink:hover` rule with same `var(--color-ground)` background; (3) added explicit `color: var(--color-ink)` to `.secondary:hover:not(:disabled)` (base was already `--color-ink` via HUE-096, hover now declares it explicitly). 311 tests pass.
  Sanity test: `cd frontend && npm run test -- --reporter=dot 2>&1 | tail -3`
