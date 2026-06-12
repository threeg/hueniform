# Hueniform — System Architecture

| | |
|---|---|
| **Document** | Architecture (Milestone 3) |
| **Status** | Draft for approval |
| **Date** | 12 June 2026 |
| **Source** | Approved project brief (`docs/project-brief.md`) and requirements (`docs/requirements.md`) |
| **Repository location** | `docs/architecture.md` |
| **Companion document** | `docs/api-contract.md` (the HTTP contract; authoritative for all endpoint shapes) |

---

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

### 2.2 The matcher (pure module)

`matcher` is a package of pure functions over small frozen dataclasses. Its submodules map one-to-one onto the requirements sections so a test file can mirror each:

| Submodule | Responsibility | Requirements |
|---|---|---|
| `constants.py` | Every numeric threshold as a named constant (arc widths, tolerances, role cut-offs, ranking weights, candidate cap) | Req. §1.4 |
| `colour.py` | RGB↔HSL conversion, wrapping hue distance (max 180°), circular mean | Req. §1.3, FR-12 |
| `taxonomy.py` | Family classification: ordered neutral rules, then chromatic arcs; half-open boundaries; canonical HSL per family | FR-1–FR-5 |
| `roles.py` | Primary / dual-primary / secondary / minor derivation from proportions | FR-6–FR-11 |
| `harmony.py` | Clustering of hues, ordered scheme test (neutral-based → monochromatic → analogous → complementary → triadic) | FR-12–FR-15 |
| `slots.py` | Anchor identification, layering dominance, covered-layer and echo-slot qualification | FR-16–FR-22 |
| `ranking.py` | Score composition (scheme strength, echo bonus, variety factor), fallback ladder | FR-39–FR-43 |
| `explain.py` | Plain-language explanation rendered from the evaluation result object | FR-37, FR-38 |

The central design point for FR-38: evaluation returns an **`EvaluationResult`** value (matched scheme, per-garment roles, the echoes found, score components, and — on failure — the constraining slot). `explain.py` renders text *only* from this object, so explanations cannot drift from the evaluation. Garment roles (primary/secondary/minor) are **derived at evaluation time** from stored proportions, never persisted, so FR-7 has a single source of truth.

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
| `id` | TEXT, PK | UUID4 string; stable across regeneration (FR-33) |
| `type` | TEXT, NOT NULL | One of the eight FR-16 values; CHECK constraint |
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

Indices: `idx_garments_type (garments.type)`, `idx_colours_family (garment_colours.family)`, `idx_colours_garment (garment_colours.garment_id)`. With both filter columns indexed, the combined type-AND-family query is comfortably inside NFR-6 at 500 garments.

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
3. SPA renders the confirm-and-correct screen (image preview served from staging). The user adjusts proportions, removes or manually adds colours (canonical HSL for the chosen family, from `GET /api/taxonomy`), and selects the mandatory type (FR-29, FR-31).
4. SPA `POST /api/garments` with the token, type and confirmed colours. The service re-derives every family server-side, validates count and the sum of 100, then in one transaction moves the image, generates the thumbnail and inserts both tables (FR-30, FR-25). Response: the saved garment.

### 4.2 Regenerate (FR-32–FR-33)

1. SPA `POST /api/garments/{id}/regenerate`. The service runs the detection pipeline on the **stored** photograph and returns a fresh proposal with a regeneration token bound to the garment.
2. The user passes through the same confirm-and-correct flow, including type selection.
3. SPA `PUT /api/garments/{id}` with the regeneration token, type and colours. The service replaces the colour rows and type **in place** — same `id`, same image — and stamps `regenerated_at`. Requiring the token is how FR-32 is enforced architecturally: there is no field-edit path, because `PUT` is only honoured as the completion of a regeneration.

### 4.3 Outfit request → evaluation → ranked suggestions (FR-36–FR-43)

1. SPA `POST /api/suggestions` naming the requested optional slots. The service loads the inventory grouped by type and **fails fast** if any included slot is empty, naming the slots (FR-36).
2. **Anchor enumeration.** Candidates are built anchors-first: bottom × outermost upper layer (jacket if requested, else jersey if requested, else top — FR-18) × covered layers. Enumeration is shuffled and capped by a named constant (`MAX_ANCHOR_CANDIDATES`), which both honours NFR-5 at 500 garments and supplies FR-42's permitted non-determinism.
3. **Anchor evaluation** (pure matcher): build the scheme set — dominant-layer primaries, bottom primaries, all anchors' secondaries (FR-19) — test schemes in FR-13 order; check anchor secondary compatibility (FR-9) and covered-layer constraints (FR-20). Failures are pruned immediately.
4. **Echo slots.** For each surviving anchor set, qualifying garments per echo slot are those whose primaries and secondaries are neutral or echo an anchor colour (FR-21), with minor-colour echoes recorded for the bonus (FR-11, FR-22). Minor colours never disqualify (FR-10).
5. **Scoring and selection** (`matcher.ranking`): scheme strength, then echo-bonus count, then a variety penalty applied greedily so the three returned combinations do not reuse the same garments (FR-41); up to 3 distinct combinations returned best-first (FR-39, FR-40).
6. **Fallback ladder** (FR-43): if nothing passes, retry restricted to all-neutral anchors and neutral echo slots, labelling results as neutral-based fallbacks; if that also fails, return zero combinations with the constraining slot named in a plain-language explanation and hint.
7. **Explanation** (FR-37/FR-38): rendered per combination from its `EvaluationResult`, naming the matched scheme and each garment's role.

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
