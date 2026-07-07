---
id: HUE-119
title: Wardrobe screen visual fidelity (audit pass 2)
type: story
status: done
milestone: 20
batch: cleanup
layer: frontend
depends_on: [HUE-101, HUE-113, HUE-114]
implements: []
tests_required: true
estimate: 2
---

## In plain English
Second-pass audit of the Wardrobe screen against the prototype. HUE-113 and HUE-114 fixed the major items (pill toggle, group badges, pill-select filters); this ticket covers the remaining gaps in empty states, loading skeleton, filter active styling, filtered count position, and error banner.

## User story
As the owner
I want the wardrobe's remaining edge-case states to match the design
so that empty, loading, filtered and error states are all polished.

## Acceptance criteria — gaps found

### Empty wardrobe state (design state D)
1. **Empty state container** — design: `max-width: 520px; margin: 40px auto; border: 2px dashed #d8c3a6; border-radius: 20px; padding: 52px 40px; background: #fdf8f0; text-align: center`. Current: flex column with `--space-8` padding, no dashed border or distinct background. **Fix:** match the dashed-border card.
2. **Empty icon** — design: `56×56px; border-radius: 18px; background: #f7e6de; color: #c66a4a; font-size: 26px` showing ◇. Current: no icon. **Fix:** add diamond icon.
3. **Empty heading** — design: `font: 500 20px 'Newsreader', serif; color: #3a3128` "Your wardrobe is empty". Current: check font family.
4. **Empty subtext** — design: `font-size: 14px; color: #8a7c66` "Photograph a garment and Hueniform will detect its colours."
5. **Empty CTA** — design: `padding: 12px 24px; border-radius: 12px; background: #c66a4a; color: #fff; font-weight: 600; box-shadow: 0 10px 20px -10px rgba(198,106,74,.8)` "Add your first garment". Current: likely close but check shadow.

### Empty filter result state (design state E)
6. **Filter-empty container** — design: `max-width: 520px; margin: 30px auto; border: 2px dashed #d8c3a6; border-radius: 20px; padding: 48px 40px; background: #fdf8f0`. Current: likely uses the same emptyState class as empty wardrobe. **Fix:** match dashed card.
7. **Filter-empty text** — design: "No garments match" at `font: 500 19px 'Newsreader', serif`, then "No beanie contains magenta. Clear the filters to see everything." with inline clay-underlined "Clear the filters" link.

### Active filter pill styling (design state C)
8. **Active pill** — design: `border: 1px solid #c66a4a; background: #f7e6de; color: #c66a4a; font-weight: 600`. Current: PillSelect has `.triggerActive` with `border-color: var(--color-primary); background: var(--color-primary-tint)`. **Check** — may already match.
9. **Colour swatch in pill** — design: `14×14px; border-radius: 4px` (rounded square, not circle). Current: `.familySwatch` uses `border-radius: 50%` (circle). **Fix:** 4px border-radius.
10. **Clear filters** — design: `color: #c66a4a; text-decoration: underline`. Current: check if matches.

### Loading skeleton state (design state F)
11. **Skeleton cards** — design shows skeleton card shells (13px radius, `#fdf8f0` background, `#efe3d0` photo area, `#e6d8c1` palette strip, small name placeholder) in a 4-column grid. Current: LoadingState component with shimmer bars. **Fix:** match skeleton cards with the card-shaped placeholders.
12. **Skeleton group badge** — design: `110×32px; border-radius: 999px; background: #efe3d0`. Current: likely not shown. **Fix:** add.
13. **Loading count** — design: `font: 400 13px 'Space Mono', monospace; color: #c1b39c` showing "…". Current: check.

### Load failure state (design state G)
14. **Error banner with inline Retry** — design: banner has an inline "Retry" button (`padding: 8px 18px; border-radius: 10px; background: #fff; border: 1px solid #e0a08c; color: #8a3a28; font-weight: 600; font-size: 13px`) inside the banner at `margin-left: auto`. Current: separate Button below the banner. **Fix:** move Retry inside the banner.

### Card "date" label in Date-added order (design state B)
15. **Date label** — design shows a small mono label ("newest"/"oldest") right-aligned in the card caption for date-ordered cards: `font: 400 10px 'Space Mono', monospace; color: #b3a892`. Current: not present. **Fix:** add date label when `order=date`.

## Technical approach
- Empty states: replace the plain emptyState with a dashed-border card matching the upload zone style
- Skeleton: create card-shaped skeleton placeholders instead of generic shimmer bars
- Active pill swatch: change border-radius from circle to 4px rounded square
- Error banner: add inline Retry variant
- Date label: conditionally show in GarmentCard when order=date
- Read `docs/designs/heuniform/project/Hueniform App.dc.html` Screen 03, states D–G (lines 560–655) for exact values
- No behaviour, route or contract change

## Design references
- Prototype: `docs/designs/heuniform/project/Hueniform App.dc.html` — Screen 03, all states (lines 418–655)
- Screenshots: `docs/designs/heuniform/project/screenshots/01-msec.png` (empty + loading + error micro-states)

## Tests
- Update `Inventory.test.tsx` for DOM changes; `jest-axe` clean

## QA steps
- [x] Empty wardrobe: dashed-border card (`border: 2px dashed #d8c3a6; border-radius: 20px; background: #fdf8f0`), diamond icon (56×56px `#f7e6de` tile, `◇` in clay), Newsreader 500 20px heading "Your wardrobe is empty", clay CTA with `box-shadow: 0 10px 20px -10px`
- [x] Empty filter result: dashed card, "No garments match" Newsreader 500 19px, inline clay-underlined "Clear the filters" link
- [x] Loading: 4 skeleton card shells in grid, skeleton group badge (110×32px `#efe3d0` pill), "…" mono count in title row
- [x] Error: banner has inline Retry button inside the alert element (not a separate button below)
- [x] Filtered pills: colour swatch `border-radius: 4px` (rounded square, not circle) — verified in devtools
- [x] Date-added order: "newest" on first card, "oldest" on last card, 10px Space Mono `#b3a892`

## Definition of done
- [x] Acceptance criteria met
- [x] Tests added/updated and passing in `make test`
- [ ] Matcher-touching work: n/a
- [x] QA steps recorded
- [x] Ticket status + notes updated in the same commit

## Notes
- 2026-07-06 — created (second-pass audit of Screen 03 against prototype)
- 2026-07-06 — completed. Empty wardrobe → dashed card with 56×56 clay diamond icon, Newsreader 500 20px heading, 14px subtext, CTA with drop shadow. Filter-empty → dashed card, Newsreader 500 19px "No garments match", inline clay clear link. Loading → replaced LoadingState with 4 skeleton card shells + skeleton group badge (no listitem roles to avoid count collisions); title row shows "…" in Space Mono during fetch. Error → Banner gains optional `action` prop; Retry moved inside the banner element. Colour swatch → border-radius 4px (was 50%). Date label → GarmentCard gets `dateLabel` prop; Wardrobe passes "newest"/"oldest" to first/last garments when `order=date`. Banner.module.css adds `.action` button style. GarmentCard.module.css adds `.metaRow` + `.dateLabel`. 334 tests passing.

  Sanity test: `cd frontend && npm run test -- Inventory --run`
