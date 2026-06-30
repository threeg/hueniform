# SFK manifest

| | |
|---|---|
| **Document** | Spec-First Kit manifest |
| **Repository location** | `process/.sfk/manifest.md` |

The single source of truth for project identity and kit versioning. `sfk-init` sets `project_code`;
`sfk-update-process` reads and updates the version fields.

```yaml
project_code: ACME        # this project's code / ticket prefix (set by sfk-init, e.g. ACME)
                          # — also the thread-name prefix: "ACME init", "ACME: Architecture", "ACME Implementation"
kit_name: spec-first-starter-kit
kit_version: 1.0.0        # the version of the kit these files were shipped from
author: Gregg Seymour
applied_version: 1.0.0    # the kit version THIS project has been updated to (sfk-update-process bumps this)
```

- **`project_code`** is the short uppercase token passed to `sfk-init` (e.g. `/sfk-init ACME`). It is
  the ticket prefix (`ACME-001`) and the prefix every skill uses to suggest a thread name.
- **`kit_version`** is stamped by the kit when it ships. In a fresh checkout it equals the latest release.
- **`applied_version`** is what *this project* is on. `sfk-init` sets it equal to `kit_version`;
  `sfk-update-process` raises it as it applies newer changelog entries.
- When `applied_version` < a newer kit's `kit_version`, run `sfk-update-process` (see `CHANGELOG.md`).

> The *kit* version is independent of your software's release version (`v0.1.0`, `v0.2.0`, …), which
> is tracked in `process/milestone-plan.md`.
