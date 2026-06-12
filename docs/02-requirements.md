# Hueniform — Functional Requirements (MVP)

| | |
|---|---|
| **Document** | Requirements (Milestone 2) |
| **Status** | Draft for approval |
| **Date** | 12 June 2026 |
| **Source** | Approved project brief (`docs/project-brief.md`) plus interview decisions |
| **Repository location** | `docs/requirements.md` |

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

**FR-3.** Neutral colours shall carry no hue for the purposes of harmony evaluation (§4): they are excluded from all hue-angle calculations.

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

## 5. Slot role rules

### 5.1 Slots and garment types

**FR-16.** Garment types are exactly: `top`, `bottom`, `jersey`, `jacket`, `socks`, `shoes`, `hat`, `accessory`. Each garment carries exactly one type, and each type is eligible only for the outfit slot of the same name.

**FR-17.** Every outfit shall contain exactly one garment in each of the required slots — **top, bottom, socks, shoes** — and one garment in each *requested* optional slot: **jersey, jacket, hat, accessories** (jersey and jacket may both be requested).

### 5.2 Anchors and layering

**FR-18.** The **anchor garments** of an outfit are: the bottom, plus the upper-body layers, with the **outermost upper-body layer dominant**. The outermost layer is the jacket if present, otherwise the jersey if present, otherwise the top.

**FR-19.** The dominant layer's primary colour(s) and the bottom's primary colour(s), together with all anchors' secondary colours, form the scheme set (§4).

**FR-20.** Covered upper-body layers (e.g. the top beneath a jersey) shall not contribute primaries to the scheme set. Instead each covered layer is constrained like an echo slot: each of its chromatic primary and secondary colours must be in-scheme, or echo a chromatic colour present on the anchors; otherwise it may be neutral. *Rationale: the outer layer frames the outfit, but inner layers remain visible at collar, chest and hem and must support rather than fight it.*

### 5.3 Echo slots

**FR-21.** **Socks, shoes, hat and accessories** are echo slots. A garment qualifies for an echo slot if and only if each of its primary and secondary colours is either (a) a neutral, or (b) an **echo** — the same family as a chromatic colour (primary, secondary or minor) present on any anchor garment.

**FR-22.** Echoing a *minor* anchor colour is explicitly valid and attracts the echo bonus (FR-11, §8).

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

**FR-30.** A garment cannot be saved without an explicitly confirmed palette and a type tag (FR-31).

### 6.4 Garment type tagging

**FR-31.** During confirmation the user shall assign exactly one type from FR-16. There is no automatic type recognition (out of scope).

### 6.5 Garment lifecycle

**FR-32.** Saved garments shall not be field-editable.

**FR-33.** Each garment shall offer **regenerate**: re-run colour detection (FR-26) on the stored photograph and re-enter the confirm-and-correct flow, including type selection; on confirmation the garment record is replaced in place (same identifier, so existing references remain valid).

**FR-34.** Each garment shall offer **delete**, with a confirmation step; deletion removes the record and its stored photograph.

### 6.6 Inventory browsing

**FR-35.** The inventory view shall display all garments with photograph thumbnail, palette swatches and type, filterable by (a) garment type and (b) colour family — matching any colour of the garment regardless of role. Filters shall be combinable (type AND colour).

### 6.7 Outfit request

**FR-36.** An outfit request shall let the user choose which optional slots (jersey, jacket, hat, accessories) to include; required slots are always included. The request fails fast with a clear message if any included slot has no garments in the inventory.

### 6.8 Suggestion output

**FR-37.** Each returned combination shall include, per slot, the garment's thumbnail and palette, plus a plain-language explanation that names the matched scheme and the role each garment plays, e.g. *“Analogous scheme: teal jersey and azure trousers sit side by side on the wheel; navy shoes and grey socks are neutrals; the orange cap echoes the stripe in the socks.”*

**FR-38.** Explanations shall be generated from the actual evaluation (scheme matched per FR-13, roles per §5, echoes per FR-11) — never canned text disconnected from the result.

---

## 7. Suggestion behaviour

**FR-39.** A request shall return **up to 3** combinations, ranked best-first. Fewer (including zero) are returned only when fewer exist.

**FR-40.** No two returned combinations shall be identical; combinations differing in at least one garment count as distinct.

**FR-41.** Ranking shall order combinations by a score composed of, in descending weight: (1) **scheme strength** — closeness of the scheme set to the scheme's ideal angles (perfect for monochromatic/neutral-based; for complementary and triadic, smaller deviation from 180°/120° scores higher; for analogous, narrower spread scores higher); (2) **echo bonus** — count of distinct minor-colour echoes (FR-11); (3) a **variety factor** so the same garments do not dominate all three results in a single response. Exact weights are named constants per §1.4.

**FR-42.** Determinism across requests is not required: repeating an identical request may return different orderings or combinations, provided every returned combination satisfies FR-15.

**FR-43.** *Fallback ladder.* If no combination satisfies FR-15 for the requested slots, the application shall: (a) attempt **neutral-based** combinations only (every anchor colour neutral, echo slots neutral); (b) if none exists, return zero combinations with a plain-language explanation of why (e.g. which slot had no compatible garment) and, where identifiable, a hint such as the slot that most constrained the search. Fallback results shall be labelled as neutral-based fallbacks.

---

## 8. Non-functional requirements

**NFR-1.** The application shall run entirely on the owner's machine with **no internet dependency at runtime**, per the brief.

**NFR-2.** The application shall start with a **single command** (script or make target) that serves both the FastAPI backend and the React frontend locally and prints the URL to open.

**NFR-3.** All persistent state shall live in SQLite plus a local images directory, such that backing up the application's data is copying a single directory.

**NFR-4.** Colour detection for one photograph shall complete in under **5 seconds** on the owner's machine.

**NFR-5.** An outfit request shall return in under **2 seconds** for a wardrobe of up to **500 garments**. If the search space requires it, the implementation may cap candidate enumeration, provided FR-39–FR-43 still hold.

**NFR-6.** Inventory browsing shall remain responsive (filter changes reflected in under 1 second) at 500 garments.

**NFR-7.** The frontend shall target current versions of mainstream desktop browsers (Chrome and Firefox at minimum); no mobile layout is required (out of scope).

**NFR-8.** The application shall collect no telemetry and make no outbound network calls at runtime.

**NFR-9.** The colour matcher (taxonomy classification §2, proportion rules §3, harmony evaluation §4, slot rules §5, ranking §7) shall be implemented as pure functions independent of the web framework, so every numbered rule in those sections is unit-testable in isolation.

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

---

*Approval of this document closes Milestone 2.*
