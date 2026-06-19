/**
 * MSW request handlers — an executable mirror of docs/03-api-contract.md.
 *
 * Each handler returns the documented success body.  Tests that need an error
 * path override the relevant handler with server.use() inside the test.
 *
 * This is the single frontend location to update when the contract changes
 * (test strategy §11.4).
 */

import { http, HttpResponse } from 'msw'
import type { HttpHandler } from 'msw'
import {
  HEALTH_OK,
  TAXONOMY_RESPONSE,
  DETECTION_RESPONSE,
  GARMENT_DETAIL,
  INVENTORY_RESPONSE,
  SUGGESTION_RESPONSE,
} from './contract-examples'

const BASE = 'http://127.0.0.1:8000'

export const handlers: HttpHandler[] = [
  // §2.1 Health
  http.get(`${BASE}/api/health`, () =>
    HttpResponse.json(HEALTH_OK),
  ),

  // §2.2 Taxonomy
  http.get(`${BASE}/api/taxonomy`, () =>
    HttpResponse.json(TAXONOMY_RESPONSE),
  ),

  // §2.3 Upload and detect
  http.post(`${BASE}/api/detections`, () =>
    HttpResponse.json(DETECTION_RESPONSE, { status: 201 }),
  ),

  // §2.4 Staged image preview
  http.get(`${BASE}/api/detections/:token/image`, () =>
    new HttpResponse(new Uint8Array([0xff, 0xd8]), {
      status: 200,
      headers: { 'Content-Type': 'image/jpeg' },
    }),
  ),

  // §2.5 Confirm and save
  http.post(`${BASE}/api/garments`, () =>
    HttpResponse.json(GARMENT_DETAIL, { status: 201 }),
  ),

  // §2.6 Inventory list
  http.get(`${BASE}/api/garments`, () =>
    HttpResponse.json(INVENTORY_RESPONSE),
  ),

  // §2.7 Garment detail
  http.get(`${BASE}/api/garments/:id`, () =>
    HttpResponse.json(GARMENT_DETAIL),
  ),

  // §2.8 Garment image / thumbnail — return minimal JPEG bytes
  http.get(`${BASE}/api/garments/:id/image`, () =>
    new HttpResponse(new Uint8Array([0xff, 0xd8]), {
      status: 200,
      headers: { 'Content-Type': 'image/jpeg' },
    }),
  ),
  http.get(`${BASE}/api/garments/:id/thumbnail`, () =>
    new HttpResponse(new Uint8Array([0xff, 0xd8]), {
      status: 200,
      headers: { 'Content-Type': 'image/jpeg' },
    }),
  ),

  // §2.9 Regenerate (re-detect)
  http.post(`${BASE}/api/garments/:id/regenerate`, () =>
    HttpResponse.json({ ...DETECTION_RESPONSE, garment_id: GARMENT_DETAIL.id }),
  ),

  // §2.10 Confirm regeneration
  http.put(`${BASE}/api/garments/:id`, () =>
    HttpResponse.json(GARMENT_DETAIL),
  ),

  // §2.10a Direct category edit
  http.patch(`${BASE}/api/garments/:id`, () =>
    HttpResponse.json(GARMENT_DETAIL),
  ),

  // §2.11 Delete
  http.delete(`${BASE}/api/garments/:id`, () =>
    new HttpResponse(null, { status: 204 }),
  ),

  // §2.12 Suggest outfit
  http.post(`${BASE}/api/suggestions`, () =>
    HttpResponse.json(SUGGESTION_RESPONSE),
  ),
]
