from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="HUENIFORM_")

    data_dir: Path = Path("data")


def _init_data_dirs(data_dir: Path) -> None:
    for name in ("images", "thumbnails", "staging", "models"):
        (data_dir / name).mkdir(parents=True, exist_ok=True)


def create_app(settings: Settings | None = None) -> FastAPI:
    if settings is None:
        settings = Settings()

    @asynccontextmanager
    async def _lifespan(_app: FastAPI):
        _init_data_dirs(settings.data_dir)
        yield

    return FastAPI(
        title="Hueniform",
        version="0.1.0",
        lifespan=_lifespan,
    )


# Module-level instance for uvicorn.
app = create_app()
