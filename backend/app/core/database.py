"""Veritabani oturumu ve semasi."""

from __future__ import annotations

import logging
from collections.abc import Iterator

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings
from app.models.entities import Base

log = logging.getLogger("nemek.db")

_settings = get_settings()

engine = create_engine(
    _settings.database_url,
    # SQLite'ta FastAPI'nin thread havuzu icin gerekli.
    connect_args={"check_same_thread": False} if _settings.database_url.startswith("sqlite") else {},
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def create_schema() -> None:
    Base.metadata.create_all(engine)
    _eksik_sutunlari_ekle()


def _eksik_sutunlari_ekle() -> None:
    """Var olan tablolara sonradan eklenen sutunlari ekler.

    `create_all` yalnizca *olmayan tablolari* olusturur; var olan bir
    tabloya sutun eklemez. Alembic kurmak bu olcekteki bir prototip icin
    fazla; ama gocsuz de birakilamaz: demo veritabani Docker biriminde
    yasiyor, yani yeni bir sutun eklendiginde juri makinesindeki mevcut
    veritabani sessizce kirilirdi (`no such column`).

    Yalnizca *eklemeli* ve nullable/varsayilanli degisiklikler icin.
    Sutun tipi degistirmek ya da silmek gerekirse veritabani sifirlanir
    (`docker compose down -v`).
    """
    beklenen = {
        "contents": {
            "tile_hashes": "JSON",
            "clip_vector": "BLOB",
            "embedding_model": "VARCHAR(64)",
        },
        "users": {
            # Var olan kullanicilar "uye" olarak devam eder; moderator
            # yetkisi acikca verilir (bkz. VERI-MODEL-ETIK.md).
            "role": "VARCHAR(16) DEFAULT 'uye'",
        },
    }

    denetci = inspect(engine)
    with engine.begin() as baglanti:
        for tablo, sutunlar in beklenen.items():
            if tablo not in denetci.get_table_names():
                continue
            mevcut = {s["name"] for s in denetci.get_columns(tablo)}
            for ad, tip in sutunlar.items():
                if ad in mevcut:
                    continue
                baglanti.execute(text(f"ALTER TABLE {tablo} ADD COLUMN {ad} {tip}"))
                log.info("sutun eklendi: %s.%s", tablo, ad)


def get_session() -> Iterator[Session]:
    """FastAPI bagimliligi."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
