# Screen 6 — Suggestion Results

| | |
|---|---|
| **Route** | `/suggest` — the results area beneath the request panel (screen 5); one page in the application |
| **Realises** | FR-37 (per-slot thumbnail + palette, scheme, role explanation), FR-38 (explanation from the actual evaluation), FR-39 (up to *N*, ranked), FR-40 (distinct), FR-41 (ranking order; **first-class neutral-based**), FR-42 (repeat may differ), FR-43 (**neutral fallback** label; zero-results explanation + hint), FR-48 (count shown) |
| **API** | `POST /api/suggestions` — the 200 response shapes (`requested_count`, `combinations`, `scheme`/`fallback`, `echoes`, `explanation`; empty with `explanation` + `hint`) |
| **Mockup** | [`06-suggestion-results.html`](06-suggestion-results.html) |

> **Amended — v0.2.0 (Milestone 11), reworked in the Milestone 12 session.** Slot captions use
> the new slot keys/labels (incl. **Mid-layer**, **Outer layer**); the results header shows the
> count (`requested_count`, FR-48); a **first-class neutral-based** outfit (`scheme:
> "neutral-based"`, `fallback: false`) is distinguished from a **neutral fallback**
> (`fallback: true`); `echoes` may include **minor-adornment** echoes. Supersedes the v0.1.0
> "up to 3" / `scheme: null` neutral handling.

## Purpose

Present up to *N* ranked combinations so the user can see at a glance *what* to wear and read
*why* it works.

## Layout

- **Results header** — a single line above the cards: how many combinations are shown against
  the count requested, e.g. "3 outfits" or "Showing 2 of 3 you asked for" (`combinations`
  length vs `requested_count`, FR-48/FR-39). Fewer than requested is normal, not an error.
- One **stacked card per combination** (decision §6), best-first:
  - **Card header**: rank ("Suggestion 1"); the scheme as a labelled chip (`scheme` mapped to
    a display name — "Analogous scheme", "Neutral-based scheme", …); and — **only when
    `fallback: true`** — an additional, visually distinct **"Neutral fallback"** label
    (FR-43a). A **first-class neutral-based** outfit (`scheme: "neutral-based"`, `fallback:
    false`) shows the scheme chip **alone**, exactly like any chromatic scheme (FR-41); the
    `scheme` + `fallback` pair is what separates the two neutral cases (contract §2.12).
  - **Slot row**: one tile per key present in `slots`, in a fixed wearing order — `hat`,
    `base`, `shirt`, `mid`, `outer`, `tie`, `scarf`, `lower_body`, `belt`, `socks`, `shoes`,
    then minor adornments (`necklace`, `watch`, `ring`, `bracelet`, `glasses`, `earrings`) —
    only the keys returned. A **one-piece** appears once under `lower_body` (no separate
    `base` tile). Each tile: slot caption (the slot's display label), garment thumbnail
    (`thumbnail_url`), proportional palette strip (FR-37). **No garment names** — identity is
    thumbnail + palette + the slot/category label, as on inventory cards. Tiles link to the
    garment's detail page.
  - **Explanation**: the response's `explanation` string **verbatim** — rendered server-side
    from the actual evaluation (FR-38), so the UI must not paraphrase or truncate it.
  - **Echo line**: when `echoes` is non-empty, a line per echo with the family's swatch:
    "Echo: Orange — Hat ↔ Socks" (from `family`, `from_slot`, `to_slot`, mapped to slot
    labels). Includes **minor-adornment** echoes (e.g. a necklace echoing an anchor) now that
    those are credited (FR-11, FR-22).
- A **"Suggest again"** affordance after the last card — repeating an identical request may
  legitimately return different combinations (FR-42), so re-rolling is presented as a feature.

## States (in mockup order)

| State | Trigger |
|---|---|
| **Ranked results** | 200 with 1–*N* combinations; mockup shows two (a chromatic scheme and a **first-class neutral-based** card), demonstrating both the distinction and that fewer than the requested count is normal (FR-39, FR-41) |
| **Neutral fallback** | A card with `fallback: true` — the "Neutral fallback" label is mandatory (FR-43a) |
| **Zero results** | 200 with `combinations: []` — `explanation` and `hint` rendered verbatim, plus the actions they imply (FR-43b); also the unsatisfiable-pin / -anchor / -constraint outcome (FR-44/FR-45/FR-52) |

Loading and the 409 error are request-panel states (screen 5).

## Annotations (callouts in the mockup)

| # | Note |
|---|---|
| ① | Rank order is the response order — best first (FR-39, FR-41); no score numbers, ranking is conveyed by position. |
| ② | Scheme chip from `scheme` (FR-13 names; FR-37). A first-class `neutral-based` outfit shows this chip alone (FR-41). |
| ③ | Slot tile: caption (slot label), thumbnail, palette strip per `GarmentSummary` (FR-37); no names; click-through to garment detail. |
| ④ | `explanation` verbatim — generated from the evaluation result, never canned (FR-38). |
| ⑤ | Echo line from the `echoes` array: family swatch + from/to slot labels, incl. minor-adornment echoes (FR-11, FR-22). |
| ⑥ | `fallback: true` → "Neutral fallback" label, visually distinct from the scheme chip (FR-43a). Absent on first-class neutral-based. |
| ⑦ | Zero-results state renders `explanation` and `hint` verbatim, with follow-up actions (drop/widen a slot / add a garment) (FR-43b, FR-52). |
| ⑧ | "Suggest again" — identical requests may return different outfits (FR-42). |
| ⑨ | Results header shows combinations returned against `requested_count` (FR-48, FR-39). |
