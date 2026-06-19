# Design handoff brief — Screen 3: Inventory Browser

| | |
|---|---|
| **Screen** | Inventory browser (`/`, the home page) |
| **Wireframe of record** | [`03-inventory.md`](03-inventory.md) · [`03-inventory.html`](03-inventory.html) |
| **Binding contract** | `docs/03-api-contract.md` §2.6 (`GET /api/garments`), §1.2 (`GarmentSummary`), §2.2 (families/categories) |
| **Status** | Structure, states, copy and contract bindings **settled** (Milestone 12). This brief is for **visual design only.** |

Self-contained brief for visual design. Cowork owns structure, states, copy and contract
bindings; Design owns spacing, typography, chrome colour, iconography and the visual treatment
of the components named here — within the hard constraints and the "must NOT change" list.

---

## 1. The screen and its states

A **filter / sort bar** above a **grouped card grid**. Visual design covers:

| State | What it shows |
|---|---|
| **Default (grouped, order = Hue)** | Per-category group sections, each with a header + count; within a group, the hue spectrum with neutral-primary garments last |
| **Order = Date added** | Same grouping; within each group, newest-first |
| **Filtered** | Category AND family active; clear-filters link; updated count |
| **Empty wardrobe** | `total: 0`, no filters; "add first garment" call to action |
| **Empty filter result** | `total: 0` with filters; "clear filters" offer |
| **Loading** | Skeleton cards |
| **Load failure (error)** | Error banner + retry |

---

## 2. Contract-bound field names and shapes — do not rename

### 2.1 Request — `GET /api/garments`

Query params (all optional, AND-combined): **`category`** (one FR-16 category — *renamed from
`type`*), **`family`** (one family name), **`order`** = **`hue`** (default) | **`date`**,
`limit` (default 500) / `offset`.

### 2.2 Response

```json
{ "garments": [ GarmentSummary ], "total": 137 }
```

`GarmentSummary` = `{ id, category, colours[], thumbnail_url }`; each colour =
`{ h, s, l, family, neutral, hex, proportion }`. The list arrives **flat, already ordered by
category then the chosen `order` key**; the client buckets it into per-category groups by
walking it (grouping is a client concern — there is no group object in the response).

---

## 3. User-facing copy and labels

- Controls: **"Category"** dropdown (*All categories* + region-grouped FR-16 categories),
  **"Colour"** dropdown (*All colours* + 20 families, each with its canonical swatch),
  **Order** segmented toggle **"Hue" / "Date added"**, **"Clear filters"** (only when active).
- Count, right-aligned: **"137 garments"** (from `total`).
- Group header: the **category name + count**, e.g. **"Jumper · 12"** (category title-cased).
- Card: thumbnail + proportional palette strip + **category** label. **No garment names.**
- Empty wardrobe: **"Your wardrobe is empty"** / "Photograph a garment and Hueniform will
  detect its colours." / **"Add your first garment"**.
- Empty filter: **"No garments match"** + a "Clear the filters" link.
- Load failure: **"Couldn't load your wardrobe."** + **Retry**.

---

## 4. Hard constraints (must hold in any visual design)

- Garments are **grouped by category**, with a visible **group header + count** per group (FR-47).
- **Order = Hue** arranges each group as a colour spectrum by the garment's **primary-colour
  hue**, with **neutral-primary garments after the chromatic spectrum** in a stable order;
  **Order = Date added** is newest-first. Default is **Hue** (FR-47).
- Palette swatches show the **measured colour** (`hex`), widths proportional to `proportion`;
  chrome may be greyscale but **swatches/palette strips show real colour** (FR-5).
- The family filter matches a family in **any** colour of a garment, any role (FR-35).
- Responsive at 500 garments; filter/order changes reflect in < 1 s (NFR-6).

---

## 5. Must NOT change (visual polish may not alter these)

1. The query-param names **`category`**, **`family`**, **`order`** and the `order` values
   **`hue`** / **`date`**.
2. `GarmentSummary` field names (`category`, `colours`, `thumbnail_url`, …).
3. **Grouping by category** and the **neutrals-after-hue-spectrum** ordering rule.
4. **Default order = Hue.**
5. **Measured-colour swatches** (FR-5) — never a representative hue; real colour in swatches.
6. **No garment names** — thumbnail + palette + category only.
7. The combinable category-AND-family filter semantics (family matches any role).

If a visual choice seems to require changing any of the above, **raise it with Cowork** rather
than absorbing it into the mockup.
