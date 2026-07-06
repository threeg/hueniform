---
id: HUE-096
title: Shared component styles
type: task
status: todo
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
- [ ] Shared components restyled per design system §5; states covered
- [ ] Visible focus indicator on all interactive components; `jest-axe` zero violations on the component set (test strategy §10.3)
- [ ] Swatch fill remains data-driven; chrome tokens never applied to swatch fills (design system §2.5)
- [ ] Tests added/updated and passing in `make test`
- [ ] Ticket status + notes updated in the same commit

## Tests / verification
- Component tests (§10.1, §10.3) with `jest-axe` over the shared components' states; `cd frontend && npm run test -- components --run`.
