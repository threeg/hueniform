---
name: sfk-init
description: Bootstrap the basic environment for a new spec-first project from the starter kit. Use ONCE, in an otherwise-empty repository that contains this kit, to set up the root CLAUDE.md, the process folder, and the gitignore. Does not start any milestones. Trigger on "init", "initialise the project", "bootstrap from the starter kit", or "set up this kit".
---

# sfk-init — set up the project environment

Run this once, in a fresh repository that contains the starter kit. Your only job is to prepare the
working environment. You do **not** start any milestones and you do **not** write application code —
that comes later, via `sfk-version` then `sfk-next-milestone`.

## Procedure

1. **Confirm the situation.** Check that the repo contains the kit (`process/`, `.claude/skills/`) and
   little or no application code. If it looks like an already-bootstrapped project, stop and ask before
   proceeding — `sfk-init` is destructive to the templates.

2. **Short essentials interview** (one round, then proceed). Ask only what is needed to set up the
   environment — not the product itself (that is the brief, owned by `sfk-version` →
   `sfk-next-milestone`):
   - project name and a one-line description;
   - the short ticket prefix (e.g. `ACME` → `ACME-001`);
   - the architecture layers and the one-line dependency rule (offer the kit default
     `core → domain → services → interface, storage beneath services` and let them adjust);
   - the command runner and the default-gate command (e.g. `make test`);
   - whether there is a UI (if not, note the wireframes milestone will be dropped);
   - whether to adopt the optional meta loop (default: no — see `process/addons/meta-loop/`).

3. **Lay down the environment**, adapting the templates to the answers:
   - fill the root `CLAUDE.md` — non-negotiables, the dependency rule, commands, definition of done,
     the milestone lifecycle (replace every `<PLACEHOLDER>`);
   - leave `process/milestone-plan.md` with an **empty** milestone table and a *Current position* line
     reading "Environment bootstrapped; run `sfk-version` to start v0.1.0." — the table is laid down by
     `sfk-version`, not here;
   - adapt the prefix and layer names throughout `process/tickets/` and `process/templates/`;
   - confirm `.gitignore` suits the stack (uncomment the relevant build-artefact lines).

4. **Tidy up.** Delete the placeholder guidance from any file you fully fill. Leave the per-milestone
   template docs under `process/` intact — they are filled later, milestone by milestone.

5. **Stop and hand off.** Tell the user the environment is ready and the next step is `sfk-version`
   (give it a version number and goals). Do **not** start Milestone 1.

## Rules

- Environment only. No milestones, no brief content, no application code in `sfk-init`.
- `sfk-init` runs **once** per project and may be deleted afterwards (one-time scaffolding).
- Keep `process/` the binding source of truth; never mark a milestone complete (that is `sfk-signoff`).
- The pristine templates in `process/.sfk/templates/` are the kit's reference copy for future updates
  — never edit them; `sfk-update-process` uses them to apply later kit improvements.
