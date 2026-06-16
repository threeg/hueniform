---
name: verify
description: Post-batch review of completed work. Audits code against the binding spec, reviews for reuse/quality/efficiency issues, and proposes cleanup tickets for the backlog. Use when the user says /verify or asks to review a completed batch.
---

# Verify: Post-Batch Review

Two-phase review of recently completed work: first verify correctness against the binding
spec, then review for code quality and propose cleanup tickets (CONVENTIONS.md §6).

---

## Phase 1 — Establish scope

1. Read `tickets/BOARD.md` and identify the most recently completed batch (a contiguous
   group of `done` tickets sharing a `batch` value).
2. Read `docs/00-milestone-plan.md` to confirm the current position.
3. Run `git log --oneline` and find the commit range for that batch.
4. Run `make test` and confirm the gate passes.

If the user specifies a batch or commit range explicitly, use that instead.
Report any inconsistencies between the board, milestone plan, and git history before
proceeding.

---

## Phase 2 — Spec-level verification

For each `done` ticket in the batch (excluding pure scaffolding/tooling tickets with no
numbered-requirement implementations), launch a **parallel background agent**
(subagent_type: Explore) to verify the ticket's implementation.

Each agent must:

1. **Read the ticket file** (`tickets/HUE-NNN-*.md`) — note the `implements` list and
   the Definition of Done.
2. **Read the relevant requirements** from `docs/02-requirements.md` — specifically the
   FR-n / NFR-n entries listed in the ticket's `implements` field.
3. **Read the implementation code** — the module(s) the ticket produced.
4. **Read the test file(s)** — the corresponding test module(s).
5. **Verify requirement by requirement:**
   - Does the code implement the requirement as written (not a loose interpretation)?
   - Do numeric thresholds match the spec exactly?
   - Are boundary conditions correct (`<` vs `<=`, half-open intervals)?
   - Are comparison operators and evaluation orders exactly as specified?
   - Do constants come from `matcher.constants`, not magic numbers?
   - Does the test suite exercise boundary values and edge cases?
6. **Check architectural constraints:**
   - `matcher/` imports standard library only (NFR-9).
   - Dependency rule: `matcher` -> `detection` -> `services` -> `api`.
   - Pure functions over frozen dataclasses where the architecture says so.
7. **Report** for each requirement: PASS, FAIL (with specific deviation), or GAP (tested
   but coverage is thin).

### Ticket-to-spec mapping guidance

Use the requirement traceability table at the bottom of `BOARD.md` to find which FR/NFR
numbers each ticket implements. Then look up those numbers in `docs/02-requirements.md`.

Key sections for reference:
- **matcher.constants** (HUE-007): §1.4 — all numeric thresholds as named constants.
- **matcher.colour** (HUE-008): §1.3 (HSL space, hue distance max 180°, wrapping), FR-12 (circular mean).
- **matcher.taxonomy** (HUE-009): FR-1–FR-5 — neutral rules in exact order, half-open chromatic arcs, representative hues.
- **matcher.roles** (HUE-010): FR-6–FR-11 — proportion rules, primary/dual-primary/secondary/minor derivation, echo bonus.
- **matcher.harmony** (HUE-011): FR-12–FR-15 — hue clustering, ordered scheme test, tolerances, neutral transparency.
- **matcher.slots** (HUE-013): FR-16–FR-22 — slot types, anchors, layering dominance, covered-layer constraint, echo-slot qualification.
- **matcher.ranking** (HUE-014): FR-39–FR-43 — scoring composition, variety factor, fallback ladder, candidate cap.
- **matcher.explain** (HUE-015): FR-37, FR-38 — plain-language explanation from evaluation result.
- **Storage, detection, services, API, frontend tickets**: check their respective FR/NFR lists from the traceability table.

---

## Phase 3 — Code quality review

Run `git diff <before-batch>..HEAD -- '*.py' '*.ts' '*.tsx'` to get the full diff.

Launch three review agents in parallel (Agent tool, all in a single message):

### Agent 1: Code Reuse Review

1. Search for existing utilities and helpers that could replace newly written code.
2. Flag new functions that duplicate existing functionality.
3. Flag inline logic that could use an existing utility.
4. Flag duplicated test helpers across test files (fixtures, factory functions, shared seams).

### Agent 2: Code Quality Review

1. Copy-paste with slight variation: near-duplicate code blocks that should be unified.
2. Redundant state or dead code.
3. Parameter sprawl: adding new parameters instead of restructuring.
4. Leaky abstractions: exposing internal details across layer boundaries.
5. Stringly-typed code where constants or enums already exist.
6. Unnecessary comments explaining WHAT not WHY.

### Agent 3: Efficiency Review

1. N+1 query patterns.
2. Unnecessary work: redundant computations, repeated file reads.
3. Missed concurrency: independent operations run sequentially.
4. TOCTOU patterns: checking existence before operating.
5. Memory: unbounded data structures, missing cleanup.
6. Overly broad operations.

---

## Phase 4 — Triage and classify findings

For each finding from both the spec verification and code quality review, classify it:

- **Critical** — Will cause a test gate failure (e.g. N+1 that blows `make test-perf`,
  a spec deviation that means a requirement is unmet, a warning that breaks the
  zero-warnings gate). These should be promoted into the main execution sequence.
- **Improvement** — Genuine issue worth fixing, but won't block any gate. Normal cleanup
  backlog.
- **Skip** — False positive, negligible impact, or pre-existing issue not introduced by
  this batch. Drop silently.

---

## Phase 5 — Present the report

Print a structured report with these sections:

### Batch summary
Which tickets were reviewed, which files were touched, total lines changed.

### Spec verification
Per-module table: ticket, requirements covered, verdict (Pass/Fail/Gap), and any
specific deviations or concerns.

### Code quality findings
For each non-skipped finding:

```
### [Critical|Improvement] — <short title>

**Files:** <file list>
**Issue:** <1-2 sentence description>
**Suggested fix:** <1 sentence>
```

### Proposed cleanup tickets
For each finding (or group of related findings), propose a ticket:

```
- **HUE-NNN: <title>** (task, <layer>, estimate: N)
  <one-line description>
  depends_on: [<tickets whose code it cleans up>]
  Critical: yes/no (if yes, state which gate it affects)
```

Use the next available ticket number after the current highest in `tickets/BOARD.md`.
Number them sequentially. Mark critical tickets clearly.

---

## Phase 6 — User picks

After presenting the report, ask the user which proposed tickets to create. Wait for
their response. Then for each accepted ticket:

1. Write the ticket file to `tickets/HUE-NNN-<slug>.md` using the project's
   `TICKET-TEMPLATE.md` format with:
   - `type: task`
   - `batch: cleanup`
   - `layer:` matching the code being cleaned up
   - `tests_required: true` (cleanup tickets must pass `make test`)
   - `implements: []` (cleanup tickets don't implement new requirements)
   - A clear Definition of Done listing the specific changes
   - A `## Notes` entry dated today recording the `/verify` run that created it

2. Add the ticket to the **Cleanup backlog** table in `tickets/BOARD.md` (not the main
   execution order table).

3. If any ticket is marked critical, note in the summary that it should be promoted to
   the main sequence before the relevant gate ticket, and suggest where it should slot in.

Do NOT create tickets the user hasn't accepted. Do NOT modify any source code — the
cleanup work is for a future session.
