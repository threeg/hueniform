# SFK manifest (read-only)

| | |
|---|---|
| **Document** | Spec-First Kit identity |
| **Repository location** | `process/.sfk/manifest.md` |

Identity of the kit these files shipped from. **Read-only** — nothing in `process/.sfk/` is edited by
the authoring skills; only `sfk-update-process` refreshes this folder from a newer kit.

```yaml
kit_name: spec-first-starter-kit
kit_version: 1.0.0        # the kit version these files shipped from
author: Gregg Seymour
```

- The **project's own state** — its project code and the kit version it has applied — is **not** kept
  here. It lives in the project-owned root `CLAUDE.md` (see its *Project & kit* section), so this
  folder stays off-limits to the day-to-day lifecycle.
- `sfk-update-process` compares the project's *applied* kit version (in root `CLAUDE.md`) against this
  `kit_version` to decide what changelog deltas to apply (see `CHANGELOG.md`).

> The *kit* version is independent of your software's release version (`v0.1.0`, …), tracked in
> `process/milestone-plan.md`.
