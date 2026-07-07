---
id: HUE-120
title: Garment detail screen visual fidelity
type: story
status: todo
milestone: 20
batch: cleanup
layer: frontend
depends_on: [HUE-102, HUE-115]
implements: []
tests_required: true
estimate: 3
---

## In plain English
Line-by-line audit of the Garment detail screen (`/garments/{id}`) against the prototype. The palette display, back link, category edit panel, delete dialog and action hint all have styling gaps.

## User story
As the owner
I want the garment detail to match the prototype in every state
so that viewing, editing and deleting a garment feels polished.

## Acceptance criteria — gaps found

### State A — Default detail
1. **Back link** — design: `font-size: 13px; color: #c66a4a; text-decoration: underline` "← Wardrobe". Current: `--text-sm`, `--color-ink-secondary`, no underline by default. **Fix:** clay colour, underline.
2. **"Edit category" link** — design: `font-size: 12.5px; color: #c66a4a; text-decoration: underline` inline after the heading. Current: a button with `--radius-md` border. **Fix:** restyle to underlined clay link (matching the prototype's casual inline style).
3. **Image dimensions** — design: `width: 360px; height: 320px`. Current: `width: 100%` with no fixed height. **Check** — may need a fixed height or aspect ratio at desktop.
4. **"Palette" label** — design: `font: 400 11px 'Space Mono', monospace; letter-spacing: .14em; text-transform: uppercase; color: #a89b86; margin-bottom: 10px`. Current: check if present.
5. **Palette rows** — design: `24×24px swatch; border-radius: 7px; gap: 13px; padding: 9px 0; max-width: 360px`. Current: swatch renders via shared component. **Check** sizes and spacing.
6. **Palette strip** — design: `height: 16px; border-radius: 6px; max-width: 360px; margin: 14px 0 6px; box-shadow: inset 0 0 0 1px rgba(0,0,0,.08)`. Current: `height={16}` ✓ but check radius and inset shadow.
7. **Date line** — design: `font: 400 12px 'Space Mono', monospace; color: #a89b86; margin: 14px 0 22px`. Current: `--text-sm`, `--color-ink-muted`. **Check** font family.
8. **Action buttons** — design: both are `padding: 10px 20px; border-radius: 12px` with white bg + border. Delete has `border: 1px solid #e0a08c; color: #a33527`. Current: Button secondary + destructive variants. **Check** exact colours.
9. **Action hint text** — design: `font-size: 12.5px; color: #a89b86; max-width: 380px` with bold "Regenerate". Current: `--text-sm`, `--color-ink-muted`. **Check.**

### State B — Category edit
10. **Edit panel** — design: `420px; border: 1px solid #ecdcc7; border-radius: 16px; background: #fff; box-shadow: 0 14px 34px -18px rgba(120,70,40,.4); overflow: hidden` with header ("Change category", bold, `padding: 12px 18px; border-bottom`) + scrollable body + footer with Save/Cancel. Current: inline picker with `--radius-md` (12px), `--color-surface` bg, no shadow, no header/footer structure. **Fix:** restructure to match the panel-with-header design.
11. **"Editing…" label** — design: `font-size: 12.5px; color: #a89b86; font-style: italic` replacing "Edit category" when in edit mode. Current: check.

### State C — Delete confirmation dialog
12. **Dialog background** — design: `background: #fbf6ee; border-radius: 18px; padding: 26px 28px; width: 440px; box-shadow: 0 24px 60px rgba(60,40,20,.4)`. Current: `--color-surface-raised`, `--radius-lg` (16px), `--space-6` (32px) padding, `max-width: 360px`, `--shadow-lg`. **Fix:** width 440px (not 360px), border-radius 18px (not 16px), padding 26px 28px, stronger shadow.
13. **Dialog heading** — design: `font: 400 22px 'Newsreader', serif; color: #3a3128`. Current: `--text-lg` (18px), `--weight-semibold`. **Fix:** 22px, weight 400.
14. **Dialog garment preview** — design shows a row with thumbnail (64×52px, 8px radius) + mini palette bar (44px tall, 60px wide, 6px radius) + text ("Jumper · teal / orange / Added 12 Jun") in a white bordered card (`padding: 12px; background: #fff; border: 1px solid #f0e2d0; border-radius: 12px`). Current: thumbnail (80×80px, 12px radius). **Fix:** match the compact row layout.
15. **Cancel button** — design: `border: 1.5px solid #c66a4a` (clay border, not the default border colour). Current: secondary variant. **Fix:** add clay border.

### State D — Regenerate pending
16. **Inline "Re-detecting" button** — design: shows a disabled-looking button with "Re-detecting colours ···" inside (`background: #fff; border: 1px solid #e2d3bf; color: #a89b86; opacity: .75`). Current: check if this state matches.
17. **Inert hint text** — design: `font-size: 12.5px; color: #a89b86; max-width: 400px` explaining all actions are inert. Current: check.

### State E — Not found
18. **Not found** — design: centred card, `font: 400 24px 'Newsreader', serif` "Garment not found", subtext at 14px, primary CTA "Back to the wardrobe". Current: check layout and styling.

## Technical approach
- Category edit panel is the biggest structural change: header/body/footer card with shadow
- Delete dialog: adjust dimensions, heading, preview row layout
- Back link and Edit category: restyle to clay underlined links
- Read prototype lines 657–798 for exact values
- No behaviour, route or contract change

## Design references
- Prototype: `docs/designs/heuniform/project/Hueniform App.dc.html` — Screen 04, states A–E (lines 657–798)

## Tests
- Update `GarmentDetail.test.tsx` for DOM changes; `jest-axe` clean

## QA steps
- [ ] Default: clay underlined "← Wardrobe" and "Edit category" links; "Palette" mono label; 24px swatches; 16px strip
- [ ] Category edit: panel with header "Change category", scrollable body, Save/Cancel footer, shadow
- [ ] Delete dialog: 440px wide, 18px radius, 22px serif heading, compact preview row with palette bar
- [ ] Regenerate pending: inert buttons with "Re-detecting colours ···" text
- [ ] Not found: centred, serif heading, primary CTA

## Definition of done
- [x] Acceptance criteria met
- [x] Tests added/updated and passing in `make test`
- [ ] Matcher-touching work: n/a
- [x] QA steps recorded
- [x] Ticket status + notes updated in the same commit

## Notes
- 2026-07-06 — created (line-by-line audit of Screen 04 against prototype)
