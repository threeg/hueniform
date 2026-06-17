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

@pytest.mark.perf
class TestSuggestionBound:
    """NFR-5: outfit request completes in under 2 s at 500 garments."""

    BOUND_S = 2.0

    def test_all_optional_slots_median(self, perf_client: TestClient) -> None:
        # Worst case: all optional slots requested.
        body = {
            "include": {
                "jersey": True,
                "jacket": True,
                "hat": True,
                "accessory": True,
            }
        }

        times = []
        for _ in range(RUNS):
            t0 = time.perf_counter()
            r = perf_client.post("/api/suggestions", json=body)
            times.append(time.perf_counter() - t0)
            assert r.status_code in {200, 409}, (
                f"unexpected status {r.status_code}: {r.text}"
            )

        median = statistics.median(times)
        assert median < self.BOUND_S, (
            f"NFR-5 violated: median={median:.3f}s >= {self.BOUND_S}s "
            f"(runs: {[f'{t:.3f}' for t in times]})"
        )


# ── NFR-6 server half: GET /api/garments < 1 s (median of 3) ────────────────

@pytest.mark.perf
class TestInventoryBound:
    """NFR-6 server half: combined type+family filter completes in under 1 s."""

    BOUND_S = 1.0

    def test_combined_filter_median(self, perf_client: TestClient) -> None:
        times = []
        for _ in range(RUNS):
            t0 = time.perf_counter()
            r = perf_client.get("/api/garments", params={"type": "top", "family": "Blue"})
            times.append(time.perf_counter() - t0)
            assert r.status_code == 200, f"unexpected status {r.status_code}: {r.text}"

        median = statistics.median(times)
        assert median < self.BOUND_S, (
            f"NFR-6 server half violated: median={median:.3f}s >= {self.BOUND_S}s "
            f"(runs: {[f'{t:.3f}' for t in times]})"
        )
