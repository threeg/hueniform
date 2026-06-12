# Screen 5 — Outfit Request

| | |
|---|---|
| **Route** | `/suggest` (sidebar: *Suggest outfit*) — one page with the results (screen 6) rendered beneath this panel |
| **Realises** | FR-17 (required slots always included), FR-36 (optional slot choice; fail fast on empty slots) |
| **API** | `POST /api/suggestions` — request body and the `409 empty_slots` error |
| **Mockup** | [`05-outfit-request.html`](05-outfit-request.html) |

## Purpose

Compose the request: which optional slots should this outfit include? The panel stays visible above the results (decision §6) so slots can be tweaked and the request repeated without navigation.

## Layout

A single **request panel**:

- **Always included** row: Top, Bottom, Socks, Shoes shown as fixed, non-interactive chips with a lock glyph — making FR-17 visible rather than implicit.
- **Optional slots** row: four toggle chips — Jersey, Jacket, Hat, Accessory — all off by default. Jersey and jacket may both be on (brief §5). The chip label is "Accessory", matching the slot key and garment type (`accessory`, contract §1 rule 3).
- **Suggest outfits** button (primary), always enabled — a request with no optional slots is valid.
- A one-line hint: "Top, bottom, socks and shoes are always included."

## Behaviour

- The button sends `POST /api/suggestions` with `include` built from the toggles, e.g. `{ "include": { "jersey": true, "jacket": false, "hat": true, "accessory": false } }`. Omitted keys default to `false`, but the UI always sends all four explicitly.
- **Loading**: results area shows a searching message; NFR-5 bounds the response under 2 s at 500 garments. The panel is inert while in flight.
- **`409 empty_slots`** (FR-36, fail fast): the envelope `message` is rendered in an error banner directly below the panel, and the offending toggle chip(s) — from `details.empty_slots` — are highlighted with an inline "none in wardrobe" marker. The user can untick the slot or follow the "Add a garment" link.
  - The 409 can also name a **required** slot (e.g. no shoes in the wardrobe yet); the banner is the same, but there is no toggle to untick — the inline link to *Add garment* is the way out.
- **200** responses (combinations, fallback, or zero results) belong to screen 6.

## States (in mockup order)

| State | Trigger |
|---|---|
| **Default** | Page open; no optional slots selected |
| **Slots selected** | Jersey + hat on; ready to request |
| **Searching** (loading) | Request in flight (&lt; 2 s, NFR-5) |
| **Empty slot** (error) | `409 empty_slots`; message verbatim, offending chip flagged |

## Annotations (callouts in the mockup)

| # | Note |
|---|---|
| ① | Required slots fixed and visibly locked (FR-17). |
| ② | Optional slot toggles; jersey and jacket can both be selected (brief §5, FR-36). All four keys are sent explicitly in `include`. |
| ③ | Always-enabled request button — required slots alone are a valid request. |
| ④ | Fail-fast banner shows the `409 empty_slots` envelope `message` verbatim; `details.empty_slots` drives the per-chip flag (FR-36). |
