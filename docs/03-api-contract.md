# Hueniform — HTTP API Contract

| | |
|---|---|
| **Document** | API contract (Milestone 3) |
| **Status** | Draft for approval |
| **Date** | 12 June 2026 |
| **Source** | `docs/requirements.md` (FR/NFR identifiers cited throughout) and `docs/architecture.md` |
| **Repository location** | `docs/api-contract.md` |

This document is the authoritative contract between frontend and backend; each may be built independently against it. FastAPI's generated OpenAPI is a convenience mirror — where they disagree, this document wins and the code is wrong.

---

## 1. Conventions

1. Base URL `http://127.0.0.1:8000`; all endpoints are prefixed `/api`. Image endpoints return binary bodies; everything else is `application/json` (UTF-8).
2. Identifiers are UUID4 strings. Timestamps are ISO 8601 UTC (e.g. `"2026-06-12T14:03:00Z"`).
3. Garment **types** (FR-16): `top`, `bottom`, `jersey`, `jacket`, `socks`, `shoes`, `hat`, `accessory`. Optional **slot keys** in requests use the same identifiers; the slot the brief calls "accessories" is keyed `accessory` to match its garment type.
4. **Scheme** names (FR-13): `neutral-based`, `monochromatic`, `analogous`, `complementary`, `triadic`.
5. Colour `family` values are exactly the names in requirements §2: `Black`, `White`, `Grey`, `Navy`, `Denim`, `Brown`, `Beige/Tan`, `Red`, `Orange`, `Yellow`, `Chartreuse`, `Green`, `Mint`, `Teal`, `Azure`, `Blue`, `Violet`, `Magenta`, `Pink`.
6. The server **always derives `family` from submitted HSL** (FR-1); a client-supplied family is never trusted and never sent on input.

### 1.1 Colour objects

**`ColourOut`** (responses) — `hex` is derived from the measured HSL so the UI can render the actual colour's swatch (FR-5).

```json
{ "h": 207.4, "s": 64.0, "l": 47.0, "family": "Azure", "neutral": false, "hex": "#2B7FC4", "proportion": 62 }
```

**`ColourIn`** (requests) — measured values from a proposal, or canonical values (from `GET /api/taxonomy`) for a manually added colour (FR-29).

```json
{ "h": 207.4, "s": 64.0, "l": 47.0, "proportion": 62 }
```

Validation: `0 ≤ h < 360`, `0 ≤ s ≤ 100`, `0 ≤ l ≤ 100`; `proportion` an integer `1–100`; a palette is 1–4 colours (FR-6) whose proportions sum to **exactly 100** — the UI normalises on save (FR-29), the server only validates, answering `422` otherwise.

### 1.2 Garment objects

**`GarmentSummary`** (inventory lists, suggestion slots — FR-35, FR-37):

```json
{
  "id": "0b6c4d1e-7a2f-4f7e-9d2a-1c3e5f7a9b0c",
  "type": "jersey",
  "colours": [ { "h": 174.0, "s": 58.0, "l": 41.0, "family": "Teal", "neutral": false, "hex": "#2CADA0", "proportion": 80 },
               { "h": 28.0, "s": 85.0, "l": 55.0, "family": "Orange", "neutral": false, "hex": "#EE8225", "proportion": 20 } ],
  "thumbnail_url": "/api/garments/0b6c4d1e-7a2f-4f7e-9d2a-1c3e5f7a9b0c/thumbnail"
}
```

**`Garment`** (detail) — `GarmentSummary` plus `"image_url"`, `"created_at"`, `"regenerated_at"` (nullable).

### 1.3 Error envelope and status codes

Every non-2xx response carries:

```json
{ "error": { "code": "unsupported_format", "message": "Only JPEG, PNG and WebP photographs are accepted.", "details": {} } }
```

`message` is always plain language fit to show the user (FR-24, FR-36, FR-43). `code` values are stable machine identifiers listed per endpoint.

| Status | Meaning here |
|---|---|
| 200 / 201 / 204 | Success / created / deleted-no-body |
| 400 | Malformed request or unreadable/unsupported upload |
| 404 | Unknown garment, or unknown/expired token |
| 409 | Request conflicts with state (empty requested slot; invalid regeneration token) |
| 413 | Upload exceeds 20 MB |
| 422 | Body failed validation (codes include the field detail in `details`) |
| 500 | Unexpected server error (`code: "internal_error"`) |

---

## 2. Endpoints

### 2.1 `GET /api/health`

Readiness probe used by the launch script before printing the URL (NFR-2). **200**: `{ "status": "ok", "version": "0.1.0" }`

### 2.2 `GET /api/taxonomy`

The palette taxonomy for UI use: family pickers for manual colour adds (FR-29) and legend display (FR-5). `canonical` is the HSL stored when the user adds a colour by family alone; each canonical value classifies into its own family.

**200:**

```json
{ "families": [
    { "name": "Navy",  "neutral": true,  "canonical": { "h": 230.0, "s": 40.0, "l": 18.0 } },
    { "name": "Teal",  "neutral": false, "representative_hue": 180.0, "hue_arc": [165.0, 195.0],
      "canonical": { "h": 180.0, "s": 70.0, "l": 50.0 } }
] }
```

(`representative_hue` and `hue_arc` are present only on chromatic families.)

### 2.3 `POST /api/detections` — upload and detect (FR-23, FR-24, FR-26, FR-27, FR-28)

`multipart/form-data` with one field `file` (JPEG, PNG or WebP, ≤ 20 MB). Stages the image, runs detection, returns the proposal for confirm-and-correct. Nothing is written to the database (FR-24).

**201:**

```json
{
  "token": "3f9d2c8e-1b4a-4c6d-8e2f-7a9b0c1d2e3f",
  "expires_at": "2026-06-12T15:03:00Z",
  "fallback_used": false,
  "image": { "url": "/api/detections/3f9d2c8e-1b4a-4c6d-8e2f-7a9b0c1d2e3f/image", "width": 1600, "height": 1200 },
  "colours": [
    { "h": 174.0, "s": 58.0, "l": 41.0, "family": "Teal",   "neutral": false, "hex": "#2CADA0", "proportion": 80 },
    { "h": 28.0,  "s": 85.0, "l": 55.0, "family": "Orange", "neutral": false, "hex": "#EE8225", "proportion": 20 }
  ]
}
```

`fallback_used: true` signals whole-image clustering after failed isolation; the UI must surface the FR-27 warning that results may include background colour.

**Errors:** `400 unsupported_format`, `400 unreadable_image`, `413 file_too_large`.

### 2.4 `GET /api/detections/{token}/image`

The staged image, for the confirmation screen preview. **200** image bytes (original content type); **404 `detection_not_found`** if unknown or expired.

### 2.5 `POST /api/garments` — confirm and save (FR-6, FR-25, FR-29, FR-30, FR-31)

```json
{
  "detection_token": "3f9d2c8e-1b4a-4c6d-8e2f-7a9b0c1d2e3f",
  "type": "jersey",
  "colours": [ { "h": 174.0, "s": 58.0, "l": 41.0, "proportion": 80 },
               { "h": 28.0,  "s": 85.0, "l": 55.0, "proportion": 20 } ]
}
```

Atomically moves the staged image into permanent storage, generates the thumbnail and creates the garment. The token is consumed.

**201:** the full `Garment`. **Errors:** `404 detection_not_found` (unknown, expired or consumed token); `422 invalid_palette` (count outside 1–4, proportions not summing to 100, values out of range); `422 invalid_type`.

### 2.6 `GET /api/garments` — inventory (FR-35, NFR-6)

Query parameters, all optional and combinable as AND: `type` (one FR-16 value), `family` (one §1 family name; matches a garment containing that family in **any** role), `limit` / `offset` (defaults 500 / 0 — a full wardrobe fits one response).

**200:**

```json
{ "garments": [ GarmentSummary ], "total": 137 }
```

**Errors:** `422 invalid_filter` for unknown `type` or `family` values.

### 2.7 `GET /api/garments/{id}`

**200:** the full `Garment`. **404 `garment_not_found`**.

### 2.8 `GET /api/garments/{id}/image` · `GET /api/garments/{id}/thumbnail` (FR-25, FR-35)

**200** binary image (original format / WebP thumbnail). **404 `garment_not_found`**.

### 2.9 `POST /api/garments/{id}/regenerate` (FR-26, FR-33)

No body. Re-runs detection on the stored photograph and returns a proposal in exactly the §2.3 response shape, plus `"garment_id"` and with `token` acting as the **regeneration token** required by §2.10. The stored image and record are untouched until confirmation.

**200** as §2.3 + `garment_id`; **404 `garment_not_found`**.

### 2.10 `PUT /api/garments/{id}` — confirm regeneration (FR-32, FR-33)

```json
{
  "regeneration_token": "9c1e7a3b-5d2f-4e8a-b6c0-2f4d6e8a0b1c",
  "type": "jersey",
  "colours": [ { "h": 176.0, "s": 60.0, "l": 40.0, "proportion": 100 } ]
}
```

Replaces the palette and type **in place** — same `id`, same photograph — so existing references remain valid (FR-33). The token requirement is the FR-32 enforcement: this endpoint only completes a regeneration; there is no field-editing path.

**200:** the updated `Garment` (`regenerated_at` set). **Errors:** `404 garment_not_found`; `409 invalid_regeneration_token` (absent, expired, consumed, or bound to a different garment); `422` as §2.5.

### 2.11 `DELETE /api/garments/{id}` (FR-34)

Removes the record, photograph and thumbnail. The confirmation step is a UI responsibility. **204** no body; **404 `garment_not_found`**.

### 2.12 `POST /api/suggestions` — outfit request (FR-36–FR-43, NFR-5)

```json
{ "include": { "jersey": true, "jacket": false, "hat": true, "accessory": false } }
```

Required slots (top, bottom, socks, shoes) are always included (FR-17); `include` selects the optional slots. Omitted keys default to `false`.

**200 — combinations found** (up to 3, ranked best-first, all distinct — FR-39, FR-40, FR-41):

```json
{
  "combinations": [
    {
      "rank": 1,
      "scheme": "analogous",
      "fallback": false,
      "slots": {
        "top":    GarmentSummary,
        "bottom": GarmentSummary,
        "jersey": GarmentSummary,
        "socks":  GarmentSummary,
        "shoes":  GarmentSummary,
        "hat":    GarmentSummary
      },
      "echoes": [ { "family": "Orange", "from_slot": "hat", "to_slot": "socks" } ],
      "explanation": "Analogous scheme: teal jersey and azure trousers sit side by side on the wheel; navy shoes and grey socks are neutrals; the orange cap echoes the stripe in the socks."
    }
  ]
}
```

`explanation` is rendered from the actual evaluation result (FR-38); `scheme` names the FR-13 match; `echoes` lists the FR-11 minor-colour echoes credited in ranking. `fallback: true` marks a neutral-based fallback combination (FR-43a) — the UI must label these.

**200 — no combination possible** (FR-43b):

```json
{
  "combinations": [],
  "explanation": "No harmonious outfit was found: no jersey in the wardrobe is compatible with any bottom under any scheme.",
  "hint": "The jersey slot most constrained the search — try the request without it, or add a neutral jersey."
}
```

**409 — fail fast, empty slot** (FR-36):

```json
{ "error": { "code": "empty_slots",
             "message": "You have no garments for the requested slot(s): jersey.",
             "details": { "empty_slots": ["jersey"] } } }
```

**Other errors:** `422 invalid_request` for unknown slot keys.

Repeated identical requests may legitimately return different results (FR-42). Responses return within NFR-5's 2-second bound at 500 garments.

---

## 3. Traceability

| Requirement | Endpoint(s) |
|---|---|
| FR-1–FR-5 (taxonomy) | Server-side family derivation everywhere; `GET /api/taxonomy` |
| FR-6 (1–4 colours, sum 100) | §2.3 response; §2.5/§2.10 validation |
| FR-23, FR-24 (upload, rejection) | §2.3 |
| FR-25 (stored photograph) | §2.5, §2.8, §2.9 |
| FR-26, FR-27 (detection, fallback) | §2.3, §2.9 (`fallback_used`) |
| FR-28–FR-31 (confirm-and-correct, type) | §2.3 → §2.5; §2.2 (canonical HSL for manual adds) |
| FR-32, FR-33 (no field editing; regenerate) | §2.9 → §2.10 (token-gated `PUT`) |
| FR-34 (delete) | §2.11 |
| FR-35 (inventory, filters) | §2.6, §2.8 |
| FR-36 (slot selection, fail fast) | §2.12 (`include`; `409 empty_slots`) |
| FR-37, FR-38 (explanations from evaluation) | §2.12 (`scheme`, `echoes`, `explanation`) |
| FR-39–FR-42 (up to 3, distinct, ranked, non-deterministic) | §2.12 |
| FR-43 (fallback ladder) | §2.12 (`fallback`, empty-result shape with `hint`) |
| NFR-2 (single command) | §2.1 |
| NFR-5, NFR-6 (response bounds) | §2.12, §2.6 |

FR-7–FR-22 (roles, harmony, slot rules) govern the evaluation behind §2.12 and are specified in `docs/requirements.md`; they impose no additional contract surface.

---

*Approval of this document, together with `docs/architecture.md`, closes Milestone 3.*
