# Hueniform — Ticket-System Conventions

| | |
|---|---|
| **Document** | Ticket-system conventions |
| **Repository location** | `tickets/CONVENTIONS.md` |
| **Applies to** | Every file in `tickets/`, alongside `TICKET-TEMPLATE.md` (the canonical format) |
| **Source** | Project brief (`docs/01-project-brief.md`) meta-goal and §13; ticket template (`tickets/TICKET-TEMPLATE.md`); test strategy (`docs/05-test-strategy.md` §12.3) |

This document defines how the Hueniform ticket system works: the identifier scheme, the status lifecycle, what each frontmatter field means, how `depends_on` expresses execution order, the rule that a ticket may not start until its dependencies are done, and how tickets are kept honest as work completes. `TICKET-TEMPLATE.md` remains canonical for the *shape* of a ticket; this document governs the *system* the tickets form. Where the two appear to disagree, the template wins on format and this document wins on process.

The ticket system replaces Jira for this project (brief §13, meta-goal): tickets are plain Markdown files living beside the code in a single repository, committed and updated in the same commits as the work they describe.

---

## 1. Identifier scheme

1. **Implementation tickets** are identified `HUE-NNN`, zero-padded to three digits: `HUE-001`, `HUE-002`, … The number is allocated in **execution order** — a ticket with a lower number never depends on a ticket with a higher number (§4). The id is permanent once allocated; numbers are never reused or renumbered, even if a ticket is later abandoned.
2. **Epics** are identified `HUE-E0N`: `HUE-E01` … `HUE-E05`. Epics are containers (brief §11 capabilities) and carry no code, so they sit *outside* the execution order; their `E` prefix keeps them visually distinct from the numbered work and stops them consuming an execution slot.
3. The filename is the id plus a short slug: `HUE-007-matcher-constants.md`, `HUE-E02-pure-colour-matcher.md`. One ticket per file (template rule).
4. A ticket's id appears in exactly one place as the source of truth — its own `id:` frontmatter field. Every other mention (a `depends_on` edge, an epic's `Children` list, a row in `BOARD.md`) is a reference to it.

---

## 2. Status lifecycle

The `status` field takes exactly one of the five values defined by the template:

| Status | Meaning | Entry condition |
|---|---|---|
| `todo` | Not started. The default for every ticket at creation. | — |
| `in-progress` | Actively being worked. **All** of the ticket's `depends_on` ids are `done` (§4). | A developer has started the work. |
| `blocked` | Cannot proceed despite dependencies being met — an external problem, a discovered defect elsewhere, or a decision needed. | Recorded with the reason in the ticket's `## Notes`. |
| `in-review` | Work complete and self-tested; awaiting the owner's review/approval before being declared done. | The definition of done in the ticket body is satisfied bar the final sign-off. |
| `done` | Complete: the definition of done holds in full, including the same-commit status update (§5) and, for implementation tickets, a green `make test` (test strategy §12.3). | All DoD checkboxes ticked. |

Normal flow is `todo → in-progress → in-review → done`. `blocked` may be entered from `in-progress` and is left back to `in-progress` once unblocked. A ticket is **not** `done` until its deliverable is committed; "done on my machine" is `in-review`.

The milestone tracker (`docs/00-milestone-plan.md`) uses its own three-symbol vocabulary (⬜ / 🔶 / ✅) for *milestones*; that is a separate, coarser lifecycle and is not the per-ticket status here.

---

## 3. Frontmatter fields

Every ticket carries the full frontmatter block defined by `TICKET-TEMPLATE.md`. The fields mean:

| Field | Meaning and rules |
|---|---|
| `id` | The unique identifier (§1). Source of truth for the ticket's identity. |
| `title` | Short imperative summary, e.g. "Implement the colour taxonomy". One line. |
| `type` | `epic` \| `story` \| `task` \| `spike`. Stories are user-facing slices (the frontend screens); tasks are backend/infrastructure work verified without a UI (matcher, detection, storage, services, API, tooling, repo); epics are containers; spikes are time-boxed investigations. The body structure is dictated by this field. |
| `status` | The lifecycle value (§2). |
| `milestone` | The milestone number from `docs/00-milestone-plan.md`. Scaffolding, tooling and fixtures are milestone **7**; all matcher/detection/storage/services/api/frontend implementation is milestone **8**. Epics record the milestone in which their last child completes. |
| `batch` | Optional grouping within a milestone. Here it carries the **architecture layer** (`scaffolding`, `tooling`, `matcher`, `storage`, `detection`, `services`, `api`, `frontend`), making the matcher → detection → services → api dependency rule legible at a glance and giving `BOARD.md` a second axis. |
| `layer` | The architecture layer the ticket sits in (`matcher` \| `detection` \| `storage` \| `services` \| `api` \| `frontend` \| `tooling` \| `docs` \| `repo`). The `depends_on` graph must respect the dependency rule for this layer (§4). |
| `depends_on` | The execution-order edges: the ids that must be `done` before this ticket may start (§4). Epics are never listed here — depending on a container would be meaningless; depend on the specific child instead. |
| `implements` | The `FR-n` / `NFR-n` identifiers from `docs/02-requirements.md` this ticket realises. Every functional and non-functional requirement is implemented by at least one ticket; `BOARD.md`'s traceability is derived from these fields. Pure scaffolding/tooling tickets may legitimately implement an NFR (e.g. NFR-9's *enforcement*) or none. |
| `tests_required` | `true` for any ticket creating or changing numbered-requirement behaviour (test strategy §12.2 — tests in the same commit). `false` only for documentation-only, pure-styling, or build-plumbing tickets, and the body must state which exemption applies. |
| `estimate` | Rough session-sizing on the Fibonacci scale (1, 2, 3, 5, 8). A sizing aid, not a commitment; every ticket is scoped to fit a single Code session. |

No ticket adds frontmatter fields beyond those the template defines, and none omits a field the template requires. A field the template marks optional (`batch`) may be absent, but in this project it is always present and carries the layer.

---

## 4. `depends_on` — ordering and the start rule

1. **`depends_on` is the execution order.** Each entry is the id of a ticket that must be `done` before this ticket may move to `in-progress`. This is the one and only place execution order is encoded; `BOARD.md` is a *view* of these edges, never an independent source.
2. **The start rule.** A ticket may not start until **every** id in its `depends_on` is `done`. Starting earlier means building on unfinished foundations and is a process violation, recorded as such if it happens.
3. **No forward dependencies.** Because ids are allocated in execution order (§1.1), every id in a `depends_on` list is numerically lower than the ticket's own id. The set of tickets is therefore a **valid topological ordering** of the dependency graph: reading `BOARD.md` top to bottom is a legal build sequence. Any forward edge (depending on a higher number) is a defect to be fixed by re-sequencing, not worked around.
4. **The dependency rule is encoded here.** The architecture's layer rule — `matcher` → `detection` → `services` → `api`, with `storage` beneath `services` and nothing importing `api` — must be reflected in the `depends_on` graph: a `services` ticket may depend on `matcher`, `detection` and `storage` tickets; an `api` ticket depends on `services` (and the API foundation), never the reverse. `detection` tickets depend only on the `matcher` submodules the architecture permits (`taxonomy`, `colour`, `constants`). The import-linter contracts and the std-library allowlist (test strategy §5) enforce the same rule in code; the ticket graph and the import contracts must agree.
5. **Frontend independence.** The API contract (`docs/03-api-contract.md`) lets the frontend be built against the contract independently of the backend. Frontend screen tickets therefore depend on the frontend skeleton, the typed API client and the MSW handlers — **not** on the backend endpoint tickets. End-to-end assembly is reconciled in the E2E capstone ticket, which depends on both sides.
6. **Epics carry no edges.** An epic lists its children in its body (`## Children`) and is referenced by them in prose, but never appears in any `depends_on`. Epics are closed when all their children are `done`.

---

## 5. Keeping tickets honest as work completes

The meta-goal (brief §11.6) is that tickets are updated *as work completes*, not retrofitted. The mechanism, binding for every implementation ticket (test strategy §12.3.7):

1. **Status and notes change in the same commit as the work.** When a commit moves a ticket's state — starting it, finishing it, blocking it — that commit edits the ticket file's `status` field and appends a dated line to its `## Notes` section. The work and the record of the work are never split across commits. A reviewer reading `git log` sees the ticket and its code move together.
2. **The definition of done is the gate.** A ticket reaches `done` only when every checkbox in its body's definition of done is satisfied. For Milestone 8+ implementation tickets that means, at minimum (test strategy §12.3): `make test` passes; new or changed numbered-requirement behaviour has tests in the same commit (§12.2); the matcher coverage gate holds for matcher-touching work; `make test-model` passes for detection-touching work; `make test-perf` passes for suggestion-/inventory-query-touching work; `make test-e2e` passes for user-flow-touching work; and the ticket's status and notes are updated in that commit.
3. **`## Notes` is the audit trail.** Creation, status transitions, blockers, and any decision that deviates from or refines the specification are recorded there with an ISO date. The ticket stays an honest, self-contained record of how the work actually went.
4. **`BOARD.md` is regenerated, not hand-edited for status.** When a ticket's status changes, `BOARD.md`'s status column is brought into line in the same commit. Because the board is a derived view (§4.1), it is kept in step with the ticket files rather than treated as a parallel source that could drift.
5. **A specification change is a documented change.** Numeric thresholds and rules are contractual (requirements §1.4). If implementing a ticket reveals the specification must change, the change is recorded in the relevant `docs/` document first and the ticket references it — tickets do not silently reinterpret a settled decision.

---

## 6. Relationship to the other index files

- `TICKET-TEMPLATE.md` — the canonical per-ticket format (frontmatter + body per type). Authoritative for shape.
- `CONVENTIONS.md` (this file) — how the ticket *system* works. Authoritative for process.
- `BOARD.md` — the single topological view of all tickets in execution order (id, title, type, layer, milestone/batch, status, `depends_on`), plus requirement traceability derived from `implements`.
