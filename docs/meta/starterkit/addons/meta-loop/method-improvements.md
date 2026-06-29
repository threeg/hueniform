# Method Improvements — Closing the Gaps

| | |
|---|---|
| **Document** | Actionable improvements to the AI-assisted development method |
| **Repository location** | `docs/meta/method-improvements.md` |
| **Last updated** | <DATE> |

> **Purpose.** A register of method gaps, each tracked from identification through to resolution.
> Items carry an explicit **status** — `proposed`, `accepted`, `rejected`, `deferred`, or `done` —
> and, crucially, the **reasoning**. Recording *why* something was rejected or deferred is as
> valuable as recording what was done: it stops the same idea being relitigated each version.
> Review this register at version boundaries.

---

## Current method strengths

> List what is in place and working, so it is not accidentally regressed. Seed list (keep what
> applies):

- **Spec-first**: binding documentation before any code.
- **Structured tickets**: self-contained work units with dependencies, acceptance criteria, and
  requirement traceability.
- **Test gates**: a fast default gate plus heavier gates per ticket type.
- **Dependency-rule enforcement**: boundary contracts and a standard-library allowlist.
- **Post-batch verification**: a review step combining spec audit and code-quality review, producing
  cleanup tickets.
- **Conditional context loading**: a slim root `CLAUDE.md` plus per-layer files.
- **Cleanup backlog**: reactive quality tickets in a separate board section with promotion rules.

---

## Proposed improvements

> One entry per proposed improvement. Use the template below. Be honest about effort and about
> whether the improvement is worth its cost — a well-reasoned `rejected` is a good outcome.

### 1. <Short title>

**Gap:** <what is missing or weak today, with the symptom that revealed it>.

**Proposed fix:** <the concrete change — a script, a `make` target, a doc, a convention>.

**Status:** <proposed | accepted | rejected | deferred | done>.

**Reason:** <the reasoning. For `rejected`/`deferred`, this is the most important line — why not, and
under what condition it would be reconsidered. A useful heuristic: mechanical gates should target
*structural* invariants that review cannot reliably catch (import contracts, frontmatter validation),
not *semantic* questions that an AI reviewer handles better.>

**Effort:** <small | medium | large, with a rough estimate>.

---

<!-- Add further numbered entries as gaps are identified. -->

---

## Done

> Move completed improvements here with a date and a pointer to the commit/doc that realised them.

| Improvement | Date | Notes |
|-------------|------|-------|
| <e.g. Conditional context loading (CLAUDE.md split)> | <DATE> | <commit / doc reference> |
