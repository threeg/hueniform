---
id: HUE-110
title: App shell navigation visual fidelity
type: story
status: done
milestone: 20
batch: cleanup
layer: frontend
depends_on: [HUE-097]
implements: []
tests_required: true
estimate: 3
---

## In plain English
The sidebar, top bar and bottom tab bar are missing several design details: the clay dot next to the wordmark, shape icons on each navigation item, and the correct active-state styling (solid clay fill instead of a light tint). This ticket brings all three navigation surfaces to pixel-level fidelity with the prototype.

## User story
As the owner
I want the navigation to match the finished design — dot, icons and active state
so that the app looks polished and complete.

## Acceptance criteria

**Scenario 1: Clay dot**
- Given any screen at any viewport
- When the wordmark "Hueniform" renders
- Then an 8 px `#c66a4a` circle appears immediately after the text

**Scenario 2: Shape icons**
- Given the desktop sidebar, tablet nav or mobile bottom tab bar
- When the three navigation items render
- Then each carries its shape icon: Wardrobe = rounded square (`border-radius: 5px`), Add garment = circle (`border-radius: 50%`), Suggest outfit = rotated diamond (`border-radius: 4px; transform: rotate(45deg)`), all 16 × 16 px with a 1.7 px border

**Scenario 3: Active state**
- Given the currently active route
- When its nav item renders
- Then it has: `background: #c66a4a; color: #fff; font-weight: 600; border-radius: 16px; box-shadow: 0 6px 14px -6px rgba(198,106,74,.7)` and its shape icon uses `currentColor` (white)

**Scenario 4: Inactive state**
- Given non-active nav items
- When they render
- Then text is `#736858`, icon border is `#c1b39c`, padding is `11px 15px`, with `border-radius: 16px`

**Scenario 5: Mobile tab bar icons**
- Given a viewport < 640 px
- When the bottom tab bar renders
- Then each tab carries the same shape icon as the sidebar, with the abbreviated label beneath

## Technical approach
- Add shape-icon `<span>` elements to each `<NavLink>` in all three navigation regions in `App.tsx` (sidebar, top nav, bottom tab bar — 9 insertions total)
- Add the clay-dot `<span>` beside each wordmark instance
- Update active/inactive CSS classes in `App.module.css` to match prototype values
- Shape icons are CSS-only (border + border-radius + transform), not SVGs — matching the prototype's technique
- No behaviour, route or contract change

## Design references
- Prototype: `docs/designs/heuniform/project/Hueniform App.dc.html` — the sidebar block repeated in every `.frame` div (lines 67–73 show the pattern: wordmark + dot, then three nav items each with a `<span>` shape icon)
- Screenshots: `docs/designs/heuniform/project/screenshots/01-s.png` (desktop sidebar), `m.png` (mobile tab bar)

## Tests
- Update `AppShell.test.tsx`: assert shape-icon elements are present in each nav region; assert active-state class produces the correct visual properties; `jest-axe` remains clean
- Existing responsive journey coverage in HUE-105 verifies the nav still functions at all breakpoints

## QA steps
- [ ] Desktop sidebar: three nav items each show a shape icon (square, circle, diamond) with the label beside it; clay dot visible next to "Hueniform"
- [ ] Click each nav item: active = solid clay fill, white text, shadow; inactive = muted text, border-only icon
- [ ] Mobile (< 640 px): bottom tab bar shows shape icons with abbreviated labels; top bar shows wordmark + dot
- [ ] Tab through: visible focus ring on all nav items

## Definition of done
- [x] Acceptance criteria met
- [x] Tests added/updated per test strategy and passing in `make test`
- [ ] Matcher-touching work: n/a
- [x] User-flow-touching work: `make test-e2e` — verify nav still passes
- [x] QA steps recorded and repeated in the chat completion report
- [x] Ticket status + notes updated in the same commit

## Notes
- 2026-07-06 — created (visual-fidelity audit of v0.3.0 against prototype)
- 2026-07-06 — done. Added `--color-nav-icon: #c1b39c` and `--shadow-nav-active` tokens to `tokens.css`. In `App.tsx`: wrapped each wordmark text with a sibling `<span class="wordmarkDot" aria-hidden>` clay dot; added a shape icon `<span aria-hidden>` inside every NavLink in all three nav tiers (9 spans total). In `App.module.css`: `.wordmarkDot` (8×8 px clay circle); `.navIconWardrobe` (5 px border-radius), `.navIconAdd` (50% = circle), `.navIconSuggest` (4 px + rotate 45°) — all 16×16 px with 1.7 px border; `.sideLink`/`.topLink`/`.tabLink` changed to flex with 11 px gap, `padding: 11px 15px`, `border-radius: var(--radius-lg)`; active states changed from light tint to solid clay (`var(--color-primary)`), white text, semibold weight, `var(--shadow-nav-active)`; tab bar links changed to flex-column (icon above label). Updated `AppShell.test.tsx`: added shape icon presence tests for all three nav tiers and a wordmark dot test. `make test-frontend` 277 passed (13 suites); `make test-e2e` 27 passed, 2 skipped. Sanity test: `make test-e2e`.

## QA steps
- [x] Desktop sidebar: each nav item shows a shape icon (square/circle/diamond) left of label; clay dot visible after "Hueniform"
- [x] Click each nav item: active = solid clay fill, white text, shadow; inactive = muted text, border-only icon
- [x] Mobile (< 640 px): bottom tab bar shows shape icons above abbreviated labels; top bar wordmark has dot
- [x] Tab through: visible focus ring on all nav items
