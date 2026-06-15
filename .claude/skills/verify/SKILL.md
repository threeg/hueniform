---
description: Deep verification of completed work against the binding spec. Use when the user asks to verify, audit, or review the quality of implementation — not just whether tests pass, but whether the code actually does what the requirements say.
disable-model-invocation: true
---

## Spec-level verification of completed tickets

You are performing a deep quality audit of the Hueniform project. The goal is not just
"do tests pass" but "does the code actually implement what the binding spec requires."

### Step 1 — Establish scope

1. Read `tickets/BOARD.md` and identify all tickets with status `done`.
2. Read `docs/00-milestone-plan.md` to confirm the current position.
3. Run `git log --oneline` and verify one commit per done ticket, in dependency order.
4. Run `make test` and confirm the gate passes.

Report any inconsistencies between the board, milestone plan, and git history before
proceeding.

### Step 2 — Verify each completed module against the spec

For each `done` ticket (excluding pure scaffolding/tooling tickets like HUE-001–HUE-006
that have no numbered-requirement implementations), launch a **parallel background agent**
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
   - Are boundary conditions correct (pay attention to `<` vs `<=`, half-open intervals)?
   - Are comparison operators and evaluation orders exactly as specified?
   - Do constants come from `matcher.constants`, not magic numbers?
   - Does the test suite exercise the boundary values and edge cases?
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

### Step 3 — Verify fixture coverage

Check that the wardrobe/scenario fixtures in `backend/tests/fixtures/` provide adequate
coverage for integration-level testing:
- Do fixtures exist for all five harmony schemes (neutral-based, monochromatic, analogous,
  complementary, triadic)?
- Is fixture data consistent (proportions sum to 100, valid types, valid HSL ranges)?
- Are fixtures actually imported and used by the test modules that need them?

### Step 4 — Compile report

Produce a single consolidated report with:

1. **Process integrity**: board/commit/milestone consistency, `make test` result.
2. **Per-module table**: ticket, requirements covered, verdict (Pass/Fail/Gap), and any
   specific deviations or concerns.
3. **Fixture coverage**: any gaps in scheme or scenario coverage.
4. **Actionable items**: anything that needs fixing or adding, ranked by severity.

Use task tracking (TaskCreate/TaskUpdate) to show progress as each module is verified.
