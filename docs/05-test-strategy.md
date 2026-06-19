# Hueniform — Test Strategy

| | |
|---|---|
| **Document** | Test strategy (living document) |
| **Status** | Approved (Milestone 5); amended for v0.2.0 (Milestone 13) |
| **Originally approved** | 12 June 2026 (Milestone 5, v0.1.0) |
| **Last amended** | 18 June 2026 — v0.2.0 test-strategy delta (Milestone 13) |
| **Source** | Approved requirements (`docs/02-requirements.md`), architecture (`docs/03-architecture.md`), API contract (`docs/03-api-contract.md`) and wireframes (`docs/04-wireframes/`), plus interview decisions (§13); v0.2.0 brief (`docs/09-v0.2.0-brief.md`) §6; F4 spike (`docs/spikes/2026-06-18-f4-category-slot-model.md`) |
| **Repository location** | `docs/05-test-strategy.md` |

This document defines how Hueniform is tested: the frameworks, the shape of the test pyramid, and the specific mechanisms for the hard problems — the pure colour matcher, the model-backed detection pipeline, the architecture's dependency rule, and legitimate non-determinism (FR-42). It is written so that Milestone 6 tickets can cite its sections in their acceptance criteria, and Milestone 7 can scaffold the test tooling from §2 and §11 without further interpretation. The FR-n/NFR-n identifiers are those of `docs/02-requirements.md`; the API shapes referenced are those of `docs/03-api-contract.md`, which remains authoritative.

> **v0.2.0 amendment note (18 June 2026).** This is a living document; it evolves in
> place rather than being forked per version (v0.2.0 brief §1). The Milestone 13 delta
> pass propagates the settled v0.2.0 decisions into the test strategy: the **test-first
> policy** for the deterministic and contract-pinned layers (§1, §12.2); the **golden-file
> snapshot baseline** of current matcher output, captured before the E08 refactor (new
> §4.10); **seedable variety** (NFR-10) and how FR-42 is asserted as invariants (§8.1);
> the new matcher coverage — the Cream family (§4.3), the region/slot/adornment model and
> the four-layer stack (§4.6), first-class neutral-based ranking and top-*N* selection
> (§4.7), and the per-category slot constraint FR-52; the rewritten `POST /api/suggestions`,
> the `PATCH /api/garments/{id}` category edit, and the grouped/ordered inventory and
> taxonomy regions (§7); the NFR-5 perf **re-baseline at count 25** (§8.2); the reworked
> e2e journeys (§9) and frontend component tests (§10); the **data-migration** test for the
> old `type` values (new §7.5); and new fixtures (§11). The import-linter dependency
> contracts and the std-library matcher allowlist (§5) are **unchanged** — the slot-model
> rewrite adds no new harmony mathematics and the matcher stays pure and standard-library-only
> (NFR-9). Superseded text is marked *(superseded — v0.2.0)* in place; requirements §1.4
> numeric thresholds remain contractual. The reasoning behind the slot-model rewrite is in
> the F4 spike note.

---

## 1. Principles

1. **The requirements are the test specification.** Requirements §1.4 makes every numeric threshold contractual; this strategy turns each numbered rule into named, traceable tests (§12 conventions, §14 traceability).
2. **The purity boundary is the testing strategy.** NFR-9 exists so that §§2–5 and §7 of the requirements are unit-testable with plain values. The bulk of the suite therefore lives against `matcher` with no I/O, no framework, no mocks.
3. **Everything runs offline.** All test tooling is installed by `make setup` (the one-time, online step). After setup, every test target runs with no network access, matching NFR-1/NFR-8's ethos: the rembg model is read from `data/models/`, Playwright browsers from its local cache, and MSW intercepts requests in-process.
4. **The default gate is fast and deterministic.** `make test` contains no model inference, no timing assertions and no randomness that can flake. Slow or machine-dependent suites are separate, explicitly invoked targets with defined places in the definition of done (§12.3).
5. **Where the system is allowed to vary (FR-42), tests assert invariants, not outputs.** The pure matcher doubles as the oracle that validates whatever the stochastic search returns (§8.1).
6. **Test-first for the deterministic and contract-pinned layers (v0.2.0).** For `matcher`, `services` logic and `api` contract shapes, the failing test is written from the requirement/contract and confirmed to fail for the right reason *before* the implementation (v0.2.0 brief §6); the same-commit rule (§12.2) is unchanged. The probabilistic `detection` layer keeps characterisation/after tests, since its output is tolerance-checked, not exact (§6). The **golden-file snapshot baseline** (§4.10) is the safety net for the one place this is hardest — the E08 rewrite of the already-shipped, 100 %-covered matcher, where the test that must "fail first" is a *changed* snapshot, reviewed in the diff.

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
| `make test-perf` | `pytest -m perf` — NFR-5/NFR-6 timing assertions at 500 garments; **v0.2.0** — NFR-5 re-baselined at the maximum requested count of 25 (§8.2) | Offline | Definition of done for suggestion- or inventory-query-touching tickets |
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
| `test_taxonomy.py` | Family classification; **v0.2.0** — the Cream neutral family | FR-1–FR-5 |
| `test_roles.py` | Primary/dual-primary/secondary/minor | FR-6–FR-11 |
| `test_harmony.py` | Clusters and the ordered scheme test | FR-12–FR-15 |
| `test_slots.py` | Anchors, the four-layer stack, covered layers, one-piece, statement/minor adornments, per-category constraint | FR-16–FR-22, FR-49–FR-52 |
| `test_ranking.py` | Scoring, distinctness, variety, the fallback ladder; **v0.2.0** — first-class neutral-based, top-*N* count, injected RNG | FR-39–FR-43, FR-48, NFR-10 |
| `test_explain.py` | Rendering from `EvaluationResult` | FR-37, FR-38 |
| `test_snapshot.py` *(v0.2.0)* | Golden-file baseline of current matcher output, captured before the E08 rewrite (§4.10) | regression guard for FR-1–FR-43 |

All tests in this directory use plain values and frozen dataclasses — no fixtures touching disk, no mocks (NFR-9 makes both unnecessary). **v0.2.0:** the one exception is `test_snapshot.py` (§4.10), which reads committed golden files; it pins outputs rather than mirroring a single submodule.

### 4.1 `test_constants.py` — the drift guard

Every named constant in `matcher/constants.py` is asserted equal to the value documented in the requirements (arc width 30, the neutral-rule thresholds, role cut-offs 30 and 15, complementary tolerance 20, triadic tolerance 15, analogous arc 60, ranking weights, `MAX_ANCHOR_CANDIDATES`). This makes requirements §1.4 mechanical: tuning a constant fails a test, forcing the requirements change to be recorded before the test is updated. Each assertion's failure message cites the requirements section it mirrors.

**v0.2.0 — additional constants asserted (requirements §1.4, §2.1, §5, §7).** The same drift guard extends to every new or changed named value: the **Cream** thresholds (`CREAM_H_LOW = 20`, `CREAM_H_HIGH = 70`, `CREAM_S_LOW = 10`, `CREAM_S_HIGH = 45`, `CREAM_L_MIN = 88` — FR-2); the **ranking** changes (`NEUTRAL_BASED_STRENGTH = 0.98`, the raised `WEIGHT_VARIETY = 15` asserted *not* to be the v0.1.0 value 5, `WEIGHT_SCHEME_STRENGTH = 100`, `WEIGHT_ECHO_BONUS = 10` — FR-41); the **count** bounds (`COUNT_MIN = 1`, `COUNT_MAX = 25`, `COUNT_DEFAULT = 3` — FR-48); and the **named sets** of the slot model (the FR-16 category set, the slot keys, the four-level upper-body layer order `base → shirt → mid → outer`, the statement vs minor adornment membership, and the default-selected slots `base`/`lower_body`/`socks`/`shoes` — FR-49–FR-51). Each set is asserted by membership and order so a renamed key (`jersey`→`mid`, `jacket`→`outer`) or a dropped/added category fails a test.

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
| **Cream** — Beige/Tan hand-off (L 88) *(v0.2.0, FR-2)* | (40, 30, 88.0) → Beige/Tan; (40, 30, 88.1) → Cream — Beige/Tan owns L ≤ 88, Cream owns L > 88 for the same S ≤ 45 band |
| **Cream** hue ceiling (H 70) *(v0.2.0, FR-2)* | (70, 30, 90) → Cream; (70.1, 30, 90) → chromatic (Yellow) — Cream's 70° ceiling vs Beige/Tan's 60° |
| **Cream** S edge (S 45) *(v0.2.0, FR-2)* | (50, 45.0, 90) → Cream; (50, 45.1, 90) → chromatic — the S ≤ 45 ceiling shared with Beige/Tan |
| **White before Cream** (order) *(v0.2.0, FR-2)* | (50, 18, 93) → White (S < 20, L > 92, order 2, evaluated first); (50, 28, 90) → Cream (order 8) — first-match order |
| **Cream** worked example *(v0.2.0, FR-2)* | (52, 28, 90) → Cream — the ecru/white-jeans case that was mis-routed to Yellow in v0.1.0 |
| FR-4 half-open arcs | H = 15.0 → Orange, 14.9 → Red; H = 345.0 → Red, 344.9 → Pink; H = 75.0 → Chartreuse; and so on — **every one of the twelve boundaries**, parametrised |

Plus:

- **Ordered evaluation (FR-2):** inputs satisfying more than one neutral rule's region classify by the first rule in table order.
- **Canonical values:** each family's canonical HSL (the `GET /api/taxonomy` values) classifies into its own family — the invariant the contract §2.2 states.
- **Hypothesis (FR-1):** for arbitrary valid HSL (`0 ≤ h < 360`, `0 ≤ s, l ≤ 100`): classification always returns exactly one family from the **twenty** *(v0.2.0: nineteen + Cream)*; the same input always returns the same family (called twice); the result is neutral **xor** chromatic; a chromatic result's arc contains the input hue.

### 4.4 `test_roles.py`

Boundary rows for the FR-7 cut-offs: proportion 30 → primary (dual-primary when two such), 29 → secondary; 15 → secondary, 14 → minor. Largest-proportion primary with the saturation tie-break (equal proportions, different S). FR-8: a dual-primary garment qualifies for a slot only when *both* primaries qualify — one passing, one failing → disqualified. FR-10 as a property: adding any minor colour to any qualifying garment never changes qualification. FR-11/FR-9 classification of secondaries (neutral / in-scheme / echo) with one example per branch and one failing example. Hypothesis: role derivation is total and stable for any valid palette (1–4 colours summing to 100).

### 4.5 `test_harmony.py`

- **Clustering (FR-12):** hues within a 30° arc form one cluster, including across the 0° wrap (e.g. {350, 5, 12}); hues 31° apart form two.
- **Ordered scheme test (FR-13):** one passing and one failing example per scheme; and the order itself — a scheme set that satisfies both monochromatic and analogous reports **monochromatic** (first match wins); an empty scheme set reports **neutral-based**.
- **Tolerance boundaries:** complementary at cluster separations 159.9 (fail), 160.0, 180.0, 200.0 (pass), 200.1 (fail); triadic pairwise at 105.0/135.0 in, 104.9/135.1 out; analogous at total spread 60.0 in, 60.1 out. Each row cites FR-13.
- **Neutral transparency (FR-3, FR-14):** adding neutral colours to any passing scheme set never changes the matched scheme (example rows plus a Hypothesis property).
- **FR-15** is exercised end-to-end through `test_slots.py` and `test_ranking.py` scenarios rather than in isolation, since it conjoins §§3–5.

### 4.6 `test_slots.py` *(rewritten — v0.2.0; supersedes the v0.1.0 three-layer/echo-slot tests)*

The v0.2.0 slot model generalises the shipped layer logic rather than replacing the maths (architecture §2.2; F4 spike): a statement adornment is evaluated exactly as a v0.1.0 echo slot and a minor adornment exactly as a minor colour, so **no new harmony primitive is introduced** — and the tests assert exactly that equivalence alongside the new structure.

- **Category → slot mapping & matcher-equivalence (FR-16, FR-49.5):** every FR-16 category maps to exactly one slot key; categories sharing a slot (`t_shirt`/`vest`/`long_sleeve` → `base`; `jeans`/`trousers`/`chinos` → `lower_body`; etc.) are asserted to be **treated identically by the matcher** — swapping one matcher-equivalent category for another in a wardrobe leaves the evaluation unchanged. The renamed keys (`jersey`→`mid`, `jacket`→`outer`) are asserted; `jacket` survives as a category in `outer`, `jersey` is gone as a category.
- **Four-layer dominance (FR-18):** the upper-body stack `base → shirt → mid → outer` — the **outermost present** layer is dominant (`outer > mid > shirt > base`); parametrised over representative subsets (all four present; gaps in the stack; a single base; none present → the lower-body garment is the sole anchor).
- **Scheme-set assembly (FR-19):** dominant-layer primaries + lower-body primaries + all anchors' secondaries; covered inner layers excluded (FR-20). Where the dominant upper layer and the lower-body anchor are the **same** garment (an uncovered one-piece), its colours are counted **once**.
- **Covered-layer constraint across four layers (FR-20):** any present layer beneath the dominant one is constrained like a statement adornment — in-scheme or echoing passes, out-of-scheme non-echoing fails, all-neutral passes — asserted for each of the up-to-three covered positions, not just one.
- **One-piece (FR-18, FR-19, FR-50.2):** a `dress`/`jumpsuit` is always the lower-body anchor and additionally occupies `base`; uncovered, it is simultaneously dominant upper layer and lower anchor (counted once); covered by `shirt`/`mid`/`outer`, the outer layer is dominant **but the one-piece is never demoted to a covered layer** (its lower portion still contributes, FR-20 exemption). It **excludes a separate `base` and a separate lower-body garment** (FR-50.2).
- **Mutual exclusion & the mandatory floor (FR-50, FR-51):** the lower-body slot holds exactly one of `trousers`/`jeans`/`chinos`/`shorts`/`skirt`/`dress`/`jumpsuit` (no two co-occur); a one-piece excludes a separate `base`; a request with no lower-body slot, or empty, is invalid; every non-lower slot is independently optional and adornment slots combine freely (FR-49.4).
- **Two adornment tiers (FR-21, FR-22):** **statement** adornments (`hat`, `tie`, `scarf`, `belt`, `socks`, `shoes`) qualify iff every primary/secondary is neutral or echoes an anchor chromatic family, else they **disqualify** — one passing, one all-neutral-passing, one failing example each; **minor** adornments (`glasses`, `earrings`, `necklace`, `watch`, `ring`, `bracelet`) **never disqualify**, whatever their colours. Echoes of any chromatic anchor colour — including a *minor* anchor colour and a *minor adornment* — are asserted to be **recorded** for the bonus (FR-11, FR-22), so a minor adornment can only help.
- **Per-category slot constraint (FR-52):** a constraint narrows a slot's candidate set to a named subset of *its own* categories; an empty list or a category not belonging to the slot is rejected; the constraint changes **which garments are eligible**, never the harmony result for a fixed garment (it is a request-time candidate filter, not new maths — asserted by showing identical evaluation of a garment whether or not its category is the constrained one). The pin case is the single-garment limit of the same idea (FR-44).

### 4.7 `test_ranking.py` — deterministic at unit level *(refined — v0.2.0)*

Enumeration's shuffle and the anchor-interleave take an **injected `random.Random`** (NFR-10; architecture §4.3); unit tests pass a seeded instance, making every ranking test exactly reproducible. FR-42's non-determinism is a property of the *system*, not of these units (§8.1). The matcher holds **no global random state** — asserted by constructing two evaluators with different seeds and observing independent streams (NFR-10).

- **Scheme strength (FR-41.1):** a complementary set at exactly 180° outranks one at 165°; a narrower analogous spread outranks a wider; monochromatic scores perfect strength.
- **First-class neutral-based (FR-41.1, FR-43 — v0.2.0):** an empty (all-neutral) scheme set scores `NEUTRAL_BASED_STRENGTH = 0.98` — it ranks **below an otherwise-equal perfect chromatic scheme yet above a weaker chromatic one** (e.g. an analogous set whose strength is < 0.98), asserted with engineered pairs at the 0.98 boundary. A first-class neutral-based result carries `scheme = "neutral-based"` and is **not** flagged a fallback (corrects the v0.1.0 defect where neutral outfits never surfaced).
- **Echo bonus (FR-41.2):** more distinct chromatic echoes outrank fewer at equal scheme strength, **including minor-adornment echoes** (FR-22) — a combination whose only extra echo comes from a minor adornment outranks the otherwise-identical one without it.
- **Variety factor (FR-41.3 — raised, v0.2.0):** with `WEIGHT_VARIETY = 15`, a wardrobe of many near-equal combinations returns results that do **not** all reuse the same base garments where alternatives exist; the **anchor-interleaved enumeration** is asserted to reach distinct anchor garments before the count-independent cap (`MAX_ANCHOR_CANDIDATES`) is hit, given a fixed seed.
- **Count & distinctness (FR-39, FR-40, FR-48):** at most *N* (the requested count, 1–25) returned, all pairwise distinct, `rank` sequential from 1; a wardrobe with exactly *k* < *N* valid combinations returns exactly *k*; `N = 1` and `N = 25` both honoured. The cap is **count-independent** — selecting *N* from the capped pool does not change the pool.
- **Fallback ladder, slimmed (FR-43 — v0.2.0):** all-neutral outfits are **normal first-class results**, not fallbacks (above). The ladder runs only when the capped main enumeration yields **no** FR-15-satisfying combination: (a) a retry restricted to **neutral-only** combinations, any result flagged a **neutral fallback** (`fallback = true`); and (b) if none exists, an empty result whose `EvaluationResult` failure names the constraining slot, asserted against a wardrobe engineered so one slot is provably the constraint. The two neutral cases — first-class `neutral-based` (`fallback = false`) vs the `fallback = true` retry — are asserted to be distinguished in the result object (architecture §2.2).
- **Anchor/colour & pin pruning (FR-44, FR-45):** a colour-family anchor prunes any candidate whose scheme set lacks that family on an anchor; a named-scheme anchor prunes any whose matched scheme differs; a pin restricts a slot to one garment. An unsatisfiable anchor/pin yields the zero result (handled by the ladder above), not a relaxed answer.

### 4.8 Property-based testing — scope and discipline

Hypothesis is used **only** where the input domain is continuous or combinatorially large and a property is crisper than examples: taxonomy totality/determinism (§4.3), hue-distance metric properties and circular-mean membership (§4.2), neutral transparency (§4.5), minor-colour harmlessness (§4.4), role-derivation totality (§4.4), and palette normalisation invariants (§6.1). Boundary behaviour remains the job of the example tables — Hypothesis is not asked to find edges the requirements already name. To keep the gate reproducible (§1.4), `make test-backend` runs Hypothesis with a derandomised profile (`derandomize=True`); developers may run with the default randomised profile locally to hunt for new counterexamples.

### 4.9 Verifying FR-38 — explanations rendered only from the `EvaluationResult`

Four complementary mechanisms:

1. **Structural purity.** `explain.render(result: EvaluationResult) -> str` is the module's only public entry point, and the §5 dependency tests confirm `explain` imports nothing outside the matcher and the standard library — it *cannot* reach the database, the request, or any other source of text.
2. **Construction tests.** Hand-built `EvaluationResult` values → assert the rendered text names the matched FR-13 scheme, mentions each slot's garment with its role, and mentions each recorded echo (family and slots) — the FR-37 content checklist, asserted on substrings, not full prose.
3. **Covariance tests.** Render a result; change exactly one field (the scheme name; remove an echo; swap a role); render again — assert the text changed in the corresponding aspect and only plausibly so. This catches canned text: a template ignoring its input fails immediately.
4. **The integration oracle.** In the §7.4 suggestion tests, for every combination the API returns, the test re-runs the pure evaluation on the returned garments (deterministic — only *enumeration* is shuffled) and asserts the response's `explanation` equals `explain.render` of the re-derived `EvaluationResult`, and the response's `scheme` and `echoes` match it. The explanation provably cannot drift from the evaluation.

Determinism of rendering itself (same result → same text) is asserted as a property.

### 4.10 The golden-file snapshot baseline *(new — v0.2.0)*

The E08 slot-model rewrite changes the rules of the 100 %-covered, deterministic matcher — the layer stack deepens 3→4, the lower-body slot generalises, the one-piece path is new, adornment slots multiply, the Cream family shifts some classifications, and the all-neutral/diversity ranking changes scores. Per `docs/meta/method-improvements.md` #2, F4 spike §6 and architecture §2.2, a **golden-file snapshot of current matcher output must be captured and committed *before* any slot-model code changes**, so every behavioural change surfaces as an explicit, reviewable diff rather than a silent regression. The mechanism:

- **What is pinned (exact).** Three golden files under `backend/tests/matcher/snapshots/`, regenerated by a `--snapshot-update` flag (or a small `make` target) and otherwise read-only in the test:
  1. **Classifications** — a fixed list of HSL inputs (the §11.3 palette tables plus each family's canonical value) → family name.
  2. **Ranking** — a fixed set of engineered wardrobes (§11.2), each evaluated with a **fixed seed** (NFR-10), → the returned combinations' **ordering, the per-combination scheme, and the numeric score components**.
  3. **Explanations** — each of those combinations → its rendered `explain` text.
- **Strictness.** Comparison is **exact** on classification, ranking order, scores and explanation text. Float scores are serialised at a **fixed precision** (the snapshot stores rounded decimal strings) so the comparison is exact and platform-float noise cannot flake it; the seed makes the otherwise non-deterministic ranking reproducible (NFR-10).
- **Sequencing & workflow.** The snapshot ticket is the **first E08 ticket, ahead of any slot-model code** (it captures *current*, pre-rewrite behaviour). During the rewrite, an intended behavioural change is realised by re-running `--snapshot-update` and **committing the changed golden files in the same commit as the code**, so the diff is the record of what changed and why (the ticket's `## Notes` explains it). An *unintended* change fails the test loudly. After E08 completes, the baseline is **re-pinned to the new behaviour** and continues as an ordinary regression guard.
- **Scope note.** The snapshot complements, not replaces, the structural matcher tests (§§4.1–4.9): those assert *correctness against the requirements*; the snapshot asserts *stability across a refactor*. It does not count toward or against the 100 % matcher coverage gate beyond the lines it naturally exercises.

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

**v0.2.0 — the contracts are unchanged.** The slot-model rewrite, the Cream family, the refined ranking and the seedable RNG all stay **inside `matcher`** and add **no new harmony mathematics** (architecture §2.1/§2.2): a statement adornment reuses the echo-slot primitive, a minor adornment the minor-colour primitive, and FR-52 is a request-time candidate filter handled in `services`, not new matcher maths. So the five import-linter contracts and the std-library allowlist hold verbatim — the injected RNG (NFR-10) is passed **in** rather than imported, so `matcher` still imports the standard library only. The allowlist test therefore needs no change; that it continues to pass over the rewritten `slots.py`/`ranking.py` is itself part of the E08 definition of done.

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

One test module per contract section, asserting **field-level shapes against the documented examples**: every success body, and **every documented error code in the §1.3 envelope** — `400 unsupported_format` / `unreadable_image`, `413 file_too_large`, `404 detection_not_found` / `garment_not_found`, `409 empty_slots` (with `details.empty_slots` listing the slots), `409 invalid_regeneration_token`, `422 invalid_palette` / `invalid_category` *(renamed — v0.2.0, was `invalid_type`)* / `invalid_filter` / `invalid_request`. Specific contract invariants:

- **Server-side family derivation (contract §1.6):** submitted HSL with a deliberately wrong implied family → stored family is the server's derivation; the response's `family`/`neutral`/`hex` are consistent with the matcher (cross-checked by calling `matcher.taxonomy` directly in the assertion).
- **Palette validation:** 0 and 5 colours, sums of 99 and 101, `h = 360`, `proportion = 0` → `422 invalid_palette`; the boundary-row method again.
- **`category` field rename (v0.2.0, contract §1.2/§1.3):** every garment representation and filter uses **`category`**, never `type`; the JSON key is asserted on `GarmentSummary`/`Garment` bodies and request bodies (`POST`/`PUT`/`PATCH /api/garments`), and a body sending `type` is rejected (no silent acceptance). Values are the FR-16 categories; `invalid_category` for anything off the allowlist (e.g. the dropped `jersey`).
- **`GET /api/taxonomy` (v0.2.0, contract §2.2):** the `families` array now has **twenty** families including **`Cream`** (neutral, `canonical` only, no `representative_hue`/`hue_arc`); `representative_hue`/`hue_arc` present exactly on the twelve chromatic families; every `canonical` classifies into its own family (Cream's `{48, 28, 91}` → Cream). The new `regions` array is asserted against §2.2: the four regions; each slot's `slot` key, `label`, `categories`, `role` ∈ `anchor`/`statement`/`minor`; `layer_order` present **only** on `base(0)/shirt(1)/mid(2)/outer(3)`; `mandatory: true` **only** on `lower_body`; `default_selected` exactly on `base`/`lower_body`/`socks`/`shoes`; `one_piece_categories`/`one_piece_also_occupies` only on `lower_body`. The slot keys `mid`/`outer` appear (not `jersey`/`jacket`).
- **Inventory filters, grouping & ordering (FR-35, FR-47, contract §2.6):** `category`-only, `family`-only and combined AND queries over a seeded wardrobe; family matches *any* role including minor; `total` correct under `limit`/`offset`. **v0.2.0** — the list arrives **ordered by category, then by the `order` key**: `order=hue` (default) sorts each category group by the **primary-colour (`position = 0`) hue** with **neutral-primary garments after the chromatic spectrum** in a stable defined order; `order=date` is `created_at` newest-first; an unknown `category`/`family`/`order` → `422 invalid_filter`. The ordering is asserted as a property over a wardrobe with known primaries (chromatic ones in hue order, neutrals trailing).
- **`PATCH /api/garments/{id}` — category edit (FR-46, contract §2.10a — v0.2.0):** a one-field `{ "category": … }` body changes **only** the category — same `id`, image, palette and `regenerated_at` (asserted unchanged by re-reading the garment); suggestion eligibility then follows the new category (cross-checked via a follow-up suggestion call). `404 garment_not_found`; `422 invalid_category` (off-allowlist value); `422 invalid_request` (missing `category`, or any extra field). The token-gated `PUT` remains the **only** palette path (FR-32) — a `PATCH` is shown not to touch colours.

### 7.3 Lifecycle, staging and persistence (NFR-3)

- **Upload → confirm:** `POST /api/detections` writes staging file + sidecar and **nothing to the database** (asserted by direct query — FR-24); `POST /api/garments` consumes the token, **moves** the staged image into `data/images/`, generates the thumbnail and inserts both tables in one transaction; the staged files are gone; a second `POST` with the same token → `404` (consumed).
- **Abandonment and TTL:** an expired token (expiry forced via a clock seam or direct sidecar edit) → `404`; the startup sweep removes expired staging entries (invoke the sweep against a prepared staging directory).
- **Rejection writes nothing:** unsupported format / oversize / unreadable → documented error, empty database, empty staging.
- **Regeneration flow (FR-32/FR-33, contract §2.9–§2.10):** `POST …/regenerate` leaves record and image untouched and returns a §2.3-shaped proposal plus `garment_id`; `PUT` with the token replaces palette and type **in place** — same `id`, same `image_file`, `regenerated_at` set; the token is consumed (second `PUT` → `409`); a token bound to a different garment → `409`; expired → `409`; and the FR-32 enforcement itself — `PUT` without a valid regeneration token **always** fails, proving there is no field-editing path.
- **Delete (FR-34):** `204`; record gone (cascade verified on `garment_colours`); image and thumbnail files removed from disk.
- **Atomicity:** a forced failure mid-confirmation (e.g. thumbnail generation made to raise via a seam) leaves no database rows and no moved image — the transaction boundary holds.

### 7.4 Suggestions *(rewritten — v0.2.0; FR-36, FR-39–FR-45, FR-48–FR-52, NFR-5, NFR-10; contract §2.12)*

The endpoint is exercised against the rewritten request `{ slots, pins, anchor, count }` (all optional; `{}` means the FR-51 defaults, no pins, no anchor, `count = 3`). The seedable RNG (NFR-10) is fixed in tests so even the stochastic path is reproducible.

- **Default & slot selection (FR-51):** `{}` selects `base`/`lower_body`/`socks`/`shoes`; a partial `slots` override (`true` selects, `false` deselects) layers over the defaults — the **beach example** `{ "base": false, "socks": false }` returns `lower_body` + `shoes`; omitted keys keep their default.
- **Category constraint (FR-52):** a `slots` value `{ "categories": [...] }` selects **and** narrows the slot; every returned combination fills it from that subset (asserted over a wardrobe where only the excluded categories would otherwise win). Empty list, or a category not in the slot's own set → `422 invalid_request` with `details: { "slot", "invalid_categories" }`.
- **Pins (FR-44):** a `pins` entry forces the pinned garment into its slot in **every** returned combination; the slot is thereby selected; multiple pins all hold. A pin whose garment id is unknown, or whose category does not map to the pinned slot key, or that disagrees with a same-slot category constraint → `422 invalid_request`.
- **Colour/scheme anchor (FR-45):** `anchor.family` → every combination's scheme set contains that family on an anchor; `anchor.scheme` → every combination matches that FR-13 scheme; both given → both hold; unknown family/scheme → `422 invalid_request`.
- **Count (FR-39, FR-48):** `requested_count` echoes the effective `count`; `combinations` holds **at most** that many, fewer only when fewer exist; `count` outside 1–25 → `422 invalid_request` with `details: { "count": … }`; default 3 when omitted.
- **Mandatory floor & contradictions (FR-50, FR-51):** `lower_body: false` → `422` (mandatory); an empty selection or no lower-body slot → fail fast; pinning a one-piece (`dress`/`jumpsuit`) to `lower_body`, or constraining `lower_body` to one-piece categories only, **while `base` is selected** → `422` (FR-50.2); two pins for one slot → `422`.
- **Fail fast (FR-36):** a *selected* slot with no eligible garment → `409 empty_slots` naming exactly those slots in `details.empty_slots`; multiple empty slots all named; an unknown slot key in `slots`/`pins` → `422 invalid_request`.
- **First-class neutral vs neutral fallback (FR-41/FR-43):** a wardrobe whose best outfit is all-neutral returns a combination with `scheme: "neutral-based"` and `fallback: false` (a normal result, ranked per §4.7); only the genuinely-unsatisfiable case produces `fallback: true` (the neutral-only retry) or the zero result. The two are asserted distinct in the response.
- **Invariant assertions over engineered wardrobes** — the FR-42-safe pattern of §8.1, including the FR-38 oracle of §4.9 (re-evaluate each returned combination; assert `scheme`, `echoes` incl. minor-adornment echoes, and `explanation` match), and the one-piece appearing once under `lower_body` with no separate `base` entry.
- **Exact-outcome wardrobes:** wardrobes with exactly one valid combination make even the stochastic path exactly assertable — used for the fallback ladder's two rungs and the zero-result shape (`explanation` + `hint` naming the constraining slot, contract §2.12), and for the pin/anchor unsatisfiable → zero-result cases.

### 7.5 The data migration — old `type` values → new categories *(new — v0.2.0; architecture §3.1)*

The `garments.type` column keeps its name, but its **value set** changes to the FR-16 categories, and the old v0.1.0 values must be migrated **before** the new CHECK allowlist is applied (the old values would otherwise fail the constraint). A dedicated migration test (`api/test_migration.py` or `storage/test_migration.py`, in the default gate) covers it:

- **Fixture.** A small SQLite database seeded with the **v0.1.0 schema and value set** (`top`, `bottom`, `jersey`, `jacket`, `socks`, `shoes`, `hat`, `accessory`) plus their colour rows — committed as a binary fixture or built by a v0.1.0-shaped seed helper.
- **Unambiguous mappings asserted exactly (FR-16):** `jacket`/`socks`/`shoes`/`hat` carry over unchanged (still valid categories); `jersey` → `jumper` (the `jersey` category was dropped, its garments land in the `mid` slot); `top` → `t_shirt`.
- **Ambiguous mappings (architecture §3.1):** `bottom` → a **defined default** among `trousers`/`jeans`/`shorts`/`skirt` (the migration's documented choice), and `accessory` → a **defined default** among the adornment categories; the test asserts the default is applied **and** that the row remains editable to the correct category via `PATCH` (FR-46) — the migration leaves a clean, re-categorisable state rather than guessing.
- **Post-conditions:** after migration every `type` value is in the new FR-16 allowlist (so the new CHECK passes); `id`, `image_file`, colour rows and counts are untouched; the row count is unchanged; running the migration twice is idempotent.

The migration **mechanism** (a one-off script/step run before the new CHECK) is an early M14 ticket; this section pins the behaviour the ticket must satisfy.

---

## 8. Non-determinism and performance

### 8.1 Asserting FR-42 without flaky tests

The rule: **endpoint tests never assert which combinations return; they assert that whatever returns is correct.** For every response *(items 1–2 refined for v0.2.0)*:

1. ≤ *N* combinations (the requested `count`, 1–25 — FR-39, FR-48), pairwise distinct (FR-40), `rank` sequential from 1.
2. Each combination fills exactly the **selected** slots (FR-51 defaults layered with the request's `slots`/`pins`/constraints), with garments of categories that map to those slot keys (FR-16, FR-49); a one-piece appears once under `lower_body` with no separate `base`; any pin/category-constraint/anchor (FR-44/FR-45/FR-52) is honoured by every combination.
3. **The oracle:** the pure matcher re-evaluates each returned combination — it must be harmonious per FR-15 (or, when `fallback: true`, valid under the FR-43a neutral-only restriction), and the response's `scheme` (including first-class `neutral-based`), `echoes` (incl. minor-adornment echoes — FR-22) and `explanation` must match the re-derived `EvaluationResult` (§4.9.4).
4. Repetition is *permitted to differ*, never *required* to differ: a test calling the endpoint repeatedly asserts every response passes 1–3, and **never** asserts inequality between runs (a small wardrobe may legitimately always return the same answer).

Order-sensitivity (does ranking *order* correctly?) is tested deterministically at unit level with the injected seeded RNG (§4.7) — the system test does not duplicate it.

**Seedable variety (NFR-10 — v0.2.0).** The randomness used for candidate enumeration, the anchor-interleave and the variety factor (FR-41.3, FR-42) is supplied by an **injected `random.Random`**, never global state (architecture §2.2/§4.3). This is what lets the otherwise non-deterministic ranking be unit-tested exactly (§4.7) and the snapshot baseline (§4.10) be stable. The test seam is asserted at each layer: `matcher.ranking` accepts the RNG as a parameter (unit tests pass `Random(seed)`); the suggestion service threads a seedable source through (service/API tests fix the seed so the §4.9.4 oracle is exact); and a test confirms **two seeds give independent streams** and the **default runtime source is unseeded** (FR-42's permitted non-determinism). The seed is server-internal and **not** part of the HTTP contract (contract §3, NFR-10 row).

### 8.2 Performance suite — marker `perf`, `make test-perf`

Run against the deterministic 500-garment wardrobe (§11.2), seeded directly through the storage layer (building it through the API would dominate the runtime).

- **NFR-5 *(re-baselined — v0.2.0)*:** `POST /api/suggestions` completes in **< 2 s**, **median of 3 runs**, asserted at the **worst case for v0.2.0: all slots selected *and* `count = 25`** at 500 garments. The bound is **count-independent** — the enumeration cap (`MAX_ANCHOR_CANDIDATES`) does not scale with *N*, so selecting 25 results from the capped pool is cheap; the suite also runs `count = 3` and asserts the two timings are comparable (selection, not enumeration, is what *N* changes). The raised variety/interleave (F5) must not breach the bound. The §11.2 `wardrobe_500` distributes across the **new FR-16 categories** so the worst case is realistic.
- **NFR-6, server half:** `GET /api/garments` with combined **`category` + `family`** filters (and each `order` value) completes in **< 1 s** (median of 3). This is necessary, not sufficient, for NFR-6 — the browser half (now including the client-side grouping of the ordered list, FR-47) is the manual check noted in §3.
- **NFR-4** lives in the `model` suite (§6.3), since it is meaningless without the real model.

These tests are excluded from the default gate because timing on an arbitrary machine is not deterministic; the bounds are contractual on the owner's machine, where the definition of done (§12.3) requires the suite to pass. A failure is a real conversation, not a retry button.

---

## 9. End-to-end smoke suite — `make test-e2e`

Playwright, **Chromium and Firefox projects** (NFR-7), against the genuinely built application: the Playwright `webServer` launches the production-style Uvicorn process (built SPA, real detection with the real model, temporary `data/` directory per run). Nothing is mocked — this suite exists to prove the assembled system works, especially valuable given Milestone 8+ implementation is AI-driven.

Journeys, kept deliberately thin *(updated — v0.2.0 for the reworked screens; HANDOFF-03/HANDOFF-05 states)*:

1. **Add a garment & browse the grouped inventory:** upload a synthetic fixture image via the file picker → confirm-and-correct shows a proposal with swatches and proportions → adjust a proportion → select a **category** from the FR-16 picker (save disabled until chosen, per the Milestone 4 decision) → save → the garment appears in the inventory **grouped by category** with its group header, survives `category` + `family` filtering, and the **Hue/Date-added** order toggle re-orders within the group (FR-47).
2. **Edit a category (FR-46):** from garment detail, change the category directly (no re-detection, no confirm flow) → the garment moves to the new category group in the inventory; the palette is unchanged.
3. **Request an outfit (reworked panel):** against a pre-seeded engineered wardrobe (§11.2), with the default slots, deselect a default slot and **constrain a multi-category slot** (e.g. lower body = shorts/skirt) and/or set a **colour/scheme anchor** and a **count**, optionally **pin a garment** from the picker → ranked result cards (up to the chosen count) render best-first with a scheme chip, per-slot tiles and a non-empty explanation; a first-class **neutral-based** result is unlabelled while a **`fallback: true`** result carries the "Neutral-based fallback" label; "Suggest again" returns a valid (not necessarily different) response (FR-42). A **one-piece** pin auto-deselects `base` with the note.
4. **Empty-slot rejection:** select a slot with no garments → the `409 empty_slots` message renders verbatim on the request panel, the named slot chip flagged "none in wardrobe" (FR-36).

The model and Playwright browsers are on disk after `make setup`; the suite skips with an explicit message if either is missing. E2E asserts user-visible behaviour only — contract details are §7's job; the suite stays thin (these four journeys), with the heavy matrix of `slots`/`pins`/`anchor`/`count`/`422` cases living in §7.4, not the browser.

---

## 10. Frontend testing

### 10.1 Component tests (Vitest + RTL + MSW) — in the default gate

MSW handlers live in one shared module (`frontend/src/test/handlers.ts`) built from the contract's documented example bodies — an executable mirror of `docs/03-api-contract.md`; when the contract changes, this module is the single frontend place to update. Components under test, by screen:

- **Upload & detect:** rejection states render the server's plain-language `message` (FR-24); the `fallback_used` warning banner (FR-27).
- **Confirm-and-correct:** the proportion editor — steppers, live total, stacked preview, **normalise-to-100 on save** (FR-29, the Milestone 4 decision); colour removal; manual add applying the canonical HSL from the taxonomy response; the **category** picker's save-disabled-until-chosen rule, populated from the `regions`/`categories` of `GET /api/taxonomy` *(v0.2.0: category, was type)* (FR-30/FR-31).
- **Inventory *(v0.2.0, FR-47):*** filter bar populated from `GET /api/taxonomy` — the `category` dropdown (region-grouped FR-16 categories) and `family` dropdown with swatches; combined filters and the **`order` toggle (Hue default / Date added)** issue the right query parameters; the client **groups the flat ordered list by `category`** with a header + count per group, neutral-primary garments after the hue spectrum; empty-wardrobe, empty-filter, loading and load-failure states (HANDOFF-03).
- **Garment detail:** regenerate enters confirm-and-correct with the regeneration token; **direct category edit issues `PATCH /api/garments/{id}` with `{ category }`** and reflects the new category without re-detection *(v0.2.0, FR-46)*; delete confirmation step before `DELETE` is issued (FR-34's UI half).
- **Outfit request/results *(rewritten — v0.2.0; HANDOFF-05):*** the request panel composes `{ slots, pins, anchor, count }` (not the v0.1.0 `include`) — slot toggles over the FR-51 defaults with `lower_body` locked-on (FR-51); a multi-category slot's **category checklist** producing a `{ "categories": [...] }` value, un-ticking the last reverting to "any" (FR-52); the **pin** picker (with "Suggest outfits around this") and removable pin chips, a **one-piece pin auto-deselecting `base`** with the note (FR-50.2); the **colour family + scheme** anchor (FR-45); the **count ±stepper** clamped 1–25, default 3 (FR-48); the **searching** state. Results: cards ranked by position (no score numbers), scheme chip, echo line from `echoes` (incl. minor-adornment echoes), a first-class **`neutral-based`** result unlabelled vs the **`fallback: true` "Neutral-based fallback"** label (FR-41/FR-43a); `409 empty_slots` rendered verbatim with per-chip "none in wardrobe" (FR-36); the zero-result state rendering `explanation` and `hint` verbatim (FR-43b).

### 10.2 What component tests do not cover

Routing across screens, real file-upload mechanics, and frontend↔backend integration belong to the E2E journeys (§9). Visual styling is not automated (§3). Pure frontend utilities (e.g. HSL→hex display helpers, if any exist beyond the API's `hex`) get plain Vitest unit tests.

---

## 11. Test data and fixtures

### 11.1 Fixture images — `backend/tests/fixtures/images/`

- **`real/`** — 4–6 small (≤ 1 MB each) genuine phone photographs of garments, committed to the repository, each with a JSON sidecar (`<name>.expected.json`) recording: expected family set, dominant family, dominant proportion ± tolerance, allowed extra families, expected colour-count range, and whether fallback is expected. One photograph is deliberately garment-free (the FR-27 fixture). These serve the `model` suite (§6.3) and journey 1 of E2E.
- **`synthetic/` (generated)** — `tests/fixtures/generate_images.py` deterministically renders garment-like shapes (flat colours, two-colour blocks, a thin-stripe minor colour) on plain contrasting backgrounds with Pillow, writing into a gitignored cache on first use (a pytest session fixture invokes it). Exact expected palettes are known by construction. No generated binaries are committed.
- **`masks/`** — committed pre-computed alpha masks paired with the synthetic images, for the §6.2 injected-segmenter tests.
- Invalid-upload fixtures: a tiny GIF (unsupported format), a truncated JPEG (unreadable), and an oversize file **generated** at test time (a >20 MB blob is never committed).
- **v0.2.0 — a pale warm near-neutral fixture (FR-2).** A synthetic `cream`/`ecru` block (around H ≈ 52°, S ≈ 28 %, L ≈ 90 — the white-jeans case) for `synthetic/`, and, where a representative real photograph exists, an `ecru`/`off-white` `real/` photograph with a sidecar expecting the **Cream** family, so the taxonomy fix is exercised end-to-end through detection as well as in the unit tables (§4.3).

### 11.2 Wardrobe factories — `backend/tests/fixtures/wardrobes.py`

Factory functions returning plain matcher values for unit tests and persisting rows for integration tests (one definition, two materialisations):

- Engineered scenario wardrobes: `single_valid_outfit()`, `two_valid_outfits()`, `neutral_fallback_only()`, `no_valid_outfit_constrained_by(slot)`, `rich_echo_wardrobe()` — each documented with the FR it exists to pin down.
- **v0.2.0 scenario wardrobes** (each documented with the FR it pins): `one_piece_outfit()` (uncovered and covered, FR-18/FR-50), `four_layer_stack()` (covered-layer constraint across `base`/`shirt`/`mid`, FR-20), `statement_vs_minor_adornments()` (a failing statement disqualifies, a clashing minor does not, FR-21), `minor_adornment_echo()` (a minor adornment earns the echo bonus, FR-22), `first_class_neutral_vs_chromatic()` (an all-neutral outfit ranked just below an equal chromatic one, above a weaker one, FR-41), `category_constrained_wardrobe()` (the constrained subset wins only when allowed, FR-52), and `pin_scenarios()` (pin honoured / unsatisfiable pin → zero result, FR-44).
- **`wardrobe_500()` *(updated — v0.2.0)*** — the NFR-5/NFR-6 fixture: 500 garments from a **seeded** RNG with a realistic distribution across the **FR-16 categories** (all slots populated, including one-piece and adornments) and the family taxonomy (now including Cream), so the perf suite is reproducible and the `count = 25` worst case is realistic (§8.2). A small CLI wrapper (`scripts/seed_test_wardrobe.py` or a make target) seeds a running instance for E2E and manual NFR-6 checks.

### 11.3 Shared palette tables — `backend/tests/fixtures/palettes.py`

The boundary tables of §4.3–§4.5 and canonical HSL values, defined once and imported by the matcher tests and the API conformance tests, so a requirements §1.4 change is reflected in exactly one fixture location plus `test_constants.py`. **v0.2.0** — the table gains the **Cream** boundary rows (§4.3) and Cream's canonical HSL, so the new family is pinned in the one shared place.

### 11.4 Frontend fixtures — `frontend/src/test/`

MSW `handlers.ts` plus `contract-examples.ts` holding the contract's documented JSON bodies as typed constants (imported by handlers and assertions alike). **v0.2.0** — the handlers mirror the rewritten contract: `GET /api/taxonomy` `regions`, `GET /api/garments` `order`, `PATCH /api/garments/{id}`, and the `POST /api/suggestions` `{ slots, pins, anchor, count }` request and combination/`409`/`422` responses.

### 11.5 Snapshot and migration fixtures *(new — v0.2.0)*

- **Matcher snapshots — `backend/tests/matcher/snapshots/`** — the three committed golden files (classifications, ranking, explanations) of §4.10, regenerated only via the documented `--snapshot-update` flow.
- **Migration fixture — `backend/tests/fixtures/legacy/`** — a v0.1.0-schema, v0.1.0-value-set SQLite database (or a v0.1.0-shaped seed helper) for the §7.5 data-migration test; small, committed, never regenerated by the app.

---

## 12. Conventions and definition of done

### 12.1 Layout and naming

```
backend/tests/
  conftest.py                  app-factory, tmp data-dir and client fixtures
  test_architecture.py         §5.2 stdlib allowlist (import-linter config in pyproject.toml)
  matcher/test_<submodule>.py  one per matcher submodule (§4)
  matcher/test_snapshot.py     §4.10 golden-file baseline; snapshots/ holds the goldens   (v0.2.0)
  detection/test_*.py          §6.1–§6.2; test_model_pipeline.py carries @pytest.mark.model
  api/test_<resource>.py       §7, one per contract section group
  api/test_migration.py        §7.5 old type → new category migration                     (v0.2.0)
  perf/test_bounds.py          @pytest.mark.perf (§8.2)
  fixtures/                    §11 (incl. fixtures/legacy/ for the migration — v0.2.0)
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

Every Milestone 8+ implementation ticket (this includes the v0.2.0 Milestone 14+ tickets) that creates or changes behaviour covered by a numbered requirement **must include or update tests in the same commit as the implementation**, citing the FR/NFR ids and the relevant section of this strategy in its acceptance criteria. Tickets exempt from new tests: documentation-only, pure-styling, and build-plumbing tickets — the exemption must be stated in the ticket.

**Test-first for v0.2.0 (the deterministic and contract-pinned layers — §1 principle 6).** For `matcher`, `services` logic and `api` contract shapes, the v0.2.0 tickets write the failing test from the requirement/contract **first**, confirm it fails for the right reason, then implement — the test and implementation still land in **one commit** (the "same commit" rule above is unchanged; "test-first" governs the *order of work within* the ticket, not the commit boundary). This is a documented working policy, deliberately **not** a new mechanical gate: a grep-for-FR-ids coverage check was considered and **rejected** (`docs/meta/method-improvements.md` #1) as shallow annotation-chasing; real coverage is assured by the structural tests, the matcher gate and `/verify`. The probabilistic `detection` layer keeps characterisation/after tests (tolerance-based, §6). The E08 snapshot baseline (§4.10) is the one case where "fail-first" manifests as a **changed golden file** reviewed in the diff rather than a red assertion.

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

### 13.1 v0.2.0 testing decisions (Milestone 13)

| Decision | Outcome |
|---|---|
| Doc structure | The delta is applied **in place** with `*(amended/rewritten — v0.2.0)*` markers plus new subsections (§4.10 snapshot, §7.5 migration), matching the requirements/architecture/API house style — not a separate appended section. |
| Test-first policy | Documented working policy for `matcher`/`services`/`api` (v0.2.0 brief §6); **not** a new mechanical gate (the grep-for-ids check is rejected, method-improvements #1). Detection keeps characterisation tests. |
| Snapshot baseline | Golden files pin **classification + ranking order + scores + explanation text, compared exactly** (scores at fixed precision); captured by the **first E08 ticket** before any slot-model code; updated in-commit during the rewrite (§4.10). |
| Seedable variety | An **injected `random.Random`** at the matcher boundary (NFR-10); fixed seed in unit/service/API tests; FR-42 asserted as invariants, never inter-run inequality (§8.1). |
| NFR-5 re-baseline | Perf asserted at the **`count = 25`, all-slots** worst case at 500 garments; bound is count-independent (the cap does not scale with *N*) (§8.2). |
| Cream | Boundary tables for the Beige/Tan→Cream hand-off and the 70° ceiling (§4.3); `GET /api/taxonomy` now twenty families; a pale-near-neutral detection fixture (§11.1). |
| Migration | A dedicated test pins the old `type` → new category mappings, including the two ambiguous cases (`bottom`/`accessory`) handled by a default + a `PATCH` re-categorisation pass (§7.5). |
| Dependency contracts | **Unchanged** — the rewrite adds no harmony maths and the RNG is injected, so the five import-linter contracts and the std-lib allowlist hold verbatim (§5). |

---

## 14. Traceability — requirements to tests

| Requirement | Primary test location (§ of this document) |
|---|---|
| FR-1–FR-5 (taxonomy) | `matcher/test_taxonomy.py` (§4.3); canonical cross-checks in `api/test_taxonomy.py` (§7.2); snapshot classifications (§4.10) |
| FR-2 (**Cream** — v0.2.0) | Cream boundary rows + ordering (§4.3); twenty families + Cream canonical (§7.2); detection fixture (§11.1) |
| FR-6 (1–4 colours, sum 100) | `detection` integerisation (§6.1); `api` palette validation (§7.2) |
| FR-7–FR-11 (roles, echoes) | `matcher/test_roles.py` (§4.4); echo recording in `test_slots.py` (§4.6) |
| FR-12–FR-15 (harmony) | `matcher/test_colour.py`, `test_harmony.py` (§4.2, §4.5) |
| FR-16–FR-22 (slots, layering — rewritten v0.2.0) | `matcher/test_slots.py` (§4.6); `category` rename + `GET /api/taxonomy` regions (§7.2); snapshot (§4.10) |
| FR-23–FR-25 (upload, rejection, storage) | `api/test_detections.py`, lifecycle tests (§7.2–§7.3) |
| FR-26–FR-27 (detection, fallback) | §6.1–§6.3 across default and `model` suites |
| FR-28–FR-31 (confirm-and-correct, type) | API flow tests (§7.3); frontend confirm components (§10.1); E2E journey 1 (§9) |
| FR-32 (amended — category editable), FR-33 (regenerate) | Regeneration token flow (§7.3); `PATCH` category does not touch palette (§7.2) |
| FR-34 (delete) | Lifecycle tests (§7.3); frontend confirmation step (§10.1) |
| FR-35 (inventory, filters) | `api/test_garments.py` filters (§7.2); frontend filter bar (§10.1) |
| FR-36 (slot selection, fail fast — amended) | `api/test_suggestions.py` (§7.4: slots/pins/anchor/count, `409`/`422`); frontend panel + 409 (§10.1) |
| FR-37–FR-38 (explanations) | `matcher/test_explain.py` + the integration oracle (§4.9, §8.1) |
| FR-39–FR-41 (count, distinct, ranking — refined) | `matcher/test_ranking.py` seeded (§4.7: first-class neutral, top-*N*); endpoint invariants (§8.1); snapshot (§4.10) |
| FR-42 (non-determinism, seedable) | Invariant-only endpoint assertions (§8.1); injected RNG (§4.7, NFR-10) |
| FR-43 (fallback ladder — slimmed) | `test_ranking.py` (§4.7); exact-outcome wardrobes (§7.4); frontend labels/zero-state (§10.1) |
| FR-44 (**pin a garment** — v0.2.0) | `test_ranking.py` pin pruning (§4.7); `api/test_suggestions.py` `pins` + `422` (§7.4); e2e (§9) |
| FR-45 (**colour/scheme anchor** — v0.2.0) | `test_ranking.py` anchor pruning (§4.7); `api/test_suggestions.py` `anchor` + `422` (§7.4) |
| FR-46 (**edit category** — v0.2.0) | `PATCH /api/garments/{id}` (§7.2); garment-detail component + e2e (§10.1, §9) |
| FR-47 (**grouping & ordering** — v0.2.0) | `api/test_garments.py` `order`/neutrals-last (§7.2); frontend grouping + order toggle (§10.1); perf (§8.2) |
| FR-48 (**count** — v0.2.0) | `test_ranking.py` top-*N* (§4.7); `count`/`422` (§7.4); count stepper (§10.1) |
| FR-49–FR-52 (**slot/region model, per-category constraint** — v0.2.0) | `matcher/test_slots.py` (§4.6); `GET /api/taxonomy` regions + `slots` constraint `422` (§7.2, §7.4) |
| NFR-1/NFR-8 (offline) | Construction: all targets offline after setup (§1.3, §2.2) |
| NFR-2 (single command) | E2E `webServer` boots the production-style process (§9); health probe in §7.2 |
| NFR-3 (single-directory state) | Temporary-`data/`-rooted integration tests; file lifecycle assertions (§7.1, §7.3) |
| NFR-4 (detection < 5 s) | Soft assertion in the `model` suite (§6.3) |
| NFR-5 (suggestions < 2 s @ 500) | `perf` suite (§8.2) |
| NFR-6 (inventory < 1 s @ 500) | Server half in `perf` (§8.2); browser half manual (§3) |
| NFR-7 (Chrome + Firefox) | Playwright Chromium + Firefox projects (§9) |
| NFR-5 (amended — bound holds at count 25) | `perf` suite at all-slots/`count=25` (§8.2) |
| NFR-9 (pure matcher) | §4 throughout; enforced by §5 and the matcher coverage gate (§2.3); unchanged by the rewrite (§5 v0.2.0 note) |
| NFR-10 (**seedable variety** — v0.2.0) | Injected RNG asserted at matcher/service/API layers; independent streams + unseeded runtime (§8.1, §4.7) |
| Data migration (old `type` → category — v0.2.0) | `api/test_migration.py` (§7.5) |
| Regression stability across the E08 refactor (v0.2.0) | Golden-file snapshot baseline (§4.10) |

---

*Approval of this document closed Milestone 5 (v0.1.0). Approval of the v0.2.0 delta above closes the test-strategy half of Milestone 13; the ticket batch (`tickets/*` HUE-059+, epics E06–E10) is the other half. This is a living document; see `docs/00-milestone-plan.md` for current status.*
