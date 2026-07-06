---
id: HUE-113
title: Wardrobe visual fidelity
type: story
status: todo
milestone: 20
batch: cleanup
layer: frontend
depends_on: [HUE-101]
implements: []
tests_required: true
estimate: 2
---

## In plain English
The wardrobe screen's order toggle, category group headers, card styling and result-count placement don't match the prototype. The toggle and headers should be pill-shaped, cards need tweaked radii and a thinner palette strip, and the garment count should sit beside the page title.

## User story
As the owner
I want the wardrobe's visual details to match the design
so that filters, groups and cards look as intended.

## Acceptance criteria

**Scenario 1: Pill-shaped order toggle**
- Given the filter bar
- When the Hue / Date added toggle renders
- Then it is pill-shaped (`border-radius: 999px`), the active option has `background: #c66a4a; color: #fff; font-weight: 600; border-radius: 999px`, inactive shows `color: #a08a72`

**Scenario 2: Pill-badge group headers**
- Given garments grouped by category
- When a group header renders (e.g. "Shirt 4")
- Then it is a pill badge: `background: #f3e6d4; border-radius: 999px; padding: 7px 16px` with the count in a white sub-pill (`background: #fff; border-radius: 999px; font: 600 11px 'Space Mono'`)

**Scenario 3: Card tweaks**
- Given the garment card grid
- When cards render
- Then `border-radius: 13px`, palette strip height is 8 px (not 12 px)

**Scenario 4: Desktop grid**
- Given a desktop viewport
- When the card grid renders
- Then it uses `grid-template-columns: repeat(4, 1fr); gap: 18px`

**Scenario 5: Result count position**
- Given garments loaded
- When the page title row renders
- Then the count (e.g. "137 garments") sits to the right of the "Wardrobe" heading, not inside the filter bar

## Technical approach
- Update `Wardrobe.module.css`: pill-radius on order toggle + active style; new `.groupBadge` and `.groupCount` classes replacing the current border-bottom header; card `border-radius: 13px`; fixed 4-column grid at desktop; move count beside heading
- Update `Wardrobe.tsx`: restructure the group header markup to a pill badge with a count sub-pill; move the result count into the title row
- Pass `height={8}` to `<PaletteStrip>` in the garment card (or change the default)
- No behaviour, route or contract change

## Design references
- Prototype: `docs/designs/heuniform/project/Hueniform App.dc.html` — Screen 03 state A (lines ~436–477: title + count row, filter pills, order toggle, group pill badges, card grid)
- Screenshots: `docs/designs/heuniform/project/screenshots/01-s.png` (desktop wardrobe)

## Tests
- Update `Inventory.test.tsx`: assert group headers render as pill badges; assert count is within the title row; `jest-axe` clean

## QA steps
- [ ] Open `/` at desktop: "137 garments" beside the "Wardrobe" heading (not in filter bar)
- [ ] Order toggle: pill-shaped, Hue = clay fill, Date added = muted text
- [ ] Group headers: pill badges with warm background and white count sub-pill
- [ ] Cards: 4-column grid, ~13 px radius, thin (8 px) palette strip
- [ ] Resize to mobile: grid goes to 2 columns, toggle and badges still render correctly

## Definition of done
- [x] Acceptance criteria met
- [x] Tests added/updated per test strategy and passing in `make test`
- [ ] Matcher-touching work: n/a
- [ ] User-flow-touching work: `make test-e2e` — wardrobe journeys still pass
- [x] QA steps recorded and repeated in the chat completion report
- [x] Ticket status + notes updated in the same commit

## Notes
- 2026-07-06 — created (visual-fidelity audit of v0.3.0 against prototype)
