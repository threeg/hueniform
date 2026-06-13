# Hueniform — Test Strategy

| | |
|---|---|
| **Document** | Test strategy (Milestone 5) |
| **Status** | Draft for approval |
| **Date** | 12 June 2026 |
| **Source** | Approved requirements (`docs/02-requirements.md`), architecture (`docs/03-architecture.md`), API contract (`docs/03-api-contract.md`) and wireframes (`docs/04-wireframes/`), plus interview decisions (§13) |
| **Repository location** | `docs/05-test-strategy.md` |

This document defines how Hueniform is tested: the frameworks, the shape of the test pyramid, and the specific mechanisms for the hard problems — the pure colour matcher, the model-backed detection pipeline, the architecture's dependency rule, and legitimate non-determinism (FR-42). It is written so that Milestone 6 tickets can cite its sections in their acceptance criteria, and Milestone 7 can scaffold the test tooling from §2 and §11 without further interpretation. The FR-n/NFR-n identifiers are those of `docs/02-requirements.md`; the API shapes referenced are those of `docs/03-api-contract.md`, which remains authoritative.

---

## 1. Principles

1. **The requirements are the test specification.** Requirements §1.4 makes every numeric threshold contractual; this strategy turns each numbered rule into named, traceable tests (§12 conventions, §14 traceability).
2. **The purity boundary is the testing strategy.** NFR-9 exists so that §§2–5 and §7 of the requirements are unit-testable with plain values. The bulk of the suite therefore lives against `matcher` with no I/O, no framework, no mocks.
3. **Everything runs offline.** All test tooling is installed by `make setup` (the one-time, online step). After setup, every test target runs with no network access, matching NFR-1/NFR-8's ethos: the rembg model is read from `data/models/`, Playwright browsers from its local cache, and MSW intercepts requests in-process.
4. **The default gate is fast and deterministic.** `make test` contains no model inference, no timing assertions and no randomness that can flake. Slow or machine-dependent suites are separate, explicitly invoked targets with defined places in the definition of done (§12.3).
5. **Where the system is allowed to vary (FR-42), tests assert invariants, not outputs.** The pure matcher doubles as the oracle that validates whatever the stochastic search returns (§8.1).

---

## 2. Frameworks, tooling and invocation

### 2.1 Tooling choices

| Concern | Choice | One-line rationale |
|---|---|---|
| Backend test framework | **pytest** | The Python standard; parametrisation is the natural vehicle for the boundary tables in §4 |
| Backend coverage | **pytest-cov** (coverage.py), branch mode | De facto standard; supports the per-path gate in §2.3 |
| Property-based testing | **Hypothesis** | Decision (§13): the taxonomy is a total function over a continuous domain — properties catch what example tables cannot |
| Import contracts | **import-linter** + one bespoke pytest module | Decision (§13): declared layer/forbidden contracts for the dependency rule, plus a bespoke standard-library allowlist test that import-linter cannot express (§5) |
| API/integration harness | **FastAPI `TestClient`** (httpx) | Exercises the real app factory, real routing and real SQLite without a server process |
| Frontend test framework | **Vitest + React Testing Library** | Native to the Vite toolchain; RTL tests behaviour, not implementation |
| Frontend API mocking | **MSW (Mock Service Worker)** | Serves contract-shaped responses in-process and fully offline; the handler module becomes an executable mirror of `docs/03-api-contract.md` |
| Frontend coverage | **Vitest coverage (v8 provider)** | Built in; reported, not gated (§2.3) |
| E2E tooling | **Playwright** | Decision (§13): a thin smoke suite over the real built app; browsers fetched once at `make setup`, offline thereafter; runs both Chromium and Firefox projects (NFR-7) |
| Performance measurement | pytest with `time.perf_counter` in a marked suite | No additional dependency; bounds and methodology in §8.2 |

All Python test dependencies are pinned alongside the application's, installed into the same virtual environment by `make setup`. `make setup` additionally runs `playwright install chromium firefox`.

### 2.2 Invocation — the Makefile pattern

Test invocation follows the architecture's Makefile pattern (`make setup` / `make run` / `make dev`):

| Target | Contents | Network | When it runs |
|---|---|---|---|
| **`make test`** | `make test-backend` + `make test-frontend` | Offline | **The default gate.** Every ticket, every commit (§12.3) |
| `make test-backend` | `lint-imports` (the §5 contracts), then `pytest` excluding the `model` and `perf` markers, with coverage and the matcher coverage gate (§2.3) | Offline | Part of `make test` |
| `make test-frontend` | `vitest run --coverage` | Offline | Part of `make test` |
| `make test-model` | `pytest -m model` — real rembg + KMeans against fixture photographs (§6.3) | Offline (model on disk) | Definition of done for detection-touching tickets |
| `make test-perf` | `pytest -m perf` — NFR-5/NFR-6 timing assertions at 500 garments (§8.2) | Offline | Definition of done for suggestion- or inventory-query-touching tickets |
| `make test-e2e` | Playwright smoke journeys against a freshly built app with a temporary data directory (§9) | Offline | Definition of done for tickets changing user-facing flows |
| `make test-all` | All of the above | Offline | Milestone completion; before declaring any FR group done |

`pytest` markers `model` and `perf` are registered in `pyproject.toml`; unregistered markers are an error (`--strict-markers`), so a typo cannot silently skip a suite.

**Continuous integration:** decision (§13) — there is no CI service for the MVP. The architecture's phrase "CI-style unit tests" resolves to these make targets: `make test` is the gate, run locally, and the definition of done (§12.3) states when the heavier targets are mandatory. A CI workflow may be added later without changing this strategy; it would run `make test` (the marked suites are excluded by construction — a runner has no model and unrepresentative timing).

### 2.3 Coverage policy

- **`backend/app/matcher/`: 100% line *and* branch coverage, enforced.** The matcher is pure, finite and contractual; an uncovered branch is an untested numbered rule. Mechanism: `make test-backend` runs pytest with `--cov=app --cov-branch`, then `coverage report --include="app/matcher/*" --fail-under=100` as a second step, so the gate is scoped to the matcher without demanding 100% of I/O-heavy code.
- **Everywhere else (backend and frontend): coverage is measured and reported, not gated.** A number in the report is a prompt for judgement, not a target to game.

---

## 3. The test pyramid

| Layer | What lives here | Approximate share |
|---|---|---|
| **Unit** | All eight matcher submodules (§4); detection's pure helpers — proportion integerisation, same-family cluster merging, k-selection, the minimum-foreground fallback predicate (§6.1); frontend components and hooks (§10) | The bulk of the suite |
| **Integration** | Every API endpoint against the contract with real SQLite and a real temporary `data/` directory (§7); the detection pipeline with injected segmentation/clustering seams (§6.2); the staging store lifecycle (§7.3) | A substantial middle |
| **Model-backed** (marked `model`) | The real rembg + KMeans pipeline over fixture photographs with tolerance-based assertions (§6.3) | A handful of tests |
| **Performance** (marked `perf`) | NFR-5 and the server half of NFR-6 at the 500-garment scale (§8.2) | A few tests |
| **E2E** (Playwright) | Two smoke journeys plus the empty-slot rejection, against the real built app including real detection (§9) | Thin by design |

**Deliberately not automated**, with reasoning:

- **Visual design and layout.** The wireframes are low-to-mid fidelity; chrome styling is placeholder. Component tests assert content and behaviour, not pixels.
- **The browser half of NFR-6** (filter changes *reflected* in under 1 s). The server half is asserted (§8.2); the remaining budget is TanStack Query cache behaviour plus render time, which is checked manually at the 500-garment fixture scale when inventory tickets close.
- **Detection *accuracy* at large scale.** A statistical accuracy benchmark over hundreds of photos would be its own project. The product's stated safety net is the confirm-and-correct flow (brief §12); automated detection tests verify the pipeline's *mechanics* and a small set of known photographs (§6.3), not a recall percentage.
- **Subjective explanation prose quality.** Tests assert that explanations are structurally faithful to the evaluation (FR-38, §4.9); whether a sentence reads elegantly is reviewed by a human.
- **`make setup` itself** (it is the one online step; it is verified by being run).

---

## 4. The colour matcher in depth

This is the heart of the strategy. `backend/tests/matcher/` mirrors the matcher's submodules one-to-one, and therefore the requirements sections one-to-one, exactly as the architecture intended:

| Test file | Exercises | Requirements |
|---|---|---|
| `test_constants.py` | Constant values | Req. §1.4 |
| `test_colour.py` | RGB↔HSL, hue distance, circular mean | Req. §1.3, FR-12 |
| `test_taxonomy.py` | Family classification | FR-1–FR-5 |
| `test_roles.py` | Primary/dual-primary/secondary/minor | FR-6–FR-11 |
| `test_harmony.py` | Clusters and the ordered scheme test | FR-12–FR-15 |
| `test_slots.py` | Anchors, layering, covered layers, echo slots | FR-16–FR-22 |
| `test_ranking.py` | Scoring, distinctness, variety, fallback ladder | FR-39–FR-43 |
| `test_explain.py` | Rendering from `EvaluationResult` | FR-37, FR-38 |

All tests in this directory use plain values and frozen dataclasses — no fixtures touching disk, no mocks (NFR-9 makes both unnecessary).

### 4.1 `test_constants.py` — the drift guard

Every named constant in `matcher/constants.py` is asserted equal to the value documented in the requirements (arc width 30, the neutral-rule thresholds, role cut-offs 30 and 15, complementary tolerance 20, triadic tolerance 15, analogous arc 60, ranking weights, `MAX_ANCHOR_CANDIDATES`). This makes requirements §1.4 mechanical: tuning a constant fails a test, forcing the requirements change to be recorded before the test is updated. Each assertion's failure message cites the requirements section it mirrors.

### 4.2 `test_colour.py`

- **Conversion:** known RGB↔HSL pairs (primaries, greys, the contract's worked examples such as `#2CADA0` ↔ (174, 58, 41)); round-trip RGB→HSL→RGB within ±1 per 8-bit channel.
- **Hue distance (FR-12, Req. §1.3.3):** table-driven — `d(350, 10) = 20` (the wrap), `d(0, 180) = 180` (the maximum), `d(h, h) = 0`; plus Hypothesis properties: symmetry, range `[0, 180]`, and invariance under adding 360 to either argument.
- **Circular mean:** `mean(350, 10) = 0` (never 180, the naïve-average trap); the mean of a cluster lies within the cluster's arc (Hypothesis property over hues drawn from a 30° window).

### 4.3 `test_taxonomy.py` — boundary-value testing

The boundary method, applied throughout the matcher: **every comparison in a classification rule is tested at the boundary value and at one small step (0.1) either side**, as a `pytest.mark.parametrize` table whose rows carry the FR identifier and a comment naming the edge. For the FR-2 neutral table and FR-4 half-open arcs that means, at minimum:

| Edge | Rows (input → expected family) |
|---|---|
| Black/not (L < 12) | (any H, any S, 11.9) → Black; (…, 12.0) → not Black |
| White (L > 92, S < 20) | (…, 19.9, 92.1) → White; (…, 20.0, 92.1) → not White; (…, 19.9, 92.0) → not White |
| Grey (S < 10, 12 ≤ L ≤ 92) | S 9.9 vs 10.0; L 12.0 and 92.0 in, 11.9 and 92.1 out |
| Navy vs Denim ordering | (220, 30, 24.9) → Navy; (220, 30, 25.0) → Denim — first-match order, FR-2 |
| Navy hue edges | H 200.0 and 260.0 in; 199.9 and 260.1 out (falling through to Azure/Violet arcs where applicable) |
| Denim S edge | S 49.9 → Denim; S 50.0 → chromatic |
| Brown/Beige gap | (30, 40, 44.9) → Brown; (30, 40, 45.0) → chromatic (Orange) — the documented 45–60 lightness gap is contractual behaviour, asserted as such |
| FR-4 half-open arcs | H = 15.0 → Orange, 14.9 → Red; H = 345.0 → Red, 344.9 → Pink; H = 75.0 → Chartreuse; and so on — **every one of the twelve boundaries**, parametrised |

Plus:

- **Ordered evaluation (FR-2):** inputs satisfying more than one neutral rule's region classify by the first rule in table order.
- **Canonical values:** each family's canonical HSL (the `GET /api/taxonomy` values) classifies into its own family — the invariant the contract §2.2 states.
- **Hypothesis (FR-1):** for arbitrary valid HSL (`0 ≤ h < 360`, `0 ≤ s, l ≤ 100`): classification always returns exactly one family from the nineteen; the same input always returns the same family (called twice); the result is neutral **xor** chromatic; a chromatic result's arc contains the input hue.

### 4.4 `test_roles.py`

Boundary rows for the FR-7 cut-offs: proportion 30 → primary (dual-primary when two such), 29 → secondary; 15 → secondary, 14 → minor. Largest-proportion primary with the saturation tie-break (equal proportions, different S). FR-8: a dual-primary garment qualifies for a slot only when *both* primaries qualify — one passing, one failing → disqualified. FR-10 as a property: adding any minor colour to any qualifying garment never changes qualification. FR-11/FR-9 classification of secondaries (neutral / in-scheme / echo) with one example per branch and one failing example. Hypothesis: role derivation is total and stable for any valid palette (1–4 colours summing to 100).

### 4.5 `test_harmony.py`

- **Clustering (FR-12):** hues within a 30° arc form one cluster, including across the 0° wrap (e.g. {350, 5, 12}); hues 31° apart form two.
- **Ordered scheme test (FR-13):** one passing and one failing example per scheme; and the order itself — a scheme set that satisfies both monochromatic and analogous reports **monochromatic** (first match wins); an empty scheme set reports **neutral-based**.
- **Tolerance boundaries:** complementary at cluster separations 159.9 (fail), 160.0, 180.0, 200.0 (pass), 200.1 (fail); triadic pairwise at 105.0/135.0 in, 104.9/135.1 out; analogous at total spread 60.0 in, 60.1 out. Each row cites FR-13.
- **Neutral transparency (FR-3, FR-14):** adding neutral colours to any passing scheme set never changes the matched scheme (example rows plus a Hypothesis property).
- **FR-15** is exercised end-to-end through `test_slots.py` and `test_ranking.py` scenarios rather than in isolation, since it conjoins §§3–5.

### 4.6 `test_slots.py`

- **Dominance (FR-18):** all three layering permutations — jacket present (jacket dominant), jersey without jacket, top alone — assert the correct anchor set and dominant layer.
- **Scheme-set assembly (FR-19):** dominant-layer primaries + bottom primaries + all anchors' secondaries; covered layers' primaries excluded (FR-20).
- **Covered-layer constraint (FR-20):** a covered top whose chromatic primary is in-scheme passes; out-of-scheme and non-echoing fails; all-neutral passes.
- **Echo slots (FR-21):** per slot — all-neutral qualifies; chromatic colour sharing a family with an anchor colour (in any role, including minor — FR-22) qualifies; a chromatic colour matching nothing disqualifies. Echoes of minor anchor colours are asserted to be *recorded* for the bonus (FR-11/FR-22).
- **FR-16/FR-17** type-to-slot eligibility and required-slot composition over engineered miniature wardrobes.

### 4.7 `test_ranking.py` — deterministic at unit level

Enumeration's shuffle takes an **injected `random.Random`** (the architecture's `MAX_ANCHOR_CANDIDATES` shuffle); unit tests pass a seeded instance, making every ranking test exactly reproducible. FR-42's non-determinism is a property of the *system*, not of these units (§8.1).

- **Scheme strength (FR-41.1):** a complementary set at exactly 180° outranks one at 165°; a narrower analogous spread outranks a wider; monochromatic and neutral-based score perfect strength.
- **Echo bonus (FR-41.2):** more distinct minor-colour echoes outrank fewer, at equal scheme strength.
- **Variety factor (FR-41.3):** with a wardrobe offering many near-equal combinations, the three returned do not all share the same garments where alternatives exist.
- **Distinctness (FR-40)** and **cap (FR-39):** never more than 3; all pairwise distinct; a wardrobe with exactly two valid combinations returns exactly two.
- **Fallback ladder (FR-43):** a wardrobe with no harmonious combination but viable all-neutral anchors → neutral-based results flagged as fallback; a wardrobe with neither → empty result whose `EvaluationResult` failure names the constraining slot, asserted against a wardrobe engineered so one slot is provably the constraint.

### 4.8 Property-based testing — scope and discipline

Hypothesis is used **only** where the input domain is continuous or combinatorially large and a property is crisper than examples: taxonomy totality/determinism (§4.3), hue-distance metric properties and circular-mean membership (§4.2), neutral transparency (§4.5), minor-colour harmlessness (§4.4), role-derivation totality (§4.4), and palette normalisation invariants (§6.1). Boundary behaviour remains the job of the example tables — Hypothesis is not asked to find edges the requirements already name. To keep the gate reproducible (§1.4), `make test-backend` runs Hypothesis with a derandomised profile (`derandomize=True`); developers may run with the default randomised profile locally to hunt for new counterexamples.

### 4.9 Verifying FR-38 — explanations rendered only from the `EvaluationResult`

Four complementary mechanisms:

1. **Structural purity.** `explain.render(result: EvaluationResult) -> str` is the module's only public entry point, and the §5 dependency tests confirm `explain` imports nothing outside the matcher and the standard library — it *cannot* reach the database, the request, or any other source of text.
2. **Construction tests.** Hand-built `EvaluationResult` values → assert the rendered text names the matched FR-13 scheme, mentions each slot's garment with its role, and mentions each recorded echo (family and slots) — the FR-37 content checklist, asserted on substrings, not full prose.
3. **Covariance tests.** Render a result; change exactly one field (the scheme name; remove an echo; swap a role); render again — assert the text changed in the corresponding aspect and only plausibly so. This catches canned text: a template ignoring its input fails immediately.
4. **The integration oracle.** In the §7.4 suggestion tests, for every combination the API returns, the test re-runs the pure evaluation on the returned garments (deterministic — only *enumeration* is shuffled) and asserts the response's `explanation` equals `explain.render` of the re-derived `EvaluationResult`, and the response's `scheme` and `echoes` match it. The explanation provably cannot drift from the evaluation.

Determinism of rendering itself (same result → same text) is asserted as a property.

---

## 5. Enforcing the dependency rule

The architecture promises the dependency rule is "tested in CI-style unit tests" and delegates the mechanism here. The mechanism is two-part, both run by `make test-backend`:

**5.1 import-linter contracts** (declared in `pyproject.toml`, executed by `lint-imports`):

| # | Contract type | Statement |
|---|---|---|
| 1 | forbidden | Nothing in `app` imports `app.api` (the API layer is a leaf above `services`) |
| 2 | forbidden | `app.matcher` imports nothing from `app.api`, `app.services`, `app.detection`, `app.storage` |
| 3 | forbidden | `app.detection` imports nothing from `app.api`, `app.services`, `app.storage`, nor any `app.matcher` submodule other than `matcher.taxonomy`, `matcher.colour` and `matcher.constants` (the conversion and classification it needs per architecture §2.3) |
| 4 | forbidden | `app.storage` imports nothing from `app.api`, `app.services`, `app.detection`, `app.matcher` |
| 5 | layers | `app.api` → `app.services` → {`app.detection`, `app.matcher`, `app.storage`} (higher may import lower, never the reverse) |

**5.2 The standard-library allowlist** (`tests/test_architecture.py`) — the rule import-linter cannot express: NFR-9's "standard library only". A bespoke pytest walks every module file under `app/matcher/` with `ast`, collects the root package of every `import`/`from … import`, and asserts each root is in `sys.stdlib_module_names` or is `app.matcher` itself. The failure message names the offending file and import. The same module asserts the matcher contains no framework markers by construction (no `fastapi`, `pydantic`, `sqlmodel` imports are possible once the allowlist holds, but the named check makes the intent legible).

Because both run inside the default gate, an illegal import fails every ticket immediately — the rule is enforced, not aspirational.

---

## 6. Detection-layer testing

Detection is non-deterministic-ish (KMeans initialisation), model-backed (rembg) and slow relative to the rest of the suite. The strategy splits it along its natural seams.

### 6.1 Pure helpers — unit tested, in the default gate

- **Proportion integerisation (FR-6):** cluster weights → integer percentages summing to *exactly* 100 (largest-remainder method or equivalent); Hypothesis property over arbitrary positive weight vectors of length 1–4: output sums to 100, every entry ≥ 1, ordering preserved.
- **Same-family cluster merging:** two centroids classifying into one family merge, weights added.
- **k-selection heuristic:** synthetic inertia curves with known elbows → expected k.
- **Fallback predicate (FR-27):** mask coverage below the minimum-foreground constant → fallback; at/above → no fallback (boundary rows per §4.3's method).

### 6.2 Pipeline integration — injected seams, in the default gate

The pipeline accepts an injectable segmenter and clusterer (constructor or function parameters — a scaffolding requirement for Milestone 7). Tests run the *real* pipeline orchestration with:

- **Pre-computed alpha masks** committed under `tests/fixtures/masks/`, paired with the synthetic fixture images, replacing rembg — so masking, sampling, clustering, classification and proportion assembly are exercised for real, deterministically.
- **Seeded KMeans** (`random_state` fixed in tests; whether production seeds is the implementation's affair — FR-42 permits either).
- **Failure paths:** a segmenter stub that raises → fallback to whole-image clustering with `fallback_used = true` (FR-27); a mask below minimum foreground → same.

Expected palettes for synthetic images are exact families with proportions within **±5 percentage points** (sampling and clustering introduce small noise even on flat colours).

### 6.3 Real-model suite — marker `model`, `make test-model`

A handful of tests run the genuine rembg (U²-Net via onnxruntime, model from `data/models/`) plus genuine KMeans over the committed real photographs (§11.1). If `data/models/` is absent the suite **skips with an explicit message** naming `make setup` — absence of setup must never read as a pass.

Assertions are **tolerance-based**, because exact pixels are not the contract:

- The detected **family set** equals the expected set recorded in the photograph's sidecar (order-free), or — where a photograph is known to be marginal — the **dominant family** matches and extra families are limited to the sidecar's allowed list.
- The dominant colour's **proportion within ±15 percentage points** of the sidecar's expectation.
- Colour count within the sidecar's expected range (and always 1–4, summing to 100 — FR-6).
- One deliberately garment-free photograph (plain background) triggers the **FR-27 fallback** for real: `fallback_used = true`.
- **NFR-4, softly:** each detection's wall time is recorded; over 5 s emits a pytest warning, over 10 s (2×) fails. The hard 5 s bound is machine-dependent and owner-machine-verified; the 2× ceiling catches genuine regressions without flaking on a cold model load.

What is mocked versus real, summarised: the default gate mocks **only** the segmenter and the clusterer's randomness; the `model` suite mocks **nothing**.

---

## 7. API and integration testing

### 7.1 Harness

`TestClient` against the real app factory. Each test (or test class, where a flow spans calls) receives a temporary directory as its `data/` root — configured through the app's settings (an environment variable / settings object the Milestone 7 scaffolding must provide) — containing a **real SQLite file** (not `:memory:`, so `PRAGMA foreign_keys = ON`, WAL mode and `ON DELETE CASCADE` are exercised as deployed) and the `images/`, `thumbnails/`, `staging/` subdirectories. Detection inside API tests uses the §6.2 injected seams except where a test explicitly composes with the `model` marker.

### 7.2 Contract conformance

One test module per contract section, asserting **field-level shapes against the documented examples**: every success body, and **every documented error code in the §1.3 envelope** — `400 unsupported_format` / `unreadable_image`, `413 file_too_large`, `404 detection_not_found` / `garment_not_found`, `409 empty_slots` (with `details.empty_slots` listing the slots), `409 invalid_regeneration_token`, `422 invalid_palette` / `invalid_type` / `invalid_filter` / `invalid_request`. Specific contract invariants:

- **Server-side family derivation (contract §1.6):** submitted HSL with a deliberately wrong implied family → stored family is the server's derivation; the response's `family`/`neutral`/`hex` are consistent with the matcher (cross-checked by calling `matcher.taxonomy` directly in the assertion).
- **Palette validation:** 0 and 5 colours, sums of 99 and 101, `h = 360`, `proportion = 0` → `422 invalid_palette`; the boundary-row method again.
- **`GET /api/taxonomy`:** all nineteen families; `representative_hue`/`hue_arc` present exactly on chromatic families; every `canonical` classifies into its own family.
- **Inventory filters (FR-35, contract §2.6):** type-only, family-only and combined AND queries over a seeded wardrobe; family matches *any* role including minor; unknown values → `422 invalid_filter`; `total` correct under `limit`/`offset`.

### 7.3 Lifecycle, staging and persistence (NFR-3)

- **Upload → confirm:** `POST /api/detections` writes staging file + sidecar and **nothing to the database** (asserted by direct query — FR-24); `POST /api/garments` consumes the token, **moves** the staged image into `data/images/`, generates the thumbnail and inserts both tables in one transaction; the staged files are gone; a second `POST` with the same token → `404` (consumed).
- **Abandonment and TTL:** an expired token (expiry forced via a clock seam or direct sidecar edit) → `404`; the startup sweep removes expired staging entries (invoke the sweep against a prepared staging directory).
- **Rejection writes nothing:** unsupported format / oversize / unreadable → documented error, empty database, empty staging.
- **Regeneration flow (FR-32/FR-33, contract §2.9–§2.10):** `POST …/regenerate` leaves record and image untouched and returns a §2.3-shaped proposal plus `garment_id`; `PUT` with the token replaces palette and type **in place** — same `id`, same `image_file`, `regenerated_at` set; the token is consumed (second `PUT` → `409`); a token bound to a different garment → `409`; expired → `409`; and the FR-32 enforcement itself — `PUT` without a valid regeneration token **always** fails, proving there is no field-editing path.
- **Delete (FR-34):** `204`; record gone (cascade verified on `garment_colours`); image and thumbnail files removed from disk.
- **Atomicity:** a forced failure mid-confirmation (e.g. thumbnail generation made to raise via a seam) leaves no database rows and no moved image — the transaction boundary holds.

### 7.4 Suggestions (FR-36–FR-43)

- **Fail fast:** requesting a slot with no garments → `409 empty_slots` naming exactly the empty slots; multiple empty slots all named.
- **Unknown slot key** → `422 invalid_request`.
- **Invariant assertions over engineered wardrobes** — the FR-42-safe pattern of §8.1, including the FR-38 oracle of §4.9.
- **Exact-outcome wardrobes:** wardrobes constructed with exactly one valid combination make even the stochastic path exactly assertable — used for the fallback ladder's two rungs and the zero-result shape (`explanation` + `hint` naming the constraining slot, contract §2.12).

---

## 8. Non-determinism and performance

### 8.1 Asserting FR-42 without flaky tests

The rule: **endpoint tests never assert which combinations return; they assert that whatever returns is correct.** For every response:

1. ≤ 3 combinations, pairwise distinct (FR-39, FR-40), `rank` sequential from 1.
2. Each combination fills exactly the required + requested slots with garments of the right types (FR-16, FR-17).
3. **The oracle:** the pure matcher re-evaluates each returned combination — it must be harmonious per FR-15 (or, when `fallback: true`, valid under the FR-43a all-neutral restriction), and the response's `scheme`, `echoes` and `explanation` must match the re-derived `EvaluationResult` (§4.9.4).
4. Repetition is *permitted to differ*, never *required* to differ: a test calling the endpoint repeatedly asserts every response passes 1–3, and **never** asserts inequality between runs (a small wardrobe may legitimately always return the same answer).

Order-sensitivity (does ranking *order* correctly?) is tested deterministically at unit level with the injected seeded RNG (§4.7) — the system test does not duplicate it.

### 8.2 Performance suite — marker `perf`, `make test-perf`

Run against the deterministic 500-garment wardrobe (§11.2), seeded directly through the storage layer (building it through the API would dominate the runtime).

- **NFR-5:** `POST /api/suggestions` (all optional slots requested — the worst case) completes in **< 2 s**, taking the **median of 3 runs** to dampen scheduler noise.
- **NFR-6, server half:** `GET /api/garments` with combined type + family filters completes in **< 1 s** (median of 3). This is necessary, not sufficient, for NFR-6 — the browser half is the manual check noted in §3.
- **NFR-4** lives in the `model` suite (§6.3), since it is meaningless without the real model.

These tests are excluded from the default gate because timing on an arbitrary machine is not deterministic; the bounds are contractual on the owner's machine, where the definition of done (§12.3) requires the suite to pass. A failure is a real conversation, not a retry button.

---

## 9. End-to-end smoke suite — `make test-e2e`

Playwright, **Chromium and Firefox projects** (NFR-7), against the genuinely built application: the Playwright `webServer` launches the production-style Uvicorn process (built SPA, real detection with the real model, temporary `data/` directory per run). Nothing is mocked — this suite exists to prove the assembled system works, especially valuable given Milestone 8+ implementation is AI-driven.

Three journeys, kept deliberately thin:

1. **Add a garment:** upload a synthetic fixture image via the file picker → confirm-and-correct shows a proposal with swatches and proportions → adjust a proportion → select a type (save disabled until chosen, per the Milestone 4 decision) → save → the garment appears in the inventory and survives type + family filtering.
2. **Request an outfit:** against a pre-seeded wardrobe (the seeding script of §11.2 with a small engineered wardrobe), request with one optional slot → ranked result cards render with scheme chip, per-slot tiles and a non-empty explanation; "Suggest again" returns a valid (not necessarily different) response.
3. **Empty-slot rejection:** request a slot with no garments → the `409 empty_slots` message renders on the request panel.

The model and Playwright browsers are on disk after `make setup`; the suite skips with an explicit message if either is missing. E2E asserts user-visible behaviour only — contract details are §7's job.

---

## 10. Frontend testing

### 10.1 Component tests (Vitest + RTL + MSW) — in the default gate

MSW handlers live in one shared module (`frontend/src/test/handlers.ts`) built from the contract's documented example bodies — an executable mirror of `docs/03-api-contract.md`; when the contract changes, this module is the single frontend place to update. Components under test, by screen:

- **Upload & detect:** rejection states render the server's plain-language `message` (FR-24); the `fallback_used` warning banner (FR-27).
- **Confirm-and-correct:** the proportion editor — steppers, live total, stacked preview, **normalise-to-100 on save** (FR-29, the Milestone 4 decision); colour removal; manual add applying the canonical HSL from the taxonomy response; the type picker's save-disabled-until-chosen rule (FR-30/FR-31).
- **Inventory:** filter bar options populated from `GET /api/taxonomy` with family swatches; combined filters issue the right query parameters; empty-result state.
- **Garment detail:** regenerate enters confirm-and-correct with the regeneration token; delete confirmation step before `DELETE` is issued (FR-34's UI half).
- **Outfit request/results:** slot panel composes the `include` body; `409 empty_slots` rendering; result cards — rank by position (no score numbers), scheme chip, echo line from the `echoes` array, the `fallback: true` "Neutral-based fallback" label (FR-43a); the zero-result state rendering `explanation` and `hint` verbatim (FR-43b).

### 10.2 What component tests do not cover

Routing across screens, real file-upload mechanics, and frontend↔backend integration belong to the E2E journeys (§9). Visual styling is not automated (§3). Pure frontend utilities (e.g. HSL→hex display helpers, if any exist beyond the API's `hex`) get plain Vitest unit tests.

---

## 11. Test data and fixtures

### 11.1 Fixture images — `backend/tests/fixtures/images/`

- **`real/`** — 4–6 small (≤ 1 MB each) genuine phone photographs of garments, committed to the repository, each with a JSON sidecar (`<name>.expected.json`) recording: expected family set, dominant family, dominant proportion ± tolerance, allowed extra families, expected colour-count range, and whether fallback is expected. One photograph is deliberately garment-free (the FR-27 fixture). These serve the `model` suite (§6.3) and journey 1 of E2E.
- **`synthetic/` (generated)** — `tests/fixtures/generate_images.py` deterministically renders garment-like shapes (flat colours, two-colour blocks, a thin-stripe minor colour) on plain contrasting backgrounds with Pillow, writing into a gitignored cache on first use (a pytest session fixture invokes it). Exact expected palettes are known by construction. No generated binaries are committed.
- **`masks/`** — committed pre-computed alpha masks paired with the synthetic images, for the §6.2 injected-segmenter tests.
- Invalid-upload fixtures: a tiny GIF (unsupported format), a truncated JPEG (unreadable), and an oversize file **generated** at test time (a >20 MB blob is never committed).

### 11.2 Wardrobe factories — `backend/tests/fixtures/wardrobes.py`

Factory functions returning plain matcher values for unit tests and persisting rows for integration tests (one definition, two materialisations):

- Engineered scenario wardrobes: `single_valid_outfit()`, `two_valid_outfits()`, `neutral_fallback_only()`, `no_valid_outfit_constrained_by(slot)`, `rich_echo_wardrobe()` — each documented with the FR it exists to pin down.
- **`wardrobe_500()`** — the NFR-5/NFR-6 fixture: 500 garments generated from a **seeded** RNG with a realistic distribution across the eight types and the family taxonomy, so the perf suite is reproducible. A small CLI wrapper (`scripts/seed_test_wardrobe.py` or a make target) seeds a running instance for E2E and manual NFR-6 checks.

### 11.3 Shared palette tables — `backend/tests/fixtures/palettes.py`

The boundary tables of §4.3–§4.5 and canonical HSL values, defined once and imported by the matcher tests and the API conformance tests, so a requirements §1.4 change is reflected in exactly one fixture location plus `test_constants.py`.

### 11.4 Frontend fixtures — `frontend/src/test/`

MSW `handlers.ts` plus `contract-examples.ts` holding the contract's documented JSON bodies as typed constants (imported by handlers and assertions alike).

---

## 12. Conventions and definition of done

### 12.1 Layout and naming

```
backend/tests/
  conftest.py                  app-factory, tmp data-dir and client fixtures
  test_architecture.py         §5.2 stdlib allowlist (import-linter config in pyproject.toml)
  matcher/test_<submodule>.py  one per matcher submodule (§4)
  detection/test_*.py          §6.1–§6.2; test_model_pipeline.py carries @pytest.mark.model
  api/test_<resource>.py       §7, one per contract section group
  perf/test_bounds.py          @pytest.mark.perf (§8.2)
  fixtures/                    §11
frontend/src/
  **/<Component>.test.tsx      co-located with the component
  test/                        MSW handlers, contract examples, setup
e2e/
  *.spec.ts                    the §9 journeys; playwright.config.ts
```

- Backend test functions: `test_<frN>_<behaviour>` where the test pins a numbered requirement (e.g. `test_fr4_hue_15_is_orange`, `test_fr40_combinations_distinct`); plain descriptive names otherwise. Parametrised boundary rows carry the FR id in the row id.
- Frontend: `describe` blocks name the screen and state as the wireframes do; test names state user-visible behaviour.
- A test asserting a contract shape names the contract section in a comment (e.g. `# contract §2.12`).

### 12.2 When tickets must include tests

Every Milestone 8+ implementation ticket that creates or changes behaviour covered by a numbered requirement **must include or update tests in the same commit as the implementation**, citing the FR/NFR ids and the relevant section of this strategy in its acceptance criteria. Tickets exempt from new tests: documentation-only, pure-styling, and build-plumbing tickets — the exemption must be stated in the ticket.

### 12.3 Definition of done — Milestone 8+ implementation tickets

A ticket is done only when **all** of the following hold:

1. `make test` passes (the default gate: backend unit + integration with import contracts and the matcher coverage gate, frontend component tests).
2. New or changed numbered-requirement behaviour has tests per §12.2, and the §14 traceability of this document still holds for the affected rows.
3. The matcher coverage gate (100% line + branch on `app/matcher/`) holds — no exceptions, no pragmas without a recorded decision.
4. Tickets touching `detection/`: `make test-model` passes on the owner's machine.
5. Tickets touching suggestion evaluation/enumeration or inventory queries: `make test-perf` passes on the owner's machine.
6. Tickets changing a user-facing flow: `make test-e2e` passes.
7. The ticket file's status and notes are updated **in the same commit** as the work, per the brief's meta-goal.

Milestone completion additionally requires a green `make test-all`.

---

## 13. Decisions log (interview outcomes)

| Decision | Outcome |
|---|---|
| Backend stack | pytest + pytest-cov; FastAPI `TestClient` for integration (default, unobjected) |
| Frontend stack | Vitest + React Testing Library + MSW (default, unobjected) |
| E2E | Yes — thin Playwright smoke suite, Chromium + Firefox, real model, offline after setup |
| Dependency-rule mechanism | import-linter declared contracts **plus** bespoke stdlib-allowlist pytest for NFR-9 |
| Real-model detection tests | Behind a `model` marker / `make test-model`; default gate uses injected masks and seeded clustering; mandatory in DoD for detection tickets |
| Performance assertions | Marked `perf` suite: NFR-5 asserted at 500 garments, NFR-6 server half asserted; NFR-4 soft-asserted in the model suite; excluded from the default gate |
| Property-based testing | Yes — Hypothesis, targeted (taxonomy totality, hue maths, normalisation, neutral/minor transparency); derandomised in the gate |
| Fixture photographs | Hybrid — deterministic synthetic generator + 4–6 committed real photographs with expectation sidecars |
| CI | None for MVP; "CI-style" resolves to the `make` targets, run locally; a future CI workflow would run `make test` unchanged |
| Coverage gates | 100% line + branch enforced on `app/matcher/` only; measured and reported elsewhere (default, unobjected) |

---

## 14. Traceability — requirements to tests

| Requirement | Primary test location (§ of this document) |
|---|---|
| FR-1–FR-5 (taxonomy) | `matcher/test_taxonomy.py` (§4.3); canonical cross-checks in `api/test_taxonomy.py` (§7.2) |
| FR-6 (1–4 colours, sum 100) | `detection` integerisation (§6.1); `api` palette validation (§7.2) |
| FR-7–FR-11 (roles, echoes) | `matcher/test_roles.py` (§4.4); echo recording in `test_slots.py` (§4.6) |
| FR-12–FR-15 (harmony) | `matcher/test_colour.py`, `test_harmony.py` (§4.2, §4.5) |
| FR-16–FR-22 (slots, layering) | `matcher/test_slots.py` (§4.6) |
| FR-23–FR-25 (upload, rejection, storage) | `api/test_detections.py`, lifecycle tests (§7.2–§7.3) |
| FR-26–FR-27 (detection, fallback) | §6.1–§6.3 across default and `model` suites |
| FR-28–FR-31 (confirm-and-correct, type) | API flow tests (§7.3); frontend confirm components (§10.1); E2E journey 1 (§9) |
| FR-32–FR-33 (no editing; regenerate) | Regeneration token flow (§7.3) |
| FR-34 (delete) | Lifecycle tests (§7.3); frontend confirmation step (§10.1) |
| FR-35 (inventory, filters) | `api/test_garments.py` filters (§7.2); frontend filter bar (§10.1) |
| FR-36 (slot selection, fail fast) | `api/test_suggestions.py` (§7.4); frontend 409 rendering (§10.1) |
| FR-37–FR-38 (explanations) | `matcher/test_explain.py` + the integration oracle (§4.9) |
| FR-39–FR-41 (count, distinct, ranking) | `matcher/test_ranking.py` seeded (§4.7); endpoint invariants (§8.1) |
| FR-42 (non-determinism) | Invariant-only endpoint assertions (§8.1) |
| FR-43 (fallback ladder) | `test_ranking.py` (§4.7); exact-outcome wardrobes (§7.4); frontend labels/zero-state (§10.1) |
| NFR-1/NFR-8 (offline) | Construction: all targets offline after setup (§1.3, §2.2) |
| NFR-2 (single command) | E2E `webServer` boots the production-style process (§9); health probe in §7.2 |
| NFR-3 (single-directory state) | Temporary-`data/`-rooted integration tests; file lifecycle assertions (§7.1, §7.3) |
| NFR-4 (detection < 5 s) | Soft assertion in the `model` suite (§6.3) |
| NFR-5 (suggestions < 2 s @ 500) | `perf` suite (§8.2) |
| NFR-6 (inventory < 1 s @ 500) | Server half in `perf` (§8.2); browser half manual (§3) |
| NFR-7 (Chrome + Firefox) | Playwright Chromium + Firefox projects (§9) |
| NFR-9 (pure matcher) | §4 throughout; enforced by §5 and the matcher coverage gate (§2.3) |

---

*Approval of this document closes Milestone 5.*
