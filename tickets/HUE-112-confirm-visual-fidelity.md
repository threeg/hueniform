---
id: HUE-112
title: Confirm colours visual fidelity
type: story
status: done
milestone: 20
batch: cleanup
layer: frontend
depends_on: [HUE-100]
implements: []
tests_required: true
estimate: 2
---

## In plain English
The confirm-and-correct screen's category picker section doesn't match the prototype: the "Garment category" label should be Space Mono uppercase, the category chips should sit inside a white bordered container, the region headings should use the mono font, and selected chips should have a solid clay fill — not a light tint.

## User story
As the owner
I want the confirm screen's category section to match the design
so that the visual hierarchy (label → container → grouped chips) is clear and polished.

## Acceptance criteria

**Scenario 1: Category section label**
- Given the palette editor
- When the category section renders
- Then the label reads "Garment category — required" in Space Mono 11 px uppercase, `letter-spacing: .14em`, colour `#a89b86`

**Scenario 2: White bordered container**
- Given the category section
- When category chips render
- Then they sit inside a container with `background: #fff; border: 1px solid #ecdcc7; border-radius: 14px; padding: 14px 16px`

**Scenario 3: Region headings**
- Given the container
- When region groups (Head, Upper body, Lower body, Feet) render their headings
- Then each is Space Mono 10 px uppercase, `letter-spacing: .14em`, colour `#b3a892`

**Scenario 4: Selected chip style**
- Given no category is selected yet
- When I choose a category
- Then the selected chip shows: `background: #c66a4a; border-color: #c66a4a; color: #fff; font-weight: 600; box-shadow: 0 5px 12px -6px rgba(198,106,74,.8)`

## Technical approach
- Update `AddConfirm.module.css`: add the `.categoryLabel` style with mono font; add `.categoryContainer` with white background + border; update `.regionHeading` to use `var(--font-mono)` at 10 px
- Update the `Chip` component's selected variant (or override via CSS Module) to use solid clay fill instead of tint — check whether this should be a Chip variant prop or a screen-level override to avoid affecting other chip uses
- No behaviour, route or contract change

## Design references
- Prototype: `docs/designs/heuniform/project/Hueniform App.dc.html` — Screen 02 state A (lines ~208–226: the category label, white container, region headings, chips) and state E (lines ~337–342: selected chip with clay fill)
- Screenshots: `docs/designs/heuniform/project/screenshots/01-t46.png` (tablet confirm screen showing the full category section)

## Tests
- Update `ConfirmCorrect.test.tsx`: assert the category container element is present; `jest-axe` remains clean
- Chip selected state: verify the correct visual treatment is applied (class or inline check)

## QA steps
- [x] Navigate to `/add/confirm` via the upload flow
- [x] "Garment category — required" label: mono font, uppercase, muted colour
- [x] Category chips sit inside a white bordered panel with rounded corners
- [x] Region headings (Head, Upper body, etc.) in mono uppercase
- [x] Select a category: chip turns solid clay with white text and shadow
- [x] Resize to mobile: container still visible, chips wrap properly

## Definition of done
- [x] Acceptance criteria met
- [x] Tests added/updated per test strategy and passing in `make test`
- [x] Matcher-touching work: n/a
- [x] User-flow-touching work: `make test-e2e` — 27 passed, 2 skipped, zero failures
- [x] QA steps recorded and repeated in the chat completion report
- [x] Ticket status + notes updated in the same commit

## Notes
- 2026-07-06 — created (visual-fidelity audit of v0.3.0 against prototype)
- 2026-07-06 — done. Added `<p class="categoryLabel">Garment category — required</p>` above the category section (Space Mono, `--text-xs`, uppercase, `letter-spacing: .14em`, `--color-ink-faint`). Wrapped region groups in `<div class="categoryContainer">` (`--color-surface-highest` background, `1px solid --color-border-subtle` border, `--radius-lg` corners, `--space-3 --space-4` padding). Updated `.regionHeading` to use `--font-mono`, `--text-xs`, uppercase with `.14em` letter-spacing, `--color-ink-faint`. Added `.categoryChip[aria-pressed='true']` override on each Chip in the picker: `--color-primary` background+border, white text, `--weight-semibold`, `--shadow-chip-selected` (new token). Added `--shadow-chip-selected` token to `tokens.css`. Tests: 282 passed; e2e: 27 passed, 2 skipped. Sanity test: `cd frontend && npx vitest run src/routes/ConfirmCorrect.test.tsx`.
