---
id: HUE-097
title: App shell and responsive navigation
type: story
status: todo
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
- [ ] Resize to desktop → expect sidebar; to phone width → expect bottom tab bar + top wordmark; to tablet → condensed nav
- [ ] Navigate Wardrobe / Add / Suggest at each width → routes unchanged

## Definition of done
- [ ] Acceptance criteria met
- [ ] Tests added/updated per test strategy §10.3 and passing in `make test`
- [ ] Matcher-touching work: n/a
- [ ] User-flow-touching work: `make test-e2e` responsive journeys — added in HUE-105
- [ ] QA steps recorded and repeated in the chat completion report
- [ ] Ticket status + notes updated in the same commit
