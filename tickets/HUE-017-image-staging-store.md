---
id: HUE-017
title: Image store, thumbnails and staging store
type: task
status: todo
milestone: 8
batch: storage
layer: storage
depends_on: [HUE-016]
implements: [FR-25, NFR-3]
tests_required: true
estimate: 5
---

## Background
Garment photographs, derived thumbnails and unconfirmed detections live on disk under `data/` (architecture §3.2, §3.3). Unconfirmed detections stay out of the database (FR-24) in a token-keyed staging store with a TTL and a startup sweep.

## Technical requirements
- Image store: save originals to `data/images/{id}.{ext}` preserving format (FR-25); thumbnail generation to `data/thumbnails/{id}.webp` (longest edge 320 px) with Pillow
- Staging store: write validated uploads to `data/staging/{token}.{ext}` plus a `{token}.json` sidecar holding the proposal, `fallback_used`, original content type and (for regenerations) the bound `garment_id` (architecture §3.3)
- UUID4 tokens with a 1-hour TTL; expired entries swept at startup and lazily on access
- A `move` operation promoting a staged image into `data/images/` (used by the confirm-save transaction)
- Backing up is copying `data/` (NFR-3); storage layer only (no matcher import)

## Definition of done (acceptance criteria)
- [ ] Originals stored preserving format; 320 px WebP thumbnails generated (FR-25)
- [ ] Staging writes file + sidecar; tokens carry a 1-hour TTL; startup + lazy sweep remove expired entries
- [ ] `move` promotes a staged image atomically; all state under `data/` (NFR-3)
- [ ] Tests added/updated per test strategy §12.2 (or exemption stated below) and passing in `make test`
- [ ] Relevant extra gate green where applicable ((none — default gate only))
- [ ] Ticket status + notes updated in the same commit

## Tests / verification
Lifecycle tests (§7.3): staging write creates file+sidecar and nothing in the DB; the sweep removes expired entries (clock seam / sidecar edit); thumbnail dimensions asserted; `move` relocates the file. File-presence assertions on disk.

## Notes
- 2026-06-15 — created
