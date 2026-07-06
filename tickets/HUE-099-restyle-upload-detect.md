---
id: HUE-099
title: Restyle Upload & detect
type: story
status: done
milestone: 20
batch: screen
layer: frontend
depends_on: [HUE-096, HUE-097, HUE-098, HUE-033]
implements: [NFR-11, NFR-7]
tests_required: true
estimate: 3
---

## In plain English
Applies the new look and the phone/tablet/desktop layouts to upload and detect, without changing what it does.

## User story
As the owner
I want upload and detect to match the new design and adapt to my screen size
so that it is attractive and usable everywhere.

## Acceptance criteria

**Scenario 1: Restyled to the design system**
- Given the upload/detect screen (drop zone, detecting, rejection states)
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
- Wireframes: docs/04-wireframes/01-upload-detect.md (all states); docs/04-wireframes/07-responsive.md §4; design system §5–§6

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

- 2026-07-06 — done. Restyled `AddGarment.module.css` — all hardcoded hex/px values replaced with design-system tokens (`var(--color-*)`, `var(--space-*)`, `var(--text-*)`, `var(--radius-*)`, `var(--font-display)`, `var(--weight-*)`, `var(--leading-*)`). Drag-over state: `--color-primary` border + `--color-primary-tint` background. Responsive: `@media (max-width: 639px)` removes `max-width` constraint and tightens padding so the drop zone fills the mobile viewport. Updated `AddGarment.tsx` to import and use the shared `Button` (variant `secondary`) instead of the inline `pickButton` style. Added `aria-hidden="true"` to the hidden file input — axe correctly flagged it as unlabelled since it is zero-size and `tabIndex={-1}` (not keyboard-reachable); the visible "Choose a file…" button is the sole interactive path. Added 2 axe tests to `UploadDetect.test.tsx` (default state + error state) using `expectNoAxeViolations`. `make test` (1120 backend + 263 frontend, zero warnings). Sanity test: `cd frontend && npm run test -- UploadDetect --run`.

## QA steps
- [ ] Run `make dev` and open `/add` at desktop width (≥ 1024 px): drop zone renders with warm cream background, clay/terracotta drag-over highlight, Newsreader display heading, secondary button style matching the design system.
- [ ] Resize to tablet (~768 px): layout unchanged (single column), drop zone full-width within the content area.
- [ ] Resize to mobile (~390 px): `max-width` removed, drop zone fills the viewport; button and text remain readable.
- [ ] Tab through the page: visible clay focus ring on the "Choose a file…" button (no focus on the hidden input).
- [ ] Drop an invalid file: error banner appears above the drop zone; drop zone remains interactive.
- [ ] Drop a valid image: loading state ("Detecting colours…") replaces zone content while request is in flight; on success, navigates to `/add/confirm`.
