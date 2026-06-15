---
id: HUE-006
title: Shared test fixtures and palette tables
type: task
status: done
milestone: 7
batch: tooling
layer: tooling
depends_on: [HUE-004, HUE-005]
implements: [FR-6]
tests_required: true
estimate: 5
---

## Background
The matcher, detection and API suites share fixtures the test strategy §11 defines: the synthetic image generator, its paired masks, invalid-upload fixtures, the boundary palette tables, and the MSW contract mirror. Building them once here keeps a requirements §1.4 change to a single fixture location. (Real photographs and the wardrobe factories arrive later — they need the model and the matcher value types respectively.)

## Technical requirements
- `backend/tests/fixtures/generate_images.py`: deterministically renders synthetic garment shapes (flat, two-colour block, thin-stripe minor colour) on plain contrasting backgrounds with Pillow; writes to a gitignored cache via a pytest session fixture (§11.1)
- `backend/tests/fixtures/masks/`: committed pre-computed alpha masks paired with the synthetic images, for the §6.2 injected-segmenter tests
- Invalid-upload fixtures: a tiny GIF (unsupported), a truncated JPEG (unreadable); the >20 MB blob is generated at test time, never committed (§11.1)
- `backend/tests/fixtures/palettes.py`: the §4.3–§4.5 boundary HSL tables and canonical values, defined once, pure data (no matcher import) (§11.3)
- `frontend/src/test/handlers.ts` (MSW) and `contract-examples.ts`: the contract's documented JSON bodies as typed constants — an executable mirror of `docs/03-api-contract.md` (§11.4)

## Definition of done (acceptance criteria)
- [x] Synthetic image generator produces deterministic images via a session fixture; masks committed and paired
- [x] Invalid-upload fixtures present (oversize generated at runtime, not committed)
- [x] `palettes.py` holds the boundary tables and canonical values as the single source for matcher and API tests
- [x] MSW handlers + contract-examples mirror the contract's documented bodies
- [x] Tests added/updated per test strategy §12.2 (or exemption stated below) and passing in `make test`
- [x] Relevant extra gate green where applicable ((none — default gate only))
- [x] Ticket status + notes updated in the same commit

## Tests / verification
The generator and palette tables are exercised by a self-check test (images render to expected sizes; every canonical value is well-formed HSL). They become load-bearing for HUE-009 (taxonomy), HUE-019 (pipeline) and the API conformance tests (§7.2). Proportion-summing-to-100 (FR-6) is asserted on the generator's known palettes.

## Notes
- 2026-06-15 — created
- 2026-06-15 — done. Three synthetic images (flat_red, two_colour_block, thin_stripe) rendered deterministically by Pillow via a session fixture; cached in gitignored `synthetic/`, three paired alpha masks committed to `masks/`. `invalid.gif` (32 bytes) and `truncated.jpg` (8 bytes) committed; oversize file generated at runtime. `palettes.py` holds all 19 family canonicals, neutral/chromatic boundary constants, and role/harmony tolerances — no matcher imports. `contract-examples.ts` and `handlers.ts` filled with typed constants and MSW handlers for all 14 contract endpoints. Added `pythonpath = ["."]` to pytest config so `tests.fixtures` is importable from conftest. 50 backend tests, 1 frontend test, all green.
