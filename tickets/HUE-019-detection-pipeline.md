---
id: HUE-019
title: Detection pipeline orchestration
type: task
status: done
milestone: 8
batch: detection
layer: detection
depends_on: [HUE-018, HUE-006]
implements: [FR-26, FR-27]
tests_required: true
estimate: 5
---

## Background
The pipeline turns a photograph into a proposed palette (architecture §2.3): decode/validate, segment, sample masked pixels, cluster, merge, convert and classify, assembling 1–4 colours with proportions. It accepts an injectable segmenter and clusterer (a scaffolding requirement, test strategy §6.2) so the default gate tests it deterministically with committed masks and seeded KMeans.

## Technical requirements
- `app/detection/pipeline.py`: decode/validate with Pillow; **injectable segmenter and clusterer** seams (constructor/function parameters)
- Masked-pixel sampling (downsampled for NFR-4); scikit-learn KMeans for k=1…4; merge same-family clusters; convert centroids → HSL (`matcher.colour`) → family (`matcher.taxonomy`); assemble integer proportions (HUE-018)
- Fallback path (FR-27): segmentation raises or mask below minimum foreground → whole-image clustering with `fallback_used = true`
- Returns a proposal value (colours, fallback flag, image dimensions) — no persistence here
- Runs synchronously; imports only the permitted matcher submodules (contract 3)

## Definition of done (acceptance criteria)
- [x] Pipeline produces 1–4 classified colours with proportions summing to 100 from a masked image (FR-26)
- [x] Injected-mask path is deterministic with seeded KMeans; expected palettes within ±5 pp (§6.2)
- [x] Failure/low-foreground paths fall back to whole-image clustering with `fallback_used = true` (FR-27)
- [x] Tests added/updated per test strategy §12.2 (or exemption stated below) and passing in `make test`
- [x] Relevant extra gate green where applicable ((none — default gate only))
- [x] Ticket status + notes updated in the same commit

## Tests / verification
`detection/test_pipeline*.py` (§6.2): real orchestration with committed masks (HUE-006) replacing rembg and seeded KMeans; expected synthetic palettes within ±5 pp; a raising segmenter stub and a below-threshold mask both trigger the fallback. In the default gate (no real model).

## Notes
- 2026-06-15 — created
- 2026-06-16 — done: `app/detection/pipeline.py` with `ColourEntry`, `DetectionProposal`, `detect()`; injectable segmenter+clusterer seams; fallback path for raising segmenter and below-threshold coverage; distinct-colour cap on max_k prevents sklearn ConvergenceWarnings on flat synthetic images; 33 tests in `tests/detection/test_pipeline.py`; 647 passed, zero warnings.
