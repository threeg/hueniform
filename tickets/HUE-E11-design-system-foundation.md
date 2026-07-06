---
id: HUE-E11
title: Design-system foundation
type: epic
status: done
milestone: 20
layer: frontend
depends_on: []
implements: [NFR-11, NFR-1, NFR-8, NFR-7]
tests_required: false
estimate: 8
---

## In plain English
Builds the shared visual foundation for the new look — colours, fonts, spacing and the common building blocks (buttons, cards, chips) — plus the responsive app frame, so every screen can be restyled consistently.

## Summary
Realises the design system (`docs/06-design-system.md`) in the SPA before any screen is restyled: a global design-tokens layer, self-hosted fonts, the shared component styles, the responsive app shell/navigation, and the frontend accessibility/responsive test tooling. Everything else in v0.3.0 (E12) composes this foundation.

## Scope
- **In scope:** CSS custom-property token layer; self-hosted fonts (offline); shared component styles; app shell + responsive navigation (sidebar → tablet → mobile bottom tab bar); jest-axe + Playwright viewport test tooling.
- **Out of scope:** per-screen restyle (that is E12); any behaviour, data or API change.

## Success criteria
All children `done`; tokens/fonts/components/shell in place; `make test` green with the new a11y token-contrast test; the offline-fonts assertion passes.

## Children
- HUE-094 — Design tokens and global stylesheet
- HUE-095 — Self-hosted fonts (offline)
- HUE-096 — Shared component styles
- HUE-097 — App shell and responsive navigation
- HUE-098 — Frontend accessibility and responsive test tooling

## References
- docs/06-design-system.md (§2–§6); docs/04-wireframes/07-responsive.md; docs/03-architecture.md §2.5; docs/02-requirements.md NFR-7, NFR-11, NFR-1, NFR-8; docs/05-test-strategy.md §10.3

## Notes
- 2026-07-05 — created (Milestone 19 ticket generation)
- 2026-07-05 — done. All five children done: HUE-094 (tokens), HUE-095 (fonts), HUE-096 (shared components), HUE-097 (app shell + responsive nav), HUE-098 (jest-axe + Playwright viewport tooling).
