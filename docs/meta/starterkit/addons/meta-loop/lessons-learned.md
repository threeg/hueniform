# Lessons Learned — AI-Assisted Development

| | |
|---|---|
| **Document** | Process observations from building <PROJECT> with an AI coding agent |
| **Repository location** | `docs/meta/lessons-learned.md` |
| **Scope** | Project-neutral where possible; intended to transfer to the next project |
| **Last updated** | <DATE> |

> **Purpose.** A living retrospective. Record transferable process observations — what worked, what
> failed, and the near-misses — as you go, not at the end. Each lesson should end with a
> **transferable rule** stated generally enough to carry to a different codebase. Review this at
> version boundaries; the best lessons graduate into the starter kit itself.
>
> The entries below are **seeds** — common lessons from spec-first agentic builds. Keep the ones that
> hold for your project, rewrite them with your own evidence, and add your own.

---

## 1. Spec-first pays compound interest

Writing the binding specification (brief, requirements, architecture, interface contract, test
strategy) *before* any code means every implementation session starts with full context. The agent
never has to guess intent — it reads the spec and implements to it. Ambiguity disputes are settled by
referencing a document, not re-explaining a decision.

**Transferable rule:** Do not start implementation until the specification is detailed enough that a
fresh session with no conversation history could implement a ticket correctly from the spec alone.

---

## 2. The ticket is the unit of agentic work

A well-structured ticket (id, dependencies, the requirements it implements, definition of done,
layer, test targets) gives an agent everything it needs to work autonomously. The ticket *is* the
prompt. Loose instructions produce loose results; a ticket with explicit acceptance criteria and a
dependency chain produces correct, reviewable commits.

**Transferable rule:** Design tickets as self-contained work units. If the ticket needs a
conversation to explain, the ticket is incomplete.

---

## 3. One ticket per commit keeps the history honest

Each commit moves exactly one ticket: its code, its tests, its status update, and its board row. This
creates a 1:1 mapping between the work record and the code record. `git log` reads like a build
journal; reverting a ticket means reverting one commit. It also prevents "drift commits" where work
accumulates untracked.

**Transferable rule:** Enforce one-ticket-per-commit from the start. The overhead is near zero; the
auditability compounds.

---

## 4. Verification is a first-class process step, not an afterthought

Tests catch code-level bugs. "Does the code implement what the spec *says*?" is a different question.
A spec-level verification pass after each batch — checking requirement-by-requirement against the
binding spec — catches loose interpretations, boundary mismatches, and missing edge cases that unit
tests happily pass through.

**Transferable rule:** Build a verification step that audits against the spec, not just the tests.
Run it at batch boundaries. Make it produce actionable tickets, not just reports.

---

## 5. Context management is a first-order concern

The agent's context window is its working memory. A monolithic instructions file forces every session
to carry patterns it will never use. A slim root file (cross-cutting rules) plus layer-specific files
(loaded only when touching that layer) keeps each session focused.

**Transferable rule:** Structure instructions hierarchically. Root for universal rules,
subdirectory-level for layer-specific patterns.

---

## 6. Reactive quality tickets belong in a separate backlog

Code review of completed work generates findings that don't fit the planned sequence. They need a
lightweight on-ramp: a cleanup backlog, visible but separate from the critical path, triaged as
critical (promote immediately) or improvement (work at discretion).

**Transferable rule:** Create a formal backlog for discovered work. Never let review findings exist
only in conversation — they must become tickets or be explicitly dismissed.

---

## 7. The dependency rule is the architecture's immune system

Declaring a layer dependency rule and enforcing it with tooling prevents the most common form of
architectural erosion: a quick expedient import that creates a circular dependency. When enforced in
the build, the agent cannot introduce a violation even when it would be the fastest path.

**Transferable rule:** Encode the dependency rule as an automated check that fails the build. Do it in
scaffolding, before any implementation.

---

## 8. Hand-holding is the bottleneck, not the process

The process (spec → tickets → implement → test → verify) is sound. Slowness comes from the interaction
model — approving every step. The infrastructure (specs, tickets, conventions, dependency rules, test
gates) exists precisely to make autonomous execution safe.

**Transferable rule:** Build the guardrails first, then gradually increase autonomy. The goal is a
system where you hand a ticket to a fresh session and review the output, not supervise every keystroke.

---

## 9. Lessons from failures and near-misses

> Record specific incidents here: the symptom, the root cause, how it was caught, and the lesson.
> A recurring pattern (a mistake hit twice) is a signal to write a rule into the relevant layer's
> `CLAUDE.md`. Examples of the *shape* of entry that belongs here:

- **<symptom>** — <root cause>. Caught by <what>. Lesson: <the rule, and where it now lives>.
