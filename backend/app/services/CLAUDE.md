# Services layer

Business logic orchestration: detection service, garment service, suggestion service.

- **Allowed imports:** `detection`, `matcher`, `storage`. Nothing from `api`.
- **Service tests that create a SQLite engine** must follow the engine fixture teardown
  pattern in `backend/app/storage/CLAUDE.md` (yield + dispose, not return).
- **Heavier gate:** `make test-perf` (NFR-5/NFR-6 timing at 500 garments) is DoD for
  suggestion- and inventory-query-touching tickets.
- **Tests:** `backend/tests/services/`
