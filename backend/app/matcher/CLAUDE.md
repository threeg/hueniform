# Matcher layer

The matcher is the innermost layer. It contains pure colour-theory logic and must remain
completely framework-free.

- **Standard library only (NFR-9).** No third-party imports. This is enforced by an
  import-linter contract and a std-library allowlist test; breaking it fails `make test`.
- **Pure functions over frozen dataclasses.** No mutable state, no I/O, no side effects.
  Every public function takes immutable inputs and returns immutable outputs.
- **100% line + branch coverage gate.** `make test` enforces this for `app/matcher/`.
  Matcher-touching tickets must hold this gate — no exceptions.
- **Constants from `matcher.constants`.** Numeric thresholds are contractual (requirements
  §1.4). Never use magic numbers; always reference the named constant.
- **Tests:** `backend/tests/matcher/`
