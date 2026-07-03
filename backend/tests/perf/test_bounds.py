"""
Performance timing assertions (test strategy §8.2, NFR-5, NFR-6).

Marked ``perf`` — excluded from the default gate (``make test``).
Run explicitly via ``make test-perf``.  Timing is contractual on the
owner's machine; a failure is a real conversation, not a retry.

Methodology
-----------
Each bound is the **median of 3 timed runs** to dampen scheduler noise,
measured with ``time.perf_counter`` around the raw HTTP call via
``TestClient`` (no network overhead).  The 500-garment wardrobe is seeded
once per test session so setup cost is paid only once.
"""

from __future__ import annotations

import statistics
import time

import pytest
from fastapi.testclient import TestClient

from app.main import Settings, create_app
from tests.fixtures.wardrobes import materialise_wardrobe, wardrobe_500

RUNS = 3


# ── Session-scoped 500-garment client ────────────────────────────────────────

@pytest.fixture(scope="session")
def perf_client(tmp_path_factory):
    """
    A single TestClient backed by a 500-garment DB, shared across all perf
    tests in the session so materialisation only happens once.
    """
    tmp = tmp_path_factory.mktemp("perf")
    settings = Settings(data_dir=tmp / "data", spa_dir=tmp / "no-spa")
    app = create_app(settings)
    with TestClient(app) as client:
        materialise_wardrobe(client.app.state.engine, wardrobe_500())
        yield client


# ── NFR-5: POST /api/suggestions < 2 s (median of 3) ────────────────────────

# All optional slots selected on top of the FR-51 defaults — worst case for the
# suggestion service (most per-slot candidate sets to iterate).
_ALL_OPTIONAL_SLOTS: dict[str, bool] = {
    "shirt": True, "mid": True, "outer": True,
    "hat": True, "glasses": True, "earrings": True,
    "tie": True, "scarf": True, "necklace": True,
    "watch": True, "ring": True, "bracelet": True,
    "belt": True,
}


@pytest.mark.perf
class TestSuggestionBound:
    """NFR-5: outfit request completes in under 2 s at 500 garments (re-baselined at count 25)."""

    BOUND_S = 2.0

    def _timed_post(self, client: TestClient, body: dict) -> float:
        t0 = time.perf_counter()
        r = client.post("/api/suggestions", json=body)
        elapsed = time.perf_counter() - t0
        assert r.status_code in {200, 409}, f"unexpected status {r.status_code}: {r.text}"
        return elapsed

    def test_count_25_all_slots_median(self, perf_client: TestClient) -> None:
        """NFR-5: count=25 with all optional slots selected — worst case (§8.2)."""
        body = {"slots": _ALL_OPTIONAL_SLOTS, "count": 25}
        times = [self._timed_post(perf_client, body) for _ in range(RUNS)]
        median = statistics.median(times)
        assert median < self.BOUND_S, (
            f"NFR-5 violated at count=25: median={median:.3f}s >= {self.BOUND_S}s "
            f"(runs: {[f'{t:.3f}' for t in times]})"
        )

    def test_count_3_all_slots_median(self, perf_client: TestClient) -> None:
        """NFR-5 count-independence: count=3 must also pass — confirms the bound is count-independent."""
        body = {"slots": _ALL_OPTIONAL_SLOTS, "count": 3}
        times = [self._timed_post(perf_client, body) for _ in range(RUNS)]
        median = statistics.median(times)
        assert median < self.BOUND_S, (
            f"NFR-5 count-independence violated at count=3: median={median:.3f}s >= {self.BOUND_S}s "
            f"(runs: {[f'{t:.3f}' for t in times]})"
        )


# ── NFR-6 server half: GET /api/garments < 1 s (median of 3) ────────────────

@pytest.mark.perf
class TestInventoryBound:
    """NFR-6 server half: combined category+family filter with each order value < 1 s."""

    BOUND_S = 1.0

    def _timed_get(self, client: TestClient, params: dict) -> float:
        t0 = time.perf_counter()
        r = client.get("/api/garments", params=params)
        elapsed = time.perf_counter() - t0
        assert r.status_code == 200, f"unexpected status {r.status_code}: {r.text}"
        return elapsed

    def test_combined_filter_hue_order_median(self, perf_client: TestClient) -> None:
        """NFR-6: combined category+family filter, order=hue (default) < 1 s."""
        params = {"category": "t_shirt", "family": "Blue", "order": "hue"}
        times = [self._timed_get(perf_client, params) for _ in range(RUNS)]
        median = statistics.median(times)
        assert median < self.BOUND_S, (
            f"NFR-6 (order=hue) violated: median={median:.3f}s >= {self.BOUND_S}s "
            f"(runs: {[f'{t:.3f}' for t in times]})"
        )

    def test_combined_filter_date_order_median(self, perf_client: TestClient) -> None:
        """NFR-6: combined category+family filter, order=date < 1 s."""
        params = {"category": "t_shirt", "family": "Blue", "order": "date"}
        times = [self._timed_get(perf_client, params) for _ in range(RUNS)]
        median = statistics.median(times)
        assert median < self.BOUND_S, (
            f"NFR-6 (order=date) violated: median={median:.3f}s >= {self.BOUND_S}s "
            f"(runs: {[f'{t:.3f}' for t in times]})"
        )
