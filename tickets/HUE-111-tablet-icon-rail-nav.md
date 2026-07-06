---
id: HUE-111
title: Tablet icon-rail navigation
type: story
status: done
milestone: 20
batch: cleanup
layer: frontend
depends_on: [HUE-110]
implements: []
tests_required: true
estimate: 3
---

## In plain English
On tablet-width screens the prototype shows a narrow icon rail (not the current inline top bar) — an ~88 px vertical strip with the abbreviated "H." wordmark, the shape icons centred in 44 × 44 px containers, and labels beneath each icon. This ticket restructures the tablet navigation to match.

## User story
As the owner
I want the tablet navigation to condense to an icon rail
so that it uses space efficiently on mid-size screens as the design intends.

## Acceptance criteria

**Scenario 1: Icon rail at tablet width**
- Given a viewport 640–1023 px
- When any screen renders
- Then a fixed vertical icon rail (~88 px wide) appears on the left with: "H." abbreviated italic wordmark at the top; three nav items as centred shape icons (from HUE-110) in 44 × 44 px containers (`border-radius: 13px`); labels below each icon at ~9.5 px

**Scenario 2: Active state on rail**
- Given the active route
- When its icon-rail item renders
- Then the icon container has a clay-tinted background (`#f7e6de`) with a subtle shadow, and the label is clay-coloured (`#c66a4a`)

**Scenario 3: Routes unchanged**
- Given the icon rail
- When I tap/click Wardrobe, Add or Suggest
- Then the same routes navigate as desktop and mobile

## Technical approach
- Replace the current 640–1023 px top-bar layout in `App.module.css` with a fixed vertical rail (similar structure to the desktop sidebar but narrower)
- Reuse the shape-icon spans and active-state CSS created in HUE-110
- Add the abbreviated "H." wordmark variant (shown only at tablet width)
- Adjust the main content area's left margin at this breakpoint
- No behaviour, route or contract change

## Design references
- Prototype: `docs/designs/heuniform/project/Hueniform App.dc.html` — the tablet section (`#st`) showing the icon-rail layout
- Screenshots: `docs/designs/heuniform/project/screenshots/02-tab.png`, `03-tab.png`

## Tests
- Update `AppShell.test.tsx`: at tablet width, assert the icon rail is present (not the top bar), abbreviated wordmark renders, three icon containers are navigable; `jest-axe` clean
- Responsive e2e journeys (HUE-105) verify tablet navigation still works

## QA steps
- [ ] Resize to ~768 px: vertical icon rail on the left, "H." wordmark, shape icons in rounded containers, labels below
- [ ] Active route: icon container has tinted background + clay label
- [ ] Navigate via the rail: all three routes reachable
- [ ] Resize narrower (< 640 px): rail disappears, bottom tab bar appears
- [ ] Resize wider (≥ 1024 px): full sidebar appears

## Definition of done
- [x] Acceptance criteria met
- [x] Tests added/updated per test strategy and passing in `make test`
- [ ] Matcher-touching work: n/a
- [x] User-flow-touching work: `make test-e2e` — verify tablet nav
- [x] QA steps recorded and repeated in the chat completion report
- [x] Ticket status + notes updated in the same commit

## Notes
- 2026-07-06 — created (visual-fidelity audit of v0.3.0 against prototype)
- 2026-07-06 — done. Removed `topNav` from the `topBar` (top bar now mobile-only wordmark). Added a new `<aside class="iconRail">` section to `App.tsx` with an abbreviated `H.` wordmark (italic H + clay bold dot), `iconRailClass` factory, and three NavLinks each containing a `navIconContainer` wrapper around the shape icon and a label beneath. Added to `App.module.css`: `.iconRail`, `.iconRailWordmark`, `.iconRailDot`, `.iconRailLink`/`iconRailLinkActive`, `.navIconContainer` (44×44, `border-radius: 13px`); active icon container gets `--color-primary-tint` bg and `--shadow-nav-active`; icons in containers override to 18×18 px, 2px border. At 640px+ breakpoint: hide `topBar`, show and position `iconRail` (88px fixed left), update `main` to `margin-left: 88px; padding: var(--space-5)`. At 1024px+: hide `iconRail`, show full sidebar. Updated `nav.spec.ts` and `responsive.spec.ts` to target `aside:has(nav[aria-label="Sidebar"])` (two `<aside>` elements now coexist in DOM). Updated `AppShell.test.tsx`: renamed describe block, added abbreviated wordmark and icon-container tests. `make test-frontend` 279 passed; `make test-e2e` 27 passed, 2 skipped. Sanity test: `make test-e2e`.

## QA steps
- [x] Resize to ~768 px: vertical icon rail on the left, "H." wordmark, shape icons in rounded containers, labels below
- [x] Active route: icon container has tinted background + clay label
- [x] Navigate via the rail: all three routes reachable
- [x] Resize narrower (< 640 px): rail disappears, bottom tab bar appears
- [x] Resize wider (≥ 1024 px): full sidebar appears
