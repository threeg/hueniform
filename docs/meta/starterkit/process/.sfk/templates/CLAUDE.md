# CLAUDE.md — <PROJECT>

Standing instructions for working in this repository. Read this first, every session. This file is
auto-loaded at the repo root. The full method and the binding specification live in `process/` (start
at `process/README.md`); layer-specific guidance lives in `<code>/<layer>/CLAUDE.md` and
`process/tickets/CLAUDE.md`, which load automatically when you touch those directories.

> This is the **root** instructions template — the project's own standing instructions, kept lean. It
> contains only what *every* session needs. Push layer-specific patterns into per-layer `CLAUDE.md`
> files (template: `process/templates/layer-CLAUDE.md`). Replace every `<PLACEHOLDER>`.

## Project & kit

- **Project code:** `<PRJ>` — the ticket prefix (`<PRJ>-001`) and the thread-name prefix
  (`<PRJ> init`, `<PRJ>: Architecture`, `<PRJ> Implementation`). Set by `sfk-init`.
- **Spec-First Kit version applied:** `1.0.0` — raised by `sfk-update-process`. The kit's own
  version, changelog and pristine templates live in `process/.sfk/` (read-only — never edit it by
  hand; skills copy templates *out* of it).

## What this project is

> One short paragraph: what the product is and its single most important goal. If there is a
> meta-goal (e.g. "the process is as much a deliverable as the software"), state it here.

## Non-negotiables

> The handful of rules that are never broken. Examples to adapt:

- **<Language/locale>** for everything: spelling, prose, comments, commit messages.
- **All documentation is Markdown.**
- The documents in `process/` are the **binding specification.** Do not reopen or reinterpret a
  settled decision — implement to the spec. If the spec is genuinely wrong or missing, raise it and
  change the relevant `process/` file first; never silently diverge.
- **<Any hard runtime constraint>** (e.g. no network at runtime).

## Where things live

- `process/README.md` — the method (the eight steps, the lifecycle, how the skills drive it).
- `process/milestone-plan.md` — the single source of truth for project status.
- `process/brief/brief.md` — scope, goals, out-of-scope (binding).
- `process/requirements/requirements.md` — the `FR-n` / `NFR-n` rules; numeric thresholds are contractual.
- `process/architecture/architecture.md` — module layout, data model, the dependency rule, flows.
- `process/architecture/api-contract.md` — authoritative interface shapes; where code and contract disagree, the contract wins.
- `process/wireframes/` — the screens, states and navigation. (Omit for non-UI projects.)
- `process/test-strategy/test-strategy.md` — frameworks, conventions, the definition of done.
- `process/tickets/` — the work queue; ticket workflow rules in `process/tickets/CLAUDE.md`.
- `process/.sfk/` — kit machinery: `manifest.md` (kit version + the version this project is on), `CHANGELOG.md`, and `templates/` (pristine copies for updates). Do not edit the mirror by hand.
- `.claude/skills/sfk-*` — the workflow skills (`sfk-init`, `sfk-version`, `sfk-next-milestone`, `sfk-signoff`, `sfk-next-ticket`, `sfk-verify`, `sfk-update-process`).

> Each authoring milestone has its own folder under `process/` (e.g. `process/architecture/`). The
> named master file in it is binding; any other files in the folder are supporting context (reference
> docs, integration specs, inspiration) and are not binding.

## Architecture dependency rule (enforced, not aspirational)

> State the one-line rule and, concretely, what each layer may import. Keep this identical to
> `process/architecture/architecture.md` §2.1. Example shape:

`core → domain → services → interface`, with `storage` beneath `services`. Concretely:

- `core/` imports the **standard library only**. Pure functions over immutable data.
- `domain/` may import only `core`.
- `services/` may import `core`, `domain`, `storage`.
- `interface/` imports only `services` and its schemas. **Nothing imports `interface`.**
- `storage/` imports nothing from `core`/`domain`/`services`/`interface`.

This is enforced by `<boundary-enforcement tool>` and a standard-library allowlist test; breaking it
fails `<the default gate>`.

## Stack

> One paragraph: languages, frameworks, datastore, process topology. Keep in step with
> `process/architecture/architecture.md` §6.

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

- **When work on a milestone starts (via `sfk-next-milestone`), mark it `In progress` (🔶)** in
  `process/milestone-plan.md` and move the *Current position* line to it.
- **Never mark a milestone `Complete` (✅) on your own initiative.** Completion requires **explicit
  sign-off from the user**, performed via the `sfk-signoff` skill — finishing the deliverable, passing
  the gates, and self-verification are not sufficient. Until sign-off, the milestone stays
  `In progress`, however done it looks.
- **`sfk-signoff`** is what flips a milestone to `Complete`, moves the *Current position* line to the
  next milestone, and commits that status change.
