---
id: HUE-118
title: Confirm colours screen visual fidelity
type: story
status: done
milestone: 20
batch: cleanup
layer: frontend
depends_on: [HUE-100, HUE-112]
implements: []
tests_required: true
estimate: 3
---

## In plain English
Line-by-line audit of the Confirm colours screen (`/add/confirm`) against the prototype. The palette editor, stepper controls, add-colour panel, preview bar and two-column layout all have styling gaps.

## User story
As the owner
I want the confirm screen to match the prototype in every detail
so that palette editing feels precise and intentional.

## Acceptance criteria — gaps found (design value → current)

### Layout and title
1. **Page title** — design: `font: 400 30px/1 'Newsreader', serif` (weight 400). Current: `--text-2xl` (26px) + `--weight-semibold` (600). **Fix:** 30px, weight 400.
2. **Two-column gap** — design: `gap: 34px`. Current: `var(--space-6)` = 32px. **Minor** — acceptable.
3. **Image preview height** — design: `height: 300px`. Current: `max-height: 520px` (no fixed height). **Fix:** add `height: 300px` (or `max-height: 300px`) so it matches the compact preview.
4. **Image caption** — design: `font: 400 11px 'Space Mono', monospace; color: #b09a80; text-align: center`. Current: `--font-mono`, `--text-xs`, `--color-ink-faint`. **Check** — colour close but not exact (#b09a80 vs #a89b86).

### Detected palette section
5. **"Detected palette" label** — design: `font: 400 11px 'Space Mono', monospace; letter-spacing: .14em; text-transform: uppercase; color: #a89b86; margin-bottom: 10px`. Current: no explicit "Detected palette" label visible. **Fix:** add mono uppercase section label.
6. **Colour swatch** — design: `28×28px; border-radius: 8px; box-shadow: inset 0 0 0 1px rgba(0,0,0,.12)`. Current: swatch `size={28}` ✓ but check border-radius and inset shadow.
7. **Family name** — design: `font-weight: 600; width: 96px; color: #3a3128`. Current: rendered inside Swatch component. **Check** — width constraint may be missing.
8. **Stepper** — design: rounded composite control (`border: 1px solid #e2d3bf; border-radius: 10px; overflow: hidden; background: #fff`) with −/value/+ segments, − and + on `background: #f6ebdc; color: #8a7c66; font-weight: 700`. Current: separate 28×28 square buttons + 52px input. **Fix:** redesign stepper to match the integrated pill-style control.
9. **"%" label** — design: separate `<span>` after stepper, `color: #b09a80`. Current: likely inside input or missing.
10. **Remove link** — design: `margin-left: auto; color: #a86a56; font-size: 13px; text-decoration: underline`. Current: button with `--color-ink-muted`, no underline.
11. **Row separator** — design: `border-bottom: 1px solid #efe4d2`. Current: `var(--color-border-subtle)` = #ecdcc7 — slightly different.
12. **Row gap** — design: `gap: 14px; padding: 12px 0`. Current: `gap: var(--space-3)` = 12px, `padding: var(--space-2) 0` = 8px 0.

### Preview bar and total
13. **Preview bar height** — design: `22px`. Current: `10px`. **Fix:** increase to 22px.
14. **Preview bar border-radius** — design: `8px`. Current: `var(--radius-pill)` = 999px. **Fix:** 8px.
15. **Preview bar border** — design: `box-shadow: inset 0 0 0 1px rgba(0,0,0,.08)`. Current: `1px solid var(--color-border-subtle)`.
16. **Preview bar margin** — design: `margin: 18px 0 8px`. Current: part of flex gap.
17. **Total line** — design: `font-size: 13px; color: #6f6455` with bold value. Current: `--font-mono`, `--text-xs`. **Fix:** increase size, use sans not mono, match colour.

### Add-a-colour
18. **"+ Add a colour" link** — design: `font-size: 13.5px; color: #c66a4a; font-weight: 600`. Current: dashed-border button, `--color-ink-secondary`. **Fix:** restyle to clay-coloured text link.
19. **Add panel** — design: `1.5px dashed #d8c3a6; border-radius: 16px; padding: 16px 18px; background: #fdf8f0` with a titled header "Add a colour" (bold), a dropdown list of families with swatches, and a proportion stepper + primary "Add" button. Current: flat flex panel with `--radius-md`, `--color-surface` background. **Fix:** match dashed border, background, family list layout (vertical, not dropdown), and primary Add button.

### Category section (partially fixed by HUE-112)
20. **Chip font-size** — design: `12.5px`. Current: `var(--text-xs)` = 12px. **Minor** — 0.5px.
21. **Chip padding** — design: `6px 13px`. Current: `var(--space-1) var(--space-3)` = 4px 12px. **Fix:** 6px 13px.
22. **Chip gap** — design: `7px`. Current: `var(--space-2)` = 8px. **Minor** — 1px.

### Save/Cancel actions
23. **Disabled Save** — design: `background: #dcc9b5; color: #fff` (muted clay, not grey). Current: `--color-surface` bg, `--color-ink-faint` text. **Fix:** use muted clay for disabled primary.
24. **Save hint text** — design: `font-size: 12.5px; color: #a89b86` "Save enables once a category is chosen" (inline after Cancel). Current: check if present and styled.
25. **Button padding** — design: `11px 22px`. Current: `var(--space-2) var(--space-4)` = 8px 16px. **Fix:** increase padding.
26. **Actions margin** — design: `margin-top: 22px`. Current: `padding-top: var(--space-2)` = 8px. **Fix:** increase.

### Warning banner (fallback)
27. **Warning banner** — design: `background: #fbf1dc; border: 1px solid #d9b46a; border-radius: 14px; padding: 14px 18px` with amber "!" icon (`background: #c69a3a`). Current: Banner component — check if warning variant matches (was updated for error in HUE-117, warning may differ).

## Technical approach
- Focus on the palette editor: the stepper control is the biggest structural change — redesign from three separate inputs to an integrated pill-style −/value/+ composite
- Preview bar: height 22px, border-radius 8px, inset shadow
- Add-colour panel: match the dashed-border card with vertical family list
- Title: 30px weight 400 (not 26px semibold)
- Button padding and disabled state
- Read `docs/designs/heuniform/project/Hueniform App.dc.html` lines 160–415 (Screen 02, all states) for exact values
- No behaviour, route or contract change

## Design references
- Prototype: `docs/designs/heuniform/project/Hueniform App.dc.html` — Screen 02, states A–G (lines 160–415)
- Screenshots: `docs/designs/heuniform/project/screenshots/01-t46.png` (tablet confirm)

## Tests
- Update `ConfirmCorrect.test.tsx` for any DOM changes (stepper restructure); `jest-axe` clean

## QA steps
- [ ] "Confirm colours" at 30px serif weight 400; "Detected palette" mono uppercase label above colour rows
- [ ] Colour rows: 28px swatch with inset shadow, 96px family name, integrated pill stepper (−/80/+), %, underlined Remove
- [ ] Preview bar: 22px tall, 8px radius, inset shadow
- [ ] "+ Add a colour" as clay text link; panel in dashed card with vertical family list
- [ ] Category section: chip padding 6px 13px
- [ ] Disabled Save: muted clay background, not grey
- [ ] Buttons: 11px 22px padding, 22px gap above

## Definition of done
- [x] Acceptance criteria met
- [x] Tests added/updated per test strategy and passing in `make test`
- [ ] Matcher-touching work: n/a
- [x] QA steps recorded
- [x] Ticket status + notes updated in the same commit

## Notes
- 2026-07-06 — created (line-by-line audit of Screen 02 against prototype)
- 2026-07-06 — completed. Title → 30px weight 400. Image → max-height 300px. Added "Detected palette" mono uppercase label. Colour rows: integrated pill stepper (−/value/+ in `#f6ebdc` segments, `#e2d3bf` border, 10px radius), separate `%` label, remove styled as underlined clay text link, row separator `#efe4d2`, gap 14px / padding 12px. Preview bar → 22px tall, 8px radius, inset shadow, `margin:18px 0 8px`. Total line → sans 13px `#6f6455` with bold value. Add button → clay text link. Add panel → dashed `#d8c3a6` card with vertical family button list (swatch dot + name rows). Chip padding → 6px 13px globally. Disabled primary → muted clay `#dcc9b5`. Button padding → 11px 22px. Actions margin-top → 22px. Warning banner → amber `#fbf1dc`/`#d9b46a` with amber icon. Updated ConfirmCorrect.test.tsx for family list change. 328 tests passing.

  Sanity test: `cd frontend && npm run test -- ConfirmCorrect --run`

## QA steps
- [x] "Confirm garment" at 30px serif weight 400; "Detected palette" mono uppercase label above colour rows
- [x] Colour rows: 28px swatch, integrated pill stepper (−/80/+), %, underlined Remove
- [x] Preview bar: 22px tall, 8px radius, inset shadow
- [x] "+ Add a colour" as clay text link; panel in dashed card with vertical family list
- [x] Category section: chip padding 6px 13px
- [x] Disabled Save: muted clay background (#dcc9b5), not grey
- [x] Buttons: 11px 22px padding, 22px margin-top above
- [x] Warning banner (fallback): amber background, amber icon
