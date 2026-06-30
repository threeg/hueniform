# Spec-First Starter Kit — the method

| | |
|---|---|
| **Kit version** | v1.0.0 |
| **Author** | Gregg Seymour |
| **Kit identity** | `process/.sfk/manifest.md` (read-only); changes in `process/.sfk/CHANGELOG.md` |
| **A project's applied kit version** | recorded in the project's root `CLAUDE.md` (*Project & kit*) |

A project-neutral way to build software **spec-first, ticket-by-ticket, with an AI coding agent**.
This file is the process guide. The kit lives entirely under `process/` plus a `.claude/skills/`
folder, so it never squats on the files your project owns at the root (`README.md`, `CLAUDE.md`, your
code).

The kit is **versioned**: a project records which kit version it is on, and `sfk-update-process` pulls
later improvements into an existing project without disturbing your filled-in docs (see *Updating*).

---

## Quick start (do this first)

1. **Drop the kit into a new, empty repository.** It adds a `process/` folder, a `.claude/skills/`
   folder, a root `CLAUDE.md`, and a `.gitignore`. Your project keeps its own root `README.md`.

2. **Install the workflow skills** in `.claude/skills/` (`sfk-init`, `sfk-version`,
   `sfk-next-milestone`, `sfk-signoff`, `sfk-next-ticket`, `sfk-verify`, `sfk-update-process`):
   - **Claude Code (CLI):** they live in `.claude/skills/` already, so they are discovered
     automatically — nothing to do.
   - **Desktop app (Cowork):** skills are not auto-discovered. Add them via **Settings → Capabilities**,
     or upload the prebuilt `.skill` packages (ask the agent: *"package the skills in `.claude/skills/`
     as installable `.skill` files"*).

3. **Trigger `sfk-init`** (optionally pass your project code, e.g. `/sfk-init ACME`). The code is your
   ticket prefix (`ACME-001`); omit it and the agent will ask. The agent confirms the basics (project
   name, stack, layers) and lays down the working structure — root `CLAUDE.md`, `process/`,
   `.gitignore` — copying templates out of `process/.sfk/templates/` and recording the project code in
   the root `CLAUDE.md`. It does **not** start any milestones; it only prepares the environment.

4. **Trigger `sfk-version`.** Give it a version number and the goals for it. It writes the version
   brief and lays down that version's milestone table in `process/milestone-plan.md`. (For the first
   release that's the full eight steps; for later versions it's the shorter delta pass.)

5. **Work the milestones.** Run `sfk-next-milestone` to work the next one — the agent interviews you,
   produces the deliverable, and commits it as a draft. Review; loop with feedback until it's right;
   then run `sfk-signoff` to mark it complete and advance. Repeat to the end of the version. During the
   implementation milestone, run `sfk-next-ticket` repeatedly and `sfk-verify` at batch boundaries.

6. **Next version:** trigger `sfk-version` again with the new number and goals.

7. **Updating the kit later:** when a newer kit version ships, run `sfk-update-process` to pull its
   improvements into this project — it refreshes the kit-owned files and the `.sfk/templates/` mirror,
   then applies the changelog deltas to your living docs, interviewing you where a change needs input.
   It never overwrites your filled-in content (see *Updating a project to a newer kit version*).

> **No skills installed?** Every skill has a fallback: point the agent at its file, e.g. *"Read
> `.claude/skills/sfk-init/SKILL.md` and follow it."* The `SKILL.md` body is the full instruction set.

This kit is the distilled *process* — nothing here is tied to any domain, language, or framework. It
is itself the output of a project that treated its development method as a deliverable (see the
optional meta loop, below).

---

## What this kit gives you

```
/                                 ← your project owns the root
├── CLAUDE.md                     ← project standing instructions (auto-loaded; template provided)
├── README.md                     ← your project's own (the kit does not touch this)
├── .gitignore                    ← sensible neutral defaults (provided)
├── .claude/
│   └── skills/                   ← the seven workflow skills (auto-discovered by Claude Code)
│       ├── sfk-init/             ← one-time environment bootstrap
│       ├── sfk-version/          ← start a version: brief + its milestone table
│       ├── sfk-next-milestone/   ← work one milestone to a committed draft
│       ├── sfk-signoff/          ← finalise & commit a milestone's completion
│       ├── sfk-next-ticket/      ← implement one ticket, one commit
│       ├── sfk-verify/           ← post-batch spec audit + quality review (TEMPLATE)
│       └── sfk-update-process/   ← pull a newer kit version into this project
└── process/                      ← your living spec + workflow (skills fill these; isolated from code)
    ├── README.md                 ← this guide (the method; kit-owned)
    ├── milestone-plan.md         ← project status (sfk-init copies it out of .sfk/templates, then fills)
    ├── brief/ requirements/      ← one folder per authoring milestone. sfk-next-milestone copies the
    │   architecture/ wireframes/   master (e.g. architecture/architecture.md) out of .sfk/templates,
    │   test-strategy/              fills the copy, and you drop supporting context alongside
    ├── tickets/                  ← the work queue (sfk-init copies it out; you then generate tickets)
    ├── templates/                ← layer-CLAUDE.md (copied out at init, into each code layer)
    ├── addons/meta-loop/         ← OPTIONAL — only if improving the method is itself a goal
    └── .sfk/                     ← the kit's READ-ONLY source — never edit by hand; skills copy OUT of it
        ├── manifest.md           ← kit identity (name, version, author) — read-only
        ├── CHANGELOG.md          ← what changed per kit version (the update migration script)
        └── templates/            ← pristine master of every living file (the source skills copy out)
```

(Pre-`sfk-init`, `process/` holds only this `README.md` and `.sfk/`; the working files above are
created by the skills as they copy templates out and fill them. The project's own state — its project
code and the kit version it has applied — lives in the root `CLAUDE.md` (*Project & kit*), so `.sfk/`
stays read-only.)

**Each authoring milestone is a folder.** The named master file in it (e.g.
`architecture/architecture.md`) is the binding deliverable; the skill that works the milestone copies
that master out of `process/.sfk/templates/` and fills it. Anything else you drop in the folder —
reference docs for an integration, inspiration images for wireframes, a vendor's API PDF — is
supporting context and is *not* binding. This keeps the master clean while giving each milestone a home
for the material that informed it.

**Nothing is numbered.** Ordering is owned by `process/milestone-plan.md`; because the docs are
*living* and evolve across versions, a number prefix would imply a fixed sequence that stops being
true. The only numbered files are point-in-time **version briefs** (e.g. `process/v0.2.0-brief.md`).

Every template is **annotated**: real section structure, `<ANGLE_BRACKET>` placeholders, and inline
guidance that doubles as the agent's interview checklist — consumed and deleted from the working copy
as each section is filled in. The skills copy a template *out* of `process/.sfk/templates/` to its
working location and fill the copy; the source in `.sfk/` is **never edited**, which is what lets
`sfk-update-process` apply later kit improvements.

---

## The core idea

Two principles run through everything:

1. **The specification is binding, and it comes first.** No code is written until the spec is detailed
   enough that a *fresh* agent session — with no conversation history — could implement any ticket
   correctly from the documents alone. Ambiguity is settled by pointing at a document, not by
   re-explaining a decision in chat.

2. **The ticket is the unit of work, and the ticket is the prompt.** A well-formed ticket gives the
   agent everything it needs to work autonomously and produce a reviewable commit. One ticket, one
   commit: the work record and the code record stay 1:1.

The pay-off compounds. Each session starts with full context. The agent never guesses intent.
`git log` reads like a build journal. Reverting a unit of work means reverting one commit.

---

## The milestone lifecycle (read this first)

Everything hangs off this. The project advances through a sequence of **milestones**, tracked in
`process/milestone-plan.md`, the single source of truth for *where the project is*. Each milestone has
exactly one status:

```
⬜ Not started  →  🔶 In progress  →  ✅ Complete
```

Two rules keep it honest, and they are non-negotiable:

- **`sfk-next-milestone` marks a milestone `In progress` (🔶)** when work starts, moves the *Current
  position* line to it, and commits the draft deliverable.
- **A milestone only becomes `Complete` (✅) by `sfk-signoff`, which you trigger.** The agent never
  self-completes a milestone. Finishing the deliverable, passing the gates, and self-verification are
  *not* sufficient — until you sign off, it stays `In progress`, however done it looks.

This is the rhythm: one milestone at a time, each its own session, drafted and committed by the agent,
completed only by you.

---

## The eight steps

A release proceeds through these steps (the milestones `sfk-version` lays down for the first version).
The first six produce documents; the last two produce code. The **Mode** column says whether a step is
*authoring* (thinking with the spec and project files) or *building* (executing against the spec) —
the recommended tool is named, but the durable point is the mode, not the brand.

| # | Step | Deliverable | Mode (tool) | Worked by |
|---|------|-------------|-------------|-----------|
| 1 | **Project brief** | `process/brief/brief.md` — scope, goals, users, out-of-scope, success criteria | Authoring (Cowork) | `sfk-next-milestone` → `sfk-signoff` |
| 2 | **Requirements** | `process/requirements/requirements.md` — numbered `FR-n` / `NFR-n` rules; testable thresholds | Authoring (Cowork) | `sfk-next-milestone` → `sfk-signoff` |
| 3 | **Architecture & contract** | `process/architecture/architecture.md`, `process/architecture/api-contract.md`, data model, dependency rule | Authoring (Cowork) | `sfk-next-milestone` → `sfk-signoff` |
| 4 | **Wireframes** | `process/wireframes/` — screens, states, navigation (skip for non-UI projects) | Authoring (Cowork) | `sfk-next-milestone` → `sfk-signoff` |
| 5 | **Test strategy** | `process/test-strategy/test-strategy.md` — frameworks, the pyramid, gates, definition of done | Authoring (Cowork) | `sfk-next-milestone` → `sfk-signoff` |
| 6 | **Ticket generation** | `process/tickets/*.md` + `CONVENTIONS.md` + `BOARD.md` — the work queue in dependency order | Authoring (Cowork) | `sfk-next-milestone` → `sfk-signoff` |
| 7 | **Scaffolding** | repo skeletons that compile and test, dependency-rule check wired in, **`sfk-verify` filled in for the stack** | Building (Code) | `sfk-next-milestone` → `sfk-signoff` |
| 8 | **Implementation** | working software; each ticket updated in the same commit as its code | Building (Code) | `sfk-next-ticket` + `sfk-verify` |

> **Why this order.** Steps 1–3 fix *what* and *how*. Step 5 fixes *how you'll know it works* before
> any code exists, so tests are written to the spec rather than the implementation. Step 6 turns the
> spec into a dependency-ordered queue. Only then does code begin. Each step's output is an input the
> next depends on; skipping ahead builds on guesses.

---

## The skills (how the agent drives the kit)

You answer questions and sign off; the agent does the rest. Seven skills, mapped to the lifecycle:

| Skill | When | What it does |
|-------|------|--------------|
| `sfk-init` | once, on a fresh repo | Short essentials interview; lays down root `CLAUDE.md`, `process/`, `.gitignore`. Prepares the environment only — starts no milestones. |
| `sfk-version` | start of each version | Takes a number + goals; writes the version brief and lays down that version's milestone table in the plan. |
| `sfk-next-milestone` | start of each milestone | Marks the next milestone `In progress`, runs its authoring interview or build, and commits the draft deliverable. Iterates on your feedback. |
| `sfk-signoff` | when you approve a milestone | Flips it to `Complete`, moves the *Current position*, commits the status change. The human gate. |
| `sfk-next-ticket` | repeatedly, in step 8 | Picks the lowest-numbered `todo` ticket whose dependencies are `done`, implements it, one ticket per commit. |
| `sfk-verify` | at batch boundaries | Audits the batch against the spec, reviews code quality, proposes cleanup tickets. Filled in for the stack during scaffolding. |
| `sfk-update-process` | when a newer kit ships | Refreshes the kit-owned files and the `.sfk/templates/` mirror, then applies the changelog deltas to your living docs — interviewing where a change needs input, never overwriting your content. |

The typical loop for an authoring milestone: **`sfk-next-milestone`** (interview → draft → WIP commit)
→ you review → optional feedback rounds (each committed) → **`sfk-signoff`** (complete + advance).

> **Tip:** run each milestone in its own thread so they stay distinguishable. Cowork can't rename a
> thread programmatically, so name them however suits you (e.g. by milestone) — the skills don't manage
> thread names.

---

## Lifecycle of the kit (what stays, what goes)

A live project should not carry a *visibly* half-filled template, but it should keep a pristine copy
of each template hidden away so future kit updates can be applied. Three buckets:

- **Working files — copied out and filled.** The documents under `process/` and the root `CLAUDE.md`.
  A skill copies each one *out* of `process/.sfk/templates/` to its working location and fills it,
  deleting the inline placeholder guidance as each section becomes real. These are your living docs;
  you edit them freely. They do not exist until a skill creates them.
- **`.sfk/` — read-only source, never edited.** `process/.sfk/templates/` holds the pristine master of
  every living file; `manifest.md` and `CHANGELOG.md` are the kit's identity and history. The authoring
  skills **only read** here (to copy out and, on update, to diff); they never write inside `.sfk/`.
  Only `sfk-update-process` refreshes it, from a newer kit. This is what makes later updates safe.
- **Kit-owned — replaced on update.** This guide and the skills. You don't edit these;
  `sfk-update-process` refreshes them wholesale. Every *enforceable* rule the guide states also lives
  in `CLAUDE.md`, `process/tickets/CONVENTIONS.md`, or the skills, so the guide itself is reference you
  could archive.

Because the whole kit sits under `process/` and `.claude/`, the project's root stays clean: your
`README.md`, your `CLAUDE.md`, your code.

---

## How versions evolve (the delta pass)

After the first release, **do not fork the spec per version.** The documents in `process/` are
*living*: they evolve in place, and your version-control tags (e.g. `v0.1.0`) are the record of what
shipped.

`sfk-version` scopes a new version with a short **version brief** (`process/vX.Y.Z-brief.md`) that
drives **requirement deltas** against the living spec:

- New requirements take **new** `FR-`/`NFR-` numbers.
- Superseded requirements are **amended in place** and annotated (e.g. *“rewritten — vX.Y”*), never
  silently reinterpreted.
- The only point-in-time artefacts are the milestone plan and each version's ticket batch. `BOARD.md`
  gains a new version section; shipped versions collapse into a “Shipped” section.

So later versions run as a delta pass (brief → requirement deltas → architecture/contract deltas →
wireframe deltas → test-strategy delta + ticket generation → implementation), driven by the same
`sfk-next-milestone` / `sfk-signoff` / `sfk-next-ticket` loop. There is no second `sfk-init`.

> Note the two distinct "version" concepts. A **project version** (`v0.1.0`, `v0.2.0`) is *your
> software's* release, scoped by `sfk-version`. A **kit version** (this kit's `v1.0.0`) is *the
> method's* release, applied by `sfk-update-process`. They are independent.

---

## Updating a project to a newer kit version

The kit improves over time (this is how the "in plain English" ticket section, the `process/` layout,
and so on arrived). To pull those improvements into an existing project **without disturbing your
filled-in docs**, use `sfk-update-process` rather than a blind file copy — a blind copy would clobber
your living documents, because the kit also ships working-named files for fresh inits.

How it works:

1. Make the newer kit available (clone the kit repo, or drop it in a temp folder). The skill compares
   the newer kit's `process/.sfk/manifest.md` (its `kit_version`) against the applied version recorded
   in your root `CLAUDE.md` (*Project & kit*).
2. It reads `process/.sfk/CHANGELOG.md` for every entry newer than your project's applied version. The
   changelog is the migration script: each entry says what changed and how to apply it.
3. It **refreshes the kit-owned files** (the skills, this guide, the `.sfk/` machinery) and the
   `process/.sfk/templates/` mirror.
4. For each living document, it reasons about the change three ways — your file vs the old pristine
   mirror vs the new one — and applies the delta: a new section is added as an empty heading; a
   guidance/wording change is applied; a change that needs a decision triggers a short interview. It
   **never** overwrites your content, and it does not touch generated artefacts such as individual
   tickets — though it will *offer* to backfill a new template section into them (e.g. "the ticket
   template gained `## In plain English`; add it to your 14 tickets?").
5. It updates the **applied kit version** in your root `CLAUDE.md` (*Project & kit*) and commits.

The result: your living spec gains the method's improvements, your content is preserved, and the
project's recorded kit version moves forward.

---

## Architecture discipline: the dependency rule

Pick a layering and write it down as a one-line rule, e.g.

```
core → domain → services → interface,   with  storage  beneath  services
```

Then make it more than aspirational: state per layer **what it may import** (the innermost layer
depends on nothing but the standard library); **enforce it with tooling** that fails the build on
violation (import-linter, module-boundary check, dependency cruiser), wired in at scaffolding; and
reflect the same rule in the ticket `depends_on` graph.

---

## Context discipline: hierarchical instructions

The agent's context window is its working memory. Split standing instructions: a lean **root
`CLAUDE.md`** (non-negotiables, dependency rule, commands, definition of done, milestone lifecycle) and
**per-layer `CLAUDE.md`** files (template: `process/templates/layer-CLAUDE.md`) loaded only when the
agent touches that layer. When you hit a non-obvious pitfall *twice*, write it into the relevant
layer's `CLAUDE.md` immediately.

---

## Test discipline

The test strategy (step 5) is written before code so tests express the spec, not the implementation.
Two habits matter most: **test-first (red-green)** for deterministic and contract-pinned layers (write
the failing test from the requirement/contract, confirm it fails for the right reason, then implement);
and **characterisation tests** for probabilistic/external layers (seeded/recorded, asserting
properties). Supporting practices: layered gates (a fast default gate every ticket, heavier gates per
type); a coverage gate on the pure core; golden-file snapshots taken *before* any risky refactor; and
the **`sfk-verify` pass** at batch boundaries, which turns spec-audit findings into cleanup tickets.

The **definition of done** for an implementation ticket lives in the root `CLAUDE.md` and the ticket
template: the default gate passes with zero warnings; new/changed numbered-requirement behaviour has
tests in the same commit; the relevant heavier gate passes where the ticket says so; and the ticket's
status + notes and its `BOARD.md` row are updated in that same commit.

---

## Optional add-on: the meta loop

`process/addons/meta-loop/` is **off by default**. Adopt it only if improving the development *method
itself* is one of your project's goals — otherwise it is overhead, and the per-layer `CLAUDE.md`
"record pitfalls here" habit already captures the practical lessons. If you do adopt it, copy the two
files into `process/meta/`:

- `lessons-learned.md` — a living retrospective of transferable process observations.
- `method-improvements.md` — a register of method gaps, each tracked from **proposed** through
  **accepted / rejected / deferred** to **done**, with the reasoning recorded.

Review them at version boundaries. This is the loop that produced *this* kit.
