---
id: HUE-102
title: Restyle Garment detail
type: story
status: todo
milestone: 20
batch: screen
layer: frontend
depends_on: [HUE-096, HUE-097, HUE-098, HUE-074]
implements: [NFR-11, NFR-7]
tests_required: true
estimate: 3
---

## In plain English
Applies the new look and the phone/tablet/desktop layouts to the garment detail screen, without changing what it does.

## User story
As the owner
I want the garment detail screen to match the new design and adapt to my screen size
so that it is attractive and usable everywhere.

## Acceptance criteria

**Scenario 1: Restyled to the design system**
- Given garment detail (image, palette, category edit, regenerate/delete, all states)
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
- Wireframes: docs/04-wireframes/04-garment-detail.md (all states); docs/04-wireframes/07-responsive.md §4; design system §5–§6

## Tests
- Screen component test (§10.1, §10.3): states render; `jest-axe` zero violations; focus-visible; token variables used
- Responsive + journey coverage in HUE-105

## QA steps
- [ ] View the screen at desktop / tablet / mobile → expect the design-system look and the reflow in 07-responsive §4
- [ ] Tab through interactive elements → expect a visible focus ring
- [ ] Confirm each documented state still appears and behaves as before

## Definition of done
- [ ] Acceptance criteria met
- [ ] Tests added/updated per test strategy §10.3 and passing in `make test`
- [ ] Matcher-touching work: n/a
- [ ] User-flow-touching work: `make test-e2e` responsive journeys — HUE-105
- [ ] QA steps recorded and repeated in the chat completion report
- [ ] Ticket status + notes updated in the same commit
