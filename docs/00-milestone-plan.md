# Hueniform — Milestone Plan and Progress Tracker

| | |
|---|---|
| **Document** | Milestone plan and progress tracker |
| **Repository location** | `docs/00-milestone-plan.md` |
| **Last updated** | 18 June 2026 (Milestone 11 complete; Milestone 12 next, not started) |

This document is the single source of truth for **where the project is**. It was extracted from the project brief (§14) so the brief stays stable after approval while this tracker is updated as each milestone completes. Update the status column and the *Current position* line in the same commit as the milestone's deliverable.

---

## Current position

> **v0.1.0 shipped and tagged `v0.1.0`. Milestone 12 complete (signed off, committed) — the wireframe deltas are in `docs/04-wireframes/` (rewritten outfit-request + results, inventory grouping/ordering, garment-detail category edit, confirm-and-correct category picker, updated index, and per-screen design-handoff briefs). During M12 the outfit-request screen revealed a genuine gap (slots too coarse to request), so M10/M11 were reopened and re-amended first: expanded FR-16 taxonomy, upper-body layer-slot rename (`jersey`/`jacket` → `mid`/`outer`), and a new per-category slot constraint (FR-52) inside the suggestion request — all committed with the wireframes. A Claude Design pass was deliberately skipped (single-user offline tool; visual styling to emerge in implementation against the committed wireframes). Next: Milestone 13 — test-strategy delta + ticket generation (`docs/05-test-strategy.md`, `tickets/*` HUE-059+, epics E06–E10), which must also cover the M12 additions (FR-52, expanded categories, layer rename, the new suggestion request/response shapes).**

---

## Milestones

### v0.1.0 — MVP (shipped, tagged `v0.1.0`)

| # | Milestone | Deliverable | Tool | Status |
|---|---|---|---|---|
| 1 | Project brief | `docs/01-project-brief.md` | **Chat** | ✅ Complete |
| 2 | Requirements document | `docs/02-requirements.md` — functional requirements incl. concrete harmony and role rules, palette taxonomy | **Chat** | ✅ Complete |
| 3 | Architecture & API contract | `docs/03-architecture.md`, `docs/03-api-contract.md`, data model | **Chat** | ✅ Complete |
| 4 | Wireframes | `docs/04-wireframes/` — key screens as Markdown + images/HTML | **Cowork** | ✅ Complete |
| 5 | Test strategy | `docs/05-test-strategy.md` — frameworks, what is unit/integration/E2E tested, esp. the colour matcher | **Chat** | ✅ Complete |
| 6 | Ticket generation | `tickets/*.md` + ticket-system conventions doc + `BOARD.md` index | **Cowork** | ✅ Complete |
| 7 | Repository setup & scaffolding | Repo initialised, docs and tickets committed, backend/frontend skeletons | **Code** | ✅ Complete |
| 8 | Implementation, ticket by ticket | Working software (HUE-007–HUE-058); tickets updated in the same commits | **Code** | ✅ Complete |

### v0.2.0 — Essential features (in planning)

| # | Milestone | Deliverable | Tool | Status |
|---|---|---|---|---|
| 9 | v0.2.0 brief | `docs/09-v0.2.0-brief.md` — seven features (F1–F7), epics E06–E10, requirement deltas | **Cowork** | ✅ Complete |
| 10 | Category-model design + requirement deltas | F4 spike output; updated `docs/02-requirements.md` (FR-16–22 rewrite, FR-44–51, NFR-10, FR-2 tuning) | **Cowork** | ✅ Complete (addended in M12 session — expanded FR-16 taxonomy, layer-slot rename, new FR-52; spike §7, requirements §9.2) |
| 11 | Architecture & API deltas | `docs/03-architecture.md`, `docs/03-api-contract.md` — category edit, pin/scheme + count suggestion API, taxonomy | **Cowork** | ✅ Complete (addended in M12 session — expanded category set, `jersey`/`jacket` → `mid`/`outer` slot keys, per-category slot constraints) |
| 12 | Wireframe deltas | `docs/04-wireframes/` — new/changed screens (category edit, build-around request, suggestion count, inventory grouping) + design-handoff briefs | **Cowork** | ✅ Complete |
| 13 | Test-strategy delta + ticket generation | `docs/05-test-strategy.md` (test-first policy, seedable variety, snapshot baseline); `tickets/*` (HUE-059+), epics E06–E10 | **Cowork** | ⬜ Not started |
| 14+ | Implementation, ticket by ticket | Working software; tickets updated in the same commits | **Code** | ⬜ Not started |

---

## Conventions

- **Status values:** ⬜ Not started · 🔶 In progress · ✅ Complete
- A milestone is marked **In progress** (🔶) when work on it starts, and is marked **Complete** (✅) only after **explicit user sign-off** — not merely when its deliverable looks finished (see root `CLAUDE.md`, *Milestone status lifecycle*). On sign-off it is committed to the repository.
- Each milestone is conducted in its own conversation/session in the assigned tool, with the relevant prior documents available as project files.
- New milestones (e.g. roadmap items from brief §10) require their own brief and are appended here only once approved.
