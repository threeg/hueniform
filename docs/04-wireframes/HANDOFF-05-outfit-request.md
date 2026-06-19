# Design handoff brief — Screen 5: Outfit Request

| | |
|---|---|
| **Screen** | Outfit request (`/suggest`); the request panel sits above the results (screen 6) on one page |
| **Wireframe of record** | [`05-outfit-request.md`](05-outfit-request.md) · [`05-outfit-request.html`](05-outfit-request.html) |
| **Binding contract** | `docs/03-api-contract.md` §2.12 (`POST /api/suggestions`), §1.3a (slot keys), §2.2 (`GET /api/taxonomy`) |
| **Status** | Structure, states, copy and contract bindings **settled** (Milestone 12). This brief is for **visual design only.** |

This brief is **self-contained**: Design should not need to re-derive anything from the
contract. Cowork owns the structure, states, navigation, copy and every field/label bound to
the API contract (below). Design owns spacing, typography, colour of the chrome, iconography,
motion and the visual treatment of the components named here — **within** the hard constraints
and the "must NOT change" list.

---

## 1. The screen and its states

A single **request panel** (sections 1–5 below) with results rendered beneath it. Visual
design covers all five states:

| State | What it shows |
|---|---|
| **Default** | FR-51 defaults selected; no pins/anchor/constraints; count 3 |
| **Category-constrained + anchored** | A slot's category checklist open (e.g. lower body = shorts/skirt); a colour family + scheme chosen; some default slots toggled off |
| **Pinned** | One or more removable pin chips; the pin picker modal; a one-piece auto-deselect note |
| **Searching** | Panel inert; results area shows a searching message |
| **Empty slot (error)** | `409` error banner; the named slot chip flagged "none in wardrobe" |

### Panel sections (top → bottom)
1. **Slots** — four region groups *Head / Upper body / Lower body / Feet*; every slot a toggle
   chip; multi-category slots carry an "any ▾" category-constraint control.
2. **Build around a garment** — "Pin a garment" button (opens a wardrobe picker modal) and a
   per-slot pin; active pins as removable chips.
3. **Build around a colour** *(optional)* — colour-family swatch-chips + a segmented scheme row.
4. **How many outfits?** — ± stepper.
5. **Generate** (primary) + hint line.

---

## 2. Contract-bound field names and shapes — do not rename

### 2.1 Slot keys (the request/response namespace — contract §1.3a / §2.2)

`base`, `shirt`, `mid`, `outer` (upper-body layers, in that innermost→outermost order);
`lower_body`; `hat`, `glasses`, `earrings`; `tie`, `scarf`, `necklace`, `watch`, `ring`,
`bracelet`; `belt`; `socks`, `shoes`.

**Display labels** (the only user-facing text for the layer slots): **Base · Shirt · Mid-layer
· Outer layer**. Other slots use their title-cased key (Hat, Glasses, Lower body, Socks…).

**Categories per slot** (the checklist contents; from `GET /api/taxonomy`): Base = t-shirt /
vest / long-sleeve; Shirt = shirt / blouse / polo; Mid-layer = jumper / hoodie / cardigan /
sweatshirt / track top / waistcoat; Outer layer = jacket / blazer / coat; Lower body =
trousers / jeans / chinos / shorts / skirt / dress / jumpsuit; Hat = hat / cap / beanie;
Glasses = glasses / sunglasses; Shoes = shoes / boots / trainers / sandals. (The rest are
single-category and have no checklist.)

### 2.2 Request body — `POST /api/suggestions`

```json
{
  "slots":  { "outer": true, "socks": false, "lower_body": { "categories": ["shorts", "skirt"] } },
  "pins":   { "outer": "<garment-id>" },
  "anchor": { "family": "Teal", "scheme": "analogous" },
  "count":  6
}
```

- `slots`: partial override of the defaults; each value is `true`, `false`, **or**
  `{ "categories": [...] }` (a non-empty subset of that slot's categories).
- `pins`: slot key → garment `id`.
- `anchor`: `{ "family"?, "scheme"? }`; `scheme` ∈ `neutral-based`, `monochromatic`,
  `analogous`, `complementary`, `triadic`.
- `count`: integer 1–25.

### 2.3 Response labels Design must accommodate (rendered in screen 6, summarised here for context)

`requested_count`; per combination `rank`, `scheme`, `fallback` (bool), `slots` (keyed by slot
key), `echoes` (`family`/`from_slot`/`to_slot`), `explanation`. Empty result carries
`explanation` + `hint`.

---

## 3. User-facing copy and messages (verbatim where quoted)

- Panel hint: **"The lower-body slot is always included; everything else is up to you."**
- Count label: **"How many outfits?"** with range hint **"(1–25)"**.
- Anchor section: **"Build around a colour"** *(optional)*; sub-labels **"Colour family"**,
  **"Scheme"**; scheme options include **"Any"**, **"Neutral-based"**, **"Monochromatic"**,
  **"Analogous"**, **"Complementary"**, **"Triadic"**.
- Pin: **"Pin a garment"**; picker actions **"Pin to request"** and **"Suggest outfits around
  this"**; one-piece note: **"A dress covers the base layer, so Base has been switched off for
  this request."**
- **`409 empty_slots`**: render the envelope `message` **verbatim** (server-provided, FR-36),
  e.g. *"You have no garments for the requested slot(s): outer layer."* Flag each slot in
  `details.empty_slots` inline with **"none in wardrobe"**; offer an **"Add a garment"** link.
- Searching: **"Searching your wardrobe for harmonious outfits…"**
- **Never invent garment names** — a garment is shown as thumbnail + palette + category (at most
  a derived "primary-family + category", e.g. "Teal dress").

---

## 4. Hard constraints (must hold in any visual design)

- **`lower_body` is mandatory** — rendered locked-on, cannot be deselected (FR-51).
- **Count is 1–25, default 3**, shown *before* Generate; the control clamps to the range (FR-48).
- A category checklist is a **non-empty subset** of that slot's own categories; un-ticking the
  last reverts to "any" (never an empty constraint) (FR-52).
- A **one-piece** pin, or a `lower_body` constraint to one-piece categories only,
  **auto-deselects `base`** with the note above (FR-50.2).
- Swatches show the **measured colour** (`hex`), never a representative hue (FR-5); chrome may
  be greyscale but **swatches/palette show real colour**.
- A pin **selects** its slot; a pin must agree with any category constraint on the same slot.
- Generate is an explicit action; **"Suggest outfits around this"** in the picker is the only
  pin-and-generate-in-one shortcut.

---

## 5. Must NOT change (visual polish may not alter these)

1. **Slot keys** `base`/`shirt`/`mid`/`outer`/`lower_body`/… and their display labels
   (Base/Shirt/Mid-layer/Outer layer).
2. The **request shape** `{ slots, pins, anchor, count }` and the `slots` value forms
   (`true`/`false`/`{categories}`).
3. **Count bounds** 1–25, default 3.
4. The **mandatory, non-deselectable** lower-body slot.
5. **Scheme names** and the family list (from the taxonomy) — names, not restyled values.
6. The fail-fast **`409`** behaviour and verbatim server `message`; the `details.empty_slots`
   per-chip flag.
7. **No garment names** anywhere — thumbnail + palette + category only.
8. Error codes/shape (`empty_slots`, `invalid_request`) are contract surface, not UI copy to
   reword (the human `message` is what's shown).

If a visual choice seems to require changing any of the above, **raise it with Cowork** — do not
absorb it into the mockup. (Cowork folds Design's returned visuals back into the wireframe
files; contract-bound fields, states and messages must survive that merge unchanged.)
