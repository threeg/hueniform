---
name: sfk-init
description: Bootstrap the basic environment for a new spec-first project from the starter kit. Use ONCE, in an otherwise-empty repository that contains this kit. Optionally takes the project code as an argument, e.g. "/sfk-init ACME". Copies the environment templates out of process/.sfk/templates/ into their working locations and fills them; does not start any milestones. Trigger on "init", "initialise the project", "bootstrap from the starter kit", or "set up this kit".
---

# sfk-init — set up the project environment

Run this once, in a fresh repository that contains the starter kit. Your only job is to prepare the
working environment by **copying templates out of `process/.sfk/templates/`** and filling the copies.
You do **not** start any milestones and you do **not** write application code — that comes later, via
`sfk-version` then `sfk-next-milestone`.

> **`process/.sfk/` is read-only.** It is the kit's pristine source (templates, changelog, manifest).
> **Never edit anything inside `.sfk/`.** Always copy a template *out* to its working location and edit
> the copy. Only `sfk-update-process` ever writes inside `.sfk/`.

**Project code.** This skill may be invoked with the project code as an argument, e.g.
`/sfk-init ACME`. The code is a short uppercase token used as the **ticket prefix** (`ACME-001`). It is
optional: if an argument is supplied, use it without asking; otherwise ask for it in the interview.

## Procedure

1. **Confirm the situation.** Check that the repo contains the kit (`process/.sfk/templates/`,
   `.claude/skills/`) and little or no application code. If it looks already-bootstrapped (a root
   `CLAUDE.md` and filled `process/` docs exist), stop and ask before proceeding.

2. **Short essentials interview** (one round, then proceed). Ask only what the environment needs — not
   the product itself (that is the brief, owned by `sfk-version` → `sfk-next-milestone`):
   - the **project code / ticket prefix** — use the argument if passed (e.g. `/sfk-init ACME` →
     `ACME`); otherwise ask;
   - project name and a one-line description;
   - the architecture layers and the one-line dependency rule (offer the kit default
     `core → domain → services → interface, storage beneath services` and let them adjust);
   - the command runner and the default-gate command (e.g. `make test`);
   - whether there is a UI (if not, note the wireframes milestone will be dropped);
   - whether to adopt the optional meta loop (default: no).

3. **Copy the environment templates out of `process/.sfk/templates/`** to their working locations, then
   fill the copies (replace every `<PLACEHOLDER>`):
   - `process/.sfk/templates/CLAUDE.md` → `./CLAUDE.md` (root). Fill it, and in its *Project & kit*
     section record the **project code** and set **Spec-First Kit version applied** to the
     `kit_version` from `process/.sfk/manifest.md`. (This is where project state lives — not in `.sfk`.)
   - `process/.sfk/templates/process/milestone-plan.md` → `process/milestone-plan.md`. Leave the
     milestone table **empty** with a *Current position* line "Environment bootstrapped; run
     `sfk-version` to start v0.1.0." — the table is laid down by `sfk-version`.
   - `process/.sfk/templates/process/tickets/*` → `process/tickets/*`, and
     `process/.sfk/templates/process/templates/layer-CLAUDE.md` → `process/templates/layer-CLAUDE.md`.
     Adapt the prefix and layer names.
   - if the meta loop was adopted: `process/.sfk/templates/process/addons/meta-loop/*` →
     `process/addons/meta-loop/*` (otherwise leave it in `.sfk` only).
   - Do **not** copy out the per-milestone spec docs (brief, requirements, architecture, wireframes,
     test-strategy) — `sfk-next-milestone` copies each out when its milestone is worked.
   - confirm the root `.gitignore` suits the stack (uncomment the relevant build-artefact lines).

4. **Stop and hand off.** Tell the user the environment is ready and the next step is `sfk-version`
   (give it a version number and goals). Do **not** start Milestone 1.

## Rules

- **Never edit `process/.sfk/`** — copy templates out and edit the copies. Project state goes in the
  root `CLAUDE.md`, never in `.sfk`.
- Environment only. No milestones, no brief content, no application code.
- `sfk-init` runs **once** per project and may be deleted afterwards (one-time scaffolding).
- Never mark a milestone complete (that is `sfk-signoff`).
