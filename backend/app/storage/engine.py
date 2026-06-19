"""
SQLite engine factory, session helper and schema initialiser (architecture §3.1).

``make_engine(db_path)``  — create an engine with PRAGMA foreign_keys and WAL.
``init_db(engine)``       — create tables if absent (idempotent).
``get_session(engine)``   — yield a Session for dependency injection.

Storage imports nothing from matcher/detection/services/api (contract 4).
"""

from __future__ import annotations

from collections.abc import Generator
from pathlib import Path

import sqlalchemy as sa
from sqlalchemy.engine import Engine
from sqlmodel import Session, SQLModel, create_engine

# Import models so their metadata is registered before create_all is called.
import app.storage.models  # noqa: F401
from app.storage.migration import migrate


def make_engine(db_path: Path) -> Engine:
    """Return an engine bound to *db_path* with required SQLite PRAGMAs active."""
    engine = create_engine(f"sqlite:///{db_path}")

    @sa.event.listens_for(engine, "connect")
    def _set_pragmas(dbapi_conn, _record: object) -> None:
        dbapi_conn.execute("PRAGMA foreign_keys = ON")
        dbapi_conn.execute("PRAGMA journal_mode = WAL")

    return engine


def init_db(engine: Engine) -> None:
    """Migrate v0.1.0 type values then create any tables that do not yet exist."""
    migrate(engine)
    SQLModel.metadata.create_all(engine)


def get_session(engine: Engine) -> Generator[Session, None, None]:
    """Yield a Session for use with FastAPI's dependency injection."""
    with Session(engine) as session:
        yield session
