---
id: HUE-033
title: Upload and detect screen
type: story
status: todo
milestone: 8
batch: frontend
layer: frontend
depends_on: [HUE-032]
implements: [FR-23, FR-24, FR-26, FR-27]
tests_required: true
estimate: 3
---

## User story
As the owner
I want to upload a garment photograph and have its colours detected automatically
so that I can start adding a garment to my wardrobe.

## Acceptance criteria

**Scenario 1: Upload a valid photo**
- Given I am on the Add-garment screen
- When I pick or drag-and-drop a JPEG/PNG/WebP under 20 MB
- Then the image is sent to `POST /api/detections` and a detecting state is shown
- And on success I am taken to confirm-and-correct with the proposed palette

**Scenario 2: Reject an invalid upload**
- Given I am on the Add-garment screen
- When I upload an unsupported format, an oversize file, or an unreadable image
- Then the server's plain-language `message` is shown in the error banner (FR-24)
- And no confirm-and-correct screen is entered

**Scenario 3: Detection fell back to whole image**
- Given the garment could not be isolated
- When detection returns `fallback_used: true`
- Then the confirm screen shows the amber fallback warning that results may include background colour (FR-27)

## Technical approach
- Frontend `frontend/src/` upload screen using the API client (HUE-032)
- `POST /api/detections` (contract §2.3); file picker + drag-and-drop with a drag-over highlight (FR-23)
- Render the three rejection codes' messages via the error banner; pass the proposal + `fallback_used` to confirm-and-correct

## Design references
- Wireframe: docs/04-wireframes/01-upload-detect.md (states: default/empty, detecting, rejection ×3, drag-over)

## Tests
- `frontend/src/**/UploadDetect.test.tsx` (§10.1): rejection states render the server `message` (FR-24); the `fallback_used` warning banner (FR-27); valid upload posts to `/api/detections`
- FR-23/FR-24/FR-26/FR-27 via MSW handlers (HUE-006); covered end-to-end by E2E journey 1 (HUE-040, §9)

## Definition of done
- [ ] Acceptance criteria met
- [ ] Tests added/updated per test strategy §12.2 and passing in `make test`
- [ ] Matcher-touching work: 100% line+branch on app/matcher/ holds (§12.3.3)
- [ ] Detection-touching work: `make test-model` passes (§12.3.4)
- [ ] Evaluation/inventory-perf-touching work: `make test-perf` passes (§12.3.5)
- [ ] User-flow-touching work: `make test-e2e` passes (§12.3.6)
- [ ] Ticket status + notes updated in the same commit (§12.3.7)

## Notes
- 2026-06-15 — created
