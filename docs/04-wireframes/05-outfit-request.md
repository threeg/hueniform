# Screen 5 — Outfit Request

| | |
|---|---|
| **Route** | `/suggest` (sidebar: *Suggest outfit*) — one page with the results (screen 6) rendered beneath this panel. Reachable pre-filled with a pin from garment detail or an inventory card (FR-44). |
| **Realises** | FR-36 (slot selection; category constraint; pin; colour/scheme anchor; count; fail fast), FR-44 (pin a garment), FR-45 (anchor to a colour family and/or scheme), FR-48 (count 1–25, default 3, before generate), FR-49–FR-51 (region/slot model; mandatory lower-body floor), FR-52 (per-category slot constraint) |
| **API** | `POST /api/suggestions` — request body (`slots` incl. category constraints, `pins`, `anchor`, `count`), `409 empty_slots`, `422 invalid_request` |
| **Mockup** | [`05-outfit-request.html`](05-outfit-request.html) |

> **Rewritten — v0.2.0, then reworked in the Milestone 12 session.** This screen supersedes
> the v0.1.0 *Outfit request* built on the `include` four-optional-slot model. The contract
> request is `{ slots, pins, anchor, count }` over the region/slot model (contract §2.12,
> §1.3a). During M12 the screen drove a spec addendum: the **upper-body layer slots are
> labelled Base / Shirt / Mid-layer / Outer layer** (keys `base`/`shirt`/`mid`/`outer`), the
> category vocabulary is finer (contract §1.3, §2.2), and a slot may be **constrained to a
> subset of its categories** (FR-52) via a value object inside `slots`.

## Purpose

Compose the request: which slots this outfit includes, optionally narrowed to specific
garment types, around which garment or colour, and how many suggestions to generate. The
panel stays visible above the results (decision §6) so the request can be tweaked and
repeated without navigation.

## Layout

A single **request panel**, top to bottom:

1. **Slots** — the slot selector, grouped into the four regions of `GET /api/taxonomy`
   (contract §2.2): **Head**, **Upper body**, **Lower body**, **Feet**. Every slot is a
   toggle chip; all slots are visible (no progressive disclosure). Within each region the
   **anchor** slots are shown first, then the region's adornment slots under a quiet
   *Accessories* sub-label.
   - **Default-selected** chips are on at open: `base`, `lower_body`, `socks`, `shoes`
     (FR-51.1; contract §1.3a). Every other chip is off.
   - **`lower_body` is mandatory** (FR-51.2): its chip is rendered **locked-on** with a lock
     glyph and cannot be deselected.
   - The **upper-body layers** use the renamed labels **Base · Shirt · Mid-layer · Outer
     layer** in stack order `base → shirt → mid → outer` (innermost→outermost; `layer_order`
     0–3, FR-18), so the visual order teaches the layering. The slot **keys** submitted are
     `base`/`shirt`/`mid`/`outer`.
   - **Per-category constraint (FR-52).** A selected slot that owns more than one category
     (e.g. Lower body, Base, Shirt, Mid-layer, Outer layer, Hat, Glasses, Shoes) carries a
     small **"any ▾"** control. Expanding it lists that slot's categories (from
     `GET /api/taxonomy`) as checkboxes; ticking a subset constrains the slot to those
     categories and the control summarises the choice ("shorts, skirt"). Leaving it on
     **"any"** keeps every category eligible (the default). Single-category slots (e.g.
     Belt, Socks, Necklace) have no control.
2. **Pins** *(FR-44)* — "Build around a garment". Two entry points (decision: both):
   - a panel-level **Pin a garment** button opening a **wardrobe picker modal** (the
     inventory cards + filters); the chosen garment auto-targets **its own slot**
     (category→slot is deterministic — contract §1.3a; a `dress`/`jumpsuit` pins to
     `lower_body`), and that slot becomes selected;
   - a per-slot **pin** action on each selected slot chip, opening the same picker
     pre-filtered to that slot's categories.
   - **Select-to-generate** (M12 decision): in the picker, selecting a garment also offers a
     one-click **"Suggest outfits around this"** that pins it and generates immediately with
     the current defaults; otherwise the pin just composes the request and Generate stays an
     explicit step.
   - Garments carry **no name** (F3 defers metadata): a garment is identified everywhere by
     **thumbnail + palette + category**, exactly as on the inventory and results cards. The
     picker cards and pin chips use that — at most a derived "primary-family + category"
     phrasing (e.g. "Teal dress"), both real fields; never an invented title or pattern word.
   - Active pins are listed as **removable chips** (garment thumbnail + category + a palette
     swatch + ✕). A pin must agree with any category constraint on the same slot (the pinned
     garment's category must be in the constraint list — contract §2.12). Pinning a
     **one-piece** to
     `lower_body`, or constraining `lower_body` to one-piece categories only, auto-deselects
     `base` with an inline note (FR-50.2).
3. **Build around a colour** *(optional, FR-45)* — an **Anchor** section with two
   independent, clearable controls that compose:
   - **Colour family** — selectable **swatch-chips**, each a canonical swatch + family name
     from `GET /api/taxonomy`; single-select with a *Clear* (none = any colour).
   - **Scheme** — a segmented row of the five FR-13 names: *Neutral-based*, *Monochromatic*,
     *Analogous*, *Complementary*, *Triadic*, plus an *Any* default. Single-select.
   - Either, both or neither may be set; when both are set, both constrain (contract §2.12).
4. **How many outfits?** *(FR-48)* — a numeric **± stepper**, default **3**, clamped to the
   inclusive range **1–25**, placed directly above Generate.
5. **Generate** (primary button) and a one-line hint: "The lower-body slot is always
   included; everything else is up to you."

## Behaviour

- **Request build.** Generate sends `POST /api/suggestions` (contract §2.12):
  - **`slots`** is a **partial override map** — only slots whose state differs from the
    FR-51 default are sent. A plain toggle sends `true`/`false`; a constrained slot sends
    `{ "categories": [ … ] }` (which also selects it). `lower_body` is never sent `false`.
  - **`pins`** maps slot key → garment `id` for each active pin; a pin selects its slot.
  - **`anchor`** carries `family` and/or `scheme` only when set.
  - **`count`** is the stepper value (1–25).
  - An empty body `{}` (all defaults) is a valid request.
- **Client-side guards** keep the request inside the contract so `422 invalid_request` is
  essentially unreachable: `lower_body` cannot be deselected; the count clamps to 1–25; a
  category checklist cannot be emptied (un-ticking the last reverts the slot to "any"); a
  one-piece-only `lower_body` constraint or a one-piece pin auto-deselects `base`; a pin is
  offered only for garments whose category is allowed by any constraint on that slot. A
  `422` that nonetheless arrives is shown as the guarded error banner (message verbatim).
- **Loading.** The panel goes inert and the results area shows a searching message; NFR-5
  bounds the response under 2 s at 500 garments, **including at `count = 25`**.
- **`409 empty_slots`** (FR-36, fail fast): the envelope `message` is rendered verbatim in an
  error banner below the panel, and each slot named in `details.empty_slots` is flagged inline
  on its chip with "none in wardrobe". A constraint that excludes every owned garment surfaces
  the same way (the slot has no eligible garment). The user can widen/deselect the slot (if
  optional) or follow the **Add a garment** link; a named **mandatory** slot has no untick.
- **Unsatisfiable pin/anchor/constraint** is **not** a 409: it returns `200` with
  `combinations: []` plus an `explanation`/`hint` — a screen-6 zero-result state (FR-43,
  FR-44, FR-45, FR-52).
- **200** responses belong to screen 6.

## Navigation

- The panel persists above the results on `/suggest` (one page, decision §6).
- **Deep-linked pin**: *Build an outfit around this* on garment detail (and an inventory
  card) navigates to `/suggest` with the pin pre-applied — the garment's slot is selected and
  the pin chip is present on arrival. *Suggest outfit* is highlighted in the sidebar.

## States (in mockup order)

| State | Trigger |
|---|---|
| **Default** | Page open; FR-51 default slots selected, no pins/anchor/constraints, count 3 |
| **Category-constrained + anchored** | Lower body constrained to shorts/skirt; beach selection (`base`, `socks` off); colour family + scheme set |
| **Pinned** | A garment pinned (chip with thumbnail); one-piece note variant shown |
| **Searching** (loading) | Request in flight (< 2 s at 500 garments, NFR-5) |
| **Empty slot** (error) | `409 empty_slots`; message verbatim, named chip(s) flagged |

## Annotations (callouts in the mockup)

| # | Note |
|---|---|
| ① | Region-grouped slot selector; all slots visible. Anchors first, then per-region *Accessories* (FR-49, contract §2.2). |
| ② | Default-selected slots on at open: `base`, `lower_body`, `socks`, `shoes` (FR-51.1). |
| ③ | `lower_body` locked-on — mandatory (FR-51.2, contract §1.3a). |
| ④ | Upper-body layers labelled Base/Shirt/Mid-layer/Outer layer, stack order `base→shirt→mid→outer`; outermost present dominant (FR-18). |
| ⑤ | Per-category constraint: a multi-category slot's "any ▾" expands to category checkboxes; a subset sends `{ categories: [...] }` (FR-52, contract §2.12). |
| ⑥ | Pin entry (both): panel-level **Pin a garment** modal + per-slot pin; active pins are removable chips; pin selects its slot; picker offers one-click "Suggest outfits around this" (FR-44). |
| ⑦ | One-piece pin or one-piece-only lower-body constraint auto-deselects `base` with an inline note (FR-50.2). |
| ⑧ | Anchor: family swatch-chips + segmented scheme incl. *Neutral-based*; either/both/neither, they compose (FR-45). |
| ⑨ | Count stepper, default 3, clamped 1–25, before Generate (FR-48). |
| ⑩ | Generate → `POST /api/suggestions` with `slots`/`pins`/`anchor`/`count`; only non-default slots sent; a constrained slot sends a category object (contract §2.12). |
| ⑪ | `409 empty_slots`: message verbatim; `details.empty_slots` drives the per-chip flag; mandatory slot has no untick (FR-36). |
