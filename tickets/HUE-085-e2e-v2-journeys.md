---
id: HUE-085
title: End-to-end smoke suite update (v0.2.0 journeys)
type: task
status: todo
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
- [ ] All four journeys pass on Chromium and Firefox against the built app with the real model (NFR-7)
- [ ] Reworked inventory, category-edit and outfit-request flows covered; nothing mocked
- [ ] `make test-e2e` runs the suite; skips clearly if model/browsers absent
- [ ] Tests added/updated per §12.2 and passing in `make test`; `make test-e2e` green (§12.3.6)
- [ ] Ticket status + notes updated in the same commit

## Tests / verification
`e2e/*.spec.ts` (§9): the four journeys asserting user-visible behaviour only (contract detail
is §7's job). Mandatory in DoD for user-flow tickets (§12.3.6); part of `make test-all`.

## Notes
- 2026-06-18 — created (Milestone 13 ticket generation)
