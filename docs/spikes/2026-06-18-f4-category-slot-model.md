# Design note — F4 category & slot-model spike

| | |
|---|---|
| **Document** | F4 spike output (design note) |
| **Date** | 18 June 2026 |
| **Milestone** | 10 — category-model design + requirement deltas |
| **Status** | Settled; drives the FR-16–22 rewrite and FR-49–51 in `docs/02-requirements.md` |
| **Repository location** | `docs/spikes/2026-06-18-f4-category-slot-model.md` |
| **Source** | v0.2.0 brief (`docs/09-v0.2.0-brief.md`) §F4, §7; scoping interview, 18 June 2026 |

This note records the *reasoning* behind the new category and slot model so the
"why" survives the requirement rewrite. The binding rules live in
`docs/02-requirements.md` §2 (taxonomy) and §5 (slots); this note explains how we
got there and what was deliberately left out.

---

## 1. The problem with the v0.1.0 model

In v0.1.0 a garment **type is its slot** (1:1): the eight types
(`top, bottom, jersey, jacket, socks, shoes, hat, accessory`) each map to exactly
one outfit slot of the same name (FR-16). Three v0.2.0 requirements break that
mapping:

1. **Several types compete for one position.** Trousers, shorts and a skirt are all
   "the lower-body garment" — three *types*, one *slot*.
2. **One type spans two positions.** A dress or jumpsuit occupies the lower body
   **and** the upper-body base at once.
3. **Slots are no longer all mandatory.** The fixed top+bottom+socks+shoes
   requirement (FR-17) must become a configurable, mostly-removable default.

So the model needs a thin abstraction the old one lacked: **category ≠ slot ≠
region**.

- **Category** — the tag the user assigns (the fuller list).
- **Slot** — a position in an outfit. An anchor slot or an adornment slot holds at
  most one garment; the upper-body layer stack holds at most one garment per layer.
- **Region** — a body area (head, upper body, lower body, feet) that groups slots
  and carries the mutual-exclusion rules.

This generalises the matcher's existing layer logic rather than replacing it: the
shipped code already stacks `top → jersey → jacket` with "outermost dominant"
(`slots.dominant_layer`, FR-18). We extend that idea, we do not discard it.

---

## 2. The model (top-down, "how you dress someone")

### 2.1 Regions and slots

Organised by region, with each slot's harmony role. Anchor slots drive harmony;
**statement** adornments are echo-constrained; **minor** adornments never
disqualify (see §2.5).

| Region | Anchor slots | Statement adornments | Minor adornments |
|---|---|---|---|
| **Head** | — | `hat` | `glasses`, `earrings` |
| **Upper body** | ordered layers `base` → `shirt` → `jersey` → `jacket` | `tie`, `scarf` (neck) | `necklace` (neck); `watch`, `ring`, `bracelet` (hands) |
| **Lower body** | one of `trousers` / `jeans` / `shorts` / `skirt`, **or** one-piece `dress` / `jumpsuit` | `belt` (waist) | — |
| **Feet** | — | `socks`, `shoes` | — |

The upper-body stack grows from 3 layers to **4** (`base, shirt, jersey, jacket`),
all independently optional — a person may wear any subset (including none →
"shirtless"). `base` ≈ t-shirt/vest; `shirt` ≈ collared shirt/blouse; `jersey` ≈
jumper/hoodie/cardigan; `jacket` ≈ coat/blazer.

### 2.2 Slot multiplicity (adornments are independent)

Each slot holds **at most one garment**, but **adornment slots are independent and
non-exclusive**: any combination of adornment slots may be worn together. You can
have glasses *and* earrings; a tie *and* a necklace; a ring *and* a bracelet; and so
on. The only co-occurrence restrictions are the anchor mutual-exclusion groups in
§2.4 — adornments never conflict with one another. (Wearing two of the *same*
category — two rings, say — is out of scope; one slot per category is sufficient for
colour harmony.)

### 2.3 Anchors and the scheme set (the matcher core)

The anchors are unchanged in spirit: **the lower-body garment plus every present
upper-body layer**, with the **outermost present upper layer dominant**
(`jacket > jersey > shirt > base`). The scheme set is the dominant layer's
primaries + the lower-body garment's primaries + all anchors' secondaries; covered
inner layers are excluded from primaries and constrained echo-like (the v0.1.0
FR-20 rule, now generalised across four layers instead of three).

Because the **lower body is mandatory**, an anchor always exists — the awkward
"no upper layer, no dominant" case from a naïve removable-slots design simply
cannot arise. When the upper region is empty, the lower-body garment is the sole
anchor and harmony is judged over it alone.

### 2.4 The one-piece (decision: *always lower anchor; layers stack over*)

A dress/jumpsuit is the one genuinely new behaviour. The matcher works on
whole-garment palettes, so we cannot split a dress into "upper colours" and "lower
colours". The resolution: a one-piece **occupies the lower-body slot and the
upper-body `base` slot**, and is **always the lower anchor** — its skirt/leg
portion is always visible, so its primaries always enter the scheme set via the
lower-body path. Layers (`shirt`/`jersey`/`jacket`) may stack over it; the
outermost becomes dominant exactly as usual. Crucially, a one-piece is **never**
demoted to a "covered layer" the way a covered `base` is — that distinction is
what keeps the visible skirt honest. A one-piece therefore *excludes* a separate
`base` and a separate lower-body garment, but not the outer layers.

When uncovered, the one-piece is simultaneously the dominant upper layer and the
lower anchor; it is the *same garment*, counted once (the scheme set is built from
the set of anchor garments, so no double-count occurs).

**Mutual-exclusion groups (anchors only):**

- The lower-body slot holds exactly one garment → trousers / jeans / shorts / skirt
  / dress / jumpsuit are mutually exclusive automatically.
- A one-piece additionally occupies the `base` slot → excludes a separate `base`.

### 2.5 Adornment weight (decision: two tiers)

Accessories differ in visual weight — a scarf reads, a watch does not. Rather than
invent new ranking maths, weight is captured with **two tiers that reuse existing
matcher concepts**:

- **Statement** — behaves like a v0.1.0 echo slot: every primary/secondary must be
  neutral or echo an anchor chromatic family, else the outfit is disqualified.
  Members: `hat`, `tie`, `scarf`, `belt`, `socks`, `shoes`.
- **Minor** — behaves like a minor colour (FR-10/FR-11): never disqualifies, but a
  colour match still earns the echo bonus. Members: `glasses`, `earrings`,
  `necklace`, `watch`, `ring`, `bracelet`.

The belt is deliberately **statement** — the app thereby encodes the
"belt coordinates with shoes" convention as a first-class rule. The neck `necklace`
is **minor** (a small jewellery layer alongside a tie/scarf, not a focal piece).

This mapping means the harmony layer needs **no new primitives**: statement
adornments are additional echo slots, minor adornments are additional minor-colour
sources. NFR-9 (pure, std-lib-only matcher) and the 100 % coverage gate are
preserved.

---

## 3. Configurable / removable slots (FR-51)

- **Default-selected** request slots: `base` (upper), the lower-body garment,
  `socks`, `shoes` — the v0.1.0 four, carried forward so the common case is
  unchanged.
- **Mandatory:** the lower-body slot only. It cannot be deselected (waist always
  covered).
- **Everything else** is freely (de)selectable per request. Beach example: deselect
  `base` and `socks` → request = lower-body (`shorts`) + `shoes`; the waist is
  covered, so it is a valid outfit.
- A request that selects no lower-body slot, or is otherwise empty, **fails fast**
  with a clear message (FR-36).

This is why the §7 Q2 "minimum viable outfit" question resolved to *waist
mandatory, torso optional* rather than the torso-cover floor first proposed: it
satisfies the brief's beach example and removes the no-anchor edge case in one
move.

---

## 4. Decisions settled in the interview (§7 of the brief)

| # | Question | Decision |
|---|---|---|
| 1 | Category list & exclusion groups | Top-down regions with a 4-level upper stack and weighted adornments (§2 above); lower-body exclusivity and one-piece spanning are the exclusion groups. Adornment slots are independent (§2.2). |
| 2 | Minimum viable outfit | **Lower body (waist) mandatory; everything else optional.** |
| 3 | "Build around a colour" | **Both** — a colour family and/or a named scheme (FR-45). |
| 4 | All-neutral outfits | **First-class results**, ranked just below an otherwise-equal chromatic scheme (FR-41/FR-43). |
| 5 | Near-neutral taxonomy | **Add a Cream family** plus minimal adjacent tuning (FR-2). |
| 6 | Count vs performance | Keep NFR-5's 2 s bound and the enumeration cap (cap is count-independent); **re-baseline at 25 outfits in `test-perf`**; surfacing 25 *distinct* outfits is the F5 diversity job. |

---

## 5. Deliberately out of scope

- **No per-accessory numeric weight.** Considered and rejected: two tiers capture
  the difference without continuous ranking maths that would be harder to keep
  deterministic and unit-testable.
- **No multiples of the same adornment category** (e.g. two rings): one slot per
  category is enough for colour harmony.
- **No metadata, availability flag, or multi-photo** — deferred by the brief (F3).
- **No storage/schema, API or wireframe changes here** — those are Milestones 11–13.
  This note and the FR rewrite specify *behaviour* only.
- **Jeans vs trousers** kept as separate categories at the user's request, though
  they are identical to the matcher (both ordinary lower-body garments); the
  distinction is for inventory grouping (FR-47), not harmony.

---

## 6. Risk flag — snapshot the matcher before implementing

The FR-16–22 rewrite changes the rules of the **100 %-covered, deterministic
matcher**: the layer stack deepens (3→4), the lower-body slot generalises, the
one-piece path is new, adornment slots multiply, the Cream family shifts some
classifications, and the all-neutral/diversity ranking changes scores. Per
`docs/meta/method-improvements.md` #2, a **golden-file snapshot baseline of current
matcher output (classification, ranking order + scores, explanation text) must be
captured *before* the M14 refactor**, so every behavioural change shows up as an
explicit, reviewable diff rather than a silent regression. M10 is spec-only; this
is a standing instruction for the implementation milestone and should become an
early E08 ticket (ahead of the slot-model code).
