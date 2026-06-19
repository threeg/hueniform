# Screen 3 — Inventory Browser

| | |
|---|---|
| **Route** | `/` (sidebar: *Wardrobe*; the home page) |
| **Realises** | FR-35 (thumbnails, palette swatches, category; combinable category AND family filters), FR-47 (grouped by category; hue or date-added ordering), NFR-6 (responsive at 500 garments) |
| **API** | `GET /api/garments?category=&family=&order=hue|date&limit=&offset=` · thumbnails via each garment's `thumbnail_url` |
| **Mockup** | [`03-inventory.html`](03-inventory.html) |

> **Amended — v0.2.0 (F6).** The filter field `type` is renamed **`category`** (the expanded
> FR-16 set, contract §1.3/§2.6); garments are now **grouped by category** with a within-group
> **order** toggle — **hue** (a colour spectrum, default) or **date added** (newest first),
> neutrals ordered after the chromatic spectrum (FR-47, contract §2.6). The existing
> category/family filters are retained (FR-35).

## Purpose

The browsable wardrobe (brief goal 2). Also the application's home page and the entry point to
garment detail.

## Layout

- **Filter / sort bar** across the top:
  - **Category** dropdown: *All categories* + the FR-16 categories, **grouped by region**
    (Head / Upper body / Lower body / Feet) in the menu so the long list stays scannable.
    *(Renamed from "Type"; maps to the `category` query parameter.)*
  - **Colour family** dropdown: *All colours* + the 20 families from `GET /api/taxonomy`, each
    option showing the family's canonical swatch and name. A garment matches if the family
    appears in **any** of its colours, regardless of role (FR-35).
  - **Order** control *(new — FR-47)*: a segmented toggle **Hue** (default) · **Date added**.
    *Hue* arranges each group as a colour spectrum by the garment's primary-colour hue (FR-7),
    with neutral-primary garments after the chromatic spectrum; *Date added* is newest-first.
    Maps to the `order` query parameter (`hue` | `date`).
  - **Clear filters** link, visible only when a filter is active.
  - **Result count** at the right: "137 garments" (from the response's `total`).
- **Grouped card grid** beneath: garments are shown in **per-category groups**, each with a
  small **group header** naming the category and its count ("Jumper · 12"). The contract
  returns a flat list already ordered by category then the chosen `order` key (contract §2.6),
  so the client groups by walking the list. Within a group the cards follow the chosen order.
- **Card**: one per `GarmentSummary` — thumbnail (`thumbnail_url`), palette strip (swatches in
  `position` order, widths proportional to `proportion`), capitalised **category** label. No
  garment names (identity is thumbnail + palette + category). Cards are uniform; clicking a
  card opens `/garments/{id}`.
- A primary **Add garment** shortcut appears in the empty-wardrobe state.

## Behaviour

- Filters combine as AND and map directly to the contract's query parameters:
  `GET /api/garments?category=jumper&family=Teal&order=hue`.
- Changing **Order** re-queries with the new `order` value; the grouping (by category) is
  unaffected, only the within-group sequence changes.
- Default `limit` 500 means a full wardrobe arrives in one response (contract §2.6); filter and
  order changes re-query and must reflect in under 1 second at 500 garments (NFR-6 — TanStack
  Query caching makes repeat views memory-fast). The grouped/ordered view continues to meet
  NFR-6.
- Filter and order state is reflected in the URL query so detail → back preserves it (overview §2).
- `422 invalid_filter` (unknown `category`, `family` or `order`) is unreachable via these
  controls; if it occurs, the envelope message shows in an error banner.

## States (in mockup order)

| State | Trigger |
|---|---|
| **Default grid (grouped, hue)** | Wardrobe with garments, no filters, `order=hue` — category group headers; within each group, the hue spectrum with neutrals last |
| **Order: date added** | `order=date` — same grouping, within-group newest-first |
| **Filtered** | Category AND family active; count updated; clear-filters visible |
| **Empty wardrobe** | `total: 0`, no filters — call to action to add the first garment |
| **Empty filter result** | `total: 0` with filters — offers to clear them |
| **Loading** | Skeleton cards while the query runs |
| **Load failure** (error) | Request failed; envelope message + retry |

## Annotations (callouts in the mockup)

| # | Note |
|---|---|
| ① | Category AND colour-family filters, combinable (FR-35); they map 1:1 to `category` / `family` query parameters. The category menu is region-grouped (FR-16). |
| ② | Family options show the canonical swatch from `GET /api/taxonomy`; matching is against any colour of the garment, any role (FR-35). |
| ③ | **Order** toggle (FR-47): Hue (spectrum, default) or Date added (newest first); maps to `order=hue|date`. |
| ④ | Per-category **group header** with count; the flat ordered list (contract §2.6) is bucketed by `category` client-side. |
| ⑤ | Within a group, **hue** orders as a spectrum by primary-colour hue; **neutral-primary** garments come after the chromatic spectrum, in a stable order (FR-47). |
| ⑥ | Card = thumbnail + proportional palette strip + category; no names. Thumbnails are pre-generated WebP so the grid stays responsive (NFR-6). |
| ⑦ | Card click → garment detail (`/garments/{id}`); filters and order survive the round trip. |
