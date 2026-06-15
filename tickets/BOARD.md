# Hueniform — Ticket Board (Execution Order)

| | |
|---|---|
| **Document** | Topological index of all tickets |
| **Repository location** | `tickets/BOARD.md` |
| **Source** | The ticket files in `tickets/`; format per `TICKET-TEMPLATE.md`; system per `CONVENTIONS.md` |

This board is the single topological view of the implementation order. Implementation tickets are listed by their execution number (`HUE-NNN`); reading top to bottom is a legal build sequence because no ticket depends on a higher-numbered one (CONVENTIONS.md §4.3). It is a *derived* view of the ticket files' `depends_on` edges and is regenerated, never hand-edited for status (CONVENTIONS.md §5.4). Epics are containers and sit outside the execution order.

**Status legend:** `todo` · `in-progress` · `blocked` · `in-review` · `done`

## Capability epics

| id | title | milestone | status |
|---|---|---|---|
| HUE-E01 | Local-first foundation and meta-goal | 8 | todo |
| HUE-E02 | Pure colour matcher | 8 | todo |
| HUE-E03 | Add a garment | 8 | todo |
| HUE-E04 | Browse the wardrobe | 8 | todo |
| HUE-E05 | Suggest an outfit | 8 | todo |

## Implementation tickets — execution order

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
| 11 | HUE-011 | Implement matcher.harmony | task | matcher | 8 / matcher | HUE-E02 | todo | HUE-009, HUE-008 |
| 12 | HUE-012 | Wardrobe and scenario fixtures | task | tooling | 8 / tooling | HUE-E02 | todo | HUE-009, HUE-010 |
| 13 | HUE-013 | Implement matcher.slots | task | matcher | 8 / matcher | HUE-E02 | todo | HUE-010, HUE-011, HUE-012 |
| 14 | HUE-014 | Implement matcher.ranking | task | matcher | 8 / matcher | HUE-E02 | todo | HUE-013, HUE-011 |
| 15 | HUE-015 | Implement matcher.explain | task | matcher | 8 / matcher | HUE-E02 | todo | HUE-014 |
| 16 | HUE-016 | Storage models and database engine | task | storage | 8 / storage | HUE-E03 | todo | HUE-002 |
| 17 | HUE-017 | Image store, thumbnails and staging store | task | storage | 8 / storage | HUE-E03 | todo | HUE-016 |
| 18 | HUE-018 | Detection pure helpers | task | detection | 8 / detection | HUE-E03 | todo | HUE-009 |
| 19 | HUE-019 | Detection pipeline orchestration | task | detection | 8 / detection | HUE-E03 | todo | HUE-018, HUE-006 |
| 20 | HUE-020 | Real-model detection integration and setup model fetch | task | detection | 8 / detection | HUE-E03 | todo | HUE-019 |
| 21 | HUE-021 | Detection service and staging orchestration | task | services | 8 / services | HUE-E03 | todo | HUE-019, HUE-017 |
| 22 | HUE-022 | Garment service: confirm-save and delete | task | services | 8 / services | HUE-E03 | todo | HUE-021, HUE-016, HUE-017, HUE-009 |
| 23 | HUE-023 | Regeneration service | task | services | 8 / services | HUE-E03 | todo | HUE-022, HUE-021 |
| 24 | HUE-024 | Suggestion service: enumeration, ranking and the fallback ladder | task | services | 8 / services | HUE-E05 | todo | HUE-015, HUE-014, HUE-013, HUE-016 |
| 25 | HUE-025 | API foundation: schemas, error envelope, health, static serving | task | api | 8 / api | HUE-E01 | todo | HUE-002, HUE-016 |
| 26 | HUE-026 | Taxonomy endpoint | task | api | 8 / api | HUE-E03 | todo | HUE-025, HUE-009 |
| 27 | HUE-027 | Detections endpoints | task | api | 8 / api | HUE-E03 | todo | HUE-025, HUE-021 |
| 28 | HUE-028 | Garment create endpoint | task | api | 8 / api | HUE-E03 | todo | HUE-027, HUE-022, HUE-026 |
| 29 | HUE-029 | Garment read endpoints and inventory filters | task | api | 8 / api | HUE-E04 | todo | HUE-025, HUE-022 |
| 30 | HUE-030 | Garment regenerate, replace and delete endpoints | task | api | 8 / api | HUE-E03 | todo | HUE-029, HUE-023, HUE-027 |
| 31 | HUE-031 | Suggestions endpoint | task | api | 8 / api | HUE-E05 | todo | HUE-025, HUE-024 |
| 32 | HUE-032 | Frontend API client, query layer and shared components | task | frontend | 8 / frontend | HUE-E01 | todo | HUE-003, HUE-005, HUE-006 |
| 33 | HUE-033 | Upload and detect screen | story | frontend | 8 / frontend | HUE-E03 | todo | HUE-032 |
| 34 | HUE-034 | Confirm-and-correct screen | story | frontend | 8 / frontend | HUE-E03 | todo | HUE-032, HUE-033 |
| 35 | HUE-035 | Inventory browser screen | story | frontend | 8 / frontend | HUE-E04 | todo | HUE-032 |
| 36 | HUE-036 | Garment detail screen | story | frontend | 8 / frontend | HUE-E03 | todo | HUE-032, HUE-034, HUE-035 |
| 37 | HUE-037 | Outfit request and suggestion results screen | story | frontend | 8 / frontend | HUE-E05 | todo | HUE-032 |
| 38 | HUE-038 | Single-command run and production serving | task | tooling | 8 / tooling | HUE-E01 | todo | HUE-025, HUE-032, HUE-020 |
| 39 | HUE-039 | Performance suite and 500-garment fixture | task | tooling | 8 / tooling | HUE-E01 | todo | HUE-031, HUE-029, HUE-024 |
| 40 | HUE-040 | End-to-end smoke suite | task | tooling | 8 / tooling | HUE-E01 | todo | HUE-033, HUE-034, HUE-035, HUE-036, HUE-037, HUE-027, HUE-028, HUE-029, HUE-030, HUE-031, HUE-020, HUE-038 |

## By milestone and batch

| milestone | batch | tickets |
|---|---|---|
| 7 | scaffolding | HUE-001, HUE-002, HUE-003 |
| 7 | tooling | HUE-004, HUE-005, HUE-006 |
| 8 | matcher | HUE-007, HUE-008, HUE-009, HUE-010, HUE-011, HUE-013, HUE-014, HUE-015 |
| 8 | tooling | HUE-012, HUE-038, HUE-039, HUE-040 |
| 8 | storage | HUE-016, HUE-017 |
| 8 | detection | HUE-018, HUE-019, HUE-020 |
| 8 | services | HUE-021, HUE-022, HUE-023, HUE-024 |
| 8 | api | HUE-025, HUE-026, HUE-027, HUE-028, HUE-029, HUE-030, HUE-031 |
| 8 | frontend | HUE-032, HUE-033, HUE-034, HUE-035, HUE-036, HUE-037 |

## Requirement traceability (derived from `implements`)

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

