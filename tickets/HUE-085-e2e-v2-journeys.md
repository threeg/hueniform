---
id: HUE-085
title: End-to-end smoke suite update (v0.2.0 journeys)
type: task
status: done
milestone: 14
batch: tooling
layer: tooling
depends_on: [HUE-070, HUE-071, HUE-074, HUE-077, HUE-080, HUE-083, HUE-069, HUE-073, HUE-076, HUE-079, HUE-082, HUE-040]
implements: [NFR-7]
tests_required: true
estimate: 5
---

## In plain English
Updates the automated walk-throughs that mimic a real person using the app, so they cover the refreshed screens from start to finish: adding and browsing garments, changing a garment's category, and requesting outfits with all the new choices.

## Background
Update the thin Playwright smoke suite for the reworked v0.2.0 screens (test strategy §9):
the grouped/ordered inventory, the direct category edit, and the rebuilt outfit request
(slot selection, category constraint, pins, anchor, count, neutral/fallback labels). Nothing
mocked; Chromium + Firefox (NFR-7). This is the cross-cutting capstone gating the user flows;
part of `make test-all` at milestone completion.

## Technical requirements
- Journey 1 — add a garment & browse: upload → confirm-and-correct selecting an FR-16 **category** → save → appears **grouped by category**, survives `category`+`family` filtering, and the Hue/Date order toggle re-orders within the group (FR-47)
- Journey 2 — edit a category: from garment detail change the category directly (no re-detection) → it moves to the new group; palette unchanged (FR-46)
- Journey 3 — request an outfit: deselect a default slot and constrain a multi-category slot and/or set a colour/scheme anchor and a count, optionally pin a garment → up to `count` ranked cards with scheme chip, per-slot tiles, explanation; first-class `neutral-based` unlabelled vs `fallback:true` labelled; one-piece pin auto-deselects base; "Suggest again" returns a valid response (FR-36/44/45/48/41/43)
- Journey 4 — empty-slot rejection: select a slot with no garments → verbatim `409 empty_slots` with the slot flagged "none in wardrobe" (FR-36)
- Chromium + Firefox; skip with an explicit message if model/browsers missing

## Definition of done (acceptance criteria)
- [x] All four journeys pass on Chromium and Firefox against the built app with the real model (NFR-7)
- [x] Reworked inventory, category-edit and outfit-request flows covered; nothing mocked
- [x] `make test-e2e` runs the suite; skips clearly if model/browsers absent
- [x] Tests added/updated per §12.2 and passing in `make test`; `make test-e2e` green (§12.3.6)
- [x] Ticket status + notes updated in the same commit

## Tests / verification
`e2e/*.spec.ts` (§9): the four journeys asserting user-visible behaviour only (contract detail
is §7's job). Mandatory in DoD for user-flow tickets (§12.3.6); part of `make test-all`.

## Notes
- 2026-06-18 — created (Milestone 13 ticket generation)
- 2026-07-03 — done. Rewrote `e2e/smoke.spec.ts` with four v0.2.0 journeys: empty-slot rejection, add garment & grouped inventory, category edit (FR-46), outfit request with new slot/count/result features. Added `npm run build` to `make test-e2e` to rebuild the SPA before running Playwright (old build was stale after frontend changes). Journey 4 required waiting for taxonomy to load before clicking suggest, so the slot-chip empty markers are present in the DOM when the 409 returns. All 8 tests (4 journeys × Chromium + Firefox) pass. Sanity test: `cd frontend && NODE_PATH=$(pwd)/node_modules npx playwright test --config ../e2e/playwright.config.ts`

## QA steps
1. Run `make test-e2e` — should report 8 passed (4 journeys × 2 browsers) in ~15 seconds.
2. With the server running (`make run`), open `http://127.0.0.1:8000/suggest` — you should see slot chips ("Base", "Lower body", "Socks", "Shoes" as locked, optional slots as buttons).
3. Click "Suggest outfits" immediately with an empty wardrobe — an error banner should appear and the Base/Socks/Shoes chips should show "— none in wardrobe".
4. Add a garment via `http://127.0.0.1:8000/add`, pick T-shirt, save — inventory should show a "T-shirt" group header with the hue-order toggle active.
5. On that garment's detail page, change category to Jumper and save — back on the inventory a "Jumper" group appears.
6. After seeding (`make seed-wardrobe`), go to `/suggest`, toggle Mid-layer on, set count to 5, click Suggest — ranked result cards with scheme chip, per-slot tiles, and explanation appear.
