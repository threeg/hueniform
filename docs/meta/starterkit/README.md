# Spec-First Starter Kit

A project-neutral starting point for building software **spec-first, ticket-by-ticket, with an
AI coding agent**. You drop this kit into an empty repository and tell the agent to `init`; the
agent then interviews you and writes the complete set of binding documents, the ticket system, and
its own standing instructions — after which it implements the project autonomously, one ticket per
commit.

This kit is the distilled *process* — nothing here is tied to any particular domain, language, or
framework. It is itself the output of a project that treated its development method as a deliverable
(see the optional meta loop, below).

---

## What this kit gives you

```
.
├── README.md                     ← this guide (the method + how to drive it)
├── CLAUDE.md                     ← root standing instructions for the agent (template)
├── docs/
│   ├── milestone-plan.md         ← single source of truth for project status
│   ├── project-brief.md          ← scope, goals, out-of-scope (binding)
│   ├── requirements.md           ← FR-n / NFR-n rules; numeric thresholds are contractual
│   ├── architecture.md           ← module layout, data model, the dependency rule, flows
│   ├── api-contract.md           ← authoritative interface shapes (HTTP / CLI / library)
│   ├── wireframes/
│   │   └── overview.md            ← screen index, navigation, shared layout, state matrix
│   └── test-strategy.md          ← frameworks, the test pyramid, the definition of done
├── src/
│   └── CLAUDE.md                 ← per-layer instructions template (one per layer)
├── tickets/
│   ├── CLAUDE.md                 ← ticket-workflow quick rules (loads when you touch tickets/)
│   ├── CONVENTIONS.md            ← how the ticket *system* works (process)
│   ├── TICKET-TEMPLATE.md        ← canonical per-ticket format (shape)
│   └── BOARD.md                  ← derived topological view of all tickets
└── addons/
    └── meta-loop/                ← OPTIONAL — only if your project's goal includes improving the method
        ├── lessons-learned.md
        └── method-improvements.md
```

The documents are not numbered. Ordering is owned by `docs/milestone-plan.md`, and because these
become **living** documents that evolve across versions, a number prefix would imply a fixed
sequence that stops being true after the first release. The only files that carry a number are
point-in-time **version briefs** (e.g. `docs/v0.2.0-brief.md`), where the version *is* the identity.

Every template is **annotated**: real section structure, placeholder tokens in `<ANGLE_BRACKETS>`,
and inline guidance telling the agent (and you) what belongs there and why. The guidance is the
agent's interview checklist — it is consumed and deleted as each section is filled in.

---

## The core idea

Two principles run through everything:

1. **The specification is binding, and it comes first.** No code is written until the spec is
   detailed enough that a *fresh* agent session — with no conversation history — could implement any
   ticket correctly from the documents alone. Ambiguity is settled by pointing at a document, never
   by re-explaining a decision in chat.

2. **The ticket is the unit of work, and the ticket is the prompt.** A well-formed ticket (id,
   dependencies, the requirements it implements, acceptance criteria, definition of done) gives the
   agent everything it needs to work autonomously and produce a reviewable commit. One ticket, one
   commit: the work record and the code record stay 1:1.

The pay-off compounds. Each session starts with full context. The agent never guesses intent.
`git log` reads like a build journal. Reverting a unit of work means reverting one commit.

---

## The milestone lifecycle (read this first)

Everything else hangs off this. The project advances through a sequence of **milestones**, tracked
in `docs/milestone-plan.md`, which is the single source of truth for *where the project is*. Each
milestone has exactly one status:

```
⬜ Not started  →  🔶 In progress  →  ✅ Complete
```

Two rules keep this honest, and they are non-negotiable:

- **When work on a milestone starts, the agent marks it `In progress` (🔶)** and moves the
  *Current position* line in `docs/milestone-plan.md` to it.
- **The agent never marks a milestone `Complete` (✅) on its own initiative.** Completion requires
  **explicit human sign-off**. Finishing the deliverable, passing the gates, and self-verification
  are *not* sufficient. Until you sign off, the milestone stays `In progress`, however done it
  looks.

This is the rhythm of the whole process: one milestone at a time, each in its own session, each
closed only by you. The eight steps below are simply the milestones of the first release.

---

## The eight steps

The first release proceeds through eight steps (= the first eight milestones). The first six produce
documents; the last two produce code. The **Mode** column says whether a step is *authoring*
(thinking with the spec and the project files) or *building* (executing against the spec) — the
recommended tool for each is named, but the durable point is the mode, not the brand.

| # | Step | Deliverable | Mode (recommended tool) |
|---|------|-------------|-------------------------|
| 1 | **Project brief** | `docs/project-brief.md` — scope, goals, users, out-of-scope, success criteria | Authoring (Cowork) |
| 2 | **Requirements** | `docs/requirements.md` — numbered `FR-n` / `NFR-n` rules; concrete, testable thresholds | Authoring (Cowork) |
| 3 | **Architecture & interface contract** | `docs/architecture.md`, `docs/api-contract.md`, the data model and dependency rule | Authoring (Cowork) |
| 4 | **Wireframes** | `docs/wireframes/` — screens, states, navigation (skip or trim for non-UI projects) | Authoring (Cowork) |
| 5 | **Test strategy** | `docs/test-strategy.md` — frameworks, the pyramid, gates, the definition of done | Authoring (Cowork) |
| 6 | **Ticket generation** | `tickets/*.md` + `CONVENTIONS.md` + `BOARD.md` — the work queue, in dependency order | Authoring (Cowork) |
| 7 | **Repository setup & scaffolding** | repo initialised, docs + tickets committed, skeletons that compile and test | Building (Code) |
| 8 | **Implementation, ticket by ticket** | working software; each ticket updated in the same commit as its code | Building (Code) |

> **Why this order.** Steps 1–3 fix *what* and *how*. Step 5 fixes *how you'll know it works* before
> any code exists, so tests are written to the spec rather than to the implementation. Step 6 turns
> the spec into a dependency-ordered queue. Only then does code begin. Each step's output is an input
> the next step depends on; skipping ahead means later steps build on guesses.

Authoring steps are done in a mode with **direct access to the project files** (Cowork), so the
agent reads and writes the docs in place rather than relying on uploads for context. Building steps
are done in the coding tool (Code). The separation that matters is authoring vs building, not the
specific product.

---

## Getting started: `init` and the trigger prompts

The agent drives the kit; you answer questions and sign off. You do **not** fill in placeholders by
hand — the placeholders are the agent's interview script.

**1. Drop the kit in.** Copy the contents of this folder into your empty repository root.

**2. Say `init`.** This is the bootstrapping prompt. On `init`, the agent:

- confirms the repository is empty/appropriate and asks for the project's name and one-line purpose;
- lays down the working structure — the root `CLAUDE.md`, `docs/milestone-plan.md`, and the
  `tickets/` system — adapted to the answers (project prefix, layer names, command runner);
- begins **Milestone 1** immediately by interviewing you for the project brief, section by section,
  writing `docs/project-brief.md` as it goes;
- **removes the consumed scaffolding** as it converts each template into a real document (see
  *Lifecycle of the kit*), so you are never left with a half-filled template beside the real thing.

**3. Work the milestones in order.** After each sign-off, start the next milestone with a prompt like
*"work the next milestone"* — the agent reads `docs/milestone-plan.md`, sees what is `In progress` or
next, and runs that step's interview or build. Each milestone is its own session.

Recommended trigger vocabulary (adapt the names to taste; what matters is that they map to the
lifecycle):

| Prompt | What the agent does |
|--------|---------------------|
| `init` | Bootstrap the repo from the kit and begin the Milestone 1 brief interview. |
| `work the next milestone` | Read the milestone plan, mark the next milestone `In progress`, run its step. |
| `start <step>` (e.g. `start the test strategy`) | Jump to a specific milestone's interview/build. |
| `sign off` | You confirm a milestone is complete; the agent marks it ✅ and advances the *Current position*. |
| `work the next ticket` (steps 7–8) | Pick the lowest-numbered `todo` ticket whose dependencies are all `done`, implement it, one ticket per commit. |

The agent must never self-certify a milestone — `sign off` is yours alone.

---

## Lifecycle of the kit (what stays, what goes)

A live project should not carry both a blank template and the filled-in document it became. Sort
everything the kit contains into three buckets:

- **Scaffolding — consumed and removed.** The blank templates in `docs/`, `tickets/`, and the
  `CLAUDE.md` files. `init` fills each into its real location and then **deletes the template
  residue**. A half-filled template is pure context noise; it must not linger.
- **Living docs — they stay and evolve.** The filled `docs/*`, the `tickets/*`, and the root and
  per-layer `CLAUDE.md` files. These *are* the project from here on; they are updated in place as
  the work proceeds and across versions.
- **Reference — archivable.** This `README` (the process narrative). Every *enforceable* rule it
  describes — the definition of done, the milestone lifecycle, the dependency rule — lives in
  `CLAUDE.md` / `tickets/CONVENTIONS.md` as the single source of truth. So once the project is up and
  running, the README can be archived or removed without losing anything the build relies on.

The net effect: once `init` has run and the spec milestones are signed off, a reader sees only the
living docs and the code — not the kit that produced them. The kit is a launch vehicle, not cargo.

> The kit is best distributed as its own template repository (or a `degit`-style starting point) and
> copied into new projects, rather than living inside any project it bootstraps. This README is
> written as though the kit sits at a repo root, because that is where it is dropped.

---

## How versions evolve (the delta pass)

After the first release, **do not fork the spec per version.** The binding documents in `docs/` are
*living*: they evolve in place, and your version-control tags (e.g. `v0.1.0`) are the record of what
shipped at each point.

A new version is scoped by a short **version brief** (`docs/vX.Y.Z-brief.md`) that drives a set of
**requirement deltas** against the living spec rather than a fresh specification:

- New requirements take **new** `FR-`/`NFR-` numbers.
- Superseded requirements are **amended in place** and annotated (e.g. *“rewritten — vX.Y”*), never
  silently reinterpreted.
- The only genuinely point-in-time artefacts are the milestone plan and each version's ticket batch.
  `BOARD.md` gains a new version section; shipped versions collapse into a “Shipped” section.

Subsequent versions therefore run as a **delta pass** (brief → requirement deltas → architecture/
contract deltas → wireframe deltas → test-strategy delta + ticket generation → implementation), not a
repeat of the full eight-step bootstrap. There is no second `init`.

---

## Architecture discipline: the dependency rule

Pick a layering for your project and write it down as a one-line rule, e.g.

```
core → domain → services → interface,   with  storage  beneath  services
```

Then make it more than aspirational:

- State, per layer, **what it may import** (the innermost layer should depend on nothing but the
  standard library / language runtime).
- **Enforce it with tooling** that fails the build on violation (an import-linter contract, a
  module-boundary check, a dependency cruiser — whatever your ecosystem offers). Do this in the
  scaffolding step, *before* any implementation. The agent then cannot introduce a circular
  dependency even when it would be the fastest path.
- Reflect the same rule in the ticket `depends_on` graph: a `services` ticket may depend on `core`
  and `storage` tickets; an `interface` ticket depends on `services`, never the reverse.

---

## Context discipline: hierarchical instructions

The agent's context window is its working memory; a monolithic instructions file wastes it. Split
your standing instructions:

- **Root `CLAUDE.md`** — only what *every* session needs: the non-negotiables, the dependency rule,
  the commands, the definition of done, the milestone lifecycle.
- **Per-layer `CLAUDE.md`** (e.g. `src/<layer>/CLAUDE.md`) — patterns and pitfalls specific to that
  layer, loaded automatically only when the agent touches that layer's files.

When you hit a non-obvious pitfall *twice*, write it into the relevant layer's `CLAUDE.md`
immediately — that is the cheapest place to stop it recurring.

---

## Test discipline

The test strategy (step 5) is written before code so tests express the spec, not the implementation.
Two habits matter most:

- **Test-first (red-green) for deterministic and contract-pinned layers.** Write the failing test
  from the requirement or the interface contract, confirm it fails *for the right reason*, then
  implement until green. Pure logic and interface shapes are exactly where this pays off.
- **Characterisation (after) tests for probabilistic or external-dependent layers.** Where output is
  non-deterministic (models, network, randomness), pin behaviour with seeded/recorded tests and
  assert properties rather than exact values.

Supporting practices: layered gates (a fast default gate run on every ticket, plus heavier gates —
performance, end-to-end, real-dependency — run for the ticket types that need them); a coverage gate
on the pure core; and **golden-file snapshots taken *before* any risky refactor** of deterministic
code, so a behavioural change shows up in the diff.

The **definition of done** for an implementation ticket lives in the root `CLAUDE.md` and the ticket
template. At minimum: the default gate passes with zero warnings; new or changed numbered-requirement
behaviour has tests **in the same commit**; the relevant heavier gate passes where the ticket says
so; and the ticket's status + notes and its `BOARD.md` row are updated in that same commit.

---

## Optional add-on: the meta loop

The `addons/meta-loop/` folder is **off by default**. Adopt it only if improving the development
*method itself* is one of your project's goals — otherwise it is overhead, and the per-layer
`CLAUDE.md` "record pitfalls here" habit already captures the practical lessons.

If you do adopt it, copy the two files into `docs/meta/`:

- `lessons-learned.md` — a living retrospective of transferable process observations.
- `method-improvements.md` — a register of method gaps, each tracked from **proposed** through
  **accepted / rejected / deferred** to **done**, with the reasoning recorded.

Review them at version boundaries. This is the loop that produced *this* starter kit: a project that
ran it long enough distilled its living method back into a reusable kit for the next project.
