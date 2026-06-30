# <Layer> layer — instructions template

> **Per-layer instructions.** Copy this file into each layer's source directory (e.g.
> `<code>/core/CLAUDE.md`, `<code>/services/CLAUDE.md`, `<code>/interface/CLAUDE.md`) and tailor it.
> It loads automatically only when the agent touches files in that directory, keeping the root
> `CLAUDE.md` slim. Put here the patterns and pitfalls **specific to this layer** — not rules that
> apply everywhere.

This describes the `<layer>` layer: <one sentence on its responsibility and where it sits in the
dependency rule>.

## Rules for this layer

> The binding constraints. Examples for an innermost "core" layer (adapt or replace per layer):

- **What it may import.** <e.g. standard library only — enforced by an import contract and an
  allowlist test; breaking it fails the default gate.>
- **Purity / state.** <e.g. pure functions over immutable data; no I/O, no side effects.>
- **Coverage gate.** <e.g. 100% line + branch on this directory; no exceptions for core-touching
  tickets.>
- **Constants.** <e.g. numeric thresholds are contractual; reference the named constant, never a
  magic number.>
- **Tests:** `<where this layer's tests live>`.

## Patterns

> Reusable patterns the agent should follow in this layer — the idiomatic way to add a new module,
> wire a new endpoint, register a new service, etc.

## Pitfalls (write these as you hit them)

> When you hit a non-obvious failure mode **twice**, record it here with the correct snippet. This is
> the cheapest place to stop a recurring mistake. Examples of the kind of thing that belongs here:
> a fixture teardown that otherwise leaks a warning and fails the zero-warnings gate; an API quirk
> that causes a silent wrong-format return; an ordering dependency between setup steps.

- <pitfall> → <the correct approach / snippet>
