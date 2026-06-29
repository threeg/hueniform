---
name: sfk-next-milestone
description: Advance the project by one milestone in the spec-first process. Reads docs/milestone-plan.md, marks the next milestone In progress, and runs that step's interview (authoring) or build (implementation). Trigger on "next milestone", "work the next milestone", "continue the project", or naming a step such as "start the requirements" or "start the test strategy".
---

# next-milestone — advance one milestone

Use after a milestone has been signed off, to pick up the next one. Each milestone is its own session.

## Procedure

1. **Read `docs/milestone-plan.md`.** Find the *Current position* line and the milestone table.
   Identify the next milestone to work: the first one that is `In progress` (🔶) but unfinished, or the
   next `Not started` (⬜) after the last signed-off one.

2. **Mark it `In progress` (🔶)** and move the *Current position* line to it, in the same commit as the
   work begins.

3. **Run the step.** Match the milestone to its activity:
   - **Authoring steps** (brief → requirements → architecture & contract → wireframes → test strategy
     → ticket generation): interview the user section by section against the relevant `docs/` template
     (or, for ticket generation, derive `tickets/*` and `BOARD.md` from the spec in dependency order).
     Write the document(s) in place.
   - **Building steps** (scaffolding → implementation): scaffolding initialises the repo, wires the
     dependency-rule check and the `sfk-verify` skill against the real stack, and commits skeletons that
     pass the empty gate. Implementation is handled ticket by ticket — use the `sfk-next-ticket` skill.

4. **Respect the dependency order.** Do not begin a milestone whose inputs (the prior milestones)
   are not signed off.

5. **Stop for sign-off.** When the deliverable is ready, present it and ask for explicit sign-off.
   **Never** mark the milestone `Complete` (✅) yourself. On sign-off, mark it ✅, advance the
   *Current position* line, and the next invocation handles the following milestone.

## Rules

- One milestone per session; one sign-off per milestone.
- The spec is binding: do not reopen settled decisions from earlier milestones — if one is genuinely
  wrong, change the relevant `docs/` file first and note it.
- For implementation milestones, defer to `sfk-next-ticket` and the ticket-workflow rules in
  `tickets/CLAUDE.md`.
