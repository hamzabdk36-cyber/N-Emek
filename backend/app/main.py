"""N-Emek API uygulamasi."""

from __future__ import annotations

import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.core.database import SessionLocal, create_schema
from app.services.registry import get_index_service

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
log = logging.getLogger("nemek")


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_schema()
    # Indeks bellekte tutulur. Acilista once diskteki anlik goruntu
    # denenir, olmazsa veritabanindaki vektorlerden kurulur; gorsel
    # okuyup CLIP calistirmak yalnizca vektoru eksik icerikler icin
    # gerekiyor (bkz. services/registry.py, docs/ACILIS-SURESI.md).
    servis = get_index_service()
    session = SessionLocal()
    started = time.perf_counter()
    try:
        count, kademe = servis.load_or_rebuild(session)
        log.info(
            "indeks hazir: %s icerik, kaynak=%s, %.0f ms",
            count,
            kademe,
            (time.perf_counter() - started) * 1000,
        )
    finally:
        session.close()

    yield

    # Kapanista anlik goruntuyu tazele: bir sonraki acilis en hizli
    # kademeden baslasin. Surec aniden olduruluse anlik goruntu bayat
    # kalir ama bu yalnizca bir onbellek - veritabani yolu yine hizli.
    servis.save_snapshot()


app = FastAPI(
    title="N-Emek",
    description=(
        "Aciklanabilir icerik atif ve adil gelir paylasim sistemi. "
        "TEKNOFEST 2026 NSosyal Inovasyon Yarismasi."
    ),
    version="0.1.0",
    lifespan=lifespan,
)

# Gelistirme sirasinda Vite ayri portta calisiyor.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/")
def root() -> dict:
    return {"name": "N-Emek", "docs": "/docs", "api": "/api/health"}
