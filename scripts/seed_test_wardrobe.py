#!/usr/bin/env python3
"""
Seed a running Hueniform instance with the reproducible 500-garment wardrobe
(test strategy §11.2) for E2E and manual NFR-6 checks.

Usage (from the repo root, with the venv active):
    python scripts/seed_test_wardrobe.py

Or via make:
    make seed-wardrobe

The script connects to the live SQLite database used by ``make run`` and
inserts rows directly through the storage layer — no HTTP calls needed.
The data directory is read from HUENIFORM_DATA_DIR (default: backend/data).
"""

from __future__ import annotations

import os
import sys

# Ensure backend/ is on sys.path so ``app.*`` imports resolve.
_repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_repo_root, "backend"))

from app.storage.engine import init_db, make_engine  # noqa: E402
from tests.fixtures.wardrobes import materialise_wardrobe, wardrobe_500  # noqa: E402

# Need tests/ on the path too so fixtures/ is importable.
sys.path.insert(0, os.path.join(_repo_root, "backend", "tests"))

from pathlib import Path


def main() -> None:
    data_dir = Path(os.environ.get("HUENIFORM_DATA_DIR",
                                   os.path.join(_repo_root, "backend", "data")))
    db_path = data_dir / "hueniform.db"

    if not db_path.exists():
        print(f"Database not found: {db_path}", file=sys.stderr)
        print("Run 'make run' first to initialise the database.", file=sys.stderr)
        sys.exit(1)

    engine = make_engine(db_path)
    init_db(engine)

    garments = wardrobe_500()
    print(f"Inserting {len(garments)} garments into {db_path} …", flush=True)
    materialise_wardrobe(engine, garments)
    engine.dispose()
    print("Done.")


if __name__ == "__main__":
    main()
