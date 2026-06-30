# Project Brief: <PROJECT>

| | |
|---|---|
| **Document** | Project brief |
| **Repository location** | `process/brief/brief.md` |
| **Status** | Draft for approval |
| **Date** | <DATE> |

> **Purpose of this document.** The brief fixes *what* we are building and *why*, the boundaries of
> the first release, and how we will know it is done. It is **binding**: once approved it is not
> reopened casually. Keep it stable — running status lives in `process/milestone-plan.md`, not here.
> Approval of this brief closes Milestone 1.

---

## 1. Overview

> Two or three sentences: what the product is, for whom, and the single sentence of value it
> delivers. If there is a **meta-goal** (e.g. "the development *process* is as much a deliverable as
> the software"), state it explicitly here — it shapes every later decision.

## 2. Problem statement

> What problem does this solve, and what is wrong with the status quo? Be concrete about the pain.

## 3. Users

> Who uses this and in what context (single user? team? offline? a specific environment?). The
> answers here justify many non-functional requirements later, so be specific.

## 4. Goals (first release)

> A short, ordered list of the capabilities the first release must deliver. Each should be testable
> and trace to one or more success criteria (§11). Resist the urge to list everything — the roadmap
> (§10) is where later ambitions go.

1. <Goal 1>
2. <Goal 2>
3. <Goal 3>

## 5. <Domain model / core structure>

> If the product has a central domain concept (an order, a document, a workflow, a transaction),
> describe its structure here in plain language. This is the seed that §2 (requirements) and the
> architecture's data model grow from. Rename this section to fit the domain.

## 6. <Core approach / algorithm>

> If the product's value rests on a particular approach (a matching algorithm, a ranking method, a
> generation pipeline), sketch the intended approach here at a level a non-specialist can follow.
> Precision comes later in requirements; here, establish the shape and the rationale.

## 7. <Secondary approach, if any>

> Optional. A second core mechanism worth flagging early (e.g. how raw input is processed before the
> core approach runs). Delete if not needed.

## 8. Technical direction

> The intended stack and shape, at a high level: language(s), key frameworks, datastore, process
> topology. These are directional, not yet contractual — the architecture document (Milestone 3)
> makes them binding. Note any hard constraints here (e.g. "must run offline", "no external
> services at runtime", "single binary").

## 9. Out of scope (first release)

> An explicit list of things this release will **not** do. This list is the contract against scope
> creep — when something is questioned later, this is what settles it. Be generous; deferring is
> cheap, creep is expensive.

- <Out of scope 1>
- <Out of scope 2>

## 10. Future roadmap (post-release, not committed)

> Ambitions deliberately deferred. Listed so they are captured, but explicitly **not committed** —
> each will require its own version brief (see README, "How versions evolve"). Note any that are
> deferred for a *structural* reason (e.g. "needs a network source, conflicts with the offline
> constraint") so the reasoning is not lost.

- <Roadmap item 1>
- <Roadmap item 2>

## 11. Success criteria

> The concrete, demonstrable conditions under which the first release is "done". Write them as
> things the user can *do*, not features that exist. If there is a meta-goal, add its criteria too
> (e.g. "every milestone is documented in Markdown and checked into the repo"; "work is tracked as
> one ticket file per unit, updated as work completes").

The release is done when <the user> can:

1. <Observable, demonstrable outcome 1>
2. <Observable, demonstrable outcome 2>

Additionally, for the meta-goal (if any):

3. <Process criterion, e.g. every milestone documented and committed>

## 12. Risks and open questions

| Risk / question | Notes / mitigation |
|-----------------|--------------------|
| <Risk 1> | <How it is mitigated, or what decision is pending> |
| <Risk 2> | <…> |

## 13. Repository strategy

> One repository or several? Where do docs, tickets, and code live relative to each other? State the
> intended top-level layout. The recommended default is a **single repository** with tickets living
> *beside* the code so they stay honest and update in the same commits:

```
/docs        – all project documentation (this brief, requirements, architecture, test strategy…)
/tickets     – one Markdown file per ticket, with YAML frontmatter
/<code>      – the application source (subdivided by layer)
```

---

*Approval of this brief closes Milestone 1.*
