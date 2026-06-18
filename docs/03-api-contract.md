# Hueniform — HTTP API Contract

| | |
|---|---|
| **Document** | API contract (living document) |
| **Status** | Approved (Milestone 3); amended for v0.2.0 (Milestone 11; category-granularity addendum during Milestone 12) |
| **Originally approved** | 12 June 2026 (Milestone 3, v0.1.0) |
| **Last amended** | 18 June 2026 — category-granularity addendum (Milestone 12 session): expanded category set, renamed layer slot keys `jersey`/`jacket` → `mid`/`outer`, per-category slot constraints in `POST /api/suggestions` |
| **Source** | `docs/02-requirements.md` (FR/NFR identifiers cited throughout) and `docs/03-architecture.md`; v0.2.0 brief (`docs/09-v0.2.0-brief.md`); F4 spike (`docs/spikes/2026-06-18-f4-category-slot-model.md`) |
| **Repository location** | `docs/03-api-contract.md` |

This document is the authoritative contract between frontend and backend; each may be built independently against it. FastAPI's generated OpenAPI is a convenience mirror — where they disagree, this document wins and the code is wrong.

> **v0.2.0 amendment note (18 June 2026).** This is a living document; it evolves in
> place (v0.2.0 brief §1). The Milestone 11 delta pass amends: **§1** (conventions —
> the garment field `type` → `category` and its new value set, the slot-key namespace);
> **§1.2** (garment objects); **§2.2** (`GET /api/taxonomy` — the slot/region model and
> the Cream family); **§2.6** (`GET /api/garments` — grouping/ordering, FR-47); adds
> **§2.10a** (`PATCH /api/garments/{id}` — direct category edit, FR-46); **§2.12** (`POST
> /api/suggestions` — slot selection, pins, colour/scheme anchor, count); and **§3**
> (traceability). Requirements §1.4 numeric thresholds are referenced, not restated.
> Superseded shapes are marked *(superseded — v0.2.0)* in place. Where this contract and
> the code disagree, the contract wins (and the code is wrong).
>
> **Category-granularity addendum (Milestone 12 session, 18 June 2026).** Wireframing the
> outfit request exposed that the single multi-category slots were too coarse to request.
> Three changes follow, applied in place: the **category value set expands** (finer
> garment vocabulary, §1.3); the **upper-body layer slot keys are renamed** `jersey` →
> `mid`, `jacket` → `outer` (§1.3a, §2.2, §2.12 — `jacket` survives as a *category* in the
> `outer` slot; `jersey` is dropped as a category); and `POST /api/suggestions` gains a
> **per-category slot constraint** carried inside the `slots` map (§2.12, FR-52). Driven by
> `docs/02-requirements.md` FR-16/FR-36/FR-49/FR-52 and the F4 spike §7.

---

## 1. Conventions

1. Base URL `http://127.0.0.1:8000`; all endpoints are prefixed `/api`. Image endpoints return binary bodies; everything else is `application/json` (UTF-8).
2. Identifiers are UUID4 strings. Timestamps are ISO 8601 UTC (e.g. `"2026-06-12T14:03:00Z"`).
3. Garment **categories** (FR-16) — *(amended — v0.2.0; the field is renamed `type` → `category` and the value set is replaced; supersedes the v0.1.0 eight `type` values `top`/`bottom`/`jersey`/`jacket`/`socks`/`shoes`/`hat`/`accessory`. Value set **expanded** in the Milestone 12 session — finer vocabulary; `jersey` removed as a category.)* A garment carries exactly one `category` from:

   - **Upper-body layers** — `base` slot: `t_shirt`, `vest`, `long_sleeve`; `shirt` slot: `shirt`, `blouse`, `polo`; `mid` slot: `jumper`, `hoodie`, `cardigan`, `sweatshirt`, `track_top`, `waistcoat`; `outer` slot: `jacket`, `blazer`, `coat`.
   - **Lower body** — `trousers`, `jeans`, `chinos`, `shorts`, `skirt`, and the **one-piece** `dress`, `jumpsuit`.
   - **Head / neck / hand / waist adornments** — `hat`, `cap`, `beanie`, `glasses`, `sunglasses`, `earrings`, `tie`, `scarf`, `necklace`, `watch`, `ring`, `bracelet`, `belt`.
   - **Feet** — `socks`, `shoes`, `boots`, `trainers`, `sandals`.

   Categories are **finer than slots**: several share one slot and are matcher-equivalent (FR-49.5). The JSON field is **`category`** everywhere a garment is represented or filtered (the underlying DB column keeps the name `type` — architecture §3.1 — but it is never exposed under that name).

3a. **Slot keys** are a *separate namespace* from categories, used as the keys of the `slots` selection map and `pins` map in a suggestion request (§2.12) and of a combination's `slots` object. Each category occupies exactly one slot; several categories may share one slot. *(Amended — Milestone 12 session: the upper-body layer slot keys `jersey`/`jacket` are renamed `mid`/`outer`; each layer slot now holds several categories.)* The slot keys and their FR-49 roles are:

   | Slot key | Display label | Region | Categories | Role |
   |---|---|---|---|---|
   | `base` | Base | upper body | `t_shirt`, `vest`, `long_sleeve` | anchor (layer 0) |
   | `shirt` | Shirt | upper body | `shirt`, `blouse`, `polo` | anchor (layer 1) |
   | `mid` | Mid-layer | upper body | `jumper`, `hoodie`, `cardigan`, `sweatshirt`, `track_top`, `waistcoat` | anchor (layer 2) |
   | `outer` | Outer layer | upper body | `jacket`, `blazer`, `coat` | anchor (layer 3; outermost dominant) |
   | `lower_body` | Lower body | lower body | `trousers`, `jeans`, `chinos`, `shorts`, `skirt`, `dress`, `jumpsuit` | anchor (**mandatory**; one-piece also occupies `base`) |
   | `hat` | Hat | head | `hat`, `cap`, `beanie` | statement |
   | `glasses` | Glasses | head | `glasses`, `sunglasses` | minor |
   | `earrings` | Earrings | head | `earrings` | minor |
   | `tie`, `scarf` | Tie / Scarf | neck | same-named category each | statement |
   | `necklace` | Necklace | neck | `necklace` | minor |
   | `watch`, `ring`, `bracelet` | Watch / Ring / Bracelet | hands | same-named category each | minor |
   | `belt` | Belt | waist | `belt` | statement |
   | `socks` | Socks | feet | `socks` | statement |
   | `shoes` | Shoes | feet | `shoes`, `boots`, `trainers`, `sandals` | statement |

   **Default-selected** slots (FR-51) are `base`, `lower_body`, `socks`, `shoes`; `lower_body` is mandatory and cannot be deselected; every other slot is optional. Category→slot is deterministic, so a pinned garment's slot key is derivable from its category (a one-piece pins to `lower_body`). A request may additionally **constrain a selected slot to a subset of its categories** (FR-52, §2.12). The authoritative machine-readable form of this table is `GET /api/taxonomy` (§2.2).
4. **Scheme** names (FR-13): `neutral-based`, `monochromatic`, `analogous`, `complementary`, `triadic`. *(v0.2.0: `neutral-based` is now a first-class result, FR-41 — see §2.12.)*
5. Colour `family` values are exactly the names in requirements §2: `Black`, `White`, `Grey`, `Navy`, `Denim`, `Brown`, `Beige/Tan`, **`Cream`** *(new — v0.2.0, FR-2)*, `Red`, `Orange`, `Yellow`, `Chartreuse`, `Green`, `Mint`, `Teal`, `Azure`, `Blue`, `Violet`, `Magenta`, `Pink`.
6. The server **always derives `family` from submitted HSL** (FR-1); a client-supplied family is never trusted and never sent on input.

### 1.1 Colour objects

**`ColourOut`** (responses) — `hex` is derived from the measured HSL so the UI can render the actual colour's swatch (FR-5).

```json
{ "h": 207.4, "s": 64.0, "l": 47.0, "family": "Azure", "neutral": false, "hex": "#2B7FC4", "proportion": 62 }
```

**`ColourIn`** (requests) — measured values from a proposal, or canonical values (from `GET /api/taxonomy`) for a manually added colour (FR-29).

```json
{ "h": 207.4, "s": 64.0, "l": 47.0, "proportion": 62 }
```

Validation: `0 ≤ h < 360`, `0 ≤ s ≤ 100`, `0 ≤ l ≤ 100`; `proportion` an integer `1–100`; a palette is 1–4 colours (FR-6) whose proportions sum to **exactly 100** — the UI normalises on save (FR-29), the server only validates, answering `422` otherwise.

### 1.2 Garment objects

**`GarmentSummary`** (inventory lists, suggestion slots — FR-35, FR-37). *(Amended — v0.2.0: the field `"type"` is renamed `"category"`, §1.3; its value is one of the FR-16 categories.)*

```json
{
  "id": "0b6c4d1e-7a2f-4f7e-9d2a-1c3e5f7a9b0c",
  "category": "jumper",
  "colours": [ { "h": 174.0, "s": 58.0, "l": 41.0, "family": "Teal", "neutral": false, "hex": "#2CADA0", "proportion": 80 },
               { "h": 28.0, "s": 85.0, "l": 55.0, "family": "Orange", "neutral": false, "hex": "#EE8225", "proportion": 20 } ],
  "thumbnail_url": "/api/garments/0b6c4d1e-7a2f-4f7e-9d2a-1c3e5f7a9b0c/thumbnail"
}
```

**`Garment`** (detail) — `GarmentSummary` plus `"image_url"`, `"created_at"`, `"regenerated_at"` (nullable).

### 1.3 Error envelope and status codes

Every non-2xx response carries:

```json
{ "error": { "code": "unsupported_format", "message": "Only JPEG, PNG and WebP photographs are accepted.", "details": {} } }
```

`message` is always plain language fit to show the user (FR-24, FR-36, FR-43). `code` values are stable machine identifiers listed per endpoint.

| Status | Meaning here |
|---|---|
| 200 / 201 / 204 | Success / created / deleted-no-body |
| 400 | Malformed request or unreadable/unsupported upload |
| 404 | Unknown garment, or unknown/expired token |
| 409 | Request conflicts with state (empty requested slot; invalid regeneration token) |
| 413 | Upload exceeds 20 MB |
| 422 | Body failed validation (codes include the field detail in `details`) |
| 500 | Unexpected server error (`code: "internal_error"`) |

---

## 2. Endpoints

### 2.1 `GET /api/health`

Readiness probe used by the launch script before printing the URL (NFR-2). **200**: `{ "status": "ok", "version": "0.1.0" }`

### 2.2 `GET /api/taxonomy`

The taxonomy for UI use: colour-family pickers for manual colour adds (FR-29) and legend display (FR-5); and *(new — v0.2.0)* the **category / slot / region model** (FR-16, FR-49–FR-51) the UI needs to render category pickers (confirm-and-correct, category edit) and the slot selector (outfit request). `canonical` is the HSL stored when the user adds a colour by family alone; each canonical value classifies into its own family.

The response is a **backward-compatible superset** of the v0.1.0 shape: the `families` array is unchanged in form (it now also contains `Cream`), and a parallel `regions` array is added.

**200:**

```json
{
  "families": [
    { "name": "Navy",  "neutral": true,  "canonical": { "h": 230.0, "s": 40.0, "l": 18.0 } },
    { "name": "Cream", "neutral": true,  "canonical": { "h": 48.0,  "s": 28.0, "l": 91.0 } },
    { "name": "Teal",  "neutral": false, "representative_hue": 180.0, "hue_arc": [165.0, 195.0],
      "canonical": { "h": 180.0, "s": 70.0, "l": 50.0 } }
  ],
  "regions": [
    { "region": "head", "slots": [
        { "slot": "hat",      "label": "Hat",      "categories": ["hat", "cap", "beanie"], "role": "statement", "default_selected": false },
        { "slot": "glasses",  "label": "Glasses",  "categories": ["glasses", "sunglasses"], "role": "minor",     "default_selected": false },
        { "slot": "earrings", "label": "Earrings", "categories": ["earrings"], "role": "minor",     "default_selected": false }
    ] },
    { "region": "upper_body", "slots": [
        { "slot": "base",     "label": "Base",        "categories": ["t_shirt", "vest", "long_sleeve"], "role": "anchor", "layer_order": 0, "default_selected": true  },
        { "slot": "shirt",    "label": "Shirt",       "categories": ["shirt", "blouse", "polo"], "role": "anchor", "layer_order": 1, "default_selected": false },
        { "slot": "mid",      "label": "Mid-layer",   "categories": ["jumper", "hoodie", "cardigan", "sweatshirt", "track_top", "waistcoat"], "role": "anchor", "layer_order": 2, "default_selected": false },
        { "slot": "outer",    "label": "Outer layer", "categories": ["jacket", "blazer", "coat"], "role": "anchor", "layer_order": 3, "default_selected": false },
        { "slot": "tie",      "label": "Tie",      "categories": ["tie"],      "role": "statement", "default_selected": false },
        { "slot": "scarf",    "label": "Scarf",    "categories": ["scarf"],    "role": "statement", "default_selected": false },
        { "slot": "necklace", "label": "Necklace", "categories": ["necklace"], "role": "minor",     "default_selected": false },
        { "slot": "watch",    "label": "Watch",    "categories": ["watch"],    "role": "minor",     "default_selected": false },
        { "slot": "ring",     "label": "Ring",     "categories": ["ring"],     "role": "minor",     "default_selected": false },
        { "slot": "bracelet", "label": "Bracelet", "categories": ["bracelet"], "role": "minor",     "default_selected": false }
    ] },
    { "region": "lower_body", "slots": [
        { "slot": "lower_body", "label": "Lower body", "role": "anchor", "mandatory": true, "default_selected": true,
          "categories": ["trousers", "jeans", "chinos", "shorts", "skirt", "dress", "jumpsuit"],
          "one_piece_categories": ["dress", "jumpsuit"], "one_piece_also_occupies": ["base"] },
        { "slot": "belt", "label": "Belt", "categories": ["belt"], "role": "statement", "default_selected": false }
    ] },
    { "region": "feet", "slots": [
        { "slot": "socks", "label": "Socks", "categories": ["socks"], "role": "statement", "default_selected": true },
        { "slot": "shoes", "label": "Shoes", "categories": ["shoes", "boots", "trainers", "sandals"], "role": "statement", "default_selected": true }
    ] }
  ]
}
```

Notes on `regions`:

- `region` ∈ `head`, `upper_body`, `lower_body`, `feet`. `role` ∈ `anchor`, `statement`, `minor` (FR-49.3). `categories` lists the FR-16 categories that occupy the slot — **several per slot** (the finer vocabulary; matcher-equivalent within a slot, FR-49.5). They are the allowed values for a per-category slot constraint (§2.12, FR-52).
- `label` *(new — Milestone 12 session)* is the user-facing slot name; `slot` is the stable machine key. The keys `mid`/`outer` *(renamed from `jersey`/`jacket`)* are the upper-body layers 2 and 3.
- `layer_order` is present only on the four upper-body anchor layers; it is the innermost-to-outermost order `base(0) → shirt(1) → mid(2) → outer(3)`, and the **outermost present layer is dominant** (FR-18). It is absent on all other slots.
- `mandatory: true` appears only on `lower_body` (FR-51); absent (falsey) elsewhere. `default_selected` reflects the FR-51 default selection.
- `one_piece_categories` / `one_piece_also_occupies` appear only on `lower_body`: `dress` and `jumpsuit` are one-piece and additionally occupy the `base` slot (FR-49.2, FR-50.2).
- `representative_hue` and `hue_arc` remain present only on chromatic families; `Cream` is a neutral family, so it carries `canonical` only.

### 2.3 `POST /api/detections` — upload and detect (FR-23, FR-24, FR-26, FR-27, FR-28)

`multipart/form-data` with one field `file` (JPEG, PNG or WebP, ≤ 20 MB). Stages the image, runs detection, returns the proposal for confirm-and-correct. Nothing is written to the database (FR-24).

**201:**

```json
{
  "token": "3f9d2c8e-1b4a-4c6d-8e2f-7a9b0c1d2e3f",
  "expires_at": "2026-06-12T15:03:00Z",
  "fallback_used": false,
  "image": { "url": "/api/detections/3f9d2c8e-1b4a-4c6d-8e2f-7a9b0c1d2e3f/image", "width": 1600, "height": 1200 },
  "colours": [
    { "h": 174.0, "s": 58.0, "l": 41.0, "family": "Teal",   "neutral": false, "hex": "#2CADA0", "proportion": 80 },
    { "h": 28.0,  "s": 85.0, "l": 55.0, "family": "Orange", "neutral": false, "hex": "#EE8225", "proportion": 20 }
  ]
}
```

`fallback_used: true` signals whole-image clustering after failed isolation; the UI must surface the FR-27 warning that results may include background colour.

**Errors:** `400 unsupported_format`, `400 unreadable_image`, `413 file_too_large`.

### 2.4 `GET /api/detections/{token}/image`

The staged image, for the confirmation screen preview. **200** image bytes (original content type); **404 `detection_not_found`** if unknown or expired.

### 2.5 `POST /api/garments` — confirm and save (FR-6, FR-25, FR-29, FR-30, FR-31)

```json
{
  "detection_token": "3f9d2c8e-1b4a-4c6d-8e2f-7a9b0c1d2e3f",
  "category": "jumper",
  "colours": [ { "h": 174.0, "s": 58.0, "l": 41.0, "proportion": 80 },
               { "h": 28.0,  "s": 85.0, "l": 55.0, "proportion": 20 } ]
}
```

*(Amended — v0.2.0: the request field `"type"` is renamed `"category"` and takes one of the FR-16 categories, §1.3.)* Atomically moves the staged image into permanent storage, generates the thumbnail and creates the garment. The token is consumed.

**201:** the full `Garment`. **Errors:** `404 detection_not_found` (unknown, expired or consumed token); `422 invalid_palette` (count outside 1–4, proportions not summing to 100, values out of range); `422 invalid_category` *(renamed — v0.2.0, was `invalid_type`)*.

### 2.6 `GET /api/garments` — inventory (FR-35, FR-47, NFR-6)

Query parameters, all optional. Filters combine as AND:

- `category` — one FR-16 category. *(Renamed — v0.2.0, was `type`.)*
- `family` — one §1 family name; matches a garment containing that family in **any** role.
- `order` *(new — v0.2.0, FR-47)* — the within-group ordering, one of:
  - `hue` *(default)* — a colour spectrum by each garment's **primary-colour hue** (the `position = 0` colour, FR-7); garments whose primary is a **neutral** (no hue, FR-3) are ordered **after** the chromatic spectrum in a stable, defined order.
  - `date` — by `created_at`, **newest first**.
- `limit` / `offset` — defaults 500 / 0 (a full wardrobe fits one response).

The server returns a **flat list already ordered** by category and then by the chosen `order` key, so the client groups by walking the list (FR-47 grouping is a frontend concern — v0.2.0 brief §F6; architecture §3.1). `total` is the full match count before pagination.

**200:**

```json
{ "garments": [ GarmentSummary ], "total": 137 }
```

(Each `GarmentSummary` carries `category`, so the client buckets the ordered list into per-category groups without a second request.)

**Errors:** `422 invalid_filter` for an unknown `category`, `family` or `order` value.

### 2.7 `GET /api/garments/{id}`

**200:** the full `Garment`. **404 `garment_not_found`**.

### 2.8 `GET /api/garments/{id}/image` · `GET /api/garments/{id}/thumbnail` (FR-25, FR-35)

**200** binary image (original format / WebP thumbnail). **404 `garment_not_found`**.

### 2.9 `POST /api/garments/{id}/regenerate` (FR-26, FR-33)

No body. Re-runs detection on the stored photograph and returns a proposal in exactly the §2.3 response shape, plus `"garment_id"` and with `token` acting as the **regeneration token** required by §2.10. The stored image and record are untouched until confirmation.

**200** as §2.3 + `garment_id`; **404 `garment_not_found`**.

### 2.10 `PUT /api/garments/{id}` — confirm regeneration (FR-32, FR-33)

```json
{
  "regeneration_token": "9c1e7a3b-5d2f-4e8a-b6c0-2f4d6e8a0b1c",
  "category": "jumper",
  "colours": [ { "h": 176.0, "s": 60.0, "l": 40.0, "proportion": 100 } ]
}
```

*(Amended — v0.2.0: the request field `"type"` is renamed `"category"`, §1.3.)* Replaces the palette and category **in place** — same `id`, same photograph — so existing references remain valid (FR-33). The token requirement is the FR-32 enforcement: this endpoint completes a regeneration (palette + category together); the direct single-field category edit is `PATCH` (§2.10a). *(Errors as §2.5, including `422 invalid_category`.)*

**200:** the updated `Garment` (`regenerated_at` set). **Errors:** `404 garment_not_found`; `409 invalid_regeneration_token` (absent, expired, consumed, or bound to a different garment); `422` as §2.5.

### 2.10a `PATCH /api/garments/{id}` — edit category *(new — v0.2.0, FR-46, F3)*

Direct, single-field edit of a saved garment's **category** (FR-16), **without
re-running detection** and without the confirm-and-correct flow. This is the only
field-edit path permitted by FR-32 (as amended); it sits beside the token-gated `PUT`
(§2.10), which remains the *only* way to change the palette (regenerate-only,
FR-32/FR-33). `PATCH` carries no regeneration token and never touches the palette,
image or identifier.

The verb split is deliberate: `PATCH` modifies a **proper subset** of the mutable
representation (the `category` field), whereas `PUT` (§2.10) **replaces the whole
mutable set** (`category` + `colours`) as the confirmed regeneration outcome. The
regeneration token is an *orthogonal* authorisation gate enforcing FR-32 (the palette
changes only via re-detection), not the basis of the verb choice.

```json
{ "category": "jacket" }
```

The body has exactly one field, `category`, one of the FR-16 categories (§1.3). The
garment keeps its `id`, photograph and stored palette; only `garments.type` changes
(architecture §3.1). Suggestion eligibility then follows the new category and its slot
role (FR-49–FR-51) at evaluation time. `regenerated_at` is **not** changed (a category
edit is not a regeneration).

**200:** the full updated `Garment`. **Errors:** `404 garment_not_found`; `422
invalid_category` (value not in the FR-16 allowlist); `422 invalid_request` (missing
`category`, or any field other than `category` supplied).

### 2.11 `DELETE /api/garments/{id}` (FR-34)

Removes the record, photograph and thumbnail. The confirmation step is a UI responsibility. **204** no body; **404 `garment_not_found`**.

### 2.12 `POST /api/suggestions` — outfit request (FR-36, FR-39–FR-45, FR-48–FR-51, NFR-5, NFR-10)

> **Rewritten — v0.2.0 (F1/F2/F4/F7).** The v0.1.0 request was `{ "include": { … } }`
> over four optional slots, with `top`/`bottom`/`socks`/`shoes` always included and "up
> to 3" results. *(Superseded — v0.2.0.)* The request below adds configurable/removable
> slot selection over the new slot model (FR-51), pins (FR-44), a colour/scheme anchor
> (FR-45) and a count (FR-48). All four fields are **optional**; an empty body `{}` means
> the FR-51 default slots, no pins, no anchor and `count = 3`.
>
> **Amended — Milestone 12 session.** The upper-body layer slot keys are `mid`/`outer`
> (was `jersey`/`jacket`). A `slots` value may now be a **bool or a category-constraint
> object** `{ "categories": [...] }` (FR-52), constraining the slot to a subset of its
> categories (§1.3a, §2.2).

```json
{
  "slots":  { "outer": true, "socks": false, "lower_body": { "categories": ["shorts", "skirt"] } },
  "pins":   { "outer": "0b6c4d1e-7a2f-4f7e-9d2a-1c3e5f7a9b0c" },
  "anchor": { "family": "Teal", "scheme": "analogous" },
  "count":  5
}
```

- **`slots`** *(optional, FR-51, FR-52)* — a **partial override map**, slot key (§1.3a) →
  **`true` / `false` / a category-constraint object**, layered over the FR-51 **default
  selection** (`base`, `lower_body`, `socks`, `shoes` selected; every other slot
  deselected). Omitted keys keep their default.
  - `true` selects the slot with **any** of its categories eligible; `false` deselects it.
  - `{ "categories": [ … ] }` *(new — Milestone 12 session, FR-52)* selects the slot **and
    constrains it** to that non-empty subset of the slot's own categories (§2.2); every
    returned combination fills the slot from that subset. Listing a category that does not
    belong to the slot, or an empty list, is `422` (below).
  - A **selected** slot must be filled in every returned combination (so an empty selected
    slot fails fast — `409`, below). `lower_body` is **mandatory**: it may be omitted, set
    `true`, or constrained, but `false` is rejected (`422`). *Beach example:* `{ "base":
    false, "socks": false }` yields `lower_body` + `shoes`.
- **`pins`** *(optional, FR-44)* — a map slot key → garment `id`. Every returned
  combination contains the pinned garment in that slot. The garment's **category must map
  to the slot key** (§1.3a; a one-piece pins to `lower_body`); a pin **selects** its slot.
  A pin and a category constraint on the **same** slot must agree — the pinned garment's
  category must be in the constraint list, else `422`. More than one slot may be pinned;
  all pins hold simultaneously.
- **`anchor`** *(optional, FR-45)* — `{ "family"?, "scheme"? }`; either or both. `family`
  is one §1 family name — every combination's scheme set (§4 of requirements) must include
  that family on an anchor garment. `scheme` is one FR-13 name — every combination must
  match it. When both are given, both must hold.
- **`count`** *(optional, FR-48)* — integer **1–25**, **default 3**. Governs how many
  combinations are returned (FR-39); it does **not** relax the enumeration cap or the
  NFR-5 bound.

**200 — combinations found** (up to `count`, ranked best-first, all distinct — FR-39, FR-40, FR-41, FR-48):

```json
{
  "requested_count": 5,
  "combinations": [
    {
      "rank": 1,
      "scheme": "analogous",
      "fallback": false,
      "slots": {
        "base":       GarmentSummary,
        "lower_body": GarmentSummary,
        "outer":      GarmentSummary,
        "socks":      GarmentSummary,
        "shoes":      GarmentSummary
      },
      "echoes": [ { "family": "Orange", "from_slot": "socks", "to_slot": "lower_body" } ],
      "explanation": "Analogous scheme: the teal blazer and azure trousers sit side by side on the wheel; the navy shoes are neutral; the orange flecks in the socks echo the trousers."
    }
  ]
}
```

- `requested_count` echoes the effective `count`; `combinations` holds **at most** that many, fewer only when fewer exist (FR-39).
- `slots` is keyed by **slot key** (§1.3a). A **one-piece** appears once, under `lower_body` (it also occupies `base` but is counted once — FR-18/FR-19); no separate `base` entry is present for that combination.
- `scheme` is a non-null FR-13 name, **including `neutral-based`** when the scheme set is empty (now a first-class result, FR-41). *(Superseded — v0.2.0: the v0.1.0 `scheme: null` for neutral outfits.)*
- `fallback: true` marks a **neutral fallback** only (FR-43a) — produced solely by the fallback retry; the UI must label these. A **first-class all-neutral** outfit has `scheme: "neutral-based"` and `fallback: false`. So `scheme` + `fallback` together distinguish the two neutral cases.
- `echoes` lists the chromatic echoes credited in ranking (FR-11, FR-22), now **including minor-adornment echoes**: `from_slot` is the adornment slot, `to_slot` the anchor slot carrying that family.
- `explanation` is rendered from the actual evaluation result (FR-38).

**200 — no combination possible** (FR-43b; also an unsatisfiable pin or anchor — FR-44/FR-45):

```json
{
  "requested_count": 5,
  "combinations": [],
  "explanation": "No harmonious outfit was found: no outer-layer garment in the wardrobe is compatible with any lower-body garment under any scheme.",
  "hint": "The outer-layer slot most constrained the search — try the request without it, or add a neutral coat."
}
```

**409 — fail fast, empty selected slot** (FR-36):

```json
{ "error": { "code": "empty_slots",
             "message": "You have no garments for the requested slot(s): outer layer.",
             "details": { "empty_slots": ["outer"] } } }
```

**Other errors — `422 invalid_request`** (FR-36, FR-44, FR-45, FR-48, FR-51), with the offending value in `details`:

- an unknown slot key in `slots` or `pins`, or an unknown `anchor.family` / `anchor.scheme`;
- `count` outside 1–25 (`details: { "count": 26 }`);
- `lower_body` set `false` (it is mandatory, FR-51);
- a **category constraint** (FR-52) that is empty, or names a category **not in the slot's own category set** (§2.2) — `details: { "slot": "lower_body", "invalid_categories": ["jacket"] }`;
- a pin whose garment `id` does not exist, or whose **category does not map to the pinned slot key**; or a pin whose category is **not in a category constraint set on the same slot**;
- a contradictory selection — e.g. pinning a one-piece (`dress`/`jumpsuit`) to `lower_body`, **or constraining `lower_body` to one-piece categories only**, while `base` is selected (FR-50.2); or two pins for one slot.

Repeated identical requests may legitimately return different results (FR-42); the variety randomness is seedable (NFR-10), unseeded at runtime. Responses return within NFR-5's 2-second bound at 500 garments **including at `count = 25`** (the enumeration cap is count-independent; re-baselined in `test-perf`).

---

## 3. Traceability

| Requirement | Endpoint(s) |
|---|---|
| FR-1–FR-5 (taxonomy) | Server-side family derivation everywhere; `GET /api/taxonomy` (§2.2) |
| FR-2 (**Cream** family — v0.2.0) | §1.5 (`Cream`); §2.2 (`families` includes `Cream`) |
| FR-6 (1–4 colours, sum 100) | §2.3 response; §2.5/§2.10 validation |
| FR-16 (**categories** — v0.2.0; **expanded** M12 session) | §1.3 (expanded category set); §1.2 garment objects (`category`); §1.3a / §2.2 (`regions`/`slots`, `mid`/`outer` keys, several categories per slot) |
| FR-23, FR-24 (upload, rejection) | §2.3 |
| FR-25 (stored photograph) | §2.5, §2.8, §2.9 |
| FR-26, FR-27 (detection, fallback) | §2.3, §2.9 (`fallback_used`) |
| FR-28–FR-31 (confirm-and-correct, category) | §2.3 → §2.5 (`category`); §2.2 (canonical HSL for manual adds; category list) |
| FR-32 (amended — category editable), FR-33 (regenerate) | §2.9 → §2.10 (token-gated `PUT`, palette); §2.10a (`PATCH`, category) |
| FR-46 (**edit category** — v0.2.0) | §2.10a (`PATCH /api/garments/{id}`) |
| FR-34 (delete) | §2.11 |
| FR-35 (inventory, filters) | §2.6 (`category`/`family`), §2.8 |
| FR-47 (**grouping & ordering** — v0.2.0) | §2.6 (`order` = `hue`/`date`; client groups by `category`) |
| FR-36 (slot selection, fail fast — amended) | §2.12 (`slots`; `409 empty_slots`; `422` for no/invalid `lower_body`) |
| FR-44 (**pin a garment** — v0.2.0) | §2.12 (`pins`) |
| FR-45 (**colour/scheme anchor** — v0.2.0) | §2.12 (`anchor`) |
| FR-37, FR-38 (explanations from evaluation) | §2.12 (`scheme`, `echoes`, `explanation`) |
| FR-39 (up to *N* — amended), FR-48 (**count** — v0.2.0) | §2.12 (`count`, `requested_count`) |
| FR-40, FR-42 (distinct, non-deterministic) | §2.12 |
| FR-41 (refined — all-neutral first-class) | §2.12 (`scheme: "neutral-based"` with `fallback: false`) |
| FR-43 (refined — slimmed fallback ladder) | §2.12 (`fallback: true` neutral fallback; empty-result shape with `hint`) |
| FR-49–FR-51 (**slot model** — v0.2.0) | §1.3a (slot keys, roles, defaults, mandatory `lower_body`); §2.2 (`regions`); §2.12 (`slots`, `pins`, exclusion `422`s) |
| FR-52 (**per-category slot constraint** — M12 session) | §1.3a (constraint pointer); §2.2 (`categories` per slot = allowed values); §2.12 (`slots` category-constraint object; FR-52 `422`s) |
| NFR-2 (single command) | §2.1 |
| NFR-5 (amended — bound holds at count 25), NFR-6 (response bounds) | §2.12, §2.6 |
| NFR-10 (**seedable variety** — v0.2.0) | §2.12 (non-determinism note; seed is server-internal, not contract surface) |

FR-7–FR-15 (roles, proportion and harmony maths) and FR-17–FR-22 (anchors, layering, the
covered-layer and adornment-tier rules) govern the evaluation behind §2.12 and are
specified in `docs/02-requirements.md`; they impose no *additional* contract surface beyond
the slot keys, roles and one-piece flags already surfaced by `GET /api/taxonomy` (§2.2) and
the combination `slots`/`echoes` of §2.12.

---

*Approval of this document, together with `docs/architecture.md`, closes Milestone 3.*
