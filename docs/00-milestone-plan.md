# Hueniform — Milestone Plan and Progress Tracker

| | |
|---|---|
| **Document** | Milestone plan and progress tracker |
| **Repository location** | `docs/00-milestone-plan.md` |
| **Last updated** | 18 June 2026 (Milestone 10 complete; v0.2.0 in progress) |

This document is the single source of truth for **where the project is**. It was extracted from the project brief (§14) so the brief stays stable after approval while this tracker is updated as each milestone completes. Update the status column and the *Current position* line in the same commit as the milestone's deliverable.

---

## Current position

> **v0.1.0 shipped and tagged `v0.1.0`. Milestone 10 complete (signed off) — the F4 category-model spike is settled (`docs/spikes/2026-06-18-f4-category-slot-model.md`) and the v0.2.0 requirement deltas are written into `docs/02-requirements.md` (FR-16–22 rewritten; FR-44–51 and NFR-10 added; FR-41–43 refined; FR-2/32/35/36/39 amended). Next: Milestone 11 — the architecture & API deltas (`docs/03-architecture.md`, `docs/03-api-contract.md`).**

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
| 10 | Category-model design + requirement deltas | F4 spike output; updated `docs/02-requirements.md` (FR-16–22 rewrite, FR-44–51, NFR-10, FR-2 tuning) | **Cowork** | ✅ Complete |
| 11 | Architecture & API deltas | `docs/03-architecture.md`, `docs/03-api-contract.md` — category edit, pin/scheme + count suggestion API, taxonomy | **Cowork** | ⬜ Not started |
| 12 | Wireframe deltas | `docs/04-wireframes/` — new/changed screens (category edit, build-around request, suggestion count, inventory grouping) | **Cowork** | ⬜ Not started |
| 13 | Test-strategy delta + ticket generation | `docs/05-test-strategy.md` (test-first policy, seedable variety, snapshot baseline); `tickets/*` (HUE-059+), epics E06–E10 | **Cowork** | ⬜ Not started |
| 14+ | Implementation, ticket by ticket | Working software; tickets updated in the same commits | **Code** | ⬜ Not started |

---

## Conventions

- **Status values:** ⬜ Not started · 🔶 In progress · ✅ Complete
- A milestone is marked **In progress** (🔶) when work on it starts, and is marked **Complete** (✅) only after **explicit user sign-off** — not merely when its deliverable looks finished (see root `CLAUDE.md`, *Milestone status lifecycle*). On sign-off it is committed to the repository.
- Each milestone is conducted in its own conversation/session in the assigned tool, with the relevant prior documents available as project files.
- New milestones (e.g. roadmap items from brief §10) require their own brief and are appended here only once approved.
