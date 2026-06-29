# <PROJECT> — Ticket Template

| | |
|---|---|
| **Document** | Ticket template and frontmatter specification |
| **Repository location** | `tickets/TICKET-TEMPLATE.md` |
| **Applies to** | Every file in `tickets/` (one ticket per file) |

This is the canonical format for tickets. Every ticket is a single Markdown file with the YAML
frontmatter and the body sections defined below. Tickets live in `tickets/` beside the code, are
committed and updated in the same commits as the work they describe, and reference requirements by
their `FR-n`/`NFR-n` identifiers and the test strategy by section number.

The format keeps a deliberate, lightweight structure — the epic / story / task / spike distinction,
Given–When–Then acceptance criteria, explicit dependencies, and a definition of done — expressed as
frontmatter fields and Markdown. There is no external tracker; these files **are** the tracker.

> **The ticket is the prompt.** A ticket is complete when a fresh agent session could implement it
> from the ticket plus the spec it references, with no conversational context. If it needs a chat to
> explain, the ticket is incomplete.

---

## Frontmatter (mandatory, all ticket types)

```yaml
---
id: <PRJ>-000                # unique, zero-padded; see CONVENTIONS.md for the scheme
title: Short imperative summary
type: story                  # epic | story | task | spike
status: todo                 # todo | in-progress | blocked | in-review | done
milestone: 8                 # milestone number from docs/milestone-plan.md
batch: scaffolding           # optional grouping; here it carries the architecture layer
layer: core                  # core | domain | storage | services | interface | frontend | tooling | docs | repo
depends_on: []               # ticket ids that must be done first, e.g. [<PRJ>-003, <PRJ>-004]
implements: []               # FR-n / NFR-n ids this ticket realises, e.g. [FR-12, FR-13, NFR-9]
tests_required: true         # false only for docs-only, pure-styling, build-plumbing (state why in the body)
estimate: 3                  # Fibonacci: 1, 2, 3, 5, 8 (rough session-sizing, not a commitment)
---
```

`depends_on` is the execution order: a ticket may not start until every id it lists is `done`.
`BOARD.md` is the topological view of these edges; the architecture dependency rule must be
reflected in the `depends_on` graph (see `CONVENTIONS.md` §4).

---

## Body — Epic

Container only; groups related stories/tasks toward one capability. No code ships against an epic.

```markdown
## Summary
Why are we building this, and which capability of the release does it deliver?

## Scope
- **In scope:** high-level features included
- **Out of scope:** explicitly excluded, to prevent creep

## Success criteria
How we know the epic is delivered (usually: all child tickets done and the relevant success
criterion from the brief met).

## Children
- <PRJ>-xxx — title
- <PRJ>-yyy — title

## References
- Specification sections (e.g. docs/requirements.md §4, docs/api-contract.md §2.x)
- Wireframes (docs/wireframes/…)
```

---

## Body — Story

A user-facing slice of behaviour (a screen, a flow, an endpoint the user feels). Acceptance criteria
are Given–When–Then.

```markdown
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
- Interface endpoint(s) and payloads, citing docs/api-contract.md by section
- Data-model touchpoints (architecture §3)

## Design references
- Wireframe: docs/wireframes/NN-screen.md (and state(s): empty/loading/error)

## Tests
- Test files to add/update (per test strategy §12.1 layout)
- FR/NFR ids covered and the test-strategy sections their assertions draw on
- Fixtures used (test strategy §11)

## QA steps
Manual checks for this screen/flow — what to do and what to expect — for the human to run.
They complement the automated e2e tests (they do not replace them) and accumulate as living
per-screen QA documentation.
- [ ] [action] → expect [result]
- [ ] …

## Definition of done
- [ ] Acceptance criteria met
- [ ] Tests added/updated per test strategy §12.2 and passing in the default gate
- [ ] Core-touching work: the core coverage gate holds (§2.3)
- [ ] Relevant heavier gate passes where applicable (§12.3)
- [ ] QA steps recorded under `## QA steps` and repeated in the chat completion report
- [ ] Ticket status + notes and BOARD.md row updated in the same commit
```

---

## Body — Task

Backend, processing, persistence, tooling, scaffolding or architectural work with no direct UI.
(Most core, domain, storage, services and tooling tickets are tasks.)

```markdown
## Background
What technical work is needed and why; the current limitation or the prerequisite this unblocks.

## Technical requirements
- Modules/files to create or modify (per architecture §2.1)
- Contracts to honour: requirements §, interface contract §, architecture dependency rule
- Constraints (e.g. the core is standard-library-only — NFR-n)

## Definition of done (acceptance criteria)
- [ ] Requirement 1
- [ ] Requirement 2
- [ ] Tests added/updated per test strategy §12.2 (or exemption stated below) and passing in the default gate
- [ ] Relevant extra gate green where applicable
- [ ] Ticket status + notes and BOARD.md row updated in the same commit

## Tests / verification
How completion is verified without a UI: the test names/files, the command, the fixture, the
tolerance. (If `tests_required: false`, state the exemption category here — docs-only, pure-styling,
or build-plumbing.)
```

---

## Body — Spike

Strictly time-boxed investigation for a genuinely unknown approach. Produces a finding, not
shippable code.

```markdown
## Objective
The specific unknown to resolve.

## Timebox
Maximum effort, e.g. half a session / 4 hours.

## Questions to answer
1. …
2. …

## Expected deliverable
What exists at the end of the timebox (e.g. a short decision note appended here, or a throwaway
prototype branch), and which follow-up ticket(s) it will spawn.
```

---

## Working notes (any type)

Append a dated notes section as work proceeds; this is where status changes, decisions and blockers
are recorded so the ticket stays an honest record. On completion, append the **completion report**
here — a plain-language summary of what was done and a one-line sanity test; UI tickets additionally
fill in the `## QA steps` section. The same content is given in the chat response (see the definition
of done in the root `CLAUDE.md`).

```markdown
## Notes
- <DATE> — created
- <DATE> — blocked on <PRJ>-004 (<reason>)
- <DATE> — done. Summary: <…>. Sanity test: `<command>`.
```
