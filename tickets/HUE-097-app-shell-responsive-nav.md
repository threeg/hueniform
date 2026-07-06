---
id: HUE-097
title: App shell and responsive navigation
type: story
status: done
milestone: 20
batch: design-system
layer: frontend
depends_on: [HUE-094, HUE-096]
implements: [NFR-7, NFR-11]
tests_required: true
estimate: 5
---

## In plain English
Restyles the app frame and makes navigation adapt to screen size — a sidebar on desktop, a condensed bar on tablet, and a bottom tab bar on phones — without changing where anything goes.

## User story
As the owner
I want the app frame and navigation to suit my screen size
so that the tool is comfortable on a phone, tablet or desktop.

## Acceptance criteria

**Scenario 1: Desktop shell**
- Given a viewport ≥ 1024 px
- When any screen renders
- Then the fixed left sidebar (Newsreader wordmark + Wardrobe / Add garment / Suggest outfit) is present, styled to the design system (07-responsive §2)

**Scenario 2: Mobile bottom tab bar**
- Given a viewport < 640 px
- When any screen renders
- Then navigation is a fixed bottom tab bar with the same three destinations and the wordmark in a slim top bar; routes and rules are unchanged (07-responsive §2)

**Scenario 3: Tablet**
- Given a viewport 640–1023 px
- Then the sidebar condenses (or moves to a top bar) with the same destinations

## Technical approach
- Restyle the app shell against tokens; implement the responsive navigation via native media/container queries (no framework).
- No route, data or contract change — a viewport-only reflow (architecture §2.5).

## Design references
- Wireframes: docs/04-wireframes/00-overview.md §2–§3; docs/04-wireframes/07-responsive.md §2; design system §5 (app shell), §6 (tiers)

## Tests
- `AppShell.test.tsx` (§10.1, §10.3): sidebar present at desktop width, bottom tab bar at mobile width; three destinations reachable each tier; `jest-axe` clean; focus-visible on nav items
- Responsive journeys added in HUE-105

## QA steps
- [x] Resize to desktop → expect sidebar; to phone width → expect bottom tab bar + top wordmark; to tablet → condensed nav
- [x] Navigate Wardrobe / Add / Suggest at each width → routes unchanged

## Notes

- 2026-07-05 — done. Rewrote `App.tsx` and `App.module.css` with a three-tier responsive shell (mobile-first). Mobile (<640px): slim top bar carrying the Newsreader italic wordmark + fixed bottom tab bar with Wardrobe / Add (aria-label "Add garment") / Suggest (aria-label "Suggest outfit"), 44 px touch targets. Tablet (640–1023px): top bar extends to include the three nav links inline; bottom tab bar hidden. Desktop (≥1024px): top bar hidden; fixed 190 px left sidebar with wordmark and nav links; main column margin-left 190 px, max-width 1290 px. All colours, spacing and radii via tokens. Updated `App.test.tsx` for the duplicate-text DOM (multiple wordmarks). Created `src/test/AppShell.test.tsx` (19 tests): sidebar/top-nav/tab-bar structure, `aria-current="page"` active state, accessible names on abbreviated tab labels, and jest-axe zero violations at /, /add, /suggest. `make test` (1120 backend + 258 frontend, zero warnings). Sanity test: `cd frontend && npm run test -- AppShell --run`.

## Definition of done
- [x] Acceptance criteria met
- [x] Tests added/updated per test strategy §10.3 and passing in `make test`
- [x] Matcher-touching work: n/a
- [x] User-flow-touching work: `make test-e2e` responsive journeys — added in HUE-105
- [x] QA steps recorded and repeated in the chat completion report
- [x] Ticket status + notes updated in the same commit
