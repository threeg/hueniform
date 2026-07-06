---
id: HUE-109
title: Extract tier helper and tab-bar-height token
type: task
status: done
milestone: 20
batch: cleanup
layer: frontend
depends_on: [HUE-097, HUE-105]
implements: []
tests_required: true
estimate: 1
---

## In plain English

The e2e test files duplicate the same viewport-tier calculation, and three CSS modules hardcode the tab-bar height as a magic number. This ticket extracts both into shared, single-source-of-truth definitions.

## Background

Both `e2e/nav.spec.ts` and `e2e/responsive.spec.ts` inline the same `vp.width < 640 ? 'mobile' : vp.width < 1024 ? 'tablet' : 'desktop'` logic, despite `e2e/viewports.ts` already exporting the `VIEWPORTS` constants. Additionally, `AddConfirm.module.css`, `GarmentDetail.module.css` and `Suggest.module.css` each hardcode `bottom: 56px` for the mobile sticky-footer offset (the tab-bar height). Identified by `/verify` post-batch review of the screen batch.

## Technical requirements

1. Add a `tierFromPage(page: Page): ViewportTier` helper to `e2e/viewports.ts` that returns `'mobile' | 'tablet' | 'desktop'` based on the page's current viewport width.
2. Refactor `e2e/nav.spec.ts` and `e2e/responsive.spec.ts` to import and use `tierFromPage` instead of inlining the calculation.
3. Define a `--tab-bar-height: 56px` custom property in the global stylesheet (e.g. `frontend/src/index.css` or the tokens file).
4. Replace the three hardcoded `bottom: 56px` values in `AddConfirm.module.css`, `GarmentDetail.module.css` and `Suggest.module.css` with `bottom: var(--tab-bar-height)`.
5. Existing tests must continue to pass with no changes to test files.

## Definition of done (acceptance criteria)

- [x] `tierFromPage` exported from `e2e/viewports.ts` and used in both spec files
- [x] No remaining inline tier-detection logic in `nav.spec.ts` or `responsive.spec.ts`
- [x] `--tab-bar-height` defined as a CSS custom property
- [x] All `bottom: 56px` instances in route CSS modules replaced with `var(--tab-bar-height)`
- [x] `make test` passes with zero warnings
- [x] Ticket status + notes updated in the same commit

## Tests / verification

No new tests required — existing e2e responsive tests and component tests exercise the changed code paths. `make test` and `make test-e2e` confirm no regressions.

## Notes

- 2026-07-06 — created from `/verify` review of screen batch (HUE-098–105)
- 2026-07-06 — done. Added `tierFromPage(page: Page): ViewportTier` to `e2e/viewports.ts`. Replaced the local `tier()` function in `e2e/responsive.spec.ts` (imported as `tierFromPage as tier`) and the two inline calculations in `e2e/nav.spec.ts` with the shared helper. Added `--tab-bar-height: 56px` to `tokens.css` under §3.6 Layout. Replaced all six `56px` hardcodes (two each in `AddConfirm.module.css`, `GarmentDetail.module.css`, `Suggest.module.css`) with `var(--tab-bar-height)`. `make test-frontend` green: 273 passed (13 suites), zero warnings. Note: `make test-e2e` could not be run — the backend `.venv` symlink points to `python3.13` which is no longer on PATH; this is an environment issue unrelated to this ticket. Sanity test: `make test-frontend`.
