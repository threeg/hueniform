# Method Improvements — Closing the Gaps

| | |
|---|---|
| **Document** | Actionable improvements to the AI-assisted development method |
| **Repository location** | `docs/meta/method-improvements.md` |
| **Context** | Identified during a review of alignment with spec-driven AI development (the "Karpathy Method") |
| **Last updated** | 6 July 2026 |

This document tracks specific improvements to the development method, from identified
gap through to resolution. Items move from "proposed" to "done" as they are addressed.

---

## Current method strengths

These are in place and working. Documented here so they are not accidentally regressed.

- **Spec-first**: Six milestones of binding documentation before any code.
- **Structured tickets**: Self-contained work units with dependencies, acceptance
  criteria, and requirement traceability.
- **Test gates**: `make test` as the default gate, heavier gates (`test-model`,
  `test-perf`, `test-e2e`) per ticket type.
- **Dependency rule enforcement**: Import-linter contracts, stdlib allowlist.
- **Post-batch verification**: `/verify` skill combining spec audit and code quality
  review, producing cleanup tickets.
- **Conditional context loading**: Root CLAUDE.md for universal rules, layer-specific
  CLAUDE.md files loaded per directory.
- **Cleanup backlog**: Reactive quality tickets in a separate board section with
  promotion rules for critical findings.

---

## Proposed improvements

### 1. Close the eval loop — automated spec traceability

**Gap:** Verifying that every FR/NFR has a test requires running `/verify` agents
manually. There is no mechanical check that a requirement listed in a ticket's
`implements` field actually has corresponding test coverage.

**Proposed fix:** A lightweight script (or `make` target) that:
1. Parses each ticket's `implements` field.
2. Greps test files for references to those FR/NFR identifiers (in test names,
   docstrings, or comments).
3. Reports any requirement with zero test references.

This runs as part of `make test` and fails if a tracked requirement has no test.

**Status:** Rejected.

**Reason:** This reduces to grepping for FR/NFR identifier strings in test files — a
shallow annotation check that duplicates what `/verify` already does with real semantic
analysis. It would gate `make test` on busywork (sprinkling ID comments into tests)
without verifying that the tests actually *cover* the requirement's behaviour. Mechanical
gates should target structural invariants (import contracts, frontmatter validation) that
AI review cannot reliably catch, not semantic coverage questions that it handles better.

**Effort:** Small (1-2 hours). Could be a cleanup ticket.

---

### 2. Regression snapshots for deterministic layers

**Gap:** The matcher layer is pure and deterministic, but there are no snapshot tests
pinning known inputs to expected outputs. If a refactor subtly changes ranking scores
or colour classification, the existing tests check structural validity (is the output
well-formed?) but not output stability (did the answer change?).

**Proposed fix:** Add a small set of golden-file snapshot tests for the matcher:
- A fixed wardrobe → expected ranking order and scores.
- A fixed HSL palette → expected family classifications.
- A fixed outfit → expected explanation text.

These snapshots are committed alongside the code. Any change to matcher output requires
an explicit snapshot update, making regressions visible in the diff.

**Status:** Proposed.

**Effort:** Medium (half a session). Natural fit for HUE-039 (performance suite) or a
standalone cleanup ticket.

---

### 3. Formalise the agentic handoff

**Gap:** The spec, tickets, and conventions are detailed enough for autonomous
execution, but there is no documented protocol for "hand this ticket to a fresh
session." The human still provides conversational context that the ticket alone should
carry.

**Proposed fix:** Document a "ticket execution protocol" — the steps a fresh Claude
Code session should follow to work a ticket autonomously:
1. Read `CLAUDE.md` (root + relevant layer files).
2. Read the ticket file.
3. Read the `depends_on` tickets' `## Notes` for context.
4. Read the relevant spec sections (`docs/02-requirements.md` for the FR/NFR ids).
5. Implement, test, update ticket, commit.

This protocol lives in `tickets/CLAUDE.md` (or `CONVENTIONS.md`) and means any session
can pick up any unblocked ticket without a human briefing.

**Status:** Proposed.

**Effort:** Small (documentation only). Could be added to CONVENTIONS.md directly.

---

### 4. Reduce context noise — on-demand spec loading

**Gap:** Even with the CLAUDE.md split, every session loads the full root file (~84
lines). For a focused single-file fix, much of this is unnecessary. The binding spec
documents (`docs/02-requirements.md`, `docs/03-architecture.md`) are large and only
needed when verifying requirement compliance, not for routine implementation.

**Proposed fix:** No immediate action needed — the current split is a good first step.
Monitor whether context pressure becomes a problem as the codebase grows. If it does,
consider:
- Moving the commands section to a `Makefile` header comment (the AI can read it from
  there).
- Using a hook to inject only the relevant FR/NFR lines based on the ticket's
  `implements` field.

**Status:** Deferred (monitoring).

---

### 5. Mechanical ticket validation

**Gap:** Ticket frontmatter is manually maintained. A typo in `depends_on` (e.g.
referencing a non-existent ticket id), a missing `implements` field, or an
inconsistency between the ticket file and BOARD.md is only caught by human review or
`/verify`.

**Proposed fix:** A `make lint-tickets` target that:
1. Parses all ticket YAML frontmatter.
2. Validates `depends_on` ids exist.
3. Validates `implements` ids match `docs/02-requirements.md`.
4. Checks BOARD.md status matches ticket file status.
5. Checks no forward dependencies (higher id in `depends_on`).

**Status:** Proposed.

**Effort:** Medium. Could be a cleanup ticket or part of the tooling batch.

---

### 6. Design-to-code handoff and visual audit process

**Gap:** Restyle tickets that reference only a design system document (tokens, component
vocabulary) will match the abstract vocabulary while missing per-screen visual details —
icons, active-state styling, control shapes, section backgrounds, exact paddings and
border-radii. A design prototype exported as standalone HTML requires a browser to
render, making it opaque to the AI. PDF exports may render blank. The result: the
implementation passes all tests and looks generically correct, but doesn't match the
design.

**Fix — three parts:**

**Part A: Design export format.** When exporting from Claude Design, use the **project
archive (zip)**, not standalone HTML or PDF. The archive contains `.dc.html` files
(plain HTML/CSS with exact inline styles — readable as source code) and pre-rendered
screenshots at multiple breakpoints. Commit this bundle to the repo (e.g.
`docs/designs/<project>/`) as part of the design milestone.

| Export format | Usable by the AI? | Why |
|---|---|---|
| **Project archive (zip)** | **Yes** | `.dc.html` is readable source; screenshots included |
| Standalone HTML | No | Requires browser + JS to unpack base64 blobs |
| PDF | No | May render blank (design tool export issue) |
| PowerPoint | Maybe | Untested |
| Video | No | Cannot process video |

**Part B: Ticket references.** Every restyle or visual-fidelity ticket must include a
Design references line pointing to the `.dc.html` file with specific section/line
pointers, not just the design system doc. The design system doc captures the *vocabulary*
(tokens, component types); the `.dc.html` is the *pixel-level spec* — both are needed,
neither replaces the other.

**Part C: Post-implementation visual audit.** After per-ticket restyle work completes,
run a holistic visual audit before signing off the milestone:

1. Read all prototype screenshots for a fast visual inventory of every screen and state.
2. Extract the full design system from `.dc.html` via an agent (prompt: "extract ALL
   visual CSS — colours, typography, spacing, radii, shadows, per-component specs").
3. Compare by category (titles, cards, controls, empty states), not screen-by-screen —
   most gaps are cross-cutting.
4. Create one ticket per screen for any remaining gaps, with exact CSS values from the
   prototype source.

This audit is distinct from `/verify` (which catches code quality and spec compliance,
not visual fidelity) and from the test gates (which verify behaviour, not appearance).

**Status:** Done.

---

## Done

| Improvement | Date | Notes |
|---|---|---|
| Conditional context loading (CLAUDE.md split) | 2026-06-16 | Root + 7 layer files. See commit `0acb03f`. |
| Cleanup backlog process | 2026-06-16 | CONVENTIONS.md §6, BOARD.md backlog table. See commit `b701f1b`. |
| Post-batch /verify skill | 2026-06-16 | Spec audit + code quality review + ticket proposals. See `.claude/skills/verify/SKILL.md`. |
| Ticket completion report | 2026-06-18 | Summary + sanity test + (for UI tickets) manual QA steps, given in chat and appended to the ticket. See CLAUDE.md definition of done, TICKET-TEMPLATE story `## QA steps`, CONVENTIONS §5.6. Extends improvement #3 (agentic handoff); QA steps build living per-screen docs. |
| Design-to-code handoff and visual audit | 2026-07-06 | Project archive export from Claude Design; `.dc.html` as pixel-level spec; per-screen visual audit tickets. See `lessons-learned.md` §10. |
