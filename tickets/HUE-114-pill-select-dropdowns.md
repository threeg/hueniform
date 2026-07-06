---
id: HUE-114
title: Custom pill-select filter dropdowns
type: story
status: done
milestone: 20
batch: cleanup
layer: frontend
depends_on: [HUE-101]
implements: []
tests_required: true
estimate: 5
---

## In plain English
The wardrobe's Category and Colour filters are currently native `<select>` elements. The prototype shows custom pill-shaped dropdown buttons with a popover panel — styled inline labels, a caret, and (for the colour filter) swatch chips next to each option. This ticket creates a reusable pill-select component and replaces both native selects.

## User story
As the owner
I want the wardrobe filters to be styled pill dropdowns matching the design
so that the filter bar looks cohesive with the rest of the warm-paper aesthetic.

## Acceptance criteria

**Scenario 1: Pill button appearance**
- Given the wardrobe filter bar
- When the Category and Colour dropdowns render (closed)
- Then each is a pill-shaped button (`border-radius: 999px; background: #fff; border: 1px solid #ecdcc7; padding: 10px 16px`) showing: a muted label (e.g. "Category"), the current value in bold (e.g. "All categories"), and a caret (`▾`)

**Scenario 2: Dropdown panel**
- Given a pill button
- When I click it
- Then a dropdown panel appears with the available options; clicking an option selects it and closes the panel; clicking outside closes the panel

**Scenario 3: Colour swatch in family dropdown**
- Given the Colour dropdown panel
- When family options render
- Then each option shows its canonical swatch beside the family name

**Scenario 4: Keyboard accessible**
- Given a pill button
- When I use keyboard navigation (Enter/Space to open, Arrow keys to navigate, Escape to close)
- Then the dropdown is fully operable without a mouse

**Scenario 5: Active filter styling**
- Given a filter with a non-default value selected
- When it renders
- Then the pill shows the selected value and the "Clear filters" link appears (existing behaviour preserved)

## Technical approach
- Create a reusable `PillSelect` component (or similar) with:
  - Trigger button (pill-shaped, label + value + caret)
  - Dropdown panel (positioned below, `border-radius: 14px`, `box-shadow`, white background)
  - `aria-haspopup="listbox"` on the trigger, `role="listbox"` on the panel, `role="option"` on items
  - Click-outside-to-close via a `useEffect` listener
  - Keyboard navigation (ArrowUp/Down, Enter, Escape)
- Replace both native `<select>` elements in `Wardrobe.tsx` with `<PillSelect>`
- The Colour variant receives a `renderOption` prop (or slot) to show swatch + name
- No behaviour, route or contract change — the same query parameters are sent

## Design references
- Prototype: `docs/designs/heuniform/project/Hueniform App.dc.html` — Screen 03 state A (lines ~441–442: the two filter pills), state C (filtered state with active pills)
- Screenshots: `docs/designs/heuniform/project/screenshots/01-s.png` (filter bar)

## Tests
- `PillSelect.test.tsx`: renders closed state with label + value; opens on click; selects option and calls onChange; closes on click-outside; keyboard navigation (Enter/Space/Arrows/Escape); `jest-axe` clean (ARIA listbox pattern)
- Update `Inventory.test.tsx`: filters still work with the new component; combined filters issue the correct query parameters

## QA steps
- [ ] Open `/`: Category and Colour are pill-shaped buttons with label + value + caret
- [ ] Click Category: dropdown opens with region-grouped categories; select one → filter applies, pill updates
- [ ] Click Colour: dropdown opens with swatch + family name for each option
- [ ] Click outside: dropdown closes
- [ ] Keyboard: Tab to filter, Enter to open, Arrows to navigate, Enter to select, Escape to close
- [ ] Mobile: pills still render and are tappable (44 px touch target)

## Definition of done
- [x] Acceptance criteria met
- [x] Tests added/updated per test strategy and passing in `make test`
- [ ] Matcher-touching work: n/a
- [x] User-flow-touching work: `make test-e2e` — wardrobe filter journeys still pass
- [x] QA steps recorded and repeated in the chat completion report
- [x] Ticket status + notes updated in the same commit

## Notes
- 2026-07-06 — created (visual-fidelity audit of v0.3.0 against prototype); separated from HUE-113 because this is a new component with accessibility requirements, not a CSS tweak
- 2026-07-06 — done. Created `PillSelect` component with roving-tabindex keyboard navigation (not `aria-activedescendant`, which is invalid on `button`), `renderOption` prop for colour swatches, grouped-option support via `PillSelectGroup`. Replaced both native `<select>` elements in `Wardrobe.tsx`. Updated `Inventory.test.tsx` to use pill-click interactions. Updated `e2e/smoke.spec.ts` journey 1 to click the pill then the option. All 307 component tests and 27 e2e tests pass.
  Sanity test: `cd frontend && npm run test -- --reporter=dot 2>&1 | tail -5`
