# Hueniform — Wireframes: Overview, Navigation and Conventions

| | |
|---|---|
| **Document** | Wireframes index (Milestone 4) |
| **Status** | Draft for approval |
| **Date** | 12 June 2026 |
| **Source** | Approved brief, requirements (`docs/02-requirements.md`), architecture (`docs/03-architecture.md`) and API contract (`docs/03-api-contract.md`) plus interview decisions (§6) |
| **Repository location** | `docs/04-wireframes/00-overview.md` |

These wireframes are **low-to-mid fidelity**: they specify structure, content and states, not final visual design. Spacing, typography and colour of the chrome are placeholders; only the **swatches and palette elements show real colour**, because colour is the application's subject matter and greyscaling it would hide the content. The API contract (`docs/03-api-contract.md`) is authoritative for every field a screen displays or submits; no screen invents data the contract does not provide. Desktop only — no mobile layout (NFR-7).

> **v0.2.0 amendment note (Milestone 12).** Screens **5 (outfit request)** and **6
> (suggestion results)** are **rewritten** to the new slot model — configurable/removable
> slots over four regions with the mandatory lower-body floor, pins, colour/scheme anchor,
> a suggestion count, the count and the first-class-neutral vs neutral-fallback labels, and
> a **per-category slot constraint** (FR-52). Screen **3 (inventory)** gains category
> grouping + hue/date ordering (FR-47) and the `type`→`category` filter rename. Screen **4
> (garment detail)** gains the direct **category edit** (FR-46, `PATCH`). Screen **2
> (confirm-and-correct)** replaces the eight-type segmented picker with the region-grouped,
> ~40-category FR-16 picker (`category`, `invalid_category`). The upper-body layer slots are
> labelled **Base / Shirt / Mid-layer / Outer layer** (keys `base`/`shirt`/`mid`/`outer`).
> Garments carry **no name** — identity is always thumbnail + palette + category. Superseded
> v0.1.0 shapes are noted in each screen's own file; this index reflects the v0.2.0 state.

---

## 1. Screen index

| # | Screen | Files | Realises | API surface |
|---|---|---|---|---|
| 1 | Upload & detect | [`01-upload-detect.md`](01-upload-detect.md) · [HTML](01-upload-detect.html) | FR-23, FR-24, FR-26, FR-27 | `POST /api/detections` |
| 2 | Confirm-and-correct | [`02-confirm-and-correct.md`](02-confirm-and-correct.md) · [HTML](02-confirm-and-correct.html) | FR-5, FR-27–FR-31 (category), FR-33 | `GET /api/detections/{token}/image`, `GET /api/taxonomy`, `POST /api/garments`, `PUT /api/garments/{id}` |
| 3 | Inventory browser | [`03-inventory.md`](03-inventory.md) · [HTML](03-inventory.html) | FR-35, **FR-47**, NFR-6 | `GET /api/garments?category=&family=&order=hue\|date`, `GET /api/garments/{id}/thumbnail` |
| 4 | Garment detail | [`04-garment-detail.md`](04-garment-detail.md) · [HTML](04-garment-detail.html) | FR-32 (amended), **FR-46**, FR-33, FR-34 | `GET /api/garments/{id}`, **`PATCH /api/garments/{id}`**, `POST /api/garments/{id}/regenerate`, `DELETE /api/garments/{id}` |
| 5 | Outfit request | [`05-outfit-request.md`](05-outfit-request.md) · [HTML](05-outfit-request.html) | **FR-36, FR-44, FR-45, FR-48, FR-49–FR-52** | `POST /api/suggestions` (`slots`/`pins`/`anchor`/`count`; `409 empty_slots`, `422 invalid_request`) |
| 6 | Suggestion results | [`06-suggestion-results.md`](06-suggestion-results.md) · [HTML](06-suggestion-results.html) | FR-37–FR-43, **FR-48** | `POST /api/suggestions` (response shapes) |

Screens 5 and 6 are **one page** in the application (decision §6): the slot-selection panel stays visible at the top and results render beneath it. They are documented separately because their states and contract surfaces are distinct.

**Design-handoff briefs** *(v0.2.0)* — self-contained per-screen briefs for the visually-rich
screens, giving Design the states, contract-bound fields, copy, hard constraints and an
explicit "must NOT change" list: [`HANDOFF-05-outfit-request.md`](HANDOFF-05-outfit-request.md)
and [`HANDOFF-03-inventory.md`](HANDOFF-03-inventory.md).

---

## 2. Navigation structure

A **fixed left sidebar** is present on every screen (decision §6), containing the wordmark and three top-level sections:

| Sidebar item | Route | Screen(s) |
|---|---|---|
| **Wardrobe** (home) | `/` | Inventory browser; garment detail at `/garments/{id}` |
| **Add garment** | `/add` | Upload & detect, then confirm-and-correct at `/add/confirm` |
| **Suggest outfit** | `/suggest` | Outfit request + suggestion results (one page) |

Rules:

1. The application opens on **Wardrobe** (`/`).
2. **Garment detail** is reached only by clicking a card in the inventory; it highlights *Wardrobe* in the sidebar and offers a "← Wardrobe" link preserving any active filters.
3. **Confirm-and-correct** is reached two ways — after a successful upload from *Add garment*, or after *Regenerate* from garment detail (FR-33). It highlights the sidebar section it was launched from. It is never a sidebar destination itself: with no pending detection token there is nothing to confirm.
4. Leaving confirm-and-correct without saving abandons the staged detection (nothing was written — FR-24, FR-30, architecture §3.3); the UI warns before discarding edits.
5. **Build around this** (FR-44): garment detail and inventory cards offer an action that navigates to **Suggest outfit** (`/suggest`) with the garment pre-pinned to its slot; the request panel opens with the pin already applied (screen 5).

---

## 3. Shared layout

Every screen renders inside the same frame, 1024 px minimum width (desktop only, NFR-7):

```
┌──────────┬──────────────────────────────────────────────┐
│ Hueniform│  Page title                                  │
│          │                                              │
│ Wardrobe │  Page content                                │
│ Add      │                                              │
│ garment  │                                              │
│ Suggest  │                                              │
│ outfit   │                                              │
└──────────┴──────────────────────────────────────────────┘
  sidebar     main column, max-width ~1100 px
  190 px
```

### Shared components

| Component | Used by | Definition |
|---|---|---|
| **Swatch** | all screens | A small square filled with the colour's `hex` (derived from measured HSL — FR-5), 1 px outline so pale colours stay visible on white. Always paired with the `family` name and, where space allows, the `proportion`. Never shows the representative hue alone (FR-5). |
| **Palette strip** | inventory, detail, results | The garment's 1–4 swatches in `position` order (descending proportion), each swatch's width proportional to its `proportion`. |
| **Garment card** | inventory, results slots, pin chips/picker | Thumbnail (`thumbnail_url`), palette strip, **category** label. In results, a slot caption is added above. Garments have **no name** — identity is thumbnail + palette + category (F3 defers metadata). |
| **Error banner** | all screens | Red-tinted banner rendering the error envelope's `message` verbatim — the contract guarantees it is plain language fit to show the user (contract §1.3). Never shows the machine `code`. |
| **Warning banner** | confirm-and-correct | Amber-tinted banner for the `fallback_used` warning (FR-27). |
| **Loading state** | all screens | Skeleton blocks or an inline "…" progress row; no spinner imagery is specified at this fidelity. |

### Category and slot labels

Garment `category` values are the expanded FR-16 identifiers (contract §1.3). The UI capitalises/humanises them for display (`t_shirt` → "T-shirt", `track_top` → "Track top"); the API identifier is always what is submitted. **Slot keys** are a separate namespace (contract §1.3a) with their own display labels — notably the upper-body layers `base`/`shirt`/`mid`/`outer` shown as **Base / Shirt / Mid-layer / Outer layer**. Category pickers (screens 2, 4) and the slot selector (screen 5) are **grouped by region** (Head / Upper body / Lower body / Feet).

---

## 4. Mockup conventions

1. Each screen has a Markdown specification (`NN-name.md`) and a static HTML mockup (`NN-name.html`). The Markdown is the specification of record; the HTML illustrates it.
2. The HTML mockups are **self-contained single files** with no backend and no JavaScript: each key state is rendered **stacked on one page** beneath a labelled state heading (decision §6).
3. Numbered amber callouts ( ① ) in the mockups are explained in the matching Markdown file's annotations table, with the FR each annotates.
4. Image placeholders are hatched grey blocks — photographs are content, not design.
5. Chrome is greyscale; real colour appears only in swatches, palette strips, proportion bars and the echo line.
6. Sample data in the mockups uses the API contract's own example values (Teal `#2CADA0`, Orange `#EE8225`, Azure `#2B7FC4`, …) so every shape shown is one the contract can actually return.
7. Each HTML mockup opens with a dark **wireframe navigation bar** linking the whole set, this overview, and the screen's own Markdown specification. It is documentation chrome, not part of the screen design — the application's real navigation is the sidebar inside each frame (§2).

---

## 5. State coverage matrix

| Screen | Empty | Loading | Error | Other states |
|---|---|---|---|---|
| Upload & detect | — (default *is* empty) | Detecting | Rejection (3 codes) | Drag-over highlight |
| Confirm-and-correct | — | Saving | Save failure (`invalid_category`) | Fallback warning; sum ≠ 100; manual add open; **region-grouped category picker**; regeneration variant |
| Inventory | Empty wardrobe; empty filter result | Skeleton grid | Load failure | Filtered; **grouped by category**; **order = hue / date** |
| Garment detail | — | Regenerate pending | Not found | **Category edit (PATCH)**; delete confirmation dialogue |
| Outfit request | — | Searching | `409 empty_slots` (`422` guarded) | Customised selection; **category-constrained slot**; **pinned**; anchored |
| Suggestion results | Zero results + hint | (covered by request) | — | **First-class neutral-based** card; **neutral-fallback** card; minor-adornment echo; fewer than the count |

---

## 6. Decisions log (Milestone 4 interview)

| Decision | Outcome |
|---|---|
| Navigation structure | Fixed left sidebar: Wardrobe (home), Add garment, Suggest outfit |
| Mockup state presentation | All states stacked on one HTML page per screen, labelled; no JavaScript |
| Inventory layout | Card grid with filter bar above *(superseded — v0.2.0: grouped by category with a hue/date order toggle, §6.1)* |
| Request/results | One page: slot panel persists above results |
| Proportion editor | Numeric steppers per colour + live total + stacked preview bar; save normalises to 100 |
| Colour-family filter | Dropdown with canonical swatch per family (from `GET /api/taxonomy`) |
| Results layout | Stacked full-width cards, best-first |
| Type picker | Segmented row of eight buttons, none pre-selected, save disabled until chosen *(superseded — v0.2.0: region-grouped ~40-category picker, §6.1)* |

### 6.1 v0.2.0 decisions (Milestone 12 session)

| Decision | Outcome |
|---|---|
| Slot selector (screen 5) | All slots visible, grouped by the four regions; defaults pre-selected; `lower_body` locked-on; upper-body layers labelled Base / Shirt / Mid-layer / Outer layer |
| Per-category constraint | A multi-category slot carries an "any ▾" expander with category checkboxes; sends `{ categories: [...] }` in `slots` (FR-52) |
| Pins | Both a panel-level "Pin a garment" modal and per-slot pin; the picker offers a one-click "Suggest outfits around this" (pin + generate); active pins are removable chips |
| Colour anchor | Family swatch-chips + segmented scheme row (incl. Neutral-based), both optional, composing |
| Count | Plain ± stepper, default 3, clamped 1–25, before Generate |
| Results labels | First-class neutral-based shows the scheme chip alone; neutral fallback adds a distinct "Neutral fallback" label; a count header shows returned vs requested |
| Inventory (screen 3) | Per-category group headers + counts; segmented Hue / Date-added order toggle; neutrals after the hue spectrum within a group |
| Category edit (screen 4) | Inline region-grouped picker → `PATCH`; palette stays regenerate-only |
| Category picker (screen 2) | Region-grouped ~40-category chip picker, none pre-selected; field `category`, error `invalid_category` |
| No garment names | Identity is thumbnail + palette + category everywhere (F3 defers metadata) |

---

*Approval of this directory's contents closes Milestone 4. The v0.2.0 amendments above were
settled during the Milestone 12 session and are committed with the reopened M10/M11 spec
amendments; sign-off closes Milestone 12.*
