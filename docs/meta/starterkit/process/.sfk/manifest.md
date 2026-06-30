# SFK manifest

| | |
|---|---|
| **Document** | Spec-First Kit manifest |
| **Repository location** | `process/.sfk/manifest.md` |

The single source of truth for kit versioning. `sfk-update-process` reads and updates this file.

```yaml
kit_name: spec-first-starter-kit
kit_version: 1.0.0        # the version of the kit these files were shipped from
author: Gregg Seymour
applied_version: 1.0.0    # the kit version THIS project has been updated to (sfk-update-process bumps this)
```

- **`kit_version`** is stamped by the kit when it ships. In a fresh checkout of the kit it equals the
  latest release.
- **`applied_version`** is what *this project* is currently on. `sfk-init` sets it equal to
  `kit_version` at bootstrap. `sfk-update-process` raises it as it applies newer changelog entries.
- When `applied_version` < the newer kit's `kit_version`, there are updates to apply: run
  `sfk-update-process` (see `process/.sfk/CHANGELOG.md`).

> This is a *kit* version, independent of your software's release version (`v0.1.0`, `v0.2.0`, …),
> which is tracked in `process/milestone-plan.md`.
