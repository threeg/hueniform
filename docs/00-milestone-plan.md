# Hueniform — Milestone Plan and Progress Tracker

| | |
|---|---|
| **Document** | Milestone plan and progress tracker |
| **Repository location** | `docs/00-milestone-plan.md` |
| **Last updated** | 5 July 2026 (v0.2.0 shipped and tagged `v0.2.0`; Milestones 15–16 signed off — the v0.3.0 brief and the design system (`docs/06-design-system.md`) with new NFR-11; Milestone 17, architecture & API deltas, is In progress) |

This document is the single source of truth for **where the project is**. It was extracted from the project brief (§14) so the brief stays stable after approval while this tracker is updated as each milestone completes. Update the status column and the *Current position* line in the same commit as the milestone's deliverable.

---

## Current position

> **v0.3.0 scoped; Milestones 15–16 signed off — Milestone 17 (architecture & API deltas) is In progress.** Milestone 16 delivered `docs/06-design-system.md` (role-named colour tokens, Newsreader/Hanken Grotesk/Space Mono typography on a normalised scale, spacing/radius/elevation, component vocabulary, native-CSS realisation with self-hosted fonts) and, from its requirement check, added binding **NFR-11** (accessibility: WCAG 2.1 AA contrast + visible focus). M17 is expected to be light/N/A — the redesign is frontend-only with no API/contract change; run it through to confirm and to record any frontend/CSS-architecture note in `docs/03-architecture.md`. The brief is in `docs/10-v0.3.0-brief.md`: a **visual + layout redesign** applying the finished design in `docs/designs/Hueniform App.html` to the React SPA, captured as a binding design-system document (`docs/06-design-system.md`) with the prototype retained as the visual reference. It carries a **single requirement delta** — **NFR-11** (accessibility: WCAG 2.1 AA contrast + visible focus), added during the M16 design pass — with no `FR` or API-contract changes; all v0.2.0 behaviour and contracts are preserved (NFR-1/NFR-8 offline and NFR-6 responsiveness re-affirmed and re-verified). The design tokens are specified in `docs/06-design-system.md`. Proposed epics **HUE-E11** (design-system foundation) and **HUE-E12** (screen restyle & layout); implementation tickets continue from **HUE-094**. Per the scoping intent, each delta-pass milestone (M16–M20) is laid down and run through to confirm what it needs; M17 (architecture/API) is expected to be N/A. Next: Milestone 16 — design system + requirement check (`sfk-next-milestone`).
>
> **v0.2.0 shipped and tagged `v0.2.0`.** Milestones 9–13 were completed and signed off; Milestone 14 (implementation) delivered epics E06–E10 (leaf tickets HUE-059–HUE-087) plus the v0.2.0 cleanup backlog (HUE-088–093), all `done`, and the release was tagged `v0.2.0`. The milestone table below marks M14 ✅ on the basis of that shipped, tagged release; if formal sign-off of M14 is still wanted, run `sfk-signoff` against it before proceeding.
>
> **v0.1.0 shipped and tagged `v0.1.0`.** Milestones 1–8 complete.

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

### v0.2.0 — Essential features (shipped, tagged `v0.2.0`)

| # | Milestone | Deliverable | Tool | Status |
|---|---|---|---|---|
| 9 | v0.2.0 brief | `docs/09-v0.2.0-brief.md` — seven features (F1–F7), epics E06–E10, requirement deltas | **Cowork** | ✅ Complete |
| 10 | Category-model design + requirement deltas | F4 spike output; updated `docs/02-requirements.md` (FR-16–22 rewrite, FR-44–51, NFR-10, FR-2 tuning) | **Cowork** | ✅ Complete (addended in M12 session — expanded FR-16 taxonomy, layer-slot rename, new FR-52; spike §7, requirements §9.2) |
| 11 | Architecture & API deltas | `docs/03-architecture.md`, `docs/03-api-contract.md` — category edit, pin/scheme + count suggestion API, taxonomy | **Cowork** | ✅ Complete (addended in M12 session — expanded category set, `jersey`/`jacket` → `mid`/`outer` slot keys, per-category slot constraints) |
| 12 | Wireframe deltas | `docs/04-wireframes/` — new/changed screens (category edit, build-around request, suggestion count, inventory grouping) + design-handoff briefs | **Cowork** | ✅ Complete |
| 13 | Test-strategy delta + ticket generation | `docs/05-test-strategy.md` (test-first policy, seedable variety, snapshot baseline); `tickets/*` (HUE-059+), epics E06–E10 | **Cowork** | ✅ Complete |
| 14 | Implementation, ticket by ticket | Working software (HUE-059–HUE-087 + cleanup HUE-088–093); tickets updated in the same commits | **Code** | ✅ Complete (shipped, tagged `v0.2.0`) |

### v0.3.0 — Visual redesign (in planning)

Delta pass applying the finished design (`docs/designs/Hueniform App.html`) to the SPA. Presentation-layer only — no requirement deltas. See `docs/10-v0.3.0-brief.md`.

| # | Milestone | Deliverable | Tool | Status |
|---|---|---|---|---|
| 15 | v0.3.0 brief | `docs/10-v0.3.0-brief.md` — visual + layout redesign scope, design-system artefact, epics E11–E12, no requirement deltas | **Cowork** | ✅ Complete |
| 16 | Design system + requirement check | New `docs/06-design-system.md` (tokens, typography, spacing, components) extracted from the prototype; requirement check added **NFR-11** (accessibility) | **Cowork / Chat** | ✅ Complete |
| 17 | Architecture & API deltas | Confirm no API/contract change; note any frontend/CSS-architecture change in `docs/03-architecture.md` if warranted (expected N/A) | **Cowork / Chat** | 🔶 In progress |
| 18 | Wireframe deltas | `docs/04-wireframes/` updated where the new layout differs materially from the committed wireframes | **Cowork** | ⬜ Not started |
| 19 | Test-strategy delta + ticket generation | `docs/05-test-strategy.md` visual-fidelity/regression approach; `tickets/*` (HUE-094+), epics E11–E12 | **Cowork** | ⬜ Not started |
| 20 | Implementation, ticket by ticket | Working, redesigned SPA; tickets updated in the same commits | **Code** | ⬜ Not started |

---

## Conventions

- **Status values:** ⬜ Not started · 🔶 In progress · ✅ Complete
- A milestone is marked **In progress** (🔶) when work on it starts, and is marked **Complete** (✅) only after **explicit user sign-off** — not merely when its deliverable looks finished (see root `CLAUDE.md`, *Milestone status lifecycle*). On sign-off it is committed to the repository.
- Each milestone is conducted in its own conversation/session in the assigned tool, with the relevant prior documents available as project files.
- New milestones (e.g. roadmap items from brief §10) require their own brief and are appended here only once approved.
