# <PROJECT> — Test Strategy

| | |
|---|---|
| **Document** | Test strategy |
| **Repository location** | `docs/test-strategy.md` |
| **Status** | Binding specification |

> **Purpose.** This document is written *before* implementation so tests express the **spec**, not
> the code. It fixes the frameworks, the test pyramid, the gates, the fixtures, and the **definition
> of done**. The build-time gates defined here are what make autonomous, ticket-by-ticket
> implementation safe.

---

## 1. Principles

1. **Test-first (red-green) for deterministic and contract-pinned layers.** For the pure core, the
   domain rules, and the interface contract shapes: write the failing test from the requirement or
   the contract, confirm it fails *for the right reason*, then implement to green.
2. **Characterisation (after) tests for probabilistic / external layers.** Where output is
   non-deterministic (models, network, randomness), pin behaviour with seeded or recorded tests and
   assert *properties*, not exact values. Make randomness **seedable** so the layer stays testable.
3. **Tests live in the same commit as the behaviour they cover** (see §12).
4. **Every numbered requirement (`FR`/`NFR`) is covered by at least one test** (§14 traceability).

---

## 2. Frameworks, tooling and invocation

### 2.1 Tooling choices

> The test runner(s), assertion/mocking libraries, coverage tool, and any boundary-enforcement tool
> (import-linter / dependency cruiser) — per layer. Pin them.

| Layer | Framework | Notes |
|-------|-----------|-------|
| core / domain | <…> | <…> |
| services / interface | <…> | <…> |
| frontend / client | <…> | <…> |
| end-to-end | <…> | <…> |

### 2.2 Invocation — the command pattern

> Wrap every test mode behind a single command runner (a `Makefile`, `just`, or npm scripts) so the
> agent invokes tests the same way every time. Define a fast **default gate** plus heavier gates run
> only for the ticket types that need them.

| Command | What it runs | When |
|---------|-------------|------|
| `<make test>` | **the default gate** — unit + integration + boundary checks + core coverage gate | every ticket |
| `<make test-<heavy-A>>` | <e.g. real-model / external-integration suite> | tickets touching that layer |
| `<make test-perf>` | performance/timing at target scale | suggestion-/query-touching tickets |
| `<make test-e2e>` | end-to-end smoke journeys | user-flow tickets |
| `<make test-all>` | everything | milestone completion |

### 2.3 Coverage policy

> Where coverage is gated and to what level. Recommended: a **100% line+branch gate on the pure
> core** (it is pure, so it is achievable and meaningful), and a softer or no numeric gate elsewhere.

---

## 3. The test pyramid

> How effort is distributed: many fast unit tests over the core and domain; fewer integration tests
> over services and the interface; a thin layer of end-to-end smoke journeys. State what each tier
> is responsible for proving.

---

## 4. The core in depth

> The pure core deserves its own section: boundary-value tests on every threshold from requirements
> §2–§5, the constants drift-guard, and **golden-file snapshot baselines taken before any risky
> refactor** so a behavioural change shows up in the diff. List the test files and what each pins.

### 4.x The golden-file snapshot baseline

> Before refactoring deterministic code, commit snapshots of known input → current output. Any
> change to output then requires an explicit snapshot update, making regressions visible in review.

---

## 5. Enforcing the dependency rule

> How the architecture's layer rule (architecture §2.1) is enforced in tests: the import-linter
> contracts, the standard-library-only allowlist for the core, and that a violation fails the
> default gate.

---

## 6. <Probabilistic / external-dependent layer> testing

> For any layer with non-deterministic or external behaviour: the pure helpers (unit-tested in the
> default gate), the integration with injected seams (in the default gate), and the real
> dependency suite behind its own marker/command (not in the default gate). Delete if not
> applicable.

---

## 7. Interface and integration testing

> The harness for exercising the interface layer, **contract conformance** (responses match
> `03-api-contract.md` exactly), lifecycle/persistence tests, and the error-envelope tests.

---

## 8. Non-determinism and performance

> How to assert behaviour involving randomness without flaky tests (fixed seeds), and the
> performance suite: the target scale, the budget (from the NFRs), and what is measured.

---

## 9. End-to-end smoke suite

> The handful of full-journey tests that prove the assembled system works, the browsers/environments
> covered, and which tickets must pass them.

---

## 10. Frontend / client testing

> Component tests (what they cover) and explicitly what they do **not** cover (left to e2e). Delete
> for non-UI projects.

---

## 11. Test data and fixtures

> Where fixtures live and how they are built: factories, shared tables, sample inputs, snapshot and
> migration fixtures. Centralise them so tests stay DRY.

---

## 12. Conventions and definition of done

### 12.1 Layout and naming

> Where test files live relative to the code, and the naming convention.

### 12.2 When tickets must include tests

> The rule: any ticket creating or changing numbered-requirement behaviour ships its tests **in the
> same commit**. The only `tests_required: false` exemptions are documentation-only, pure-styling,
> and build-plumbing tickets, which must state the exemption in the body.

### 12.3 Definition of done — implementation tickets

> The binding checklist a ticket must satisfy to be `done`. Keep this in sync with the root
> `CLAUDE.md` and the ticket template. At minimum:

- [ ] The default gate (`<make test>`) passes **with zero warnings**.
- [ ] New/changed numbered-requirement behaviour has tests in the same commit (§12.2).
- [ ] The core coverage gate holds for core-touching work (§2.3).
- [ ] The relevant heavier gate passes where the ticket says so (`<test-heavy>` / `<test-perf>` / `<test-e2e>`).
- [ ] The ticket's `status` + `## Notes` and its `BOARD.md` row are updated in **that same commit**.
- [ ] A completion report (summary + one-line sanity test; QA steps for UI tickets) is recorded.

---

## 13. Decisions log

> Dated record of testing decisions (framework choices, coverage levels, what is deliberately not
> tested and why). Append per version.

- **<DATE>** — <decision and rationale>.

---

## 14. Traceability — requirements to tests

> A table mapping each `FR`/`NFR` to the test(s) that cover it. The mechanical guarantee that the
> spec is exercised. Generate or maintain this as part of ticket work.

| Requirement | Covered by |
|-------------|-----------|
| FR-1 | <test file / name> |
| NFR-1 | <…> |
