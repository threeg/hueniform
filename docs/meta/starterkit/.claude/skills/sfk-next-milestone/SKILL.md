---
name: sfk-next-milestone
description: Work the next milestone in the spec-first process to a committed draft. Reads process/milestone-plan.md, marks the next milestone In progress, runs its authoring interview or build, commits the draft deliverable, and iterates on the user's feedback. Does NOT mark the milestone complete — that is sfk-signoff. Trigger on "next milestone", "work the next milestone", "continue the project", or naming a step such as "start the requirements" or "start the test strategy".
---

# sfk-next-milestone — work one milestone to a committed draft

Use to work the next milestone the current version has laid down. Each milestone is its own session.
You produce and **commit** the deliverable as a draft and iterate with the user; you do **not** sign it
off — that is the separate `sfk-signoff` skill, which the user triggers.

## Procedure

1. **Read `process/milestone-plan.md`.** Find the *Current position* and the milestone table. Identify
   the next milestone: the one already `In progress` (🔶) but not yet signed off, or the next
   `Not started` (⬜) after the last completed one. Confirm its inputs (prior milestones) are signed off.

2. **Mark it `In progress` (🔶)** and move the *Current position* line to it.

3. **Run the step** and write the deliverable into its `process/` folder:
   - **Authoring steps** (brief → requirements → architecture & contract → wireframes → test strategy →
     ticket generation): interview the user section by section against the relevant master template (or,
     for ticket generation, derive `process/tickets/*` and `BOARD.md` from the spec in dependency order).
   - **Building steps** (scaffolding → implementation): scaffolding initialises the repo, wires the
     dependency-rule check and fills in the `sfk-verify` skill for the real stack, and commits skeletons
     that pass the empty gate. Implementation is handled ticket by ticket — defer to `sfk-next-ticket`.

4. **Commit the draft (WIP).** Commit the status change (step 2) and the draft deliverable together,
   e.g. `process: <milestone> — draft for review`. Do not wait for the user to commit.

5. **Present and iterate.** Show the user the deliverable and ask for feedback. If they have changes,
   revise and **commit each revision** (`process: <milestone> — revise <what>`). Loop until the user is
   satisfied. The milestone stays `In progress` throughout.

6. **Hand off to sign-off.** When the user is happy, tell them the deliverable is ready and that
   `sfk-signoff` will mark the milestone complete and advance the plan. **Never** mark it `Complete`
   yourself.

## Rules

- One milestone per session. You commit drafts and revisions; you never mark a milestone `Complete`.
- The spec is binding: do not reopen settled decisions from earlier milestones — if one is genuinely
  wrong, change the relevant `process/` file first and note it.
- For implementation milestones, defer to `sfk-next-ticket` and `process/tickets/CLAUDE.md`.


## Thread name

Run this in its own thread. Cowork auto-titles a thread and **cannot rename it programmatically** —
only the user can. As your **first action**, suggest the name below and ask the user to rename this
thread to it. `PROJCODE` is the project code (the ticket prefix) recorded as `project_code` in
`process/.sfk/manifest.md`, set when the project was created with `sfk-init` (e.g. `/sfk-init HUE`).

**Suggested name:** `PROJCODE: <Milestone>`  (e.g. `HUE: Architecture`)
