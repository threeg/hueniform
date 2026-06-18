# Hueniform — Functional Requirements

| | |
|---|---|
| **Document** | Requirements (living specification) |
| **Status** | Approved; amended for v0.2.0 (Milestone 10) |
| **Originally approved** | 12 June 2026 (Milestone 2, v0.1.0 MVP) |
| **Last amended** | 18 June 2026 — v0.2.0 requirement deltas (Milestone 10) |
| **Source** | Approved project brief (`docs/01-project-brief.md`); v0.2.0 brief (`docs/09-v0.2.0-brief.md`); interview decisions |
| **Repository location** | `docs/02-requirements.md` |

> **v0.2.0 amendment note (18 June 2026).** This document is the living spec; it
> evolves in place rather than being forked per version (v0.2.0 brief §1). The
> v0.2.0 delta pass (Milestone 10) **rewrites FR-16–FR-22** (the category & slot
> model), **adds FR-44–FR-51 and NFR-10**, **refines FR-41–FR-43**, and **amends
> FR-2, FR-32, FR-35, FR-36 and FR-39**. Superseded text is marked *(superseded —
> v0.2.0)* in place; numeric thresholds remain contractual (§1.4). The reasoning
> behind the FR-16–22 rewrite is recorded in
> `docs/spikes/2026-06-18-f4-category-slot-model.md`.

---

## 1. Conventions

1. Requirements are numbered **FR-n** (functional) and **NFR-n** (non-functional). Tickets must reference these identifiers.
2. *Shall* denotes a mandatory requirement; *should* denotes a strong preference that may be traded off with justification recorded in the relevant ticket.
3. All colour mathematics is defined in **HSL** space: hue **H** in degrees (0–360, wrapping), saturation **S** and lightness **L** as percentages (0–100). Hue distance is always the shorter way round the wheel (maximum 180°).
4. Numeric thresholds in this document are the contract for testing. They are expected to be defined as named constants in code so they can be tuned in one place; changing a value is a requirements change and shall be recorded here.
5. The brief's out-of-scope list is binding: no authentication, no hosting, no weather logic, no wear tracking, no automatic garment-type recognition, no pattern-clash logic.

---

## 2. Palette taxonomy

The taxonomy maps any RGB value (converted to HSL) to exactly one **colour family**. Families divide into **neutrals** and **chromatic families**.

**FR-1.** The application shall classify every detected colour into exactly one family from the taxonomy below, deterministically: the same HSL input always yields the same family.

**FR-2.** Neutral rules shall be evaluated first, in the order listed in the table below; the first matching rule wins. A colour matching no neutral rule shall be classified into the chromatic family owning its hue arc.

### 2.1 Neutral families

| Order | Family | Classification rule (HSL) |
|---|---|---|
| 1 | Black | L < 12 |
| 2 | White | L > 92 and S < 20 |
| 3 | Grey | S < 10 and 12 ≤ L ≤ 92 |
| 4 | Navy | 200 ≤ H ≤ 260 and S ≥ 10 and L < 25 |
| 5 | Denim | 200 ≤ H ≤ 250 and 10 ≤ S < 50 and 25 ≤ L ≤ 65 |
| 6 | Brown | 15 ≤ H ≤ 50 and 10 ≤ S ≤ 70 and 15 ≤ L < 45 |
| 7 | Beige/Tan | 20 ≤ H ≤ 60 and 10 ≤ S ≤ 45 and 60 ≤ L ≤ 88 |
| 8 | Cream | 20 ≤ H ≤ 70 and 10 ≤ S ≤ 45 and L > 88 |

> **Amended — v0.2.0 (F5).** **Cream** (order 8) is a new neutral family for pale
> warm near-neutrals (cream, ecru, ivory, off-white) that the v0.1.0 table
> mis-routed into the chromatic Yellow arc. Worked example: white/ecru jeans at
> roughly H ≈ 52°, S ≈ 28 %, L ≈ 90 % failed White (needs L > 92 **and** S < 20),
> Grey (needs S < 10) and Beige/Tan (needs L ≤ 88), and so fell through to Yellow;
> they now classify as **Cream**. The fix is a clean hand-off rather than a
> reshuffle: Beige/Tan still owns the warm band up to **L ≤ 88** and Cream owns
> **L > 88** for the same low-to-moderate saturation (S ≤ 45); the minor tuning is
> Cream's hue ceiling of **70°** (vs Beige/Tan's 60°) so pale yellow-creams are
> caught too. White (evaluated first, order 2) is unchanged, so a genuinely
> low-saturation pale colour (S < 20, L > 92) is still White. The thresholds are
> named constants per §1.4 (`CREAM_H_LOW = 20`, `CREAM_H_HIGH = 70`,
> `CREAM_S_LOW = 10`, `CREAM_S_HIGH = 45`, `CREAM_L_MIN = 88`).

**FR-3.** Neutral colours shall carry no hue for the purposes of harmony evaluation (§4): they are excluded from all hue-angle calculations. This applies to Cream as to every other neutral.

### 2.2 Chromatic families

Each chromatic family owns a 30° hue arc. The **representative hue** (arc centre) is used in explanations; harmony mathematics uses each colour's *measured* hue (§4).

| Family | Hue arc | Representative hue |
|---|---|---|
| Red | 345–15° | 0° |
| Orange | 15–45° | 30° |
| Yellow | 45–75° | 60° |
| Chartreuse | 75–105° | 90° |
| Green | 105–135° | 120° |
| Mint | 135–165° | 150° |
| Teal | 165–195° | 180° |
| Azure | 195–225° | 210° |
| Blue | 225–255° | 240° |
| Violet | 255–285° | 270° |
| Magenta | 285–315° | 300° |
| Pink | 315–345° | 330° |

**FR-4.** Arc boundaries are half-open: a hue equal to a boundary value belongs to the arc that *starts* at that value (e.g. H = 15° is Orange, not Red).

**FR-5.** The user-facing UI shall display family names together with a swatch of the *actual measured* colour, never the representative hue alone.

---

## 3. Proportion rules

**FR-6.** Colour detection shall describe each garment as 1–4 colours, each with an integer percentage proportion; proportions shall sum to exactly 100.

**FR-7.** Colour roles within a garment are defined as follows:

- **Primary:** the colour with the largest proportion (ties broken by higher saturation). Additionally, *any* colour with proportion ≥ 30% is treated as a primary; a garment with two such colours is **dual-primary**.
- **Secondary:** any non-primary colour with proportion ≥ 15% and < 30%.
- **Minor:** any colour with proportion < 15%.

**FR-8.** All primary colours of a garment shall satisfy the matching rules of the slot it occupies. A dual-primary garment qualifies only if *both* primaries qualify.

**FR-9.** Secondary colours on **anchor** garments (§5) shall be required to be *compatible*: each must be a neutral, in-scheme (§4), or echo (same family as) another chromatic colour already present on the anchors. Secondary colours on echo slots are required only to be neutral or an echo.

**FR-10.** Minor colours shall **never disqualify** a garment or combination.

**FR-11.** Minor colours may be used positively: when a minor colour on one garment shares a family with any chromatic colour elsewhere in the outfit, the combination earns an **echo bonus** in ranking (§8).

---

## 4. Colour harmony rules

Harmony is evaluated over the **scheme set**: the multiset of chromatic primary and secondary colours of the outfit's anchor garments (§5). Neutrals and minor colours are excluded (FR-3, FR-10).

**FR-12.** *Hue cluster.* Colours whose measured hues all lie within a 30° arc form a single cluster; a cluster's hue is the circular mean of its members.

**FR-13.** An outfit's scheme shall be determined by testing the scheme set against the definitions below **in this order**, taking the first that passes. The matched scheme's name is used in the explanation (FR-37).

| Order | Scheme | Definition (testable) |
|---|---|---|
| 1 | **Neutral-based** | The scheme set is empty (all anchor colours are neutral). |
| 2 | **Monochromatic** | All scheme-set hues fall within a single family's 30° arc. |
| 3 | **Analogous** | All scheme-set hues fall within a single 60° arc. |
| 4 | **Complementary** | The scheme set forms exactly two clusters whose hues are 180° ± 20° apart. |
| 5 | **Triadic** | The scheme set forms exactly three clusters whose hues are pairwise 120° ± 15° apart. |

**FR-14.** Neutrals shall never count against any scheme: an outfit of neutrals plus colours satisfying one of the definitions above is harmonious under that scheme.

**FR-15.** An outfit is **harmonious** if and only if (a) its scheme set satisfies at least one scheme per FR-13, and (b) every garment satisfies its slot-role rules (§5) and proportion rules (§3).

---

## 5. Category & slot model

> **Rewritten — v0.2.0 (F4).** This section replaces the v0.1.0 slot model
> (the original FR-16–FR-22, which assumed a fixed 1:1 type-to-slot mapping and a
> mandatory top+bottom+socks+shoes outfit). The reasoning is recorded in the design
> note `docs/spikes/2026-06-18-f4-category-slot-model.md`. The model is **top-down**:
> *category* (the user's tag) ≠ *slot* (a position) ≠ *region* (a body area). All
> numeric and named-set values below are contractual (§1.4) and are expected to be
> defined as constants in `matcher.constants` / `matcher.slots`.

### 5.1 Categories and regions

**FR-16.** *(Rewritten — v0.2.0; supersedes the v0.1.0 eight-type list.)* A garment
carries exactly **one category**. The categories, grouped by the body region and
slot they occupy, are exactly:

| Region | Slot(s) | Categories | Slot role |
|---|---|---|---|
| **Head** | head garment | `hat` | statement adornment |
| | head adornment | `glasses`, `earrings` | minor adornment |
| **Upper body** | layer stack (ordered base→outer) | `base`, `shirt`, `jersey`, `jacket` | anchor (layer) |
| | neck adornment | `tie`, `scarf` | statement adornment |
| | neck jewellery | `necklace` | minor adornment |
| | hand jewellery | `watch`, `ring`, `bracelet` | minor adornment |
| **Lower body** | lower-body garment | `trousers`, `jeans`, `shorts`, `skirt` | anchor |
| | one-piece (spans lower + upper-base) | `dress`, `jumpsuit` | anchor (one-piece) |
| | waist adornment | `belt` | statement adornment |
| **Feet** | feet | `socks`, `shoes` | statement adornment |

There is no automatic category recognition (out of scope, §1.5); the category is
assigned by the user (FR-31) and may later be edited directly (FR-46).

**FR-49.** *(New — v0.2.0.)* The taxonomy above is structured as **regions
containing slots**, with these structural rules:

1. **Upper-body layer stack.** The four upper-body layers are **ordered**
   base → shirt → jersey → jacket (innermost to outermost) and are each
   **independently optional**. A garment's category fixes its layer position. At
   most one garment occupies each layer.
2. **One-piece garments.** `dress` and `jumpsuit` are **one-piece**: a one-piece
   occupies the **lower-body slot and the upper-body `base` slot simultaneously**
   (see FR-50 for the exclusions this implies and FR-18 for its anchor behaviour).
3. **Adornment weight tiers.** Every non-anchor slot is either **statement** or
   **minor** (FR-21). Statement adornments are `hat`, `tie`, `scarf`, `belt`,
   `socks`, `shoes`. Minor adornments are `glasses`, `earrings`, `necklace`,
   `watch`, `ring`, `bracelet`.
4. **Adornment slots are independent.** Each adornment is its own optional slot,
   holding at most one garment, and the adornment slots are **not mutually
   exclusive**: any combination may be worn together — e.g. `glasses` *and*
   `earrings`; a `tie` *and* a `necklace`; a `ring` *and* a `bracelet`. The only
   co-occurrence restrictions are the anchor mutual-exclusion groups (FR-50);
   adornments never conflict with one another. Wearing two garments of the *same*
   category (e.g. two rings) is out of scope — one slot per category suffices for
   colour harmony.
5. **Jeans vs trousers.** `jeans` and `trousers` are distinct categories for
   inventory grouping (FR-47) but are treated identically by the matcher (both are
   ordinary lower-body anchor garments).

### 5.2 Slots, defaults and mutual exclusion

**FR-17.** *(Rewritten — v0.2.0; supersedes the v0.1.0 fixed required set.)* An
outfit is assembled from a **per-request slot selection** (FR-36). At most one
garment fills each slot, except that the upper-body layer stack may hold up to one
garment per layer. Adornment slots are independent and may be filled in any
combination (FR-49.4). The **lower-body slot is mandatory** (FR-51); every other
slot is optional and freely selectable per request.

**FR-50.** *(New — v0.2.0.)* The following **mutual-exclusion groups** hold; a
combination violating any of them is not a valid outfit:

1. **Lower-body exclusivity.** The lower-body slot holds exactly one garment, so
   `trousers`, `jeans`, `shorts`, `skirt`, `dress` and `jumpsuit` are mutually
   exclusive — no two may co-occur.
2. **One-piece spanning.** Because a one-piece (`dress`/`jumpsuit`) occupies the
   `base` slot as well as the lower-body slot, it **excludes a separate `base`
   garment and any separate lower-body garment**. Outer layers (`shirt`, `jersey`,
   `jacket`) may still be worn over a one-piece (FR-18).

**FR-51.** *(New — v0.2.0.)* Required slots are **configurable and removable per
request**, with one fixed floor:

1. **Default-selected slots** are `base`, the lower-body garment, `socks` and
   `shoes` — the v0.1.0 default carried forward, so the common case is unchanged.
2. The **lower-body slot is mandatory** and cannot be deselected (the waist is
   always covered). A one-piece satisfies the lower-body requirement.
3. **Every other slot is optional** and may be selected or deselected per request.
   *Example (beach):* deselecting `base` and `socks` yields a valid request of
   lower-body (`shorts`) + `shoes`.
4. **Minimum viable outfit.** A request that selects no lower-body slot, or selects
   no slots at all, is rejected and **fails fast** with a plain-language message
   (FR-36). No other floor applies: the upper body, feet, head and adornments may
   all be absent.

### 5.3 Anchors and layering

**FR-18.** *(Rewritten — v0.2.0.)* The **anchor garments** of an outfit are the
**lower-body garment** plus every present **upper-body layer**, with the
**outermost present upper-body layer dominant**. The dominant layer is the
outermost present of `jacket` → `jersey` → `shirt` → `base`. A **one-piece** is
always an anchor and is treated as the **lower-body anchor**; it additionally
occupies the `base` layer position, so when no separate layer is worn over it the
one-piece is also the dominant upper layer (counted once). When a `shirt`, `jersey`
or `jacket` is worn over a one-piece, that outer layer is dominant, but the
one-piece is **never** demoted to a covered layer (FR-20) — its lower portion
remains visible and always contributes (FR-19). Because the lower body is mandatory
(FR-51), at least one anchor always exists; when no upper-body layer is present the
lower-body garment is the sole anchor.

**FR-19.** *(Rewritten — v0.2.0.)* The **scheme set** (§4) is formed from: the
**dominant layer's** primary colour(s); the **lower-body garment's** primary
colour(s) (this is the one-piece itself when present); and **all anchors'**
secondary colours. Neutral and minor colours are excluded (FR-3, FR-10). Where the
dominant upper layer and the lower-body anchor are the **same** garment (an
uncovered one-piece), its colours are counted once.

**FR-20.** *(Rewritten — v0.2.0; generalised from three layers to four.)* A
**covered upper-body layer** — any present layer beneath the dominant layer — shall
not contribute primaries to the scheme set. Instead each covered layer is
constrained like a statement adornment (FR-21): each of its chromatic primary and
secondary colours must be in-scheme, or echo a chromatic colour present on the
anchors; otherwise it may be neutral. A **one-piece is exempt** from this rule (it
is always a contributing anchor, never a covered layer; see FR-18). *Rationale: the
outermost layer frames the outfit, but inner layers remain visible at collar, chest
and hem and must support rather than fight it; a one-piece's skirt/legs are always
on show.*

### 5.4 Statement and minor adornments

**FR-21.** *(Rewritten — v0.2.0; generalises "echo slots" into two weight tiers.)*
Every adornment slot carries a **weight tier** (FR-49.3):

- **Statement adornments** (`hat`, `tie`, `scarf`, `belt`, `socks`, `shoes`) behave
  as the v0.1.0 echo slots did: such a garment **qualifies if and only if** each of
  its primary and secondary colours is either (a) a neutral, or (b) an **echo** —
  the same family as a chromatic colour (primary, secondary or minor) present on any
  anchor garment. A statement adornment that fails this test **disqualifies** the
  combination.
- **Minor adornments** (`glasses`, `earrings`, `necklace`, `watch`, `ring`,
  `bracelet`) behave like minor colours (FR-10): they **never disqualify** a
  combination, whatever their colours.

**FR-22.** *(Rewritten — v0.2.0.)* Echoing a chromatic anchor colour — including a
*minor* anchor colour — attracts the **echo bonus** (FR-11, §8). This applies to
both tiers: a statement adornment that echoes earns the bonus, and a **minor
adornment that echoes** a chromatic anchor colour also earns it (so a minor
adornment can only ever help, never harm, an outfit's score).

---

## 6. Functional requirements by capability

### 6.1 Photo upload

**FR-23.** The application shall accept garment photographs in JPEG, PNG and WebP formats up to 20 MB, via file picker and drag-and-drop.

**FR-24.** Invalid uploads (unsupported format, oversize, unreadable file) shall be rejected with a plain-language error and no partial record created.

**FR-25.** The original photograph shall be stored on the local filesystem and associated with the garment record; it is displayed in the inventory and reused by *regenerate* (FR-33).

### 6.2 Colour detection

**FR-26.** On upload, the application shall automatically propose the garment's palette: 1–4 colours with proportions per FR-6, each classified per §2, with the garment isolated from the image background so background pixels do not contribute. (Anticipated implementation — segmentation plus pixel clustering — is an architecture concern, not a requirement.)

**FR-27.** Detection shall complete within the performance bound in NFR-4. Detection failure (e.g. garment cannot be isolated) shall fall back to whole-image clustering and inform the user that the result may include background colour.

### 6.3 Confirm-and-correct

**FR-28.** Before a garment is saved, the application shall present the proposed palette — swatch, family name and proportion per colour — for confirmation.

**FR-29.** The user shall be able to: adjust any proportion, remove a colour, add a colour manually (choosing a family and proportion), or accept the proposal unchanged. The UI shall keep proportions summing to 100 (normalising on save).

**FR-30.** A garment cannot be saved without an explicitly confirmed palette and a category (FR-31).

### 6.4 Garment type tagging

**FR-31.** During confirmation the user shall assign exactly one category from FR-16. There is no automatic category recognition (out of scope, §1.5).

### 6.5 Garment lifecycle

**FR-32.** *(Amended — v0.2.0, F3.)* Saved garments shall not be field-editable,
**except the garment's category**, which is directly editable per FR-46. The
palette remains regenerate-only (FR-33). *(Superseded — v0.2.0: the original blanket
"not field-editable" rule.)*

**FR-46.** *(New — v0.2.0, F3.)* A saved garment's **category** (FR-16) shall be
editable directly, without re-running detection and without re-entering the
confirm-and-correct flow. The edit is a single-field change to one of the FR-16
categories; the garment keeps its identifier and stored palette, and its
suggestion eligibility simply follows the new category and that category's slot
role (FR-49–FR-51). Colour/palette changes remain regenerate-only (FR-33). No other
metadata is editable in v0.2.0 (brand, season, notes and availability are deferred).

**FR-33.** Each garment shall offer **regenerate**: re-run colour detection (FR-26) on the stored photograph and re-enter the confirm-and-correct flow, including category selection; on confirmation the garment record is replaced in place (same identifier, so existing references remain valid).

**FR-34.** Each garment shall offer **delete**, with a confirmation step; deletion removes the record and its stored photograph.

### 6.6 Inventory browsing

**FR-35.** *(Extended — v0.2.0, F6.)* The inventory view shall display all garments with photograph thumbnail, palette swatches and category, filterable by (a) garment category and (b) colour family — matching any colour of the garment regardless of role. Filters shall be combinable (category AND colour). The existing filters are retained; grouping and ordering are added by FR-47.

**FR-47.** *(New — v0.2.0, F6.)* The inventory shall display garments **grouped by
category** (FR-16). Within each group, garments shall be orderable by either:

- **Hue** — arranged as a colour spectrum using each garment's **primary-colour
  hue** (FR-7); this is the **default** ordering. Neutrals (which carry no hue,
  FR-3) are ordered after the chromatic spectrum in a stable, defined order.
- **Date added** — newest first (left-to-right).

Search, multi-sort and multi-photo are out of scope for v0.2.0. NFR-6 (responsive at
500 garments) continues to apply to the grouped, ordered view.

### 6.7 Outfit request

**FR-36.** *(Amended — v0.2.0, F1/F2/F4.)* An outfit request shall let the user:

1. **Choose the slot selection** per FR-51 — select or deselect any slot, subject to
   the mandatory lower-body floor;
2. **Pin a garment** to its slot (FR-44);
3. **Anchor to a colour** — a colour family and/or a named scheme (FR-45);
4. **Choose how many** combinations to generate (FR-48).

The request **fails fast** with a clear message when it cannot be satisfied: an
empty selection or no lower-body slot (FR-51); an included slot with no eligible
garments in the inventory; or a pin/colour anchor that no harmonious combination can
honour (FR-44, FR-45). *(Superseded — v0.2.0: the original "required slots are
always included" wording, which assumed the fixed v0.1.0 required set.)*

**FR-44.** *(New — v0.2.0, F1.)* A request may **pin a specific garment** to its
slot ("build around this jacket / these shoes"). Every returned combination shall
include the pinned garment in that slot, and shall otherwise satisfy FR-15. The
pinned garment's slot is treated as selected. If no harmonious combination includes
the pinned garment, the request returns zero combinations with a plain-language
explanation (consistent with the FR-43 zero-result behaviour). More than one slot
may be pinned in a single request; all pins must be honoured simultaneously.

**FR-45.** *(New — v0.2.0, F2.)* A request may **anchor to a colour**, by either or
both of:

- a **target colour family** (e.g. "around teal") — every returned combination's
  scheme set (§4) shall include at least one colour of that family on an anchor
  garment; and/or
- a **named scheme** — one of the FR-13 schemes (`neutral-based`, `monochromatic`,
  `analogous`, `complementary`, `triadic`) — every returned combination shall match
  that scheme per FR-13.

When both are given, both constraints must hold. Colour anchoring composes with slot
selection (FR-51) and pinning (FR-44). If no harmonious combination satisfies the
anchor, the request returns zero combinations with a plain-language explanation
(FR-43).

### 6.8 Suggestion output

**FR-37.** Each returned combination shall include, per slot, the garment's thumbnail and palette, plus a plain-language explanation that names the matched scheme and the role each garment plays, e.g. *“Analogous scheme: teal jersey and azure trousers sit side by side on the wheel; navy shoes and grey socks are neutrals; the orange cap echoes the stripe in the socks.”*

**FR-38.** Explanations shall be generated from the actual evaluation (scheme matched per FR-13, roles per §5, echoes per FR-11) — never canned text disconnected from the result.

---

## 7. Suggestion behaviour

**FR-39.** *(Amended — v0.2.0, F7.)* A request shall return **up to *N*** combinations, ranked best-first, where *N* is the user-selected count (FR-48). Fewer (including zero) are returned only when fewer exist. *(Superseded — v0.2.0: the fixed "up to 3".)*

**FR-48.** *(New — v0.2.0, F7.)* The request shall carry a **suggestion count** *N*, an integer in the inclusive range **1–25**, **defaulting to 3**, presented as a setting *before* generation. Values outside 1–25 are rejected with a plain-language validation message (`COUNT_MIN = 1`, `COUNT_MAX = 25`, `COUNT_DEFAULT = 3`; §1.4). The count governs how many combinations are returned (FR-39); it does **not** relax the enumeration cap or the performance bound (NFR-5).

**FR-40.** No two returned combinations shall be identical; combinations differing in at least one garment count as distinct. Diversity beyond mere non-identity is governed by the variety factor (FR-41.3).

**FR-41.** *(Refined — v0.2.0, F5.)* Ranking shall order combinations by a score composed of, in descending weight:

1. **Scheme strength** — closeness of the scheme set to the scheme's ideal angles, normalised to [0, 1] (perfect for monochromatic; for complementary and triadic, smaller deviation from 180°/120° scores higher; for analogous, narrower spread scores higher). **All-neutral outfits are first-class results**: an empty scheme set matches the **neutral-based** scheme (FR-13 order 1) and is scored at strength `NEUTRAL_BASED_STRENGTH = 0.98`, i.e. just below a perfect chromatic scheme — so an all-neutral outfit ranks **just below an otherwise-equal chromatic scheme**, yet still above weaker chromatic schemes. (This corrects the v0.1.0 defect in which neutral outfits never surfaced.)
2. **Echo bonus** — `WEIGHT_ECHO_BONUS` × the count of distinct chromatic echoes (FR-11, FR-22), including minor-adornment echoes.
3. **Variety factor** — a greedy per-result penalty `WEIGHT_VARIETY` × (garments shared with an already-selected result), applied during selection so the same garments do not dominate the response. To strengthen diversity (F5), the variety penalty is raised and candidate **enumeration is interleaved** across distinct anchor garments so that genuinely different outfits are reached before the enumeration cap (NFR-5) is hit, rather than exhausting the budget on near-duplicates of one base.

Weights are named constants per §1.4: `WEIGHT_SCHEME_STRENGTH = 100`, `WEIGHT_ECHO_BONUS = 10`, `WEIGHT_VARIETY = 15` (raised from the v0.1.0 value of 5), `NEUTRAL_BASED_STRENGTH = 0.98`.

**FR-42.** *(Refined — v0.2.0, F5.)* Determinism across requests is not required: repeating an identical request may return different orderings or combinations, provided every returned combination satisfies FR-15. The variety/enumeration randomness shall be **seedable** (NFR-10): a fixed seed yields deterministic output for tests, while runtime uses an unseeded source.

**FR-43.** *(Refined — v0.2.0, F5.)* *Fallback ladder.* All-neutral outfits are now **normal first-class results** (FR-41) and are **not** labelled fallbacks. The ladder remains only for the genuinely-unsatisfiable case: if the (capped) main enumeration finds **no** combination satisfying FR-15, the application shall (a) retry restricted to **neutral-only** combinations — covering the case where the cap was exhausted before neutral combinations were reached — labelling any such result a *neutral fallback*; and (b) if none exists, return zero combinations with a plain-language explanation of why (e.g. which slot had no compatible garment) and, where identifiable, the slot that most constrained the search.

---

## 8. Non-functional requirements

**NFR-1.** The application shall run entirely on the owner's machine with **no internet dependency at runtime**, per the brief.

**NFR-2.** The application shall start with a **single command** (script or make target) that serves both the FastAPI backend and the React frontend locally and prints the URL to open.

**NFR-3.** All persistent state shall live in SQLite plus a local images directory, such that backing up the application's data is copying a single directory.

**NFR-4.** Colour detection for one photograph shall complete in under **5 seconds** on the owner's machine.

**NFR-5.** *(Amended — v0.2.0, F7.)* An outfit request shall return in under **2 seconds** for a wardrobe of up to **500 garments**, **including at the maximum requested count of 25 (FR-48)**. The 2-second bound is independent of the requested count: enumeration is capped (architecture §4.3) regardless of *N*, and selecting *N* results from the capped candidate pool is cheap. This shall be **re-baselined at 25 outfits / 500 garments in `test-perf`** when the F7 count and the F5 diversity changes land. If the search space requires it, the implementation may cap candidate enumeration, provided FR-39–FR-43 still hold; raising the cap to surface more distinct outfits (F5) must not breach this bound.

**NFR-6.** Inventory browsing shall remain responsive (filter changes reflected in under 1 second) at 500 garments.

**NFR-7.** The frontend shall target current versions of mainstream desktop browsers (Chrome and Firefox at minimum); no mobile layout is required (out of scope).

**NFR-8.** The application shall collect no telemetry and make no outbound network calls at runtime.

**NFR-9.** The colour matcher (taxonomy classification §2, proportion rules §3, harmony evaluation §4, the category & slot model §5, ranking §7) shall be implemented as pure functions independent of the web framework, so every numbered rule in those sections is unit-testable in isolation. The v0.2.0 additions — the Cream family (FR-2), the region/slot/adornment model (FR-49–FR-51) and the refined ranking (FR-41) — remain within this pure, standard-library-only matcher (the two-tier adornment model reuses the existing echo-slot and minor-colour primitives, adding no new harmony mathematics).

**NFR-10.** *(New — v0.2.0, F5.)* Suggestion **variety shall be seedable**: the randomness used for candidate enumeration and the variety factor (FR-41.3, FR-42) shall be supplied by an **injected random source**, so a fixed seed produces deterministic, unit-testable matcher output (preserving NFR-9 and supporting the golden-snapshot baseline), while runtime uses an unseeded source to deliver FR-42's permitted non-determinism. The matcher shall hold no global random state.

---

## 9. Decisions log (interview outcomes)

| Decision | Outcome |
|---|---|
| Brown classification | Added as a neutral (FR-2 table) |
| Layering dominance | Outermost layer dominates; covered layers constrained as echo-like (FR-18–FR-20) |
| Shoes role | Echo slot, per professional convention (FR-21) |
| Suggestion count | Up to 3 (FR-39) |
| No harmonious outfit | Fall back to neutral-based, then explain (FR-43) |
| Garment editing | No field editing; regenerate + delete (FR-32–FR-34) |

### 9.1 v0.2.0 decisions (Milestone 10 — F4 spike, 18 June 2026)

| Decision | Outcome |
|---|---|
| Category model | Top-down regions (head / upper body / lower body / feet) with a 4-level ordered upper-layer stack and weighted adornments (FR-16, FR-49). See `docs/spikes/2026-06-18-f4-category-slot-model.md`. |
| Lower-body categories | `trousers`, `jeans`, `shorts`, `skirt` (mutually exclusive) plus one-piece `dress`, `jumpsuit` (FR-16, FR-50) |
| One-piece behaviour | Always the lower anchor; occupies the `base` slot too; outer layers stack over it; never a covered layer (FR-18, FR-50) |
| Minimum viable outfit | **Lower body (waist) mandatory; everything else optional/removable** (FR-51) |
| Adornment weight | Two tiers — statement (echo-constrained: hat, tie, scarf, belt, socks, shoes) vs minor (never disqualifies: glasses, earrings, necklace, watch, ring, bracelet) (FR-21, FR-49). Belt is statement, encoding belt↔shoes coordination; the neck necklace is minor jewellery. Adornment slots are independent and combine freely (FR-49.4). |
| Edit category | Category directly editable; palette stays regenerate-only (FR-32, FR-46) |
| Build around a garment | Pin a garment to its slot (FR-44) |
| Build around a colour | A colour family and/or a named scheme — both may combine (FR-45) |
| All-neutral outfits | First-class results, scored at `NEUTRAL_BASED_STRENGTH = 0.98` — just below an otherwise-equal chromatic scheme (FR-41, FR-43) |
| Near-neutral taxonomy | New **Cream** neutral family (order 8) + minimal adjacent tuning (FR-2) |
| Suggestion count | User-selected **1–25, default 3** (FR-39, FR-48) |
| Count vs performance | NFR-5's 2 s bound retained (cap is count-independent); re-baseline at 25 outfits / 500 garments in `test-perf` (NFR-5) |
| Seedable variety | Variety randomness injected/seedable for testable, deterministic matcher output (NFR-10, FR-42) |
| Inventory grouping | Grouped by category; ordered by hue (default spectrum) or date added, newest first (FR-47) |

---

*Approval of the original document closed Milestone 2 (v0.1.0). Approval of the
v0.2.0 deltas above closes Milestone 10. This is a living specification; see
`docs/00-milestone-plan.md` for current status.*
