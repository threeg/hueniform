---
id: HUE-027
title: Detections endpoints
type: task
status: todo
milestone: 8
batch: api
layer: api
depends_on: [HUE-025, HUE-021]
implements: [FR-23, FR-24, FR-26, FR-27, FR-28]
tests_required: true
estimate: 5
---

## Background
Upload and detect (contract §2.3–§2.4): validate the multipart upload (format, 20 MB), run detection via the service, return the proposal for confirm-and-correct, and serve the staged image for preview — writing nothing to the database (FR-24).

## Technical requirements
- `POST /api/detections` (multipart `file`, JPEG/PNG/WebP ≤20 MB): validate format/size at the boundary (FR-23); call the detection service; return token, expiry, `fallback_used`, image info, colours (contract §2.3)
- `GET /api/detections/{token}/image`: the staged image bytes for the preview; `404 detection_not_found` if unknown/expired (contract §2.4)
- Errors: `400 unsupported_format`, `400 unreadable_image`, `413 file_too_large` (contract §2.3)
- Nothing written to the database (FR-24); `api` → `services` only

## Definition of done (acceptance criteria)
- [ ] Valid upload returns the §2.3 proposal; rejections return the documented plain-language errors with no DB write (FR-24)
- [ ] `fallback_used` surfaced for the FR-27 warning; staged image served; expired token → 404
- [ ] Format/size validated at the boundary (FR-23)
- [ ] Tests added/updated per test strategy §12.2 (or exemption stated below) and passing in `make test`
- [ ] Relevant extra gate green where applicable ((none — default gate only))
- [ ] Ticket status + notes updated in the same commit

## Tests / verification
`api/test_detections.py` (§7.2, §7.3): the §2.3 success body; `400 unsupported_format`/`unreadable_image` (GIF + truncated JPEG fixtures), `413 file_too_large` (runtime-generated blob); staged-image serving and expiry 404; DB empty after upload.

## Notes
- 2026-06-15 — created
