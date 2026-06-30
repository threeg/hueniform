# SFK changelog

Changes to the Spec-First Kit, newest first. Each entry is the migration script `sfk-update-process`
follows: it applies every entry newer than a project's `applied_version` (see `manifest.md`).

For each change, the **Apply** note tells the update skill how to bring it into an existing project:
*refresh* (overwrite the kit-owned file), *add* (insert a new section/heading into a living file),
*amend* (apply a wording/guidance change), or *interview* (ask the user, because content is needed).

---

## v1.0.0 — initial release

Baseline. A project bootstrapped at v1.0.0 needs no migration.

The kit provides:

- The eight-step spec-first method and the milestone lifecycle (`process/README.md`).
- The living spec templates under `process/` (brief, requirements, architecture + api-contract,
  wireframes, test-strategy), the milestone plan, and the ticket system (BOARD, CONVENTIONS,
  TICKET-TEMPLATE with an `## In plain English` section, tickets/CLAUDE.md).
- A lean root `CLAUDE.md` and the per-layer `CLAUDE.md` template.
- The workflow skills: `sfk-init`, `sfk-version`, `sfk-next-milestone`, `sfk-signoff`,
  `sfk-next-ticket`, `sfk-verify`, `sfk-update-process`.
- The optional meta loop (`process/addons/meta-loop/`).
- Versioning machinery (`process/.sfk/`).

**Apply:** n/a (baseline).

<!-- Template for future entries:

## vX.Y.Z — <short title>

- <change one>. **Apply:** add — insert `## <heading>` into `process/<file>` after `<anchor>`; leave its body for the user to fill (interview if they want it filled now).
- <change two>. **Apply:** refresh — overwrite `<kit-owned file>`.
- <change three>. **Apply:** amend — reword `<section>` in `process/<file>` to match the new pristine template; preserve any user edits.
-->
