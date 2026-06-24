# Hueniform — Ticket Board (Execution Order)

| | |
|---|---|
| **Document** | Topological index of all tickets |
| **Repository location** | `tickets/BOARD.md` |
| **Source** | The ticket files in `tickets/`; format per `TICKET-TEMPLATE.md`; system per `CONVENTIONS.md` |

This board is the single topological view of the implementation order. Implementation tickets are listed by their execution number (`HUE-NNN`); reading top to bottom is a legal build sequence because no ticket depends on a higher-numbered one (CONVENTIONS.md §4.3). It is a *derived* view of the ticket files' `depends_on` edges and is regenerated, never hand-edited for status (CONVENTIONS.md §5.4). Epics are containers and sit outside the execution order.

The version sections are ordered **latest first**: v0.2.0 (Milestone 14, in planning) above v0.1.0 (Milestones 7–8, shipped). Each version's execution order is followed by its own cleanup backlog.

**Status legend:** `todo` · `in-progress` · `blocked` · `in-review` · `done`

## Capability epics

| id | title | milestone | status |
|---|---|---|---|
| HUE-E06 | Constrained suggestions | 14 | todo |
| HUE-E07 | Edit a garment's category | 14 | todo |
| HUE-E08 | Category & slot-model overhaul | 14 | todo |
| HUE-E09 | Suggestion quality & count | 14 | todo |
| HUE-E10 | Inventory grouping & ordering | 14 | todo |
| HUE-E01 | Local-first foundation and meta-goal | 8 | done |
| HUE-E02 | Pure colour matcher | 8 | done |
| HUE-E03 | Add a garment | 8 | done |
| HUE-E04 | Browse the wardrobe | 8 | done |
| HUE-E05 | Suggest an outfit | 8 | done |

## v0.2.0 — execution order (Milestone 14)

Leaf tickets for v0.2.0 (epics E06–E10). Reading top to bottom is a legal build sequence; no ticket depends on a higher-numbered one. The snapshot baseline (HUE-059) is sequenced first among the E08 slot-model work (test strategy §4.10; architecture §2.2). Epics close when their children are all `done`.

| # | id | title | type | layer | M / batch | epic | status | depends_on |
|---|---|---|---|---|---|---|---|---|
| 59 | HUE-059 | Matcher golden-file snapshot baseline | task | matcher | 14 / matcher | HUE-E08 | done | HUE-015 |
| 60 | HUE-060 | matcher.constants v0.2.0 — category/slot model and new named values | task | matcher | 14 / matcher | HUE-E08 | done | HUE-059, HUE-007 |
| 61 | HUE-061 | matcher.slots rewrite — regions, four-layer stack, one-piece, adornment tiers | task | matcher | 14 / matcher | HUE-E08 | done | HUE-060, HUE-013 |
| 62 | HUE-062 | matcher.taxonomy — the Cream family | task | matcher | 14 / matcher | HUE-E09 | done | HUE-060, HUE-009 |
| 63 | HUE-063 | matcher.ranking refinements — first-class neutral, diversity, top-N, seedable RNG | task | matcher | 14 / matcher | HUE-E09 | done | HUE-061, HUE-062, HUE-014 |
| 64 | HUE-064 | matcher.explain — new slot vocabulary and neutral vs fallback wording | task | matcher | 14 / matcher | HUE-E09 | done | HUE-061, HUE-063, HUE-015 |
| 65 | HUE-065 | Storage category value-set and data migration | task | storage | 14 / storage | HUE-E08 | done | HUE-016 |
| 66 | HUE-066 | GET /api/taxonomy — regions/slots model | task | api | 14 / api | HUE-E08 | done | HUE-061, HUE-062, HUE-026 |
| 67 | HUE-067 | Frontend API client and MSW handlers — v0.2.0 contract | task | frontend | 14 / frontend | HUE-E08 | done | HUE-032 |
| 68 | HUE-068 | Suggestion service — slot-selection and per-category constraint rewrite | task | services | 14 / services | HUE-E08 | done | HUE-061, HUE-063, HUE-064, HUE-065, HUE-024 |
| 69 | HUE-069 | POST /api/suggestions — slot-selection and constraint request/response | task | api | 14 / api | HUE-E08 | done | HUE-068, HUE-066, HUE-031 |
| 70 | HUE-070 | Confirm-and-correct category picker | story | frontend | 14 / frontend | HUE-E08 | done | HUE-067, HUE-034 |
| 71 | HUE-071 | Outfit-request slot selector and category-constraint checklist | story | frontend | 14 / frontend | HUE-E08 | todo | HUE-067, HUE-037 |
| 72 | HUE-072 | Garment service — direct category edit | task | services | 14 / services | HUE-E07 | todo | HUE-065, HUE-022 |
| 73 | HUE-073 | PATCH /api/garments/{id} — edit category | task | api | 14 / api | HUE-E07 | todo | HUE-072, HUE-030 |
| 74 | HUE-074 | Garment-detail category edit UI | story | frontend | 14 / frontend | HUE-E07 | todo | HUE-067, HUE-036 |
| 75 | HUE-075 | Inventory ordering (hue spectrum / date) in the read query | task | services | 14 / services | HUE-E10 | todo | HUE-022, HUE-047 |
| 76 | HUE-076 | GET /api/garments — order parameter and category filter rename | task | api | 14 / api | HUE-E10 | todo | HUE-075, HUE-029 |
| 77 | HUE-077 | Grouped inventory view with order toggle | story | frontend | 14 / frontend | HUE-E10 | todo | HUE-067, HUE-035 |
| 78 | HUE-078 | Suggestion service — count and refined ranking integration | task | services | 14 / services | HUE-E09 | todo | HUE-068, HUE-063 |
| 79 | HUE-079 | POST /api/suggestions — count field and neutral/fallback response | task | api | 14 / api | HUE-E09 | todo | HUE-078, HUE-069 |
| 80 | HUE-080 | Outfit-request count control and neutral/fallback labels | story | frontend | 14 / frontend | HUE-E09 | todo | HUE-071 |
| 81 | HUE-081 | Suggestion service — pins and colour/scheme anchor | task | services | 14 / services | HUE-E06 | todo | HUE-068, HUE-063 |
| 82 | HUE-082 | POST /api/suggestions — pins and anchor request and validation | task | api | 14 / api | HUE-E06 | todo | HUE-081, HUE-069 |
| 83 | HUE-083 | Outfit-request pin picker and anchor controls | story | frontend | 14 / frontend | HUE-E06 | todo | HUE-071 |
| 84 | HUE-084 | Performance re-baseline at count 25 and wardrobe_500 update | task | tooling | 14 / tooling | HUE-E09 | todo | HUE-079, HUE-076, HUE-039 |
| 85 | HUE-085 | End-to-end smoke suite update (v0.2.0 journeys) | task | tooling | 14 / tooling | HUE-E06 | todo | HUE-070, HUE-071, HUE-074, HUE-077, HUE-080, HUE-083, HUE-069, HUE-073, HUE-076, HUE-079, HUE-082, HUE-040 |

## Cleanup backlog — v0.2.0

Reactive tickets from `/verify` post-batch reviews of the Milestone 14 work (CONVENTIONS.md §6). Worked between batches or at milestone end; critical tickets are promoted into the v0.2.0 execution order above. Allocated after the current highest number (next is HUE-086), preserving the no-forward-dependency invariant.

| # | id | title | type | layer | source batch | status | depends_on |
|---|---|---|---|---|---|---|---|
| _none yet_ | | | | | | | |

## Implementation tickets — execution order (v0.1.0 — shipped)

| # | id | title | type | layer | M / batch | epic | status | depends_on |
|---|---|---|---|---|---|---|---|---|
| 1 | HUE-001 | Initialise the repository | task | repo | 7 / scaffolding | HUE-E01 | done | — |
| 2 | HUE-002 | Backend skeleton and application settings | task | tooling | 7 / scaffolding | HUE-E01 | done | HUE-001 |
| 3 | HUE-003 | Frontend skeleton and navigation shell | task | frontend | 7 / scaffolding | HUE-E01 | done | HUE-001 |
| 4 | HUE-004 | Backend test tooling and dependency-rule gate | task | tooling | 7 / tooling | HUE-E01 | done | HUE-002 |
| 5 | HUE-005 | Frontend test tooling and Playwright harness | task | tooling | 7 / tooling | HUE-E01 | done | HUE-003 |
| 6 | HUE-006 | Shared test fixtures and palette tables | task | tooling | 7 / tooling | HUE-E01 | done | HUE-004, HUE-005 |
| 7 | HUE-007 | Implement matcher.constants | task | matcher | 8 / matcher | HUE-E02 | done | HUE-004 |
| 8 | HUE-008 | Implement matcher.colour | task | matcher | 8 / matcher | HUE-E02 | done | HUE-007 |
| 9 | HUE-009 | Implement matcher.taxonomy | task | matcher | 8 / matcher | HUE-E02 | done | HUE-008, HUE-006 |
| 10 | HUE-010 | Implement matcher.roles | task | matcher | 8 / matcher | HUE-E02 | done | HUE-009 |
| 11 | HUE-011 | Implement matcher.harmony | task | matcher | 8 / matcher | HUE-E02 | done | HUE-009, HUE-008 |
| 12 | HUE-012 | Wardrobe and scenario fixtures | task | tooling | 8 / tooling | HUE-E02 | done | HUE-009, HUE-010 |
| 13 | HUE-013 | Implement matcher.slots | task | matcher | 8 / matcher | HUE-E02 | done | HUE-010, HUE-011, HUE-012 |
| 14 | HUE-014 | Implement matcher.ranking | task | matcher | 8 / matcher | HUE-E02 | done | HUE-013, HUE-011 |
| 15 | HUE-015 | Implement matcher.explain | task | matcher | 8 / matcher | HUE-E02 | done | HUE-014 |
| 16 | HUE-016 | Storage models and database engine | task | storage | 8 / storage | HUE-E03 | done | HUE-002 |
| 17 | HUE-017 | Image store, thumbnails and staging store | task | storage | 8 / storage | HUE-E03 | done | HUE-016 |
| 18 | HUE-018 | Detection pure helpers | task | detection | 8 / detection | HUE-E03 | done | HUE-009 |
| 19 | HUE-019 | Detection pipeline orchestration | task | detection | 8 / detection | HUE-E03 | done | HUE-018, HUE-006 |
| 20 | HUE-020 | Real-model detection integration and setup model fetch | task | detection | 8 / detection | HUE-E03 | done | HUE-019 |
| 21 | HUE-021 | Detection service and staging orchestration | task | services | 8 / services | HUE-E03 | done | HUE-019, HUE-017 |
| 22 | HUE-022 | Garment service: confirm-save and delete | task | services | 8 / services | HUE-E03 | done | HUE-021, HUE-016, HUE-017, HUE-009 |
| 23 | HUE-023 | Regeneration service | task | services | 8 / services | HUE-E03 | done | HUE-022, HUE-021 |
| 24 | HUE-024 | Suggestion service: enumeration, ranking and the fallback ladder | task | services | 8 / services | HUE-E05 | done | HUE-015, HUE-014, HUE-013, HUE-016 |
| 41 | HUE-041 | Fix N+1 query in suggestion_service _load_wardrobe | task | services | 8 / cleanup | — | done | HUE-024 |
| 25 | HUE-025 | API foundation: schemas, error envelope, health, static serving | task | api | 8 / api | HUE-E01 | done | HUE-002, HUE-016 |
| 26 | HUE-026 | Taxonomy endpoint | task | api | 8 / api | HUE-E03 | done | HUE-025, HUE-009 |
| 27 | HUE-027 | Detections endpoints | task | api | 8 / api | HUE-E03 | done | HUE-025, HUE-021 |
| 28 | HUE-028 | Garment create endpoint | task | api | 8 / api | HUE-E03 | done | HUE-027, HUE-022, HUE-026 |
| 29 | HUE-029 | Garment read endpoints and inventory filters | task | api | 8 / api | HUE-E04 | done | HUE-025, HUE-022 |
| 30 | HUE-030 | Garment regenerate, replace and delete endpoints | task | api | 8 / api | HUE-E03 | done | HUE-029, HUE-023, HUE-027 |
| 31 | HUE-031 | Suggestions endpoint | task | api | 8 / api | HUE-E05 | done | HUE-025, HUE-024 |
| 32 | HUE-032 | Frontend API client, query layer and shared components | task | frontend | 8 / frontend | HUE-E01 | done | HUE-003, HUE-005, HUE-006 |
| 33 | HUE-033 | Upload and detect screen | story | frontend | 8 / frontend | HUE-E03 | done | HUE-032 |
| 34 | HUE-034 | Confirm-and-correct screen | story | frontend | 8 / frontend | HUE-E03 | done | HUE-032, HUE-033 |
| 35 | HUE-035 | Inventory browser screen | story | frontend | 8 / frontend | HUE-E04 | done | HUE-032 |
| 36 | HUE-036 | Garment detail screen | story | frontend | 8 / frontend | HUE-E03 | done | HUE-032, HUE-034, HUE-035 |
| 37 | HUE-037 | Outfit request and suggestion results screen | story | frontend | 8 / frontend | HUE-E05 | done | HUE-032 |
| 38 | HUE-038 | Single-command run and production serving | task | tooling | 8 / tooling | HUE-E01 | done | HUE-025, HUE-032, HUE-020 |
| 39 | HUE-039 | Performance suite and 500-garment fixture | task | tooling | 8 / tooling | HUE-E01 | done | HUE-031, HUE-029, HUE-024, HUE-041 |
| 40 | HUE-040 | End-to-end smoke suite | task | tooling | 8 / tooling | HUE-E01 | done | HUE-033, HUE-034, HUE-035, HUE-036, HUE-037, HUE-027, HUE-028, HUE-029, HUE-030, HUE-031, HUE-020, HUE-038 |

## Cleanup backlog — v0.1.0

Reactive tickets from `/verify` post-batch reviews (CONVENTIONS.md §6). Worked between batches or at milestone end; critical tickets are promoted to the main sequence.

| # | id | title | type | layer | source batch | status | depends_on |
|---|---|---|---|---|---|---|---|
| 42 | HUE-042 | DRY garment_service internal helpers | task | services | services | done | HUE-022, HUE-023 |
| 43 | HUE-043 | Shared conftest for service tests | task | tooling | services | done | HUE-021, HUE-022, HUE-023, HUE-024 |
| 44 | HUE-044 | DRY API response conversion helpers | task | api | api | done | HUE-031 |
| 45 | HUE-045 | API error code constants and dead validate_palette removal | task | api | api | done | HUE-031 |
| 46 | HUE-046 | Shared API test conftest | task | tooling | api | done | HUE-031 |
| 47 | HUE-047 | SQL-level pagination and lightweight garment lookup | task | services | api | done | HUE-029, HUE-030 |
| 48 | HUE-048 | Fix SCHEME_LABELS map and add neutral-based test coverage | task | frontend | frontend | done | HUE-037 |
| 49 | HUE-049 | Extract shared GARMENT_TYPES constant and remove TYPE_LABELS duplication | task | frontend | frontend | done | HUE-032, HUE-034, HUE-035 |
| 50 | HUE-050 | Shared frontend test utilities (renderRoute, createTestQueryClient) | task | tooling | frontend | done | HUE-032, HUE-033, HUE-034, HUE-035, HUE-036, HUE-037 |
| 51 | HUE-051 | Memoise taxonomy lookups in Suggest, Wardrobe and AddConfirm | task | frontend | frontend | done | HUE-034, HUE-035, HUE-037 |
| 52 | HUE-052 | Configure staleTime for taxonomy and garments queries | task | frontend | frontend | done | HUE-032 |
| 53 | HUE-053 | Consolidate ErrorBanner and WarningBanner into Banner component | task | frontend | frontend | done | HUE-032 |
| 54 | HUE-054 | Deduplicate GARMENT_TYPES constant in backend | task | services | cleanup | done | HUE-013, HUE-016, HUE-025 |
| 55 | HUE-055 | Type-safe colour_out converter with Protocol | task | api | cleanup | done | HUE-044 |
| 56 | HUE-056 | Extract colour-row grouping helper | task | services | cleanup | done | HUE-042, HUE-047 |
| 57 | HUE-057 | React.memo for GarmentCard and PaletteStrip | task | frontend | cleanup | done | HUE-032 |
| 58 | HUE-058 | Lazy route loading with React.lazy and Suspense | task | frontend | cleanup | done | HUE-032 |

## By milestone and batch

| milestone | batch | tickets |
|---|---|---|
| 14 | matcher | HUE-059, HUE-060, HUE-061, HUE-062, HUE-063, HUE-064 |
| 14 | storage | HUE-065 |
| 14 | api | HUE-066, HUE-069, HUE-073, HUE-076, HUE-079, HUE-082 |
| 14 | services | HUE-068, HUE-072, HUE-075, HUE-078, HUE-081 |
| 14 | frontend | HUE-067, HUE-070, HUE-071, HUE-074, HUE-077, HUE-080, HUE-083 |
| 14 | tooling | HUE-084, HUE-085 |
| 8 | matcher | HUE-007, HUE-008, HUE-009, HUE-010, HUE-011, HUE-013, HUE-014, HUE-015 |
| 8 | tooling | HUE-012, HUE-038, HUE-039, HUE-040 |
| 8 | storage | HUE-016, HUE-017 |
| 8 | detection | HUE-018, HUE-019, HUE-020 |
| 8 | services | HUE-021, HUE-022, HUE-023, HUE-024 |
| 8 | api | HUE-025, HUE-026, HUE-027, HUE-028, HUE-029, HUE-030, HUE-031 |
| 8 | frontend | HUE-032, HUE-033, HUE-034, HUE-035, HUE-036, HUE-037 |
| 7 | scaffolding | HUE-001, HUE-002, HUE-003 |
| 7 | tooling | HUE-004, HUE-005, HUE-006 |

## Requirement traceability (derived from `implements`)

### v0.2.0 requirement traceability (Milestone 14; new and amended requirements)

New or amended FRs/NFRs and the v0.2.0 tickets that realise them (the v0.1.0 tickets below still implement the original behaviour where a requirement was amended in place).

| requirement | tickets |
|---|---|
| FR-2 (Cream — amended) | HUE-062, HUE-066 |
| FR-16 (categories — rewritten) | HUE-060, HUE-061, HUE-065, HUE-066, HUE-067, HUE-070, HUE-072, HUE-073 |
| FR-17–FR-22 (slot model — rewritten) | HUE-061, HUE-068 |
| FR-32 (category editable — amended) | HUE-072, HUE-073 |
| FR-35 (inventory filters — extended) | HUE-076, HUE-077 |
| FR-36 (slot selection, fail fast — amended) | HUE-068, HUE-069, HUE-071 |
| FR-39 (up to N — amended) | HUE-063, HUE-078, HUE-079, HUE-080 |
| FR-40 (distinct) | HUE-063 |
| FR-41 (ranking, first-class neutral — refined) | HUE-063, HUE-079, HUE-080 |
| FR-42 (non-determinism, seedable — refined) | HUE-063 |
| FR-43 (fallback ladder — slimmed) | HUE-063, HUE-078, HUE-079, HUE-080 |
| FR-44 (pin a garment — new) | HUE-081, HUE-082, HUE-083 |
| FR-45 (colour/scheme anchor — new) | HUE-081, HUE-082, HUE-083 |
| FR-46 (edit category — new) | HUE-072, HUE-073, HUE-074 |
| FR-47 (grouping & ordering — new) | HUE-075, HUE-076, HUE-077 |
| FR-48 (suggestion count — new) | HUE-063, HUE-078, HUE-079, HUE-080 |
| FR-49 (region/slot structure — new) | HUE-060, HUE-061, HUE-066, HUE-068, HUE-069, HUE-071 |
| FR-50 (mutual exclusion — new) | HUE-061, HUE-068, HUE-069, HUE-071 |
| FR-51 (configurable required slots — new) | HUE-060, HUE-061, HUE-068, HUE-069, HUE-071 |
| FR-52 (per-category slot constraint — new) | HUE-068, HUE-069, HUE-071 |
| NFR-5 (perf — re-baselined at count 25) | HUE-063, HUE-068, HUE-084 |
| NFR-6 (inventory responsive) | HUE-075, HUE-077, HUE-084 |
| NFR-7 (Chrome + Firefox) | HUE-085 |
| NFR-9 (pure matcher — preserved) | HUE-059, HUE-060, HUE-061, HUE-062, HUE-063, HUE-064 |
| NFR-10 (seedable variety — new) | HUE-063 |

> **Snapshot/migration guards (no requirement, regression safety):** HUE-059 (golden-file
> snapshot baseline of current matcher output, captured before the E08 rewrite — test strategy
> §4.10); the §7.5 data-migration test is delivered by HUE-065.

### v0.1.0 requirement traceability

Each FR/NFR maps to the implementation tickets that realise it (epics omitted; they aggregate their children).

| requirement | tickets |
|---|---|
| FR-1 | HUE-009, HUE-022, HUE-026 |
| FR-2 | HUE-009, HUE-026 |
| FR-3 | HUE-009, HUE-026 |
| FR-4 | HUE-009, HUE-026 |
| FR-5 | HUE-009, HUE-026, HUE-032, HUE-034 |
| FR-6 | HUE-006, HUE-010, HUE-018, HUE-028 |
| FR-7 | HUE-010 |
| FR-8 | HUE-010 |
| FR-9 | HUE-010 |
| FR-10 | HUE-010 |
| FR-11 | HUE-010 |
| FR-12 | HUE-008, HUE-011 |
| FR-13 | HUE-011 |
| FR-14 | HUE-011 |
| FR-15 | HUE-011 |
| FR-16 | HUE-013 |
| FR-17 | HUE-013, HUE-031, HUE-037 |
| FR-18 | HUE-013 |
| FR-19 | HUE-013 |
| FR-20 | HUE-013 |
| FR-21 | HUE-013 |
| FR-22 | HUE-013 |
| FR-23 | HUE-027, HUE-033 |
| FR-24 | HUE-021, HUE-027, HUE-033 |
| FR-25 | HUE-017, HUE-022, HUE-028 |
| FR-26 | HUE-019, HUE-020, HUE-021, HUE-027, HUE-033 |
| FR-27 | HUE-018, HUE-019, HUE-020, HUE-021, HUE-027, HUE-033, HUE-034 |
| FR-28 | HUE-021, HUE-027, HUE-034 |
| FR-29 | HUE-022, HUE-026, HUE-028, HUE-034 |
| FR-30 | HUE-022, HUE-028, HUE-034 |
| FR-31 | HUE-028, HUE-034 |
| FR-32 | HUE-023, HUE-030, HUE-036 |
| FR-33 | HUE-023, HUE-030, HUE-034, HUE-036 |
| FR-34 | HUE-022, HUE-030, HUE-036 |
| FR-35 | HUE-029, HUE-035 |
| FR-36 | HUE-024, HUE-031, HUE-037 |
| FR-37 | HUE-015, HUE-024, HUE-031, HUE-037 |
| FR-38 | HUE-015, HUE-024, HUE-031, HUE-037 |
| FR-39 | HUE-014, HUE-024, HUE-031, HUE-037 |
| FR-40 | HUE-014, HUE-024, HUE-031, HUE-037 |
| FR-41 | HUE-014, HUE-024, HUE-031, HUE-037 |
| FR-42 | HUE-014, HUE-024, HUE-031, HUE-037 |
| FR-43 | HUE-014, HUE-024, HUE-031, HUE-037 |
| NFR-1 | HUE-002, HUE-020, HUE-038 |
| NFR-2 | HUE-002, HUE-025, HUE-038 |
| NFR-3 | HUE-001, HUE-002, HUE-016, HUE-017, HUE-038 |
| NFR-4 | HUE-020 |
| NFR-5 | HUE-024, HUE-031, HUE-039 |
| NFR-6 | HUE-029, HUE-035, HUE-039 |
| NFR-7 | HUE-003, HUE-005, HUE-040 |
| NFR-8 | HUE-020, HUE-038 |
| NFR-9 | HUE-004, HUE-007, HUE-008, HUE-009, HUE-010, HUE-011, HUE-012, HUE-013, HUE-014, HUE-015 |
