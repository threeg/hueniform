# CLAUDE.md — Hueniform

Standing instructions for working in this repository. Read this first, every session.

## What this project is

Hueniform is a local-first, single-user web app that builds a digital wardrobe from garment
photos, detects each garment's colours, and suggests harmonious outfits using colour theory.
It has a deliberate **meta-goal**: the *process* — documented in Markdown, tracked as
Markdown tickets, built milestone by milestone — is as much a deliverable as the software.

## Non-negotiables

- **UK English** for everything: spelling, grammar, prose, comments, commit messages.
- **All documentation is Markdown.**
- The documents in `docs/` are the **binding specification**. Do not reopen or reinterpret a
  settled decision — implement to the spec. If the spec is genuinely wrong or missing, raise it
  and change the relevant `docs/` file first; never silently diverge.
- **No internet at runtime** (NFR-1, NFR-8). The only online step is `make setup`.

## Where things live

- `docs/01-project-brief.md` — scope, goals, out-of-scope (binding).
- `docs/02-requirements.md` — the `FR-n` / `NFR-n` rules; numeric thresholds are contractual (§1.4).
- `docs/03-architecture.md` — module layout, data model, the dependency rule, flows.
- `docs/03-api-contract.md` — authoritative HTTP shapes; where code and contract disagree, the contract wins.
- `docs/04-wireframes/` — the screens, states and navigation.
- `docs/05-test-strategy.md` — frameworks, test conventions, the definition of done (§12.3).
- `docs/00-milestone-plan.md` — the single source of truth for project status.
- `tickets/` — the work queue (see below).

## How we work: tickets

The build runs ticket by ticket. The system is defined in `tickets/CONVENTIONS.md`; the per-ticket
format in `tickets/TICKET-TEMPLATE.md`; the execution order in `tickets/BOARD.md`.

- **Work tickets, not epics.** Epics (`HUE-E0n`) are a capability view only — no code ships against
  them; they close when their children are `done`. The unit of work is the leaf ticket (`HUE-NNN`).
- **Go in order.** Pick the lowest-numbered `todo` ticket whose every `depends_on` id is `done`.
  `BOARD.md` top-to-bottom is a legal sequence. **Never start a ticket whose dependencies aren't done.**
- **One ticket per commit.** A commit moves exactly one ticket: its code, its tests, its
  `status`/`## Notes`, and its `BOARD.md` row — together. This is the §12.3.7 rule and what keeps the
  history honest and reviewable.
- **Status lifecycle:** `todo → in-progress → in-review → done` (`blocked` when stuck). Set
  `in-progress` when you start; `done` only when the ticket's Definition of done holds in full.
- **Commit message:** `HUE-NNN: <short imperative>` (e.g. `HUE-007: matcher.constants`).

## Architecture dependency rule (enforced, not aspirational)

`matcher → detection → services → api`, with `storage` beneath `services`. Concretely:

- `matcher/` imports the **standard library only** (NFR-9). Pure functions over frozen dataclasses.
- `detection/` may import only `matcher.taxonomy`, `matcher.colour`, `matcher.constants` (plus its
  image/maths libs).
- `services/` may import `detection`, `matcher`, `storage`.
- `api/` imports only `services` and its schemas. **Nothing imports `api`.**
- `storage/` imports nothing from `matcher`/`detection`/`services`/`api`.

This is enforced by import-linter contracts and a std-library allowlist test (test strategy §5);
breaking it fails `make test`.

## Stack

Python 3.12 · FastAPI + Uvicorn · SQLModel over SQLite + local image files · rembg (U²-Net,
onnxruntime) + scikit-learn KMeans for detection · React + Vite + TypeScript SPA (React Router,
TanStack Query, CSS Modules). One process serves `/api` and the built SPA at `/`.

## Commands

- `make setup` — one-time, online: venv, pinned deps, fetch the rembg model, build the SPA, install Playwright browsers.
- `make run` — the single offline command (NFR-2): init data, sweep staging, serve, print the URL.
- `make dev` — Uvicorn reload + Vite dev server proxying `/api`.

Test targets (all offline after setup):

- `make test` — **the default gate**: backend unit+integration with the import contracts and the
  matcher coverage gate, plus frontend component tests. Run it on every ticket.
- `make test-backend` / `make test-frontend` — the two halves of the gate.
- `make test-model` — real rembg + KMeans over fixture photos (DoD for detection-touching tickets).
- `make test-perf` — NFR-5 / NFR-6 timing at 500 garments (DoD for suggestion-/inventory-query tickets).
- `make test-e2e` — Playwright smoke journeys, Chromium + Firefox (DoD for user-flow tickets).
- `make test-all` — everything; required at milestone completion.

## Definition of done (implementation tickets)

A ticket is `done` only when: `make test` passes **with zero warnings**; new/changed
numbered-requirement behaviour has tests **in the same commit** (§12.2); the matcher 100%
line+branch gate holds for matcher-touching work; the relevant heavier gate passes where the ticket
says so (`test-model` / `test-perf` / `test-e2e`); and the ticket's status + `## Notes` and its
`BOARD.md` row are updated in that commit. Docs-only, pure-styling and build-plumbing tickets may
set `tests_required: false` and must state the exemption in the body.

End each ticket summary with a one-line sanity test the user can run, e.g.
`cd backend && .venv/bin/pytest tests/<layer>/test_<module>.py -q`.

## Storage testing patterns

These apply to every ticket that touches `app/storage/` or writes tests that create a SQLite engine:

- **Engine fixture teardown:** always `yield` the engine and call `engine.dispose()` afterwards —
  not `return`. Without dispose, Python 3.13 raises `ResourceWarning: unclosed database` for every
  connection in the pool, which fails the zero-warnings gate.
  ```python
  @pytest.fixture()
  def engine(tmp_path):
      e = make_engine(tmp_path / "test.db")
      init_db(e)
      yield e
      e.dispose()
  ```
- **Parent/child insert ordering:** SQLModel has no ORM relationship between `GarmentRow` and
  `GarmentColourRow`, so SQLAlchemy does not know insertion order. Call `session.flush()` after
  adding the parent row before adding child rows, or the FK constraint fires on the child insert.

## When a milestone completes

Update `docs/00-milestone-plan.md` — the milestone's status **and** the *Current position* line —
in the same commit as the milestone's deliverable.
