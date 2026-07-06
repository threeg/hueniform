---
id: HUE-115
title: Screens 4–6 visual audit and fixes
type: story
status: todo
milestone: 20
batch: cleanup
layer: frontend
depends_on: [HUE-102, HUE-103, HUE-104, HUE-110]
implements: []
tests_required: true
estimate: 3
---

## In plain English
Garment detail, Suggest outfit and Suggestion results were restyled with tokens but haven't been audited against the prototype at the same level of detail as screens 1–3. This ticket reads the prototype source for screens 4–6, documents every visual gap, and fixes them in one pass.

## User story
As the owner
I want screens 4–6 to match the prototype as closely as screens 1–3
so that the entire app is visually consistent with the design.

## Acceptance criteria

**Scenario 1: Garment detail**
- Given the garment detail screen (`/garments/{id}`)
- When it renders at desktop
- Then it matches the prototype's Screen 04 states (default, category edit, delete confirmation, regenerate pending, not found) in layout, spacing, typography and component styling

**Scenario 2: Suggest outfit**
- Given the suggest screen (`/suggest`)
- When it renders at desktop
- Then the slot selector panel, region cards, pin/anchor controls and Generate button match the prototype's Screen 05 states

**Scenario 3: Suggestion results**
- Given suggestion results rendered below the request panel
- When results display
- Then the suggestion cards (slot labels, garment tiles, scheme chip, reasoning text, echo line), count header and zero-results state match the prototype's Screen 06 states

**Scenario 4: Navigation inherits shell fixes**
- Given any of these screens
- When the nav renders
- Then the clay dot, shape icons and active states from HUE-110 appear correctly (no screen-specific nav overrides needed)

## Technical approach
- Read `docs/designs/heuniform/project/Hueniform App.dc.html` screens 4–6 (sections `#s4`, `#s5`, `#s6`) and compare against the current implementation
- Document gaps, then fix — expected to be mostly CSS (spacing, radii, typography, colours) with minor JSX adjustments
- If the audit reveals a gap large enough to warrant its own ticket, note it in `## Notes` and create a follow-up rather than bloating this ticket
- No behaviour, route or contract change

## Design references
- Prototype: `docs/designs/heuniform/project/Hueniform App.dc.html` — sections `#s4` (Garment detail), `#s5` (Suggest outfit), `#s6` (Suggestion results)
- Screenshots: `docs/designs/heuniform/project/screenshots/02-s.png`, `03-s.png` (desktop), `02-tab.png`, `03-tab.png` (tablet), `02-mall.png`, `03-mall.png` (mobile)

## Tests
- Update screen component tests as needed for any DOM structure changes; `jest-axe` remains clean on all states
- Responsive e2e journeys (HUE-105) verify the screens still function at all breakpoints

## QA steps
- [ ] Garment detail: compare each state against prototype Screen 04 at desktop, tablet and mobile
- [ ] Suggest outfit: compare slot selector, pin/anchor controls, Generate button against prototype Screen 05
- [ ] Suggestion results: compare result cards, count header, zero-results against prototype Screen 06
- [ ] Tab through each screen: visible focus ring on all interactive elements

## Definition of done
- [x] Acceptance criteria met
- [x] Tests added/updated per test strategy and passing in `make test`
- [ ] Matcher-touching work: n/a
- [ ] User-flow-touching work: `make test-e2e` — all journeys still pass
- [x] QA steps recorded and repeated in the chat completion report
- [x] Ticket status + notes updated in the same commit

## Notes
- 2026-07-06 — created (visual-fidelity audit of v0.3.0 against prototype); depends on HUE-110 so the nav fixes are in place before auditing their appearance on these screens
