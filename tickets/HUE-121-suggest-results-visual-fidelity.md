---
id: HUE-121
title: Suggest outfit & results visual fidelity
type: story
status: todo
milestone: 20
batch: cleanup
layer: frontend
depends_on: [HUE-103, HUE-104, HUE-115]
implements: []
tests_required: true
estimate: 3
---

## In plain English
Line-by-line audit of the Suggest outfit and Suggestion results screens (`/suggest`) against the prototype. The slot region cards, pin section, anchor controls, result card layout and zero-results state all have styling gaps.

## User story
As the owner
I want the suggest and results screens to match the prototype in every detail
so that outfit building and reviewing feels as polished as the rest of the app.

## Acceptance criteria — gaps found

### Screen 05 — Suggest outfit (request panel)

#### Slot region cards
1. **Slot group card** — design: each region is a distinct card with `border: 1px solid; border-radius: 12px; padding: 12px 16px`. Current: already has `.slotGroup` with these values. **Check** — may already match.
2. **Slot label** — design: region headers are `font: 400 11px 'Space Mono', monospace; letter-spacing: .14em; text-transform: uppercase; color: #a89b86`. Current: `--font-mono`, `--text-xs`, `--weight-semibold` (600), `letter-spacing: 0.1em`. **Fix:** weight should be 400, letter-spacing .14em.
3. **Locked lower-body chip** — design: dark olive/green chip with a lock icon (🔒). Current: check if lock icon is present.

#### Pin section
4. **Section heading** — design: not explicitly shown as a separate section label in the prototype for pins. Current: `.sectionHeading` uppercase. **Check** against prototype.
5. **Pin chip** — design: shows removable pin chips with thumbnail + label + × button. Current: has `.pinChip` with similar structure. **Check** exact styling.
6. **"Pin a garment" button** — design: `border: 1px dashed` style. Current: already dashed. **Check** exact border colour.

#### Anchor section
7. **"Colour family" label** — design: `font: 400 11px 'Space Mono', monospace; letter-spacing: .14em; text-transform: uppercase; color: #a89b86`. Current: `.anchorLabel` uses `--font-mono`, `--text-xs`. **Check** letter-spacing value (.14em vs .1em).
8. **Family swatch** — design: `14×14px rounded square (border-radius: 4px)`. Current: `.familySwatch` uses `border-radius: 50%` (circle), `10×10px`. **Fix:** 14px, border-radius 4px.

#### Count and Generate row
9. **Count stepper** — design shows ± buttons on either side of the count value in a cohesive row. Current: `.countStepper`. **Check** exact styling.
10. **Generate button position** — design: Generate button is in the bottom-right of the panel, large and prominent. Current: in `.panelFooter`. **Check** exact placement.

### Screen 06 — Suggestion results

#### Results header
11. **"Showing X of Y you asked for"** — design: `font-size: 13px; color: #5f5646` with "— fewer than the count is normal" suffix. Current: `.resultsHeader` with similar values. **Check** exact text match.

#### Result cards
12. **Card header background** — design: the header row (`Suggestion 1 + scheme chip`) has a distinct `background: #fbf4ea; border-bottom: 1px solid #ecdcc7; padding: 12px 24px`. Current: `.cardHeader` already has these values. **Verify** — should be correct from HUE-115.

#### Slot tiles
13. **Slot caption** — design: `font: 400 11px 'Space Mono', monospace; letter-spacing: .14em; text-transform: uppercase; color: #a89b86` above each tile. Current: `.slotCaption` uses `--text-xs`, `--color-ink-secondary`. **Fix:** mono font, uppercase, different colour.
14. **Slot thumbnail** — design: shows the slot tiles at roughly `130×100px` with rounded top corners. Current: `100×80px`. **Check** — HUE-115 may have adjusted this.

#### Explanation and echoes
15. **Explanation** — design: `font-size: 14px; color: #3a3128; line-height: 1.5`. Current: `.explanation` matches. **Verify.**
16. **Echo swatch** — design: `14×14px; border-radius: 4px` (rounded square). Current: `--radius-sm` (6px). **Check** — HUE-115 changed this.

#### Zero results state
17. **Zero results** — design: a bordered card with "No outfit this time" at `font: 400 20px 'Newsreader', serif`, explanation text, a "Hint:" callout in an amber-bordered box, and two action buttons ("Remove outer layer" primary + "Add a garment" secondary). Current: `.zeroResults` has `--radius-md` border. **Check** heading font, hint callout style, button layout.
18. **Hint callout** — design: `background: #fbf1dc; border: 1px solid #d9b46a; border-radius: 12px; padding: 12px 16px` with "Hint:" bold prefix. Current: may be plain text. **Fix** if not styled as a callout.

#### Suggest again
19. **"Suggest again" button** — design: secondary style, centred below results. Current: check.

## Technical approach
- Most items are CSS fixes (font-family, letter-spacing, border-radius, sizing)
- Family swatch border-radius change from circle to rounded square affects both Suggest and Wardrobe — coordinate or use a shared class
- Slot caption: add mono uppercase treatment
- Zero results hint callout: may need a small styled callout component
- Read prototype Screen 05 and 06 sections for exact values
- No behaviour, route or contract change

## Design references
- Prototype: `docs/designs/heuniform/project/Hueniform App.dc.html` — Screen 05 and Screen 06 (read from `#s5` and `#s6` sections)
- Screenshots: `docs/designs/heuniform/project/screenshots/02-s.png` (desktop suggest), `03-s.png` (desktop results)

## Tests
- Update Suggest/results component tests for any DOM changes; `jest-axe` clean

## QA steps
- [ ] Suggest: slot labels in mono weight-400 with .14em spacing; family swatches are 14px rounded squares
- [ ] Results: slot captions in mono uppercase; echo swatches are rounded squares
- [ ] Zero results: serif heading, hint callout in amber box, two action buttons
- [ ] Suggest again: centred secondary button below results

## Definition of done
- [x] Acceptance criteria met
- [x] Tests added/updated and passing in `make test`
- [ ] Matcher-touching work: n/a
- [x] QA steps recorded
- [x] Ticket status + notes updated in the same commit

## Notes
- 2026-07-06 — created (line-by-line audit of Screens 05–06 against prototype)
