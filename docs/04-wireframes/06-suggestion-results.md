# Screen 6 — Suggestion Results

| | |
|---|---|
| **Route** | `/suggest` — the results area beneath the request panel (screen 5); one page in the application |
| **Realises** | FR-37 (per-slot thumbnail + palette, scheme, role explanation), FR-38 (explanation from the actual evaluation), FR-39 (up to 3, ranked), FR-40 (distinct), FR-41 (ranking surfaced as order), FR-42 (repeat may differ), FR-43 (fallback label; zero-results explanation + hint) |
| **API** | `POST /api/suggestions` — the 200 response shapes (combinations, fallback combinations, empty with `explanation` + `hint`) |
| **Mockup** | [`06-suggestion-results.html`](06-suggestion-results.html) |

## Purpose

Present up to three ranked combinations so the user can see at a glance *what* to wear and read *why* it works.

## Layout

One **stacked card per combination** (decision §6), best-first:

- **Card header**: rank ("Suggestion 1"), the scheme as a labelled chip ("Analogous scheme" — `scheme` mapped to a display name), and — when `fallback: true` — an additional **"Neutral-based fallback"** label visually distinct from the scheme chip (FR-43a: the UI must label these).
- **Slot row**: one tile per key present in `slots`, in a fixed wearing order (top, jersey, jacket, bottom, socks, shoes, hat, accessory — only the keys returned). Each tile: slot caption, garment thumbnail (`thumbnail_url`), proportional palette strip (FR-37). Tiles link to the garment's detail page.
- **Explanation**: the response's `explanation` string verbatim — it is rendered server-side from the actual evaluation (FR-38), so the UI must not paraphrase or truncate it.
- **Echo line**: when `echoes` is non-empty, a line per echo with the family's swatch: "Echo: Orange — hat ↔ socks" (from `family`, `from_slot`, `to_slot`). Shown as a supporting detail under the explanation (FR-11's bonus made visible).
- A **"Suggest again"** affordance after the last card — repeating an identical request may legitimately return different combinations (FR-42), so re-rolling is presented as a feature.

## States (in mockup order)

| State | Trigger |
|---|---|
| **Ranked results** | 200 with 1–3 combinations; mockup shows two, demonstrating that fewer than three is normal (FR-39) |
| **Fallback combination** | A card with `fallback: true` — neutral-based fallback label (FR-43a) |
| **Zero results** | 200 with `combinations: []` — `explanation` and `hint` rendered verbatim, plus the actions they imply (FR-43b) |

Loading and the 409 error are request-panel states (screen 5).

## Annotations (callouts in the mockup)

| # | Note |
|---|---|
| ① | Rank order is the response order — best first (FR-39, FR-41); no score numbers are shown, ranking is conveyed by position. |
| ② | Scheme chip from `scheme` (FR-13 names; FR-37). |
| ③ | Slot tile: caption, thumbnail, palette strip per `GarmentSummary` (FR-37); click-through to garment detail. |
| ④ | `explanation` verbatim — generated from the evaluation result, never canned (FR-38). |
| ⑤ | Echo line from the `echoes` array: family swatch + from/to slots (FR-11, FR-22). |
| ⑥ | `fallback: true` → "Neutral-based fallback" label (FR-43a). |
| ⑦ | Zero-results state renders `explanation` and `hint` verbatim, with follow-up actions (drop a slot / add a garment) (FR-43b). |
| ⑧ | "Suggest again" — identical requests may return different outfits (FR-42). |
