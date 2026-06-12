# Screen 1 — Upload & Detect

| | |
|---|---|
| **Route** | `/add` (sidebar: *Add garment*) |
| **Realises** | FR-23 (formats, size, picker + drag-and-drop), FR-24 (rejection), FR-26 (automatic detection), FR-27 (fallback warning handoff) |
| **API** | `POST /api/detections` (multipart, field `file`) |
| **Mockup** | [`01-upload-detect.html`](01-upload-detect.html) |

## Purpose

Entry point for inventory building. The user supplies one garment photograph; the application stages it, runs detection and hands the proposal to confirm-and-correct. Nothing touches the database from this screen (FR-24, contract §2.3).

## Layout

A single centred **drop zone** dominates the main column:

- Dashed border, hatched placeholder feel; headline "Drag a garment photograph here".
- A **Choose a file…** button as the equivalent file-picker path (FR-23 requires both).
- A format hint beneath: *JPEG, PNG or WebP, up to 20 MB* — surfacing the FR-23 limits before failure rather than after.
- A photography tip in small print (plain, contrasting background recommended), per the brief's risk note.

## Behaviour

1. Drop or pick a file → the SPA sends `POST /api/detections` with the file as multipart field `file`.
2. **201** → navigate to `/add/confirm` carrying the response (`token`, `expires_at`, `fallback_used`, `image`, `colours`). If `fallback_used` is `true`, confirm-and-correct opens with the FR-27 warning banner (shown in this mockup's final state and specified in screen 2).
3. **Error** → render the envelope's `message` in an error banner above the drop zone; the drop zone remains usable, no record exists (FR-24). Codes: `400 unsupported_format`, `400 unreadable_image`, `413 file_too_large`.

Multiple-file drops are reduced to the first file with a notice; the contract accepts exactly one `file` per detection.

## States (in mockup order)

| State | Trigger | Contract basis |
|---|---|---|
| **Default** | Page open | — |
| **Drag-over** | File held over the zone | UI affordance only |
| **Detecting** (loading) | Request in flight | NFR-4 bounds this under 5 s; zone is inert while detecting |
| **Rejected** (error) | Non-2xx response | `message` shown verbatim (FR-24); examples for all three codes |
| **Fallback handoff** | 201 with `fallback_used: true` | FR-27 — warning banner rendered on arrival at confirm-and-correct |

## Annotations (callouts in the mockup)

| # | Note |
|---|---|
| ① | Both input paths required by FR-23: drag-and-drop and file picker. |
| ② | Limits stated up front: JPEG/PNG/WebP, ≤ 20 MB (FR-23). |
| ③ | Error banner shows the envelope `message` verbatim — guaranteed plain language (FR-24, contract §1.3). No partial record exists; retry is immediate. |
| ④ | Detection runs synchronously within the request (architecture §2.3); completes in < 5 s (NFR-4). |
| ⑤ | `fallback_used: true` → amber warning that colours may include background (FR-27), displayed atop confirm-and-correct. |
