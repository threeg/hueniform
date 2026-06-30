---
name: sfk-update-process
description: Pull a newer version of the Spec-First Kit into an existing project without disturbing the project's filled-in docs. Compares kit versions, refreshes kit-owned files and the pristine template mirror, and applies changelog deltas to the living spec — interviewing the user where a change needs input. Trigger on "update the process", "update the kit", "pull the latest starter kit", "upgrade sfk", or "apply the new kit version".
---

# sfk-update-process — bring a newer kit version into this project

Use when a newer version of the kit has shipped and you want its improvements in an existing project.
You apply the *method's* updates to the project's living spec **without overwriting the user's
content**. This is a semantic migration, not a blind file copy — a blind copy would clobber filled-in
docs, because the kit also ships working-named files for fresh inits.

## Inputs you need

- **This project**, with `process/.sfk/manifest.md` recording its `applied_version`.
- **The newer kit**, available somewhere readable (a clone of the kit repo, or a temp folder the user
  points you at). You will read its `process/.sfk/manifest.md` (its `kit_version`), its
  `process/.sfk/CHANGELOG.md`, its `process/.sfk/templates/` mirror, and its kit-owned files.

If you cannot see the newer kit, ask the user where it is before proceeding.

## Procedure

1. **Compare versions.** Read the project's `applied_version` and the newer kit's `kit_version`. If
   they are equal, report "already up to date" and stop. If the project's is higher, stop and ask
   (something is off).

2. **Collect the deltas.** From the newer kit's `CHANGELOG.md`, take every entry with a version greater
   than the project's `applied_version`, oldest-to-newest. The changelog is your migration script:
   each entry carries an **Apply** note (*refresh* / *add* / *amend* / *interview*).

3. **Refresh kit-owned files.** Overwrite the files the user does not edit, from the newer kit: the
   skills in `.claude/skills/`, `process/README.md`, and the `process/.sfk/` machinery
   (`manifest.md` body, `CHANGELOG.md`). Before overwriting any kit-owned file, check whether the user
   has locally modified it (compare against the old pristine where one exists); if so, show the
   difference and confirm rather than silently discarding their change.

4. **Refresh the pristine mirror.** Copy the newer kit's `process/.sfk/templates/` over the project's,
   but **keep the previous mirror** available for the three-way comparison in step 5 (e.g. read the old
   one from version control, or copy it aside first).

5. **Apply each delta to the living docs.** For every changed living file, reason three ways — the
   user's working file vs the *old* pristine mirror vs the *new* pristine mirror — and apply only the
   kit's change, preserving the user's content:
   - **add:** insert the new section/heading where the new template has it; leave the body empty (or
     interview the user if they want it filled now).
   - **amend:** apply the wording/guidance change; keep any user edits in that section.
   - **refresh:** for a living file the changelog says to replace wholesale, confirm with the user first.
   - **interview:** when the change needs a decision or content, ask the user, then write their answer.
   Never overwrite filled-in content, and never touch generated artefacts (individual tickets, code).

6. **Offer optional backfills.** When a template gained a section that existing artefacts could also
   carry (e.g. the ticket template gained `## In plain English`), *offer* — do not force — to backfill
   it into the existing instances, interviewing per item for the wording. Skip if the user declines.

7. **Bump and commit.** Set `applied_version` in `process/.sfk/manifest.md` to the newer kit's
   `kit_version`. Commit the refresh + applied deltas together, e.g.
   `process: update kit to vX.Y.Z`. Summarise for the user what changed, what you interviewed them
   about, and anything you deliberately left for them.

## Rules

- Never overwrite the user's filled-in living docs or their code; apply only the kit's deltas.
- Kit-owned files are refreshed wholesale, but warn before discarding any local modification to one.
- The CHANGELOG is authoritative for *what* changed; the pristine mirrors are authoritative for the
  *exact* before/after text. Use both.
- Do not mark milestones complete or alter project status — this skill changes the *method*, not the
  *project's* progress.


## Thread name

Run this in its own thread. Cowork auto-titles a thread and **cannot rename it programmatically** —
only the user can. As your **first action**, suggest the name below and ask the user to rename this
thread to it. `PROJCODE` is the project code (the ticket prefix) recorded as `project_code` in
`process/.sfk/manifest.md`, set when the project was created with `sfk-init` (e.g. `/sfk-init ACME`).

**Suggested name:** `PROJCODE: Kit Update <version>`  (e.g. `ACME: Kit Update v1.1.0`)
