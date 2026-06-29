# Hueniform — Ticket Template

| | |
|---|---|
| **Document** | Ticket template and frontmatter specification |
| **Repository location** | `tickets/TICKET-TEMPLATE.md` |
| **Applies to** | Every file in `tickets/` (one ticket per file) |

This is the canonical format for Hueniform tickets. Every ticket is a single Markdown file with the YAML frontmatter and body sections defined below. Tickets live in `tickets/` beside the code, are committed and updated in the same commits as the work they describe, and reference requirements by their `FR-n`/`NFR-n` identifiers and the test strategy by section number.

It adapts the AvoTech Jira templates to this project: a single-developer, local-first, file-based monorepo with no Jira, no RICE/Tier scoring, no OutSystems modules and no feature-flag release machinery. The useful structure is kept — the epic/story/task/spike distinction, Given–When–Then acceptance criteria, explicit dependencies, and a definition of done — expressed as front-matter fields and Markdown rather than Jira fields.

**Every ticket — epic, story, task or spike — opens with an `## In plain English` section.** It is always the first body section, before the type-specific sections below. Write one or two sentences a non-technical reader can follow: what the ticket delivers and why it matters, with no jargon and no implementation steps. The technical sections that follow are unchanged.

---

## Frontmatter (mandatory, all ticket types)

```yaml
---
id: HUE-000                  # unique, zero-padded; see CONVENTIONS.md for the scheme
title: Short imperative summary
type: story                  # epic | story | task | spike
status: todo                 # todo | in-progress | blocked | in-review | done
milestone: 7                 # milestone number from docs/00-milestone-plan.md
batch: scaffolding           # optional grouping within a milestone
layer: matcher               # matcher | detection | storage | services | api | frontend | tooling | docs | repo
depends_on: []               # list of ticket ids that must be done first, e.g. [HUE-003, HUE-004]
implements: []               # FR-n / NFR-n ids this ticket realises, e.g. [FR-12, FR-13, NFR-9]
tests_required: true         # false only for docs-only, pure-styling, build-plumbing (state why in the body)
estimate: 3                  # Fibonacci: 1, 2, 3, 5, 8 (rough session-sizing, not a commitment)
---
```

`depends_on` is the execution order: a ticket may not start until every id it lists is `done`. The board (`tickets/BOARD.md`) is the topological view of these edges; the matcher → detection → services → api dependency rule from the architecture must be reflected in the `depends_on` graph.

---

## Body — Epic

Container only; groups related stories/tasks toward one capability. No code ships against an epic directly.

```markdown
## In plain English
One or two plain sentences for a non-technical reader: what this group of work delivers and why it matters. No jargon, no implementation steps.

## Summary
Why are we building this, and which capability of the MVP does it deliver?

## Scope
- **In scope:** high-level features included
- **Out of scope:** explicitly excluded, to prevent creep

## Success criteria
How we know the epic is delivered (usually: all child tickets done and the relevant success criterion from the brief §11 met).

## Children
- HUE-xxx — title
- HUE-yyy — title

## References
- Specification sections (e.g. docs/02-requirements.md §4, docs/03-api-contract.md §2.12)
- Wireframes (docs/04-wireframes/…)
```

---

## Body — Story

A user-facing slice of behaviour (a screen, a flow, an endpoint the user feels). Acceptance criteria are Given–When–Then.

```markdown
## In plain English
One or two plain sentences for a non-technical reader: what this lets someone do and why it matters. No jargon, no implementation steps.

## User story
As a [role]
I want [feature]
so that [benefit].

## Acceptance criteria

**Scenario 1: [title]**
- Given [context]
- When [event]
- Then [outcome]
- And [further outcome]

**Scenario 2: …**

## Technical approach
- Module(s)/layer touched (per architecture §2.1)
- API endpoint(s) and payloads, citing docs/03-api-contract.md by section
- Data-model touchpoints (architecture §3)

## Design references
- Wireframe: docs/04-wireframes/NN-screen.md (and state(s): empty/loading/error)

## Tests
- Test files to add/update (per test strategy §12.1 layout)
- FR/NFR ids covered and the test-strategy sections their assertions draw on
- Fixtures used (test strategy §11)

## QA steps
Manual browser checks for this screen/flow — what to do and what to expect — for the user to run.
They complement the automated e2e tests (they do not replace them) and accumulate as living
per-screen QA documentation.
- [ ] [action] → expect [result]
- [ ] …

## Definition of done
- [ ] Acceptance criteria met
- [ ] Tests added/updated per test strategy §12.2 and passing in `make test`
- [ ] Matcher-touching work: 100% line+branch on app/matcher/ holds (§12.3.3)
- [ ] Detection-touching work: `make test-model` passes (§12.3.4)
- [ ] Evaluation/inventory-perf-touching work: `make test-perf` passes (§12.3.5)
- [ ] User-flow-touching work: `make test-e2e` passes (§12.3.6)
- [ ] QA steps recorded under `## QA steps` and repeated in the chat completion report
- [ ] Ticket status + notes updated in the same commit (§12.3.7)
```

---

## Body — Task

Backend, detection, persistence, tooling, scaffolding or architectural work with no direct UI. (Most matcher, detection, storage, services and tooling tickets are tasks.)

```markdown
## In plain English
One or two plain sentences for a non-technical reader: what this piece of work delivers and why it matters. No jargon, no implementation steps.

## Background
What technical work is needed and why; the current limitation or the prerequisite this unblocks.

## Technical requirements
- Modules/files to create or modify (per architecture §2.1)
- Contracts to honour: requirements §, API contract §, architecture dependency rule
- Constraints (e.g. matcher is standard-library-only — NFR-9)

## Definition of done (acceptance criteria)
- [ ] Requirement 1
- [ ] Requirement 2
- [ ] Tests added/updated per test strategy §12.2 (or exemption stated below) and passing in `make test`
- [ ] Relevant extra gate green where applicable (`make test-model` / `make test-perf` / `make test-e2e`, §12.3)
- [ ] Ticket status + notes updated in the same commit

## Tests / verification
How completion is verified without a UI: the test names/files, the make target, the fixture, the tolerance.
(If `tests_required: false`, state the exemption category here — docs-only, pure-styling, or build-plumbing.)
```

---

## Body — Spike

Strictly time-boxed investigation for a genuinely unknown approach. Produces a finding, not shippable code.

```markdown
## In plain English
One or two plain sentences for a non-technical reader: what question this investigation answers and why it matters. No jargon, no implementation steps.

## Objective
The specific unknown to resolve.

## Timebox
Maximum effort, e.g. half a session / 4 hours.

## Questions to answer
1. …
2. …

## Expected deliverable
What exists at the end of the timebox (e.g. a short decision note appended here, or a throwaway prototype branch), and which follow-up ticket(s) it will spawn.
```

---

## Working notes (any type)

Append a dated notes section as work proceeds; this is where status changes, decisions and blockers are recorded so the ticket stays an honest record. On completion, append the **completion report** here — a plain-language summary of what was done and the one-line sanity test; UI/frontend tickets additionally fill in the `## QA steps` section. The same content is given in the chat response (see the definition of done in the root `CLAUDE.md`).

```markdown
## Notes
- 2026-06-15 — created
- 2026-06-16 — blocked on HUE-004 (taxonomy constants)
```
