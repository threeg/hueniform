---
name: sfk-verify
description: Post-batch verification pass — audit completed work against the binding spec and review code quality, then propose cleanup tickets. This is a template — fill the placeholder commands and stack-specific checks during scaffolding (Milestone 7). Trigger on "verify", "review this batch", "run the verifier", or "spec-audit the recent work".
---

# sfk-verify — post-batch spec audit + quality review

> **This is a template.** During scaffolding (Milestone 7), replace every `PLACEHOLDER` with the
> project's real commands and stack-specific checks, and delete this note. A verifier that names the
> actual gates and the actual spec sections catches far more than a generic one.

Run after a batch of related tickets completes — before the gate the batch feeds into. Verification is
a first-class step: tests answer "is the code correct?"; this answers "does the code implement what the
spec *says*?" — a different question that tests alone do not cover.

## What to check

1. **Spec audit (requirement by requirement).** For each `FR`/`NFR` the batch's tickets `implement`,
   open `process/requirements/requirements.md` and confirm the behaviour matches — exact thresholds,
   ordering, boundary conditions, error cases. Flag loose interpretations and missing edge cases, not
   just outright bugs.
2. **Contract conformance.** Where the batch touched the interface, confirm requests/responses match
   `process/architecture/api-contract.md` exactly (shapes, status codes, error envelope).
3. **Architecture & dependency rule.** Confirm no layer imports something it may not (the
   boundary-enforcement tool), and that the ticket `depends_on` graph still agrees with the import
   contracts.
4. **Code quality.** Look for duplication, dead code, needless complexity, and efficiency traps the
   tests would pass but a gate would later fail (e.g. an N+1 query, an unbounded loop, a missing index).
   Run the default gate and any heavier gate the batch affects (perf / e2e / real-dependency).
5. **Honesty of the record.** Confirm each ticket's status, `## Notes` completion report, and `BOARD.md`
   row were updated in the same commit as the work.

## What to produce

- A short findings list, each tagged **critical** (would fail a gate — promote into the main sequence
  before that gate) or **improvement** (work at discretion between batches).
- For accepted findings, draft **cleanup tickets** per `process/tickets/CONVENTIONS.md` §6: ordinary
  `task` tickets, `batch: cleanup`, `implements: []`, numbered after the current highest id, placed in
  the Cleanup backlog table in `BOARD.md`. Do not auto-promote — flag candidates and let the user decide.

## Rules

- Verification proposes tickets; it does not silently rewrite shipped code.
- A finding that reveals a genuine spec gap is a specification change (CONVENTIONS §5.5), recorded in
  `process/` first — not a cleanup ticket.
- Never sign off a milestone here; that is the user's call via `sfk-signoff`.


## Thread name

Run this in its own thread. Cowork auto-titles a thread and **cannot rename it programmatically** —
only the user can. As your **first action**, suggest the name below and ask the user to rename this
thread to it. `PROJCODE` is the project code (the ticket prefix) recorded as `project_code` in
`process/.sfk/manifest.md`, set when the project was created with `sfk-init` (e.g. `/sfk-init HUE`).

**Suggested name:** `PROJCODE: Verify (<batch>)`  (e.g. `HUE: Verify (matcher batch)`)
