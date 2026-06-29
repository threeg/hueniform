---
id: HUE-E02
title: Pure colour matcher
type: epic
status: done
milestone: 8
batch: matcher
layer: matcher
depends_on: []
implements: [FR-1, FR-2, FR-3, FR-4, FR-5, FR-6, FR-7, FR-8, FR-9, FR-10, FR-11, FR-12, FR-13, FR-14, FR-15, FR-16, FR-17, FR-18, FR-19, FR-20, FR-21, FR-22, FR-37, FR-38, FR-39, FR-40, FR-41, FR-42, FR-43, NFR-9]
tests_required: false
estimate: 8
---

## In plain English
The colour brain of the app: the self-contained rules that name colours, work out how garments' colours relate, decide which combinations look harmonious, rank them and explain the choices in plain language.

## Summary
Build the framework-independent colour matcher (NFR-9): the taxonomy, role derivation, harmony evaluation, slot rules, ranking and explanation — pure functions over frozen dataclasses, standard-library only, mirrored one-to-one by their test files. This is the heart of the product and the bulk of the test suite (test strategy §4).

## Scope
- **In scope:**
  - Named constants for every threshold (requirements §1.4)
  - RGB↔HSL, hue distance, circular mean
  - Family classification (taxonomy)
  - Colour roles and proportion rules
  - Harmony clustering and the ordered scheme test
  - Slot/anchor/layering/echo rules
  - Ranking, distinctness, variety and the fallback ladder
  - Explanation rendered solely from the EvaluationResult
- **Out of scope:**
  - Any I/O, framework or persistence (forbidden by the dependency rule and NFR-9)
  - Pixel clustering and segmentation (the detection epic)
  - Endpoint and UI surfaces (their own epics)

## Success criteria
All child tickets done; the matcher is standard-library-only (enforced by §5 allowlist); 100% line + branch coverage on `app/matcher/` holds; every numbered rule in requirements §2–§5 and §7 is unit-tested by the mirroring test file.

## Children
- HUE-007 — matcher.constants
- HUE-008 — matcher.colour
- HUE-009 — matcher.taxonomy
- HUE-010 — matcher.roles
- HUE-011 — matcher.harmony
- HUE-012 — Wardrobe and scenario fixtures
- HUE-013 — matcher.slots
- HUE-014 — matcher.ranking
- HUE-015 — matcher.explain

## References
- docs/02-requirements.md §1–§5, §7
- docs/03-architecture.md §2.2
- docs/05-test-strategy.md §4, §5

## Notes
- 2026-06-15 — created
- 2026-06-16 — done: all nine children complete (HUE-007–015 including HUE-012); 100% line+branch coverage on `app/matcher/` confirmed; std-library-only constraint verified by import-linter.
