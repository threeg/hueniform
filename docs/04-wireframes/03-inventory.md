# Screen 3 — Inventory Browser

| | |
|---|---|
| **Route** | `/` (sidebar: *Wardrobe*; the home page) |
| **Realises** | FR-35 (thumbnails, palette swatches, type; combinable type AND family filters), NFR-6 (responsive at 500 garments) |
| **API** | `GET /api/garments?type=&family=&limit=&offset=` · thumbnails via each garment's `thumbnail_url` |
| **Mockup** | [`03-inventory.html`](03-inventory.html) |

## Purpose

The browsable wardrobe (brief goal 2). Also the application's home page and the entry point to garment detail.

## Layout

- **Filter bar** across the top:
  - **Type** dropdown: *All types* + the eight FR-16 types.
  - **Colour family** dropdown: *All colours* + the 19 families from `GET /api/taxonomy`, each option showing the family's canonical swatch and name (decision §6). A garment matches if the family appears in **any** of its colours, regardless of role (FR-35).
  - **Clear filters** link, visible only when a filter is active.
  - **Result count** at the right: "137 garments" (from the response's `total`).
- **Card grid** beneath: one card per `GarmentSummary` — thumbnail (`thumbnail_url`), palette strip (swatches in `position` order, widths proportional to `proportion`), capitalised type label. Cards are uniform; roughly 5 per row at 1280 px. Clicking a card opens `/garments/{id}`.
- A primary **Add garment** shortcut appears in the empty-wardrobe state.

## Behaviour

- Filters are combinable as AND and map directly to the contract's query parameters: `GET /api/garments?type=jersey&family=Teal`.
- Default `limit` 500 means a full wardrobe arrives in one response (contract §2.6); filter changes re-query and must reflect in under 1 second at 500 garments (NFR-6 — TanStack Query caching per architecture §2.5 makes repeat filters memory-fast).
- Filter state is reflected in the URL query so detail → back preserves it (overview §2).
- `422 invalid_filter` is unreachable via these dropdowns; if it occurs, the envelope message shows in an error banner.

## States (in mockup order)

| State | Trigger |
|---|---|
| **Default grid** | Wardrobe with garments, no filters |
| **Filtered** | Type AND family active; count updated; clear-filters visible |
| **Empty wardrobe** | `total: 0`, no filters — call to action to add the first garment |
| **Empty filter result** | `total: 0` with filters — offers to clear them |
| **Loading** | Skeleton cards while the query runs |
| **Load failure** (error) | Request failed; envelope message + retry |

## Annotations (callouts in the mockup)

| # | Note |
|---|---|
| ① | Type AND colour-family filters, combinable (FR-35); they map 1:1 to `type` / `family` query parameters. |
| ② | Family options show the canonical swatch from `GET /api/taxonomy`; matching is against any colour of the garment, any role (FR-35). |
| ③ | Count from the response's `total`; updates with every filter change in &lt; 1 s at 500 garments (NFR-6). |
| ④ | Card = thumbnail + proportional palette strip + type (FR-35). Thumbnails are pre-generated WebP (architecture §3.1) so the grid stays responsive. |
| ⑤ | Card click → garment detail (`/garments/{id}`); filters survive the round trip. |
