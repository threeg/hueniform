---
id: HUE-106
title: Extract classNames utility and refactor NavLink helpers
type: task
status: todo
milestone: 20
batch: cleanup
layer: frontend
depends_on: [HUE-096, HUE-097]
implements: []
tests_required: true
estimate: 1
---

## In plain English

Several components repeat the same logic for joining CSS class names together. This ticket pulls that logic into a single shared helper and tidies up a similar repetition in the navigation code, so future components can reuse the pattern instead of copying it.

## Background

The v0.3.0 design-system batch introduced three new shared components (Button, Chip, TextInput) that each inline the same `[styles.x, condition && styles.y, className].filter(Boolean).join(' ')` pattern. A fourth instance pre-exists in `Wardrobe.tsx`. Additionally, `App.tsx` defines three near-identical NavLink className helpers (`sideClass`, `topClass`, `tabClass`) that differ only in which CSS Module classes they reference.

Identified by `/verify` post-batch review of the design-system batch.

## Technical requirements

1. Create `frontend/src/utils/classNames.ts` exporting a `classNames(...classes: (string | false | undefined)[]): string` utility.
2. Refactor `Button.tsx`, `Chip.tsx`, `TextInput.tsx` and `Wardrobe.tsx` to use `classNames()` instead of inline `.filter(Boolean).join(' ')`.
3. In `App.tsx`, replace the three one-liner helpers with a single `createNavClass(base, active)` factory function and three derived constants.
4. Existing tests must continue to pass with no changes to test files.

## Definition of done (acceptance criteria)

- [ ] `classNames` utility created and used in all four component files
- [ ] NavLink helpers replaced with factory pattern in `App.tsx`
- [ ] `make test` passes with zero warnings
- [ ] Ticket status + notes updated in the same commit

## Tests / verification

No new tests required — the utility is exercised transitively through existing component and shell tests. `make test` (frontend component gate) confirms no regressions.

## Notes

- 2026-07-05 — created from `/verify` review of design-system batch (HUE-094–098)
