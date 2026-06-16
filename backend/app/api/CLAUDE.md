# API layer

FastAPI routes, Pydantic schemas, error envelope. The outermost backend layer.

- **Imports only `services` and its schemas.** Nothing imports `api`. The API layer must
  not bypass services to reach lower layers directly. Enforced by import-linter.
- **`docs/03-api-contract.md` is authoritative.** Where code and contract disagree, the
  contract wins. Change the contract document first if the spec needs updating.
- **Heavier gate:** `make test-e2e` (Playwright smoke journeys) is DoD for user-flow
  tickets.
- **Tests:** `backend/tests/api/`
