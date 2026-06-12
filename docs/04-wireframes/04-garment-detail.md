# Screen 4 — Garment Detail

| | |
|---|---|
| **Route** | `/garments/{id}` (sidebar: *Wardrobe* remains highlighted) |
| **Realises** | FR-25 (stored photograph displayed), FR-32 (no field editing), FR-33 (regenerate entry point), FR-34 (delete with confirmation) |
| **API** | `GET /api/garments/{id}` · `GET /api/garments/{id}/image` · `POST /api/garments/{id}/regenerate` · `DELETE /api/garments/{id}` |
| **Mockup** | [`04-garment-detail.html`](04-garment-detail.html) |

## Purpose

One garment in full: the photograph at usable size, the confirmed palette, and the only two lifecycle actions a saved garment has — regenerate and delete.

## Layout

- **"← Wardrobe"** link at the top, preserving the inventory's filter state.
- Two columns:
  - **Left** — the full photograph (`image_url`, original format — FR-25).
  - **Right** — top to bottom:
    1. Type as the heading (e.g. "Jersey").
    2. **Palette list**: one row per colour — swatch (`hex`), `family` name, `proportion` (FR-5). Plus the proportional palette strip for at-a-glance reading.
    3. **Dates**: "Added 12 June 2026" (`created_at`); "Colours regenerated 14 June 2026" only when `regenerated_at` is non-null.
    4. **Actions**: *Regenerate colours* and *Delete garment*.
- Deliberately **no edit control** — FR-32 says saved garments are not field-editable, and the wireframe makes that absence visible rather than accidental. A short caption under the actions explains: "Wrong colours? Regenerate re-detects them from the photograph."

## Behaviour

- **Regenerate** (FR-33): `POST /api/garments/{id}/regenerate` (no body). While the detection runs (&lt; 5 s, NFR-4) the button shows a pending state. The 200 response is a fresh proposal with a regeneration token; the UI enters confirm-and-correct (screen 2, state G). The stored record and image are untouched until that flow is confirmed; cancelling there leaves the garment exactly as it was.
- **Delete** (FR-34): opens a confirmation dialogue naming the garment by type and showing its thumbnail. Confirming sends `DELETE /api/garments/{id}`; on `204` the UI returns to the inventory with the card gone (record, photograph and thumbnail all removed). The dialogue's destructive button is visually distinct and not the default focus.
- `404 garment_not_found` (stale link) renders an inline message with a link back to the wardrobe.

## States (in mockup order)

| State | Trigger |
|---|---|
| **Default** | Garment loaded |
| **Delete confirmation** | *Delete garment* clicked (FR-34's confirmation step — a UI responsibility per contract §2.11) |
| **Regenerate pending** (loading) | `POST …/regenerate` in flight |
| **Not found** (error) | `404 garment_not_found` |

## Annotations (callouts in the mockup)

| # | Note |
|---|---|
| ① | Full stored photograph (`image_url`), original format (FR-25). |
| ② | Palette rows: measured swatch + family + proportion (FR-5); strip widths proportional. |
| ③ | `regenerated_at` line appears only when non-null. |
| ④ | Regenerate → detection on the stored photograph → confirm-and-correct (FR-33); same `id`, record replaced in place only on confirmation. |
| ⑤ | Delete requires explicit confirmation (FR-34); destructive action styled apart and not default-focused. |
| ⑥ | No edit affordance anywhere — the FR-32 rule embodied in the layout. |
