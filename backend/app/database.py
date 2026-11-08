from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import get_settings

_settings = get_settings()
_url = _settings.database_url
_is_sqlite = _url.startswith("sqlite")
_in_memory = _url in ("sqlite://", "sqlite:///:memory:")

_kwargs: dict = {}
if _is_sqlite:
    _kwargs["connect_args"] = {"check_same_thread": False}
    if _in_memory:
        _kwargs["poolclass"] = StaticPool  # one shared connection (used by tests)

engine = create_engine(_url, **_kwargs)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


def init_db() -> None:
    """Create the storage folder and all tables (no migrations yet)."""
    Path(_settings.storage_dir).mkdir(parents=True, exist_ok=True)
    if _is_sqlite and not _in_memory and engine.url.database:
        Path(engine.url.database).parent.mkdir(parents=True, exist_ok=True)
    from app import models  # noqa: F401  (register tables)

    Base.metadata.create_all(engine)
