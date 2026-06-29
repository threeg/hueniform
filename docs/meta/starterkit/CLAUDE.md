# CLAUDE.md — <PROJECT>

Standing instructions for working in this repository. Read this first, every session.
Layer-specific guidance lives in `<code>/<layer>/CLAUDE.md` and `tickets/CLAUDE.md` — those load
automatically when you touch files in those directories.

> This is the **root** instructions template. Keep it slim: it should contain only what *every*
> session needs. Push layer-specific patterns into per-layer `CLAUDE.md` files (see the template at
> `<code>/CLAUDE.md`). Replace every `<PLACEHOLDER>`.

## What this project is

> One short paragraph: what the product is and its single most important goal. If there is a
> meta-goal (e.g. "the process is as much a deliverable as the software"), state it here.

## Non-negotiables

> The handful of rules that are never broken. Examples to adapt:

- **<Language/locale>** for everything: spelling, prose, comments, commit messages.
- **All documentation is Markdown.**
- The documents in `docs/` are the **binding specification.** Do not reopen or reinterpret a settled
  decision — implement to the spec. If the spec is genuinely wrong or missing, raise it and change
  the relevant `docs/` file first; never silently diverge.
- **<Any hard runtime constraint>** (e.g. no network at runtime).

## Where things live

- `docs/project-brief.md` — scope, goals, out-of-scope (binding).
- `docs/requirements.md` — the `FR-n` / `NFR-n` rules; numeric thresholds are contractual.
- `docs/architecture.md` — module layout, data model, the dependency rule, flows.
- `docs/api-contract.md` — authoritative interface shapes; where code and contract disagree, the contract wins.
- `docs/wireframes/` — the screens, states and navigation. (Omit for non-UI projects.)
- `docs/test-strategy.md` — frameworks, conventions, the definition of done.
- `docs/milestone-plan.md` — the single source of truth for project status.
- `tickets/` — the work queue; ticket workflow rules in `tickets/CLAUDE.md`.

## Architecture dependency rule (enforced, not aspirational)

> State the one-line rule and, concretely, what each layer may import. Keep this identical to
> architecture §2.1. Example shape:

`core → domain → services → interface`, with `storage` beneath `services`. Concretely:

- `core/` imports the **standard library only**. Pure functions over immutable data.
- `domain/` may import only `core`.
- `services/` may import `core`, `domain`, `storage`.
- `interface/` imports only `services` and its schemas. **Nothing imports `interface`.**
- `storage/` imports nothing from `core`/`domain`/`services`/`interface`.

This is enforced by `<boundary-enforcement tool>` and a standard-library allowlist test; breaking it
fails `<the default gate>`.

## Stack

> One paragraph: languages, frameworks, datastore, process topology. Keep in step with architecture §6.

## Commands

> The single command runner the agent should always use. Examples:

- `<make setup>` — one-time, online: install pinned deps, fetch any models, build, install browsers.
- `<make run>` — the single command to start the app.
- `<make dev>` — development mode (reload + client dev server).

Test targets (all offline after setup):

- `<make test>` — **the default gate**: unit + integration + the dependency-rule contracts + the
  core coverage gate. Run it on every ticket.
- `<make test-<heavy>>` / `<make test-perf>` / `<make test-e2e>` — heavier gates, per ticket type.
- `<make test-all>` — everything; required at milestone completion.

## Definition of done (implementation tickets)

A ticket is `done` only when: `<make test>` passes **with zero warnings**; new/changed
numbered-requirement behaviour has tests **in the same commit**; the core coverage gate holds for
core-touching work; the relevant heavier gate passes where the ticket says so; and the ticket's
status + `## Notes` and its `BOARD.md` row are updated in that commit. Docs-only, pure-styling and
build-plumbing tickets may set `tests_required: false` and must state the exemption in the body.

End each ticket with a **completion report**, given in the chat response and appended to the ticket:
(1) a short plain-language **summary** of what was done; (2) a one-line **sanity test** the user can
run; and (3) for any ticket that touches the UI, **QA steps** — the manual actions and their expected
results. The summary and sanity test go in the ticket's `## Notes`; the QA steps go in `## QA steps`.

## Milestone status lifecycle

Milestones move `Not started (⬜) → In progress (🔶) → Complete (✅)`.

- **When you start work on a milestone, mark it `In progress` (🔶)** in `docs/milestone-plan.md`
  and move the *Current position* line to it.
- **Never mark a milestone `Complete` (✅) on your own initiative.** Completion requires **explicit
  sign-off from the user** — finishing the deliverable, passing the gates, and self-verification are
  not sufficient. Until sign-off, the milestone stays `In progress`, however done it looks.
- **When the user signs off,** mark the milestone `Complete` and move the *Current position* line to
  the next milestone — in the same commit as the milestone's deliverable.
