---
name: sfk-version
description: Start a new version of the project. Takes a version number and its goals, writes the version brief, and lays down that version's milestone table in process/milestone-plan.md. Use after sfk-init for the first release, and again at the start of each later version. Trigger on "start a version", "new version", "begin v0.2.0", "plan the next version", or "start v1".
---

# sfk-version — start a version

Use to open a version: the first release right after `sfk-init`, and each later version once the
previous one has shipped. It defines *what* the version delivers and lays out the milestones to get
there; it does **not** work the milestones (that is `sfk-next-milestone`).

## Procedure

1. **Get the number and goals.** Ask the user for the version number (e.g. `v0.1.0`, `v0.2.0`) and its
   goals — the capabilities or changes it should deliver. One round of questions to make the goals
   concrete.

2. **Write the version brief.**
   - **First release (v0.1.0):** the brief is the full project brief — interview-light here; the depth
     comes in Milestone 1. Record the version's goals and scope in `process/brief/brief.md` (or, if you
     prefer to keep v0.1.0 goals with the milestone, a short `process/v0.1.0-brief.md`).
   - **Later versions:** write `process/vX.Y.Z-brief.md` — a short brief that scopes the version as
     **requirement deltas** against the living spec (new `FR`/`NFR` numbers; amend-in-place for
     superseded ones), per the delta-pass model in `process/README.md`.

3. **Lay down the milestone table** in `process/milestone-plan.md` for this version:
   - **First release:** the full eight steps — brief, requirements, architecture & contract, wireframes
     (omit if no UI), test strategy, ticket generation, scaffolding, implementation.
   - **Later versions:** the shorter delta pass — version brief, requirement deltas, architecture/
     contract deltas, wireframe deltas (if UI), test-strategy delta + ticket generation, implementation.
   Number the milestones continuing from the previous version; set all to `Not started` (⬜); set the
   *Current position* to the first one.

4. **Commit** the brief and the milestone table together.

5. **Hand off.** Tell the user the version is scoped and the next step is `sfk-next-milestone` to work
   the first milestone. Do **not** start it yourself, and do **not** mark anything complete.

## Rules

- `sfk-version` defines scope and milestones only — it never authors a milestone's deliverable or
  writes code.
- Do not fork the spec per version: later versions evolve `process/` in place via deltas; the version
  brief and the milestone batch are the only point-in-time artefacts.
- Run `sfk-version` again only once the current version's milestones are all signed off.


## Thread name

Run this in its own thread. Cowork auto-titles a thread and **cannot rename it programmatically** —
only the user can. As your **first action**, suggest the name below and ask the user to rename this
thread to it. `PROJCODE` is the project code (the ticket prefix) recorded as `project_code` in
`process/.sfk/manifest.md`, set when the project was created with `sfk-init` (e.g. `/sfk-init HUE`).

**Suggested name:** `PROJCODE: <version> Planning`  (e.g. `HUE: v0.2.0 Planning`)
