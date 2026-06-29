---
name: init
description: Bootstrap a new spec-first project from the starter kit. Use ONCE, in an otherwise-empty repository that contains this kit, to interview the user for the project brief and lay down the working structure (root CLAUDE.md, milestone plan, ticket system). Trigger on "init", "initialise the project", "bootstrap from the starter kit", or "set up this kit".
---

# init — bootstrap the project

Run this once, in a fresh repository that contains the starter kit. Your job is to turn the blank
templates into a real project skeleton and start Milestone 1. Do **not** write application code here —
this step produces the brief and the working structure only.

## Procedure

1. **Confirm the situation.** Check that the repo contains the kit (`README.md`, `CLAUDE.md`, `docs/`,
   `tickets/`) and little or no application code. If it looks like an already-bootstrapped project,
   stop and ask before proceeding — `init` is destructive to the templates.

2. **Interview for the essentials** (one short round of questions, then proceed):
   - project name and one-line purpose;
   - the short ticket prefix (e.g. `ACME` → `ACME-001`);
   - the architecture layers and the one-line dependency rule (offer the kit's default
     `core → domain → services → interface, storage beneath services` and let them adjust);
   - the command runner and the default-gate command (e.g. `make test`);
   - whether there is a UI (if not, the wireframes milestone is dropped);
   - whether to adopt the optional meta loop (default: no — see `addons/meta-loop/`).

3. **Lay down the working structure**, adapting the templates to the answers:
   - fill `CLAUDE.md` (root) — non-negotiables, dependency rule, commands, definition of done,
     milestone lifecycle;
   - fill `docs/milestone-plan.md` — the milestone table and the *Current position* line, with
     Milestone 1 marked `In progress` (🔶);
   - adapt `tickets/CONVENTIONS.md`, `tickets/TICKET-TEMPLATE.md`, `tickets/CLAUDE.md`, `tickets/BOARD.md`
     to the chosen prefix and layer names;
   - replace `<PRJ>` / `<PROJECT>` / layer placeholders throughout.

4. **Wire in the verifier.** Fill the `verify` skill template against the chosen stack (the actual
   gate commands and the spec-audit checklist) so post-batch review works from the start. This is the
   scaffolding (Milestone 7) responsibility, but record the intent now in the milestone plan.

5. **Begin Milestone 1 — the project brief.** Interview the user section by section against
   `docs/project-brief.md`, writing the document as you go. Do not rush to later milestones.

6. **Remove the consumed scaffolding.** As each template becomes a real document, delete the leftover
   placeholder guidance. Move the optional `addons/` into `docs/meta/` only if the user opted in;
   otherwise leave it untouched. The `init` skill itself may be deleted once bootstrap is complete —
   it is one-time.

7. **Stop for sign-off.** Do **not** mark Milestone 1 complete. Tell the user the brief is ready for
   review and that completion needs their explicit sign-off (see the milestone lifecycle in
   `CLAUDE.md`). After sign-off, the next step is the `next-milestone` skill.

## Rules

- Never mark a milestone `Complete` on your own initiative — that is the user's call.
- Keep `docs/` the binding source of truth; do not start application code during `init`.
- One round of clarifying questions is enough to start; refine inside the brief interview.
