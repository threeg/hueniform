# <PROJECT> — Ticket-System Conventions

| | |
|---|---|
| **Document** | Ticket-system conventions |
| **Repository location** | `tickets/CONVENTIONS.md` |
| **Applies to** | Every file in `tickets/`, alongside `TICKET-TEMPLATE.md` (the canonical format) |

This document defines how the ticket system works: the identifier scheme, the status lifecycle, what
each frontmatter field means, how `depends_on` expresses execution order, the rule that a ticket may
not start until its dependencies are done, and how tickets are kept honest as work completes.
`TICKET-TEMPLATE.md` is canonical for the *shape* of a ticket; this document governs the *system* the
tickets form. Where the two appear to disagree, the template wins on format and this document wins on
process.

The ticket system replaces an external tracker: tickets are plain Markdown files living beside the
code in a single repository, committed and updated in the same commits as the work they describe.

> Replace `<PRJ>` throughout with your project's short prefix (e.g. `HUE`, `ACME`). Replace the layer
> names with your architecture's layers.

---

## 1. Identifier scheme

1. **Implementation tickets** are `<PRJ>-NNN`, zero-padded to three digits: `<PRJ>-001`,
   `<PRJ>-002`, … The number is allocated in **execution order** — a ticket with a lower number
   never depends on a higher-numbered one (§4). The id is permanent once allocated; numbers are never
   reused or renumbered, even if a ticket is later abandoned.
2. **Epics** are `<PRJ>-E0N`: `<PRJ>-E01`, `<PRJ>-E02`, … Epics are containers (brief capabilities)
   and carry no code, so they sit *outside* the execution order; the `E` prefix keeps them visually
   distinct and stops them consuming an execution slot.
3. The filename is the id plus a short slug: `<PRJ>-007-core-constants.md`,
   `<PRJ>-E02-pure-core.md`. One ticket per file.
4. A ticket's id appears in exactly one place as the source of truth — its own `id:` frontmatter
   field. Every other mention (a `depends_on` edge, an epic's `Children` list, a `BOARD.md` row) is a
   reference to it.

---

## 2. Status lifecycle

The `status` field takes exactly one of the five values defined by the template:

| Status | Meaning | Entry condition |
|--------|---------|-----------------|
| `todo` | Not started. The default at creation. | — |
| `in-progress` | Actively being worked. **All** `depends_on` ids are `done` (§4). | Work has started. |
| `blocked` | Cannot proceed despite dependencies being met — an external problem, a discovered defect elsewhere, or a decision needed. | Recorded with the reason in `## Notes`. |
| `in-review` | Work complete and self-tested; awaiting the owner's review before being declared done. | Definition of done satisfied bar final sign-off. |
| `done` | Complete: the definition of done holds in full, including the same-commit status update (§5) and a green default gate. | All DoD checkboxes ticked. |

Normal flow is `todo → in-progress → in-review → done`. `blocked` may be entered from `in-progress`
and is left back to `in-progress` once unblocked. A ticket is **not** `done` until its deliverable is
committed; "done on my machine" is `in-review`.

The milestone tracker (`docs/milestone-plan.md`) uses its own three-symbol vocabulary (⬜ / 🔶 /
✅) for *milestones*; that is a separate, coarser lifecycle and is not the per-ticket status here.

---

## 3. Frontmatter fields

| Field | Meaning and rules |
|-------|-------------------|
| `id` | The unique identifier (§1). Source of truth for the ticket's identity. |
| `title` | Short imperative summary. One line. |
| `type` | `epic` \| `story` \| `task` \| `spike`. Stories are user-facing slices; tasks are backend/infra work verified without a UI; epics are containers; spikes are time-boxed investigations. The body structure follows from this field. |
| `status` | The lifecycle value (§2). |
| `milestone` | The milestone number from `docs/milestone-plan.md`. Scaffolding/tooling/fixtures and implementation are typically separate milestones. Epics record the milestone in which their last child completes. |
| `batch` | Optional grouping within a milestone. Here it carries the **architecture layer**, making the dependency rule legible at a glance and giving `BOARD.md` a second axis. |
| `layer` | The architecture layer (`core` \| `domain` \| `storage` \| `services` \| `interface` \| `frontend` \| `tooling` \| `docs` \| `repo`). The `depends_on` graph must respect the dependency rule for this layer (§4). |
| `depends_on` | The execution-order edges: ids that must be `done` before this ticket may start (§4). Epics are never listed here — depend on the specific child instead. |
| `implements` | The `FR-n` / `NFR-n` ids from `docs/requirements.md` this ticket realises. Every requirement is implemented by at least one ticket; `BOARD.md` traceability derives from these fields. Pure scaffolding/tooling tickets may implement an NFR's *enforcement* or none. |
| `tests_required` | `true` for any ticket creating/changing numbered-requirement behaviour (tests in the same commit). `false` only for docs-only, pure-styling, or build-plumbing tickets; the body states which exemption applies. |
| `estimate` | Rough session-sizing on the Fibonacci scale (1, 2, 3, 5, 8). A sizing aid, not a commitment; every ticket is scoped to fit a single implementation session. |

No ticket adds frontmatter fields beyond those the template defines, and none omits a required field.

---

## 4. `depends_on` — ordering and the start rule

1. **`depends_on` is the execution order.** Each entry is the id of a ticket that must be `done`
   before this ticket may move to `in-progress`. This is the one and only place execution order is
   encoded; `BOARD.md` is a *view* of these edges, never an independent source.
2. **The start rule.** A ticket may not start until **every** id in its `depends_on` is `done`.
   Starting earlier means building on unfinished foundations and is a process violation.
3. **No forward dependencies.** Because ids are allocated in execution order (§1.1), every id in a
   `depends_on` list is numerically lower than the ticket's own id. The set of tickets is therefore a
   **valid topological ordering**: reading `BOARD.md` top to bottom is a legal build sequence. Any
   forward edge is a defect, fixed by re-sequencing, not worked around.
4. **The dependency rule is encoded here.** The architecture's layer rule (architecture §2.1) must be
   reflected in the `depends_on` graph: a `services` ticket may depend on `core`/`domain`/`storage`
   tickets; an `interface` ticket depends on `services`, never the reverse. The boundary-enforcement
   tooling enforces the same rule in code; the ticket graph and the import contracts must agree.
5. **Frontend independence.** Because the interface contract (`docs/api-contract.md`) is fixed, the
   frontend/client can be built against the contract independently of the backend. Frontend tickets
   therefore depend on the frontend skeleton, the typed client, and the request mocks — **not** on the
   backend endpoint tickets. End-to-end assembly is reconciled in an e2e capstone ticket that depends
   on both sides.
6. **Epics carry no edges.** An epic lists its children in its body and is referenced by them in
   prose, but never appears in any `depends_on`. Epics close when all their children are `done`.

---

## 5. Keeping tickets honest as work completes

Tickets are updated *as work completes*, not retrofitted. The mechanism, binding for every
implementation ticket:

1. **Status and notes change in the same commit as the work.** When a commit moves a ticket's state —
   starting it, finishing it, blocking it — that commit edits the ticket's `status` and appends a
   dated line to `## Notes`. The work and the record of the work are never split across commits.
2. **The definition of done is the gate.** A ticket reaches `done` only when every checkbox in its
   body's definition of done is satisfied (test strategy §12.3).
3. **`## Notes` is the audit trail.** Creation, status transitions, blockers, and any decision that
   deviates from or refines the spec are recorded there with an ISO date.
4. **`BOARD.md` is regenerated, not hand-edited for status.** When a ticket's status changes,
   `BOARD.md`'s status column is brought into line in the same commit. The board is a derived view
   (§4.1), kept in step with the ticket files rather than treated as a parallel source.
5. **A specification change is a documented change.** Numeric thresholds and rules are contractual. If
   implementing a ticket reveals the spec must change, the change is recorded in the relevant `docs/`
   document first and the ticket references it — tickets do not silently reinterpret a settled
   decision.
6. **Every completed ticket carries a completion report.** On completion the ticket records — and the
   chat response repeats — a plain-language **summary** and a one-line **sanity test**; UI tickets
   additionally record manual **QA steps**. The QA steps accumulate as living per-screen documentation.

---

## 6. Cleanup backlog

Reactive tickets discovered by post-batch review rather than planned up front.

1. **Creation.** After each batch completes, run the **`sfk-verify` skill** (`skills/sfk-verify/SKILL.md`),
   which audits the committed code against the spec and reviews it for reuse, quality and efficiency
   issues. Accepted findings become cleanup tickets — ordinary `task` tickets with `batch: cleanup`,
   numbered after the current highest id so the no-forward-dependency invariant (§4.3) holds
   automatically.
2. **Board placement.** Cleanup tickets live in a dedicated **Cleanup backlog** table in `BOARD.md`,
   separate from the main execution-order table, so they stay visible without cluttering the critical
   path.
3. **Dependencies.** Each cleanup ticket's `depends_on` lists the tickets whose code it cleans up.
   Nothing in the main sequence depends on a cleanup ticket unless explicitly promoted.
4. **When to work them.** Between batches or at the end of a milestone, at the developer's discretion,
   under the same lifecycle and definition-of-done rules.
5. **Promotion.** If a cleanup ticket is **critical** — it would cause a gate failure (e.g. a
   performance regression, a warning that breaks the zero-warnings gate) — it is promoted into the
   main sequence, slotted before the gate it would affect.
6. **Scope.** Cleanup tickets do not implement new requirements (`implements: []`); they improve
   internal quality of already-shipped code. A finding that reveals a genuine spec gap is a
   specification change (§5.5), not a cleanup ticket.

---

## 7. Relationship to the other index files

- `TICKET-TEMPLATE.md` — the canonical per-ticket format. Authoritative for shape.
- `CONVENTIONS.md` (this file) — how the ticket *system* works. Authoritative for process.
- `BOARD.md` — the single topological view of all tickets in execution order, plus requirement
  traceability derived from `implements`.
- `CLAUDE.md` (in this folder) — the quick workflow rules an agent loads when touching `tickets/`.
