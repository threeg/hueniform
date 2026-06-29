# <PROJECT> — Milestone Plan and Progress Tracker

| | |
|---|---|
| **Document** | Milestone plan and progress tracker |
| **Repository location** | `docs/milestone-plan.md` |
| **Last updated** | <DATE> (<one-line note: which milestone just completed; what is next>) |

This document is the single source of truth for **where the project is**. It is extracted from the
project brief so the brief stays stable after approval while this tracker is updated as each
milestone completes. Update the status column **and** the *Current position* line in the same commit
as the milestone's deliverable.

---

## Current position

> <One paragraph in plain language: what has shipped and been signed off, what milestone is in
> progress, and exactly what the next action is. This line is what a fresh session reads first to
> orient itself. Keep it current — it is the most-read line in the repo.>

---

## Milestones

### v0.1.0 — <MVP / first release> (<status: in progress | shipped, tagged `v0.1.0`>)

| # | Milestone | Deliverable | Tool | Status |
|---|-----------|-------------|------|--------|
| 1 | Project brief | `docs/project-brief.md` | Cowork | ⬜ |
| 2 | Requirements | `docs/requirements.md` — functional + non-functional rules | Cowork | ⬜ |
| 3 | Architecture & interface contract | `docs/architecture.md`, `docs/api-contract.md`, data model | Cowork | ⬜ |
| 4 | Wireframes | `docs/wireframes/` — key screens as Markdown + images/HTML (omit for non-UI projects) | Cowork | ⬜ |
| 5 | Test strategy | `docs/test-strategy.md` — frameworks, what is unit/integration/E2E tested | Cowork | ⬜ |
| 6 | Ticket generation | `tickets/*.md` + conventions + `BOARD.md` index | Cowork | ⬜ |
| 7 | Repository setup & scaffolding | repo initialised, docs + tickets committed, skeletons, dependency-rule check wired in, `sfk-verify` skill filled in for the stack | Code | ⬜ |
| 8 | Implementation, ticket by ticket | working software; tickets updated in the same commits | Code | ⬜ |

<!-- Append a new table per version. Subsequent versions run as a DELTA PASS (see README): a
     version brief drives requirement deltas rather than a fresh spec. Example skeleton: -->

<!--
### vX.Y.0 — <theme> (in planning)

| # | Milestone | Deliverable | Tool | Status |
|---|-----------|-------------|------|--------|
| 9  | vX.Y.0 brief | `docs/vX.Y.0-brief.md` — feature set, epics, requirement deltas | Cowork | ⬜ |
| 10 | Requirement deltas | updated `docs/requirements.md` (new + amended FR/NFR) | Cowork | ⬜ |
| 11 | Architecture & contract deltas | updated `docs/architecture.md`, `docs/api-contract.md` | Cowork | ⬜ |
| 12 | Wireframe deltas | new/changed screens only | Cowork | ⬜ |
| 13 | Test-strategy delta + ticket generation | updated `docs/test-strategy.md`; new tickets | Cowork | ⬜ |
| 14+| Implementation, ticket by ticket | working software | Code | ⬜ |
-->

---

## Conventions

- **Status values:** ⬜ Not started · 🔶 In progress · ✅ Complete
- A milestone is marked **In progress** (🔶) when work on it starts, and **Complete** (✅) only
  after **explicit human sign-off** — not merely when its deliverable looks finished (see root
  `CLAUDE.md`, *Milestone status lifecycle*). On sign-off it is committed to the repository.
- Each milestone is conducted in its own session in the assigned tool, with the relevant prior
  documents available as context.
- New versions require their own brief and are appended here only once approved.
