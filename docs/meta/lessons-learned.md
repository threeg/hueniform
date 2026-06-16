# Lessons Learned — AI-Assisted Development

| | |
|---|---|
| **Document** | Process observations from building Hueniform with Claude Code |
| **Repository location** | `docs/meta/lessons-learned.md` |
| **Scope** | Project-neutral; intended to transfer to any new AI-assisted project |
| **Last updated** | 16 June 2026 |

These observations come from building a non-trivial full-stack application (wardrobe
manager with colour-theory matching) using Claude Code as the primary implementation
tool, with a single developer directing the work. The lessons are written to be
reusable — nothing here is specific to this codebase.

---

## 1. Spec-first pays compound interest

Writing binding specifications (brief, requirements, architecture, API contract,
wireframes, test strategy) across six milestones *before* any code was written is the
single highest-leverage decision in the project. Every implementation session starts
with full context. The AI never has to guess intent — it reads the spec and implements
to it. Ambiguity disputes are settled by referencing a document, not re-explaining a
decision.

**Transferable rule:** Do not start implementation until the specification is detailed
enough that a fresh session with no conversation history could implement a ticket
correctly from the spec alone.

---

## 2. Tickets are the unit of agentic work

A well-structured ticket (id, dependencies, requirements it implements, definition of
done, layer, test targets) gives an AI agent everything it needs to work autonomously.
The ticket *is* the prompt. Loose instructions ("improve the API") produce loose
results; a ticket with explicit acceptance criteria and a dependency chain produces
correct, reviewable commits.

**Transferable rule:** Design tickets as self-contained work units. If the ticket
needs a conversation to explain, the ticket is incomplete.

---

## 3. One ticket per commit keeps the history honest

Each commit moves exactly one ticket: its code, its tests, its status update, and its
board row. This creates a 1:1 mapping between the work record (ticket) and the code
record (commit). Reviewing history is trivial — `git log` reads like a build journal.
Reverting a ticket means reverting one commit.

This also prevents "drift commits" where work accumulates without being tracked, and
ensures the AI cannot silently combine unrelated changes.

**Transferable rule:** Enforce one-ticket-per-commit from the start. The overhead is
near zero; the auditability benefit compounds over time.

---

## 4. Verification is a first-class process step, not an afterthought

Tests catch code-level bugs. But "does the code implement what the spec says?" is a
different question that tests alone don't answer. A spec-level verification pass after
each batch (checking requirement-by-requirement against the binding spec) catches
subtle deviations — loose interpretations, boundary condition mismatches, missing edge
cases — that unit tests happily pass through.

Combining spec verification with code quality review (reuse, efficiency, duplication)
in a single `/verify` step creates a natural quality gate between batches.

**Transferable rule:** Build a verification step that audits against the spec, not just
the tests. Run it at batch boundaries. Make it produce actionable tickets, not just
reports.

---

## 5. Context management is a first-order concern

The AI's context window is its working memory. Loading irrelevant instructions wastes
it. A monolithic instructions file that covers every layer forces every session to
carry patterns it will never use.

Splitting instructions into a slim root file (cross-cutting rules) plus layer-specific
files (loaded automatically when touching that layer's code) keeps each session focused.
The root should contain only what *every* session needs: non-negotiables, the dependency
rule, commands, definition of done.

**Transferable rule:** Structure your AI instructions hierarchically. Root-level for
universal rules, subdirectory-level for layer-specific patterns. Assume the AI loads
what's relevant; don't force it to load everything.

---

## 6. Reactive quality tickets belong in a separate backlog

Code review of completed work generates findings that don't fit the pre-planned ticket
sequence. These need a lightweight on-ramp: a cleanup backlog that's visible but
separate from the critical path. Findings are triaged as "critical" (would fail a
gate — promote immediately) or "improvement" (work between batches at discretion).

This prevents two failure modes: ignoring review findings entirely (they vanish with
the conversation), and blocking forward progress to fix non-critical issues.

**Transferable rule:** Create a formal backlog for discovered work. Distinguish critical
(promote into the main sequence) from improvement (work at discretion). Never let
review findings exist only in conversation — they must become tickets or be explicitly
dismissed.

---

## 7. The dependency rule is the architecture's immune system

Declaring and enforcing a layer dependency rule (e.g. `matcher → detection → services
→ api`) with automated tooling (import-linter) prevents the most common form of
architectural erosion: a quick expedient import that creates a circular dependency.
When the rule is enforced in CI, the AI cannot introduce violations even when it would
be the fastest path.

**Transferable rule:** Encode the architecture's dependency rule as an automated check
that fails the build. Do this in the scaffolding phase, before any implementation. The
cost is a few lines of configuration; the benefit is permanent.

---

## 8. Hand-holding is the bottleneck, not the process

The process (spec → tickets → implement → test → verify) is sound. The slowness comes
from the interaction model: a human approving every tool call, confirming every ticket
choice, saying "yes, do it" at each step. The infrastructure (specs, tickets,
conventions, dependency rules, test gates) exists precisely to make autonomous execution
safe. As trust in the system grows, the human role shifts from approver to reviewer.

**Transferable rule:** Build the guardrails first (specs, tests, conventions), then
gradually increase autonomy. The goal is a system where you can hand a ticket to a
fresh session and review the output, not supervise every keystroke.

---

## 9. Lessons from failures and near-misses

- **N+1 query in `_load_wardrobe`**: Introduced in a services ticket, would have failed
  the performance gate (500-garment test). Caught by `/verify` code quality review, not
  by any test. Lesson: efficiency review at batch boundaries catches what tests miss.

- **Engine fixture teardown**: Forgetting `engine.dispose()` causes `ResourceWarning`
  under Python 3.13, which fails the zero-warnings gate. Hit this twice before encoding
  it as a testing pattern. Lesson: when you hit a pitfall twice, write it into the
  layer's instructions file immediately.

- **Detection segmenter returning RGB instead of RGBA**: Causes silent fallback
  activation (dark images produce near-zero alpha coverage). Spent a full debugging
  cycle before understanding the failure mode. Lesson: document non-obvious failure
  modes in the layer's instructions, with the correct code snippet.

- **Skill placed in wrong location**: Created a `/verify` skill in the global
  `~/.claude/skills/` directory instead of the project-level `.claude/skills/`. The
  project already had a verify skill; the global one shadowed it. Lesson: always check
  for existing files before creating new ones. Prefer project-level over global.
