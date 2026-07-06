---
id: HUE-101
title: Restyle Inventory (Wardrobe)
type: story
status: done
milestone: 20
batch: screen
layer: frontend
depends_on: [HUE-096, HUE-097, HUE-098, HUE-077]
implements: [NFR-11, NFR-7]
tests_required: true
estimate: 3
---

## In plain English
Applies the new look and the phone/tablet/desktop layouts to the wardrobe/inventory, without changing what it does.

## User story
As the owner
I want the wardrobe/inventory to match the new design and adapt to my screen size
so that it is attractive and usable everywhere.

## Acceptance criteria

**Scenario 1: Restyled to the design system**
- Given the grouped inventory (category groups, hue/date order, filters, all states)
- When the screen renders on desktop
- Then it matches `docs/06-design-system.md` (tokens, components) with unchanged content, states and behaviour

**Scenario 2: Responsive reflow**
- Given the same screen
- When the viewport is mobile (< 640 px) or tablet (640–1023 px)
- Then it reflows per `docs/04-wireframes/07-responsive.md` §4 (stacking, grid columns, sticky primary action on mobile) with all states intact

**Scenario 3: Accessible**
- Given any state of the screen
- Then contrast, visible focus and colour-not-sole-cue hold (NFR-11)

## Technical approach
- Restyle against tokens and shared components (HUE-094/096); apply the responsive rules (HUE-097 shell + media/container queries). No behaviour, data, route or contract change.
- Update component tests to assert on roles/text/`data-testid`, not class names.

## Design references
- Wireframes: docs/04-wireframes/03-inventory.md (all states); docs/04-wireframes/07-responsive.md §4; design system §5–§6

## Tests
- Screen component test (§10.1, §10.3): states render; `jest-axe` zero violations; focus-visible; token variables used
- Responsive + journey coverage in HUE-105

## QA steps
- [ ] View the screen at desktop / tablet / mobile → expect the design-system look and the reflow in 07-responsive §4
- [ ] Tab through interactive elements → expect a visible focus ring
- [ ] Confirm each documented state still appears and behaves as before

## Definition of done
- [x] Acceptance criteria met
- [x] Tests added/updated per test strategy §10.3 and passing in `make test`
- [x] Matcher-touching work: n/a
- [ ] User-flow-touching work: `make test-e2e` responsive journeys — HUE-105
- [x] QA steps recorded and repeated in the chat completion report
- [x] Ticket status + notes updated in the same commit

## Notes

- 2026-07-06 — done. Restyled `Wardrobe.module.css` — all hardcoded hex/px replaced with design-system tokens. Card grid uses `auto-fill minmax(180px, 1fr)` on desktop; `@media (max-width: 639px)` forces 2 columns and makes the filter bar horizontally scrollable (wireframe §4); `@media (640–1023px)` forces 3 columns for tablet. Order toggle active state uses `--color-primary`/`--color-surface-highest` instead of hard-coded dark. `addLink` empty-state CTA restyled with primary button token set. Retry button replaced with shared `Button` (secondary variant). Added 2 axe tests to `Inventory.test.tsx` (loaded grid + empty wardrobe). `make test` (1120 backend + 267 frontend, zero warnings). Sanity test: `cd frontend && npm run test -- Inventory --run`.

## QA steps
- [ ] Open `/` at desktop: warm cream page, category group headers with dividers, card grid fills the width.
- [ ] Resize to tablet (~768 px): grid shows 3 columns.
- [ ] Resize to mobile (~390 px): grid shows 2 columns; filter bar scrolls horizontally without wrapping.
- [ ] Tab through: clay focus ring visible on all controls (selects, order buttons, card links).
- [ ] Select a filter: result count updates; Clear filters appears as an underlined clay link.
- [ ] Empty wardrobe: "Add your first garment" CTA appears as a primary button-style link.
