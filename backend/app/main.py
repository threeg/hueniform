from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.api.detections import router as detections_router
from app.api.errors import register_error_handlers
from app.api.garments import router as garments_router
from app.api.health import router as health_router
from app.api.taxonomy import router as taxonomy_router
from app.storage.engine import init_db, make_engine


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="HUENIFORM_")

    data_dir: Path = Path("data")
    # Path to the built SPA.  Defaults to the Vite output directory relative to
    # the project root (where ``make run`` is invoked).  Override via
    # HUENIFORM_SPA_DIR when the working directory differs.
    spa_dir: Path = Path("frontend/dist")


def _init_data_dirs(data_dir: Path) -> None:
    for name in ("images", "thumbnails", "staging", "models"):
        (data_dir / name).mkdir(parents=True, exist_ok=True)


def create_app(settings: Settings | None = None) -> FastAPI:
    if settings is None:
        settings = Settings()

    @asynccontextmanager
    async def _lifespan(_app: FastAPI):
        _init_data_dirs(settings.data_dir)
        engine = make_engine(settings.data_dir / "hueniform.db")
        init_db(engine)
        _app.state.engine = engine
        yield
        engine.dispose()

    app = FastAPI(
        title="Hueniform",
        version="0.1.0",
        lifespan=_lifespan,
    )

    # Make settings accessible to endpoint handlers via request.app.state.settings.
    app.state.settings = settings

    register_error_handlers(app)
    app.include_router(health_router, prefix="/api")
    app.include_router(taxonomy_router, prefix="/api")
    app.include_router(detections_router, prefix="/api")
    app.include_router(garments_router, prefix="/api")

    # SPA static serving with history-API fallback (architecture §5).
    # Skipped when the SPA has not been built (e.g. in dev mode or tests that
    # do not need it).
    if settings.spa_dir.exists():
        _spa = settings.spa_dir

        @app.get("/{full_path:path}", include_in_schema=False)
        async def _spa_fallback(full_path: str) -> FileResponse:
            # Let unmatched /api/* paths surface as 404 rather than the SPA.
            if full_path.startswith("api"):
                raise HTTPException(status_code=404, detail="Not found")
            target = _spa / full_path
            if target.is_file():
                return FileResponse(target)
            return FileResponse(_spa / "index.html")

    return app


# Module-level instance for uvicorn.
app = create_app()
