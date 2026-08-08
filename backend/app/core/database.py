"""Veritabani oturumu ve semasi."""

from __future__ import annotations

from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings
from app.models.entities import Base

_settings = get_settings()

engine = create_engine(
    _settings.database_url,
    # SQLite'ta FastAPI'nin thread havuzu icin gerekli.
    connect_args={"check_same_thread": False} if _settings.database_url.startswith("sqlite") else {},
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def create_schema() -> None:
    Base.metadata.create_all(engine)


def get_session() -> Iterator[Session]:
    """FastAPI bagimliligi."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
