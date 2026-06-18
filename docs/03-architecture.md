# Hueniform — System Architecture

| | |
|---|---|
| **Document** | Architecture (living document) |
| **Status** | Approved (Milestone 3); amended for v0.2.0 (Milestone 11) |
| **Originally approved** | 12 June 2026 (Milestone 3, v0.1.0) |
| **Last amended** | 18 June 2026 — v0.2.0 architecture deltas (Milestone 11) |
| **Source** | Approved project brief (`docs/01-project-brief.md`) and requirements (`docs/02-requirements.md`); v0.2.0 brief (`docs/09-v0.2.0-brief.md`); F4 spike (`docs/spikes/2026-06-18-f4-category-slot-model.md`) |
| **Repository location** | `docs/03-architecture.md` |
| **Companion document** | `docs/03-api-contract.md` (the HTTP contract; authoritative for all endpoint shapes) |

---

> **v0.2.0 amendment note (18 June 2026).** This is a living document; it evolves
> in place rather than being forked per version (v0.2.0 brief §1). The Milestone 11
> delta pass propagates the settled M10 decisions — the category & slot model
> (requirements §5, FR-16–FR-22, FR-49–FR-51), the Cream family (FR-2), the
> constrained/­counted suggestion request (FR-44, FR-45, FR-48, FR-51), all-neutral
> outfits as first-class results (FR-41), the slimmed fallback ladder (FR-43) and the
> seedable matcher RNG (NFR-10) — into **§2.1/§2.2** (the matcher module), **§3.1**
> (the data model) and **§4.3** (the outfit-request flow). The HTTP shapes are in the
> companion contract `docs/03-api-contract.md`. Requirements §1.4 numeric thresholds
> remain contractual and are referenced here, not restated. Superseded text is marked
> *(superseded — v0.2.0)* in place. The reasoning behind the slot-model rewrite is in
> the F4 spike note.

## 1. Architectural overview

Hueniform is a local-first, single-user web application: a **React single-page application** served as static files by a **FastAPI backend**, persisting to **SQLite plus a local images directory**. All colour reasoning lives in a **pure, framework-independent matcher module** (NFR-9); colour detection (segmentation plus clustering, FR-26/FR-27) is a separate pipeline that depends on the matcher's taxonomy but nothing else of it.

```
┌──────────────────────────── Browser ────────────────────────────┐
│  React SPA (Vite + TypeScript)                                  │
│  upload & confirm UI · inventory browser · outfit request UI    │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP/JSON  (see api-contract.md)
┌────────────────────────────▼────────────────────────────────────┐
│  FastAPI (single Uvicorn process)                               │
│  ├─ static mount: serves built SPA at /                         │
│  ├─ api/        routers + Pydantic schemas (/api/…)             │
│  ├─ services/   orchestration (detection, garments, suggestions)│
│  ├─ detection/  rembg segmentation + k-means clustering         │
│  ├─ matcher/    PURE colour logic — no framework imports        │
│  └─ storage/    SQLModel models · image store · staging store   │
└───────┬──────────────────────────────┬──────────────────────────┘
        ▼                              ▼
  data/hueniform.db              data/images/ · data/thumbnails/
  (SQLite)                       data/staging/ · data/models/
```

One process, one data directory, no outbound network traffic at runtime (NFR-1, NFR-2, NFR-3, NFR-8).

---

## 2. Component breakdown

### 2.1 Module layout and the dependency rule

```
backend/
  app/
    main.py            FastAPI app factory; routers; static SPA mount; startup sweep
    api/               HTTP layer: routers and Pydantic request/response schemas
    services/          use-case orchestration (detection, garment lifecycle, suggestions)
    detection/         image → proposed palette (rembg + scikit-learn)
    matcher/           pure colour logic (NFR-9) — standard library only
    storage/           SQLModel models, engine/session, image & staging stores
frontend/
  src/                 React + TypeScript SPA (Vite)
scripts/               run / setup entry points (Makefile + shell script)
data/                  runtime state — gitignored (NFR-3)
docs/  tickets/        per the brief's repository strategy
```

The **dependency rule** is enforced by convention and tested in CI-style unit tests (Milestone 5 will define how): `matcher` imports only the Python standard library; `detection` may import `matcher.taxonomy` plus its image/maths libraries; `services` may import `detection`, `matcher` and `storage`; `api` imports only `services` and its schemas. Nothing imports `api`. This keeps every numbered rule in requirements §2–§5 and §7 unit-testable with plain values (NFR-9).

**v0.2.0 (F4) — the rule is unchanged; the slot model stays inside the matcher.** The
rewritten category & slot model (requirements §5: regions, the four-level upper-body
layer stack, one-piece garments, the statement/minor adornment tiers) lives entirely
in `matcher` (`slots.py`, `constants.py`). It adds **no new harmony mathematics**: a
statement adornment is evaluated exactly as a v0.1.0 echo slot, and a minor adornment
exactly as a minor colour (FR-21, FR-22), so the two tiers reuse the existing
echo-slot and minor-colour primitives. The matcher therefore remains pure and
standard-library-only (NFR-9), and the 100 % line+branch coverage gate continues to
apply to it. The seedable variety RNG (NFR-10) is **injected** into the matcher rather
than held as global state, so determinism is a property of the caller's seed, not of
the module (see §4.3). No layer gains a dependency; in particular nothing new imports
`api`, and `storage` still imports none of the upper layers.

### 2.2 The matcher (pure module)

`matcher` is a package of pure functions over small frozen dataclasses. Its submodules map one-to-one onto the requirements sections so a test file can mirror each:

| Submodule | Responsibility | Requirements |
|---|---|---|
| `constants.py` | Every numeric threshold and named set as a constant: arc widths, tolerances, role cut-offs, ranking weights, candidate cap; **v0.2.0** — the Cream thresholds, the category set, slot keys, the upper-body layer order, the statement/minor adornment membership, the default-selected slots, `NEUTRAL_BASED_STRENGTH`, the raised `WEIGHT_VARIETY`, and the count bounds (`COUNT_MIN/MAX/DEFAULT`) | Req. §1.4 |
| `colour.py` | RGB↔HSL conversion, wrapping hue distance (max 180°), circular mean | Req. §1.3, FR-12 |
| `taxonomy.py` | Family classification: ordered neutral rules, then chromatic arcs; half-open boundaries; canonical HSL per family. **v0.2.0** — adds the **Cream** neutral family (order 8) for pale warm near-neutrals | FR-1–FR-5 (FR-2) |
| `roles.py` | Primary / dual-primary / secondary / minor derivation from proportions | FR-6–FR-11 |
| `harmony.py` | Clustering of hues, ordered scheme test (neutral-based → monochromatic → analogous → complementary → triadic) | FR-12–FR-15 |
| `slots.py` | **v0.2.0 — region/slot/role model.** Category→slot mapping; the four-level upper-body layer stack (`base → shirt → jersey → jacket`) with outermost-dominant; one-piece garments (lower-body anchor that also occupies `base`, never a covered layer); covered-layer constraint generalised across four layers; the two adornment tiers (statement = echo-constrained; minor = never disqualifies), each reusing the existing echo-slot/minor-colour primitives; mutual-exclusion groups and the mandatory lower-body floor | FR-16–FR-22, FR-49–FR-51 |
| `ranking.py` | Score composition (scheme strength, echo bonus, variety factor) and the fallback ladder. **v0.2.0** — all-neutral outfits scored first-class at `NEUTRAL_BASED_STRENGTH`; minor-adornment echoes credited in the echo bonus; raised variety penalty with **anchor-interleaved enumeration** so diverse outfits are reached before the cap; selection of the top *N* (FR-48) from the capped pool; variety/enumeration randomness from an **injected** RNG | FR-39–FR-43, FR-48, NFR-5, NFR-10 |
| `explain.py` | Plain-language explanation rendered from the evaluation result object | FR-37, FR-38 |

The central design point for FR-38: evaluation returns an **`EvaluationResult`** value (matched scheme, per-garment roles, the echoes found, score components, and — on failure — the constraining slot). `explain.py` renders text *only* from this object, so explanations cannot drift from the evaluation. Garment roles (primary/secondary/minor) are **derived at evaluation time** from stored proportions, never persisted, so FR-7 has a single source of truth. **v0.2.0:** the result also distinguishes a **first-class neutral-based** outfit (scheme `neutral-based`, scored at `NEUTRAL_BASED_STRENGTH`, FR-41) from a **neutral fallback** (FR-43a), so the contract's `scheme`/`fallback` fields (contract §2.12) are rendered from the evaluation rather than inferred by the API.

> **Regression-snapshot baseline (v0.2.0, standing instruction for M14).** The slot-model
> rewrite changes the rules of the 100 %-covered, deterministic matcher: the layer stack
> deepens 3→4, the lower-body slot generalises, the one-piece path is new, adornment slots
> multiply, the Cream family shifts some classifications, and the all-neutral/diversity
> ranking changes scores. Before the E08 refactor (Milestone 14), a **golden-file snapshot
> of current matcher output** — family classifications, ranking order **and** scores, and
> explanation text — must be captured and committed, so every behavioural change in the
> rewrite surfaces as an explicit, reviewable diff rather than a silent regression
> (`docs/meta/method-improvements.md` #2; F4 spike §6 risk flag). This is recorded here as
> an architecture/test-strategy commitment; the **mechanism** (fixtures, the snapshot test
> and its update workflow) is specified in the test-strategy delta (Milestone 13), and it
> should be an **early E08 ticket, ahead of the slot-model code**. The injected, seedable
> RNG (NFR-10) is what makes such a snapshot stable for the otherwise non-deterministic
> ranking (FR-42).

### 2.3 The detection pipeline

`detection` turns a photograph into a proposed palette (FR-26):

1. **Decode & validate** with Pillow (format, size, readability — FR-23/FR-24 enforced at the API boundary before this pipeline runs).
2. **Segment** the garment with rembg (U²-Net via onnxruntime), producing an alpha mask. The model file is fetched once at install time into `data/models/` (`U2NET_HOME` points there); at runtime inference is fully offline (NFR-1, NFR-8).
3. **Fallback check** (FR-27): if the mask covers below a minimum-foreground constant or segmentation raises, fall back to whole-image pixels and set `fallback_used = true` so the API can warn the user.
4. **Cluster** masked pixels with scikit-learn `KMeans` for k = 1…4 (downsampled pixel sample for the NFR-4 bound), choosing k by an inertia-elbow heuristic, then merging clusters whose centroids classify into the same family.
5. **Convert & classify**: centroids → HSL (`matcher.colour`) → family (`matcher.taxonomy`); cluster weights → integer proportions normalised to exactly 100 (FR-6).

The pipeline runs **synchronously inside the request** — the 5-second bound (NFR-4) makes a job queue unnecessary complexity.

### 2.4 Services and API layer

`services` owns the use cases described in §4 (flows), transactional boundaries, and the staging store. `api` is a thin translation layer: Pydantic validation in, schema objects out, error mapping to the envelope defined in the API contract. The colour `family` is **always computed server-side** from submitted HSL (FR-1's determinism is never delegated to the client).

### 2.5 Frontend

A Vite + TypeScript React SPA with four areas: upload & confirm-and-correct, inventory browser with combinable filters, garment detail (regenerate/delete), and outfit request/results. Server state is cached with TanStack Query so filter changes hit memory or a fast indexed query (NFR-6); routing via React Router; styling via CSS Modules (no heavyweight UI kit for a single-user tool). The proportion editor enforces the sum-to-100 rule with normalise-on-save (FR-29). In production the SPA is static files served by FastAPI; in development Vite's dev server proxies `/api` to Uvicorn.

---

## 3. Data model

### 3.1 Entities

Two persistent entities suffice. Suggestions are computed, not stored (FR-42 imposes no persistence); unconfirmed detections deliberately stay **out of the database** (FR-24: no partial record) and live in the staging store (§3.3).

**`garments`**

| Column | Type | Notes |
|---|---|---|
| `id` | TEXT, PK | UUID4 string; stable across regeneration (FR-33) and across a category edit (FR-46) |
| `type` | TEXT, NOT NULL | The garment's **category** (FR-16). One of the FR-16 category values; CHECK constraint. *(v0.2.0: the **value set** changes to the FR-16 categories — see note below — but the column, its name and its index are unchanged. The API exposes this field as `category`; the column keeps the name `type`.)* |
| `image_file` | TEXT, NOT NULL | Filename in `data/images/`, original format preserved (FR-25) |
| `thumbnail_file` | TEXT, NOT NULL | Filename in `data/thumbnails/` (WebP, longest edge 320 px) — generated at save so inventory browsing stays responsive (FR-35, NFR-6) |
| `created_at` | TEXT, NOT NULL | ISO 8601 UTC |
| `regenerated_at` | TEXT, NULL | ISO 8601 UTC; set when a regeneration is confirmed |

**`garment_colours`** — 1–4 rows per garment (FR-6)

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER, PK | Autoincrement |
| `garment_id` | TEXT, FK → `garments.id` | `ON DELETE CASCADE` (FR-34) |
| `position` | INTEGER, NOT NULL | 0–3; display order, descending proportion |
| `h` | REAL, NOT NULL | 0 ≤ h < 360; measured hue stored even for neutrals (display honesty, FR-5) |
| `s` | REAL, NOT NULL | 0–100 |
| `l` | REAL, NOT NULL | 0–100 |
| `family` | TEXT, NOT NULL | Denormalised, deterministically derived from (h, s, l) on write (FR-1); stored solely so the FR-35 colour filter is an indexed query |
| `proportion` | INTEGER, NOT NULL | 1–100; CHECK; per-garment sum is validated as exactly 100 in the service layer |

Indices: `idx_garments_type (garments.type)`, `idx_colours_family (garment_colours.family)`, `idx_colours_garment (garment_colours.garment_id)`. With both filter columns indexed, the combined category-AND-family query is comfortably inside NFR-6 at 500 garments. `idx_garments_type` also serves the FR-47 grouping (by category) and the date/hue ordering query.

> **v0.2.0 (F3/F4/F6) — no schema change.** The category model and its new features
> require **no change to the table shapes**:
>
> - **Category value set (FR-16, F4).** The `garments.type` CHECK constraint's
>   *allowed values* become the FR-16 categories — `base`, `shirt`, `jersey`, `jacket`
>   (upper-body layers); `trousers`, `jeans`, `shorts`, `skirt`, `dress`, `jumpsuit`
>   (lower body, the last two one-piece); `hat`, `glasses`, `earrings`, `tie`, `scarf`,
>   `necklace`, `watch`, `ring`, `bracelet`, `belt` (head/neck/hand/waist adornments);
>   `socks`, `shoes` (feet) — superseding the v0.1.0 eight-type list. This is a constant
>   change (the allowlist), not a column or index change. The slot a category occupies,
>   its region and its harmony role are **derived in the matcher** (`matcher.slots`),
>   not stored — so no new column is needed.
>
>   **Data migration (no schema change, M14).** The `type` → `category` rename is
>   **API-only** — the DB column keeps the name `type` (contract §1.3), so the rename
>   moves and drops nothing. The **value** change, however, needs a one-off migration of
>   existing rows *before* the new CHECK allowlist is applied (the old values would
>   otherwise fail the constraint):
>     - **Carry over unchanged:** `jersey`, `jacket`, `socks`, `shoes`, `hat`.
>     - `top` → `base` (sensible default; a collared shirt stored as `top` would ideally
>       be re-tagged `shirt`).
>     - `bottom` → **ambiguous**: one of `trousers` / `jeans` / `shorts` / `skirt` —
>       needs a default plus a manual re-categorisation pass (FR-46).
>     - `accessory` → **ambiguous**: one of `hat` / `belt` / `tie` / `scarf` /
>       `necklace` / `watch` / `ring` / `bracelet` / `glasses` / `earrings` — manual
>       re-categorisation (FR-46).
>
>   The migration mechanism and the handling of the two ambiguous cases belong to the
>   test-strategy delta (M13) and an early M14 ticket; they are recorded here so they are
>   not lost, not implemented here. FR-46's `PATCH /api/garments/{id}` is the tool for the
>   manual pass.
> - **Direct category edit (FR-46, F3).** Editing a garment's category writes a single
>   value to `garments.type` (validated against the FR-16 allowlist) and **touches
>   nothing else** — no colour rows, no image, no re-detection, same `id`. The palette
>   stays regenerate-only (FR-32/FR-33). Suggestion eligibility simply follows the new
>   category and its slot role at evaluation time. *(See contract §2.10a — `PATCH
>   /api/garments/{id}`.)*
> - **Metadata, availability and multi-photo remain DEFERRED (F3).** No `brand`,
>   `season`, `notes`, availability flag or additional image columns are added in
>   v0.2.0; the two-entity model stands.
> - **Inventory ordering (FR-47, F6).** Hue-spectrum ordering uses each garment's
>   **primary colour** — the `garment_colours` row at `position = 0` (descending
>   proportion, FR-7) — with neutral-primary garments ordered after the chromatic
>   spectrum in a stable, defined order; date ordering uses `created_at` newest-first.
>   Both are applied in the service/query layer over the existing rows and indices; no
>   schema change and no new persisted ordering value.

SQLite runs with `PRAGMA foreign_keys = ON` and WAL journal mode. Models are declared with **SQLModel**, giving one class per table shared between persistence and (via separate API schemas) validation.

### 3.2 Disk layout (NFR-3)

```
data/
  hueniform.db          SQLite database
  images/{id}.{ext}     original photographs, named by garment UUID
  thumbnails/{id}.webp  derived thumbnails
  staging/              unconfirmed uploads (see §3.3) — excluded from backup advice
  models/               rembg ONNX model, fetched at install time
```

Backing up the application is copying `data/` — a single directory.

### 3.3 Staging store (unconfirmed detections)

`POST /api/detections` writes the validated upload to `data/staging/{token}.{ext}` plus a JSON sidecar `{token}.json` holding the proposal, `fallback_used`, the original content type and, for regenerations, the bound `garment_id`. Tokens are UUID4 strings with a 1-hour TTL; expired entries are swept at startup and lazily on access. Confirming a garment **moves** the staged image into `data/images/` and inserts the `garments` + `garment_colours` rows in one transaction; abandoning the flow leaves nothing in the database (FR-24, FR-30).

---

## 4. Key flows

### 4.1 Upload → detect → confirm → save (FR-23–FR-31)

1. SPA `POST /api/detections` (multipart). API validates format and the 20 MB limit (FR-23); rejection returns a plain-language error and writes nothing (FR-24).
2. Detection service stages the file, runs the §2.3 pipeline, stores the proposal in the sidecar, and returns it: token, per-colour swatch values (h, s, l, hex), family names, proportions, and `fallback_used` (FR-27's user warning, FR-28).
3. SPA renders the confirm-and-correct screen (image preview served from staging). The user adjusts proportions, removes or manually adds colours (canonical HSL for the chosen family, from `GET /api/taxonomy`), and selects the mandatory **category** (FR-29, FR-31; v0.2.0 — one of the FR-16 categories).
4. SPA `POST /api/garments` with the token, category and confirmed colours. The service re-derives every family server-side, validates count and the sum of 100, then in one transaction moves the image, generates the thumbnail and inserts both tables (FR-30, FR-25). Response: the saved garment.

### 4.2 Regenerate (FR-32–FR-33)

1. SPA `POST /api/garments/{id}/regenerate`. The service runs the detection pipeline on the **stored** photograph and returns a fresh proposal with a regeneration token bound to the garment.
2. The user passes through the same confirm-and-correct flow, including category selection.
3. SPA `PUT /api/garments/{id}` with the regeneration token, category and colours. The service replaces the colour rows and category **in place** — same `id`, same image — and stamps `regenerated_at`. Requiring the token is how FR-32's *palette* immutability is enforced architecturally: `PUT` is honoured only as the completion of a regeneration. *(v0.2.0: the **category** alone is additionally editable directly via `PATCH /api/garments/{id}` without a token or re-detection — FR-46, contract §2.10a; that path never touches the palette.)*

### 4.3 Outfit request → evaluation → ranked suggestions (FR-36–FR-45, FR-48–FR-51, NFR-5, NFR-10)

> **Rewritten — v0.2.0 (F1/F2/F4/F5/F7).** The v0.1.0 flow assumed a fixed
> top+bottom+socks+shoes outfit, three fixed upper layers, "up to 3" results and
> all-neutral outfits only as a fallback. The flow below replaces it: a configurable,
> mostly-removable slot selection over the new region/slot model with a mandatory
> lower-body floor (FR-51); optional pins (FR-44) and colour/scheme anchors (FR-45); a
> user-chosen count *N* (FR-48); all-neutral outfits as first-class results (FR-41);
> the slimmed fallback ladder (FR-43); and a seedable RNG (NFR-10). The HTTP request
> and response shapes are the companion contract §2.12.

1. **Request and fail-fast.** SPA `POST /api/suggestions` carrying the slot selection,
   any pins, an optional colour/scheme anchor and the count *N* (contract §2.12). The
   service resolves the **selected slot set** by layering the request over the FR-51
   defaults (`base`, the lower-body slot, `socks`, `shoes`), enforces the **mandatory
   lower-body floor** (FR-51), loads the inventory grouped by category, and **fails
   fast** (FR-36) when: no lower-body slot is selected or the selection is empty; a
   *selected* slot has no eligible garment (`409 empty_slots`, naming the slots); or a
   pin/anchor cannot be honoured (handled at step 6 as a zero result). A pin marks its
   slot selected (FR-44); a pin to the lower-body slot of a **one-piece** is
   incompatible with a separately selected `base` (FR-50.2) and is rejected up front.
2. **Anchor enumeration** (seedable, capped). Candidates are built anchors-first over
   the selected slots: the **lower-body garment** (one of `trousers`/`jeans`/`shorts`/
   `skirt`, or a one-piece `dress`/`jumpsuit`) × the present **upper-body layers**
   (`base`, `shirt`, `jersey`, `jacket`), with the **outermost present layer dominant**
   (`jacket > jersey > shirt > base`, FR-18). A one-piece fills the lower-body slot
   **and** the `base` slot, excludes a separate `base` and a separate lower-body
   garment (FR-50), and is never demoted to a covered layer (FR-18/FR-20). Any **pins**
   fix their slot to one garment, shrinking the space. Enumeration is **interleaved
   across distinct anchor garments** (F5 diversity) and **capped** by the
   count-independent named constant (`MAX_ANCHOR_CANDIDATES`); the shuffle and
   interleave draw from an **injected `random.Random`** (NFR-10) — a fixed seed in
   tests, an unseeded source at runtime (FR-42). The cap does **not** scale with *N*
   (NFR-5).
3. **Anchor evaluation** (pure matcher): build the scheme set — dominant-layer
   primaries, lower-body primaries (the one-piece itself when present, counted once),
   and all anchors' secondaries (FR-19) — test schemes in FR-13 order (including
   **neutral-based** when the scheme set is empty); check anchor secondary
   compatibility (FR-9) and the covered-layer constraint across the four layers
   (FR-20). If a **colour/scheme anchor** is set (FR-45), prune any candidate whose
   scheme set lacks the target family or whose matched scheme is not the named one.
   Failures are pruned immediately.
4. **Adornment slots (two tiers).** For each surviving anchor set, **statement**
   adornments (`hat`, `tie`, `scarf`, `belt`, `socks`, `shoes`) qualify only if every
   primary/secondary is neutral or echoes an anchor colour (FR-21) — a failing one
   disqualifies the combination; **minor** adornments (`glasses`, `earrings`,
   `necklace`, `watch`, `ring`, `bracelet`) never disqualify (FR-10/FR-21). Echoes of
   any chromatic anchor colour — including minor-anchor and minor-adornment echoes —
   are recorded for the bonus (FR-11, FR-22). Adornment slots are independent and
   combine freely (FR-49.4).
5. **Scoring and selection** (`matcher.ranking`): scheme strength — with an empty
   (all-neutral) scheme set scored **first-class** at `NEUTRAL_BASED_STRENGTH`, just
   below a perfect chromatic scheme (FR-41) — then the echo-bonus count, then a
   **raised** variety penalty applied greedily during selection so results do not
   reuse the same garments (FR-41.3). The top **_N_** distinct combinations (FR-48,
   1–25) are returned best-first (FR-39, FR-40); selecting *N* from the capped pool is
   cheap, so the NFR-5 bound holds at the maximum count (re-baselined in `test-perf`).
6. **Fallback ladder** (FR-43, slimmed). All-neutral outfits are now **normal
   first-class results** (step 5) and are **not** fallbacks. Only when the capped main
   enumeration yields **no** combination satisfying FR-15 does the ladder run: (a)
   retry restricted to **neutral-only** combinations — covering a cap exhausted before
   neutral combinations were reached — labelling any result a **neutral fallback**; and
   (b) if none exists, return **zero** combinations with a plain-language explanation
   and, where identifiable, the most constraining slot. An unsatisfiable pin or anchor
   (FR-44/FR-45) resolves here as a zero result with the reason named.
7. **Explanation** (FR-37/FR-38): rendered per combination from its `EvaluationResult`,
   naming the matched scheme (including `neutral-based`), each garment's role and slot,
   and the echoes credited.

---

## 5. Startup and runtime topology

- **`make setup`** (one-time, online): creates the Python virtual environment, installs pinned dependencies, fetches the rembg model into `data/models/`, installs frontend dependencies and builds the SPA into `frontend/dist/`.
- **`make run`** (the NFR-2 single command, offline): initialises `data/` and the schema if absent, sweeps the staging store, starts one Uvicorn process serving the API under `/api` and the built SPA at `/` (history-API fallback to `index.html`), and prints the URL to open (`http://127.0.0.1:8000`).
- **`make dev`** (development convenience, not a requirement): Uvicorn with reload plus the Vite dev server proxying `/api`.

At runtime the process binds to localhost only, makes **no outbound calls** and collects **no telemetry** (NFR-1, NFR-8): the segmentation model is read from disk, and no library update checks are enabled. Same-origin serving means no CORS configuration in production.

---

## 6. Technology choices

All choices sit within the brief's binding stack (Python + FastAPI, React SPA, SQLite + local files).

| Concern | Choice | One-line rationale |
|---|---|---|
| Language / runtime | Python 3.12 | Current stable; full typing support for the pure matcher |
| Web framework | FastAPI + Uvicorn | Brief-mandated; Pydantic validation and generated OpenAPI back the written contract |
| Data layer | SQLModel | Decision: single Pydantic-native class per table; trivial fit with FastAPI and SQLite |
| Segmentation | rembg (U²-Net) on onnxruntime | Decision: best isolation quality on phone photos; model fetched at install, inference offline (NFR-1/NFR-8) |
| Clustering | scikit-learn `KMeans` | Brief-anticipated; mature, fast on downsampled pixels within NFR-4 |
| Imaging | Pillow + NumPy | Decode/validate/thumbnail and pixel arrays with no further dependencies |
| Colour conversion | Pure-Python RGB↔HSL in `matcher.colour` | Keeps the matcher standard-library-only (NFR-9); the §1.3 maths is small enough to own and unit-test |
| Frontend build | Vite + TypeScript | Fast builds, typed API client, first-class React support |
| Server-state cache | TanStack Query | Keeps inventory filter changes under NFR-6's 1 s without bespoke caching |
| Routing / styling | React Router / CSS Modules | Minimal, boring choices for a single-user image-heavy UI |
| API style | REST over JSON | One resource model (detections, garments, suggestions); contract in `docs/api-contract.md`, FastAPI's OpenAPI as secondary reference |

Test frameworks are deliberately **not** chosen here; that is Milestone 5 (`docs/test-strategy.md`). The architecture's only commitment is the purity boundary that makes the matcher trivially testable (NFR-9).

---

*Approval of this document, together with `docs/api-contract.md`, closes Milestone 3.*
