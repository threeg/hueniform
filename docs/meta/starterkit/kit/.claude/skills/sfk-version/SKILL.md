---
name: sfk-version
description: Start a new version of the project. Takes a version number and its goals, writes the version brief, and lays down that version's milestone table in spec/milestone-plan.md. Use after sfk-init for the first release, and again at the start of each later version. Trigger on "start a version", "new version", "begin v0.2.0", "plan the next version", or "start v1".
---

# sfk-version — start a version

Use to open a version: the first release right after `sfk-init`, and each later version once the
previous one has shipped. It defines *what* the version delivers and lays out the milestones to get
there; it does **not** work the milestones (that is `sfk-next-milestone`).

> **In Cowork, do not commit.** Where a step below says to "commit" during a planning milestone,
> author and save the files and leave the changes for the **user** to review and commit — the
> assistant must not run `git commit`/`git add`/`git tag` in Cowork (see the project root `CLAUDE.md`,
> *Version control — who commits*). Automated committing applies only to the implementation milestone
> in Claude Code.

## Procedure

1. **Get the number and goals.** Ask the user for the version number and its
   goals — the capabilities or changes it should deliver. One round of questions to make the goals
   concrete.

2. **Write the version brief.**
   - **First release (whatever number the user gives):** the brief is the full project brief —
     interview-light here; the depth comes in Milestone 1. Record the version's goals and scope in
     `spec/brief/brief.md` (or a short `spec/<version>-brief.md`).
   - **Later versions:** write `spec/vX.Y.Z-brief.md` — a short brief that scopes the version as
     **requirement deltas** against the living spec (new `FR`/`NFR` numbers; amend-in-place for
     superseded ones), per the delta-pass model in `spec/README.md`.

3. **Lay down the milestone table** in `spec/milestone-plan.md` for this version:
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

- **No default version.** The project decides where its versioning starts (e.g. `v0.1.0` or
  `v1.0.0`). Never suggest or assume a default — use exactly the number the user provides.
- **Never edit `.sfk/`** — it is the kit's read-only source (templates, changelog, manifest).
- `sfk-version` defines scope and milestones only — it never authors a milestone's deliverable or
  writes code.
- Do not fork the spec per version: later versions evolve `spec/` in place via deltas; the version
  brief and the milestone batch are the only point-in-time artefacts.
- Run `sfk-version` again only once the current version's milestones are all signed off.
