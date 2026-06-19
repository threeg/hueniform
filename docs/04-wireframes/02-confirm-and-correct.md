# Screen 2 — Confirm-and-Correct

| | |
|---|---|
| **Route** | `/add/confirm` (after upload) — also entered from garment detail via *Regenerate* (FR-33) |
| **Realises** | FR-5 (measured swatch + family name), FR-27 (fallback warning), FR-28 (present proposal), FR-29 (adjust/remove/add, sum-to-100), FR-30 (no save without confirmed palette + category), FR-31 (mandatory category), FR-33 (regeneration variant) |
| **API** | `GET /api/detections/{token}/image` (preview) · `GET /api/taxonomy` (family **and category** pickers) · `POST /api/garments` (save) · `PUT /api/garments/{id}` (confirm regeneration) |
| **Mockup** | [`02-confirm-and-correct.html`](02-confirm-and-correct.html) |

> **Amended — v0.2.0.** The garment **type** picker becomes the **category** picker: the
> request/response field is `category` (was `type`) and the value is one of the expanded,
> region-grouped FR-16 categories (contract §1.3/§2.2), so the old segmented row of eight
> types is replaced by a **region-grouped picker** (Head / Upper body / Lower body / Feet).
> The save validation error is `invalid_category` (was `invalid_type`).

## Purpose

The safety net of the whole detection approach (brief §7): the proposed palette is presented for explicit confirmation, with correction tools, before anything is written to the database.

## Layout

Two columns:

- **Left — image preview.** The staged photograph from `GET /api/detections/{token}/image` (or, for regeneration, the stored photograph). Below it, the source filename is *not* shown (the contract does not return one); instead the image dimensions from the detection response may caption it.
- **Right — palette editor and save controls**, top to bottom:
  1. Fallback warning banner, only when `fallback_used` is `true` (FR-27).
  2. **Colour rows**, one per proposed colour in descending proportion: measured swatch (`hex`) + `family` name (FR-5), proportion stepper (numeric input with ±, integer 1–100), and a *Remove* control. A palette must keep 1–4 colours (FR-6): *Remove* is disabled on the last remaining colour, *Add* is hidden at four.
  3. **Stacked preview bar**: one 100 %-wide bar, segments sized by current proportions, live.
  4. **Live total**: "Total: 95 % — will be normalised to 100 % on save" whenever the sum ≠ 100 (FR-29: UI normalises on save; server only validates).
  5. **Add a colour**: opens an inline row with a family picker fed by `GET /api/taxonomy` — each option shows the family's `canonical` swatch and name — plus a proportion input. Choosing a family submits the canonical HSL for that family (contract §1.1).
  6. **Category picker**: the ~40 FR-16 categories **grouped by region** (Head / Upper body /
     Lower body / Feet), as selectable chips fed by `GET /api/taxonomy`; **none pre-selected**
     (FR-31); explicit choice required. (Replaces the v0.1.0 segmented row of eight types.)
  7. **Save garment** (primary; disabled until a category is chosen — FR-30) and **Cancel**.

## Behaviour

- Save sends `POST /api/garments` with `detection_token`, `category` and the normalised `colours` (`ColourIn`: `h`, `s`, `l`, `proportion` only — `family` is never sent; the server re-derives it, contract §1 rule 6).
- Manually added colours submit the family's canonical HSL exactly as returned by `GET /api/taxonomy`.
- Normalisation happens in the UI at save time: proportions are scaled and rounded to integers summing to exactly 100; the server answers `422 invalid_palette` otherwise.
- **Regeneration variant** (FR-33): entered from `POST /api/garments/{id}/regenerate`; identical screen, but the heading names the action, the photograph is the stored one, the **category** defaults to *unselected again* (FR-33 requires category selection to be part of the flow), and Save sends `PUT /api/garments/{id}` with `regeneration_token`. A `409 invalid_regeneration_token` (expired token) is surfaced as an error banner with a "Start regeneration again" action. (Note: a saved garment's category can also be changed directly on garment detail via `PATCH`, FR-46 — regeneration re-confirms category *and* palette together.)
- Cancel (or navigating away) abandons the staged detection — nothing was saved (FR-24, FR-30); a discard warning protects edits.
- Token lifetime: detections expire (`expires_at`, 1-hour TTL). An expired token on save returns `404 detection_not_found`, surfaced with a "Upload it again" action.

## States (in mockup order)

| State | Trigger |
|---|---|
| **Default proposal** | Arrival from a successful detection |
| **Fallback warning** | `fallback_used: true` (FR-27) |
| **Editing, sum ≠ 100** | User adjusted a stepper; live total + normalisation notice |
| **Manual add open** | "Add a colour" clicked; taxonomy family picker visible |
| **Ready to save** | Category chosen; Save enabled |
| **Save failed** (error) | `404 detection_not_found` (expired) or `422 invalid_category` / `invalid_palette` |
| **Regeneration variant** | Entered via FR-33; PUT instead of POST |

## Annotations (callouts in the mockup)

| # | Note |
|---|---|
| ① | Preview served from `GET /api/detections/{token}/image` (staging); for regeneration, the stored photograph. |
| ② | Each row: measured-colour swatch + family name — never the representative hue alone (FR-5). |
| ③ | Proportion stepper, integer 1–100; remove per colour; 1–4 colours enforced (FR-6, FR-29). |
| ④ | Live stacked bar previews the split; total line announces normalise-on-save when sum ≠ 100 (FR-29). |
| ⑤ | Family picker options come from `GET /api/taxonomy`: canonical swatch + name; submitting uses the canonical HSL (FR-29, contract §2.2). |
| ⑥ | Mandatory **category**, region-grouped FR-16 picker, none pre-selected (FR-31); Save disabled until chosen (FR-30). |
| ⑦ | Save = `POST /api/garments` (or `PUT /api/garments/{id}` with `regeneration_token` for FR-33) carrying `category`. Colours are submitted as `h`/`s`/`l`/`proportion` only; the server derives `family`. The validation error for a bad category is `invalid_category`. |
| ⑧ | Fallback warning per FR-27 — result may include background colour. |
