---
id: HUE-096
title: Shared component styles
type: task
status: done
milestone: 20
batch: design-system
layer: frontend
depends_on: [HUE-094]
implements: [NFR-11]
tests_required: true
estimate: 3
---

## In plain English
Restyles the common building blocks — buttons, cards, chips/tags, colour swatches and form controls — to the new look, so every screen reuses the same polished pieces.

## Background
Design system §5 defines the shared component vocabulary and its states. These are restyled once against the tokens (HUE-094) so screen tickets (E12) compose them rather than re-inventing styling.

## Technical requirements
- Restyle the shared components per design system §5: buttons (primary/secondary/ghost/destructive + focus + disabled), cards, chips/tags (incl. selected), colour swatches (border + selected ring; fill stays data-driven, design system §2.5), form controls (input/select/checkbox/toggle + focus), feedback states (empty/loading skeleton/error).
- All colour/size/ radius via tokens; visible focus ring on every interactive element (NFR-11).
- Assert on roles/text/`data-testid`, not class names.

## Definition of done (acceptance criteria)
- [x] Shared components restyled per design system §5; states covered
- [x] Visible focus indicator on all interactive components; `jest-axe` zero violations on the component set (test strategy §10.3)
- [x] Swatch fill remains data-driven; chrome tokens never applied to swatch fills (design system §2.5)
- [x] Tests added/updated and passing in `make test`
- [x] Ticket status + notes updated in the same commit

## Tests / verification
- Component tests (§10.1, §10.3) with `jest-axe` over the shared components' states; `cd frontend && npm run test -- components --run`.

## Notes

- 2026-07-05 — done. Restyled Banner, GarmentCard, Swatch, LoadingState, PaletteStrip CSS modules to use `var(--...)` tokens exclusively (no hardcoded hex/px values except animation keyframe position offsets). Updated `index.css` base styles (body → `--font-sans`/`--text-base`/`--color-ink`/`--color-ground`; global `focus-visible` clay ring for NFR-11). Created three new shared components: `Button` (primary/secondary/ghost/destructive + disabled; all states token-driven), `Chip` (default/selected/disabled, `aria-pressed`, `--radius-pill`), `TextInput` (surface-highest bg, focus ring, label association via `htmlFor`). Added `src/test/shared-components.test.tsx` (26 tests): role/text/aria-pressed assertions plus `jest-axe` zero-violation checks on every variant and state. `make test` (1120 backend + 239 frontend, zero warnings). Sanity test: `cd frontend && npm run test -- shared-components --run`.

## QA steps

1. Open the app (`make run`, navigate to `http://localhost:8000`).
2. Check the page background is warm cream (`--color-ground` #eae0d0) and body text is warm dark brown, not pure black.
3. Tab through any interactive controls — a visible clay-coloured focus ring should appear on every focusable element.
4. (No Button/Chip UI is visible yet until screen tickets wire them in; the components are available for HUE-097 onwards.)
