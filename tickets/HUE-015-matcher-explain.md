---
id: HUE-015
title: Implement matcher.explain
type: task
status: done
milestone: 8
batch: matcher
layer: matcher
depends_on: [HUE-014]
implements: [FR-37, FR-38, NFR-9]
tests_required: true
estimate: 3
---

## In plain English
Turns the reasoning behind a suggested outfit into a plain-language explanation — naming the colour combination, each garment's part in it, and any matching accents — written from the real decision rather than a stock phrase.

## Background
Explanations must be generated from the actual evaluation, never canned (FR-38). `explain.render` takes an `EvaluationResult` and nothing else — the §5 dependency tests confirm it cannot reach the database, the request or any other source of text.

## Technical requirements
- `app/matcher/explain.py`: `render(result: EvaluationResult) -> str` as the module's only public entry point
- Names the matched FR-13 scheme, each slot's garment and its role, and each recorded echo (family + slots) — the FR-37 content
- Deterministic rendering (same result → same text)
- Standard library only (NFR-9); imports nothing outside the matcher

## Definition of done (acceptance criteria)
- [x] `render` names the scheme, every slot garment with its role, and every echo (FR-37)
- [x] Text is derived solely from the EvaluationResult; changing a field changes the text correspondingly (FR-38)
- [x] Rendering is deterministic; standard library only; passes the §5.2 allowlist
- [x] Tests added/updated per test strategy §12.2 (or exemption stated below) and passing in `make test`
- [x] Relevant extra gate green where applicable (`make test` matcher coverage gate: 100% line+branch on app/matcher/ (§12.3.3))
- [x] Ticket status + notes updated in the same commit

## Tests / verification
`matcher/test_explain.py` (§4.9): construction tests (hand-built results → substring checks for scheme/roles/echoes); covariance tests (change one field → text changes correspondingly, catching canned text); determinism property. The integration oracle in §7.4/§4.9.4 cross-checks the endpoint later.

## Notes
- 2026-06-15 — created
- 2026-06-15 — implemented. `app/matcher/explain.py` (new): `render(EvaluationResult) -> str` with three output shapes — sentinel (empty outfit, names constraining_slot), fallback (labelled "Neutral fallback"), and normal (scheme name, per-slot colour family + role label, minor echo families). Echo families re-derived from `qualify_echo_slot` over echo slots using `outfit` in the result. 536 tests; 100% line+branch on `app/matcher/`.
