# Screen 4 — Garment Detail

| | |
|---|---|
| **Route** | `/garments/{id}` (sidebar: *Wardrobe* remains highlighted) |
| **Realises** | FR-25 (stored photograph displayed), FR-32 (amended — only the category is field-editable), FR-46 (direct category edit), FR-33 (regenerate entry point; palette regenerate-only), FR-34 (delete with confirmation) |
| **API** | `GET /api/garments/{id}` · `PATCH /api/garments/{id}` (category edit) · `POST /api/garments/{id}/regenerate` · `DELETE /api/garments/{id}` |
| **Mockup** | [`04-garment-detail.html`](04-garment-detail.html) |

> **Amended — v0.2.0 (F3).** A saved garment's **category** is now directly editable
> (FR-46, FR-32 as amended) via `PATCH /api/garments/{id}` — no re-detection, no
> confirm-and-correct flow, same `id` and palette. The category picker offers the expanded,
> region-grouped FR-16 categories (contract §2.2). The palette stays **regenerate-only**
> (FR-32/FR-33). The v0.1.0 "no field editing anywhere" caption is superseded.

## Purpose

One garment in full: the photograph at usable size, the confirmed palette, and the lifecycle
actions a saved garment has — **edit its category**, regenerate its colours, and delete it.

## Layout

- **"← Wardrobe"** link at the top, preserving the inventory's filter and order state.
- Two columns:
  - **Left** — the full photograph (`image_url`, original format — FR-25).
  - **Right** — top to bottom:
    1. **Category** as the heading (e.g. "Jumper"), with a small **Edit** affordance beside
       it (FR-46). Activating it opens the **category picker** in place: the ~40 FR-16
       categories **grouped by region** (Head / Upper body / Lower body / Feet), the current
       category pre-selected; **Save** and **Cancel**. Save sends `PATCH /api/garments/{id}`
       `{ "category": … }`; on `200` the heading updates in place. The `id`, photograph and
       palette are untouched, and `regenerated_at` is **not** changed (a category edit is not
       a regeneration — contract §2.10a).
    2. **Palette list**: one row per colour — swatch (`hex`), `family` name, `proportion`
       (FR-5). Plus the proportional palette strip for at-a-glance reading.
    3. **Dates**: "Added 12 June 2026" (`created_at`); "Colours regenerated 14 June 2026"
       only when `regenerated_at` is non-null.
    4. **Actions**: *Regenerate colours* and *Delete garment*.
- A short caption under the actions explains the editing model now that it has two halves:
  "The **category** is editable above. The **colours** are regenerate-only — *Regenerate*
  re-detects them from the photograph." (FR-32 amended, FR-33, FR-46.)

## Behaviour

- **Edit category** (FR-46): inline picker → `PATCH /api/garments/{id}` with the single
  `category` field. The picker only offers valid FR-16 categories, so `422 invalid_category` /
  `invalid_request` are unreachable from the UI; a `404 garment_not_found` (stale link)
  surfaces inline. Suggestion eligibility then follows the new category and its slot role
  (FR-49–FR-51) at the next request. The palette and `regenerated_at` are unchanged.
- **Regenerate** (FR-33): `POST /api/garments/{id}/regenerate` (no body). While detection runs
  (< 5 s, NFR-4) the button shows a pending state. The 200 response is a fresh proposal with a
  regeneration token; the UI enters confirm-and-correct (screen 2, regeneration variant). The
  stored record and image are untouched until that flow is confirmed; cancelling leaves the
  garment exactly as it was. (This is the **only** path that changes the palette.)
- **Delete** (FR-34): opens a confirmation dialogue naming the garment by category and showing
  its thumbnail. Confirming sends `DELETE /api/garments/{id}`; on `204` the UI returns to the
  inventory with the card gone. The destructive button is visually distinct and not the
  default focus.
- `404 garment_not_found` (stale link) renders an inline message with a link back to the wardrobe.

## States (in mockup order)

| State | Trigger |
|---|---|
| **Default** | Garment loaded |
| **Category edit** | *Edit* clicked — region-grouped category picker open (FR-46) |
| **Delete confirmation** | *Delete garment* clicked (FR-34) |
| **Regenerate pending** (loading) | `POST …/regenerate` in flight |
| **Not found** (error) | `404 garment_not_found` |

## Annotations (callouts in the mockup)

| # | Note |
|---|---|
| ① | Full stored photograph (`image_url`), original format (FR-25). |
| ② | Palette rows: measured swatch + family + proportion (FR-5); strip widths proportional. |
| ③ | `regenerated_at` line appears only when non-null; a category edit does **not** set it (contract §2.10a). |
| ④ | **Edit category** (FR-46): inline region-grouped FR-16 picker → `PATCH /api/garments/{id}`; same `id`, palette and photograph; no re-detection. |
| ⑤ | Regenerate → detection on the stored photograph → confirm-and-correct (FR-33); the **only** way to change the palette. |
| ⑥ | Delete requires explicit confirmation (FR-34); destructive action styled apart and not default-focused. |
| ⑦ | Editing model caption: category editable here; colours regenerate-only (FR-32 amended, FR-46, FR-33). |
