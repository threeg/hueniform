---
id: HUE-094
title: Design tokens and global stylesheet
type: task
status: done
milestone: 20
batch: design-system
layer: frontend
depends_on: [HUE-032]
implements: [NFR-11]
tests_required: true
estimate: 3
---

## In plain English
Sets up the app's palette, type sizes, spacing and corner-rounding as named variables in one place, so the whole interface shares one consistent visual language.

## Background
The redesign is realised as a single global **design-tokens layer** (architecture §2.5). Today's styling uses ad-hoc CSS Modules values; v0.3.0 introduces CSS custom properties for the design-system tokens so every component references intent (`var(--color-primary)`) rather than literals.

## Technical requirements
- Create a global tokens stylesheet defining CSS custom properties at `:root` for the design-system §2–§3 sets: colour (surfaces, ink, borders, accents, semantic), typography (font stacks, the `--text-*` scale, weights, line-heights), spacing (`--space-*`, 4px base), radius, and elevation (warm shadows). Import once at the SPA entry point.
- No CSS framework (architecture §2.5). Native CSS only.
- Values per `docs/06-design-system.md` (normalised scale); colours are the prototype's exact hexes.
- Components consume tokens via `var(--…)`; no raw colour/size literals introduced by this ticket.

## Definition of done (acceptance criteria)
- [ ] Token stylesheet created and imported globally; tokens named per design system §2–§3
- [ ] A **token-contrast unit test** asserts the foreground/background token pairings meet WCAG AA ratios (test strategy §10.3) — the single source of truth for contrast
- [ ] Tests added/updated per test strategy §10.3 and passing in `make test`
- [ ] Ticket status + notes updated in the same commit

## Tests / verification
- `tokens.test.ts` (§10.3): parse the token values and assert AA contrast ratios for the documented ink/paper and text-on-accent pairings. `cd frontend && npm run test -- tokens --run`.

## Notes

- 2026-07-05 — done. Created `src/tokens.css` defining all CSS custom properties from design system §2–§3 (colours, typography, spacing, radius, elevation); imported globally in `main.tsx` before `index.css`. Added `src/test/tokens.test.ts` (15 contrast tests, §10.3): parses the live CSS file via `fs.readFileSync`, asserts WCAG AA ratios for ink/paper pairings (≥ 4.5:1) and accent/large-text pairings (≥ 3:1). All 15 pass. Button-text constraint documented in test: `--color-surface-highest` on `--color-primary` gives ≈ 3.8:1 (passes UI-component boundary, not body-text AA; button labels must be large/bold or use `--color-primary-deep` — enforced in HUE-096). `make test` (1120+203, zero warnings). Sanity test: `cd frontend && npm run test -- tokens --run`.
