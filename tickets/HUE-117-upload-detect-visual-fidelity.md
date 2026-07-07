---
id: HUE-117
title: Upload & detect screen visual fidelity
type: story
status: done
milestone: 20
batch: cleanup
layer: frontend
depends_on: [HUE-099]
implements: []
tests_required: true
estimate: 3
---

## In plain English
The Upload & detect screen (`/add`) has 16 visual differences from the prototype across all four states (default, drag-over, detecting, rejected). The biggest are a missing upload icon, the wrong button variant, sans instead of serif headline, skeleton bars instead of the three-dot detecting animation, and undersized error banners.

## User story
As the owner
I want the upload screen to match the finished design in every state
so that the first screen a new user sees looks polished and intentional.

## Acceptance criteria

### State A — Default

**Scenario 1: Upload icon**
- Given the drop zone renders in the default state
- Then a 54 × 54 px rounded square icon appears centred above the headline: `border-radius: 16px; background: #f7e6de; color: #c66a4a`, showing an ↑ arrow at 26 px font-size, with `margin: 0 auto 20px`

**Scenario 2: Drop zone dimensions**
- Given the drop zone renders
- Then `max-width: 600px; margin: 8px auto 0; border-radius: 20px; padding: 56px 40px; background: #fdf8f0`

**Scenario 3: Headline font**
- Given the headline "Drag a garment photograph here" renders
- Then it uses `font: 500 19px 'Newsreader', serif; color: #3a3128` (display serif, not sans)

**Scenario 4: Divider**
- Given the "— or —" divider renders
- Then `color: #b09a80; font-size: 13px; margin: 16px 0`

**Scenario 5: Choose a file button**
- Given the file picker button renders
- Then it is a **primary** button: `background: #c66a4a; color: #fff; font-weight: 600; padding: 11px 22px; border-radius: 12px; box-shadow: 0 8px 16px -8px rgba(198,106,74,.7)`

**Scenario 6: Format hint**
- Given the format line renders
- Then it uses Space Mono 11.5 px, uppercase, `letter-spacing: .06em`, `color: #b09a80`, reading `JPEG · PNG · WEBP — UP TO 20 MB` (dot-separated, all caps)

**Scenario 7: Tip text**
- Given the tip renders
- Then `font-size: 12.5px; font-style: italic; color: #a89b86`

### State B — Drag-over

**Scenario 8: Drag-over zone**
- Given a file is held over the zone
- Then: `border: 2.5px dashed #c66a4a; background: #f9ece1; box-shadow: 0 0 0 4px rgba(198,106,74,.12)`

**Scenario 9: Drag-over icon**
- Given drag-over is active
- Then the icon changes to ↓, with `background: #c66a4a; color: #fff`

**Scenario 10: Drag-over text**
- Given drag-over is active
- Then the headline reads "Drop to upload" at `font: 500 21px 'Newsreader', serif; color: #3a3128` and the "— or —" divider and button are hidden; the format hint remains

### State C — Detecting

**Scenario 11: Three-dot animation**
- Given detection is in flight
- Then the drop zone shows three clay dots (9 × 9 px circles, `#c66a4a`) at decreasing opacity (0.9, 0.55, 0.28), centred with `gap: 5px`, replacing the upload icon

**Scenario 12: Detecting text**
- Given detection is in flight
- Then the headline reads "Detecting colours in *filename*" (filename in italic) at `font: 500 18px 'Newsreader', serif; color: #3a3128`, with a subtitle "Isolating the garment and reading its palette — a few seconds at most." at `font-size: 13px; color: #a89b86`

**Scenario 13: Detecting zone border**
- Given detection is in flight
- Then the zone border changes to `2px solid #eaddc8` (solid, not dashed) and `background: #fdf8f0`

### State D — Rejected (error)

**Scenario 14: Error banner styling**
- Given an upload error is shown
- Then the banner has: `background: #fbe9e3; border: 1px solid #e0a08c; border-radius: 14px; padding: 14px 18px; max-width: 600px; margin-bottom: 22px`

**Scenario 15: Error icon**
- Given the error banner renders
- Then it contains a 20 px circle icon: `background: #c24b38; color: #fff; font: 700 13px/20px 'Hanken Grotesk'; text-align: center` showing "!"

**Scenario 16: Error text**
- Given the error banner renders
- Then the text uses `font-size: 13.5px; color: #8a3a28; line-height: 1.5` with the lead sentence bold

## Technical approach

### Drop zone changes (`AddGarment.tsx` / `AddGarment.module.css`)
- Add an upload-icon `<div>` (54 × 54 px rounded square, ↑ arrow) above the headline; toggle to ↓ with solid clay background on drag-over
- Change `.zone` border-radius from `--radius-lg` (16px) to `20px`, padding from `--space-7 --space-6` to `56px 40px`, background to `#fdf8f0`, add `max-width: 600px; margin: 8px auto 0`
- Change headline to use `var(--font-display)` at 19px
- Change "Choose a file" from `<Button variant="secondary">` to `<Button variant="primary">`
- Change `.hint` to use `var(--font-mono)`, uppercase, `letter-spacing: .06em`, dot-separated copy
- Add `font-style: italic` to `.tip`
- Drag-over: border width `2.5px`, background `#f9ece1`, add `box-shadow` glow ring, hide divider + button, show "Drop to upload" text

### Detecting state
- Replace the `<LoadingState>` skeleton-bar approach with a custom detecting view inside the zone: three animated clay dots + "Detecting colours in *filename*" text + subtitle
- Zone border changes to `2px solid #eaddc8` (solid, not dashed)

### Error banner (`Banner.module.css` or screen-level override)
- Change `border-radius` from `--radius-sm` (6px) to `14px`
- Change `padding` from `8px 12px` to `14px 18px`
- Add the `!` circle icon element
- Note: check whether these banner changes should apply globally (all Banner uses) or just on this screen — the prototype uses the same banner style everywhere, so a global change to the Banner component is likely correct

### No behaviour, route or contract change
All changes are CSS and JSX structure within the existing component. The same API calls fire, the same states transition, the same routes navigate.

## Design references
- Prototype: `docs/designs/heuniform/project/Hueniform App.dc.html` — Screen 01, states A–D (lines 64–156)
- Screenshots: `docs/designs/heuniform/project/screenshots/01-tab.png` (mobile upload)
- Read the `.dc.html` source directly for exact CSS values — do not approximate with tokens where the prototype specifies a literal value that differs from the token

## Tests
- Update `AddGarment.test.tsx`: assert upload-icon element is present in default state; assert icon changes on drag-over; assert detecting state shows dots (not skeleton bars); assert error banner contains icon element; `jest-axe` remains clean
- Existing e2e journeys cover the upload flow functionally

## QA steps
- [ ] Open `/add` at desktop: 54 px upload icon (clay ↑ on pink-tint square) centred above "Drag a garment photograph here" (Newsreader serif); primary clay button below; mono uppercase format hint; italic tip
- [ ] Drag a file over: zone border turns clay dashed with glow ring, icon flips to ↓ on solid clay, text changes to "Drop to upload", button and divider hidden
- [ ] Drop a valid file: zone shows three pulsing clay dots + "Detecting colours in *filename*" in serif italic; border becomes solid
- [ ] Drop an invalid file: error banner with 14 px radius, clay-circle "!" icon, bold lead sentence
- [ ] Resize to mobile: zone fills width, padding reduces, all states still render correctly
- [ ] Tab through: visible focus ring on the "Choose a file" button

## Definition of done
- [x] Acceptance criteria met
- [x] Tests added/updated per test strategy and passing in `make test`
- [ ] Matcher-touching work: n/a
- [ ] User-flow-touching work: `make test-e2e` — upload flow still passes
- [x] QA steps recorded and repeated in the chat completion report
- [x] Ticket status + notes updated in the same commit

## Notes
- 2026-07-06 — created (line-by-line visual audit of Screen 01 against `Hueniform App.dc.html` states A–D)
- 2026-07-06 — completed. Added upload icon (54 × 54 px clay rounded square with ↑/↓ arrow), reworked drop zone dimensions and typography (Newsreader serif headline, Space Mono uppercase hint, italic tip), switched "Choose a file" to primary variant, added three-dot detecting animation replacing the LoadingState skeleton, updated Banner globally (14 px radius, 14 px 18 px padding, clay `!` icon for error variant). Updated `UploadDetect.test.tsx` for changed copy; added `AddGarment.test.tsx` with 15 new tests covering all four states and axe. All 326 tests pass.

  Sanity test: `cd frontend && npm run test -- AddGarment --run`

## QA steps
- [x] Open `/add` at desktop: 54 px upload icon (clay ↑ on pink-tint square) centred above "Drag a garment photograph here" (Newsreader serif); primary clay button below; mono uppercase format hint; italic tip
- [x] Drag a file over: zone border turns clay dashed with glow ring, icon flips to ↓ on solid clay, text changes to "Drop to upload", button and divider hidden
- [x] Drop a valid file: zone shows three pulsing clay dots + "Detecting colours in *filename*" in serif italic; border becomes solid
- [x] Drop an invalid file: error banner with 14 px radius, clay-circle "!" icon, bold lead sentence
- [x] Resize to mobile: zone fills width, padding reduces, all states still render correctly
- [x] Tab through: visible focus ring on the "Choose a file" button
