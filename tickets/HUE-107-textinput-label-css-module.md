---
id: HUE-107
title: Move TextInput label styles to CSS Module
type: task
status: todo
milestone: 20
batch: cleanup
layer: frontend
depends_on: [HUE-096]
implements: []
tests_required: true
estimate: 1
---

## In plain English

The text input component styles its label with an inline style object instead of a CSS class, unlike the other new components which all use CSS Modules. This ticket moves those styles into the component's CSS file for consistency.

## Background

`TextInput.tsx` applies four CSS properties to its `<label>` element via an inline `style` object (display, marginBottom, fontSize, color — all referencing design tokens via `var()`). Button and Chip use CSS Modules exclusively. Moving the label styles to `TextInput.module.css` aligns the component with the established pattern and keeps all design decisions in the stylesheet.

Identified by `/verify` post-batch review of the design-system batch.

## Technical requirements

1. Add a `.label` class to `TextInput.module.css` with the four properties currently inline.
2. Replace the inline `style` object on the `<label>` in `TextInput.tsx` with `className={styles.label}`.
3. Existing tests must continue to pass with no changes to test files.

## Definition of done (acceptance criteria)

- [ ] Label styles defined in `TextInput.module.css` as a `.label` class
- [ ] Inline `style` object removed from `TextInput.tsx`
- [ ] `make test` passes with zero warnings
- [ ] Ticket status + notes updated in the same commit

## Tests / verification

No new tests required — existing `shared-components.test.tsx` tests (including jest-axe) cover the labelled TextInput and confirm no regressions. `make test` (frontend component gate) is the verification target.

## Notes

- 2026-07-05 — created from `/verify` review of design-system batch (HUE-094–098)
