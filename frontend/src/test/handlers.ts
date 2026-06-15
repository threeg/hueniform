import type { HttpHandler } from 'msw'

// API mock handlers — populated in HUE-006 alongside the shared fixtures.
// Every handler here is an executable mirror of docs/03-api-contract.md (test strategy §10.1).
export const handlers: HttpHandler[] = []
