"""N-Emek API uygulamasi."""

from __future__ import annotations

import logging
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
    # Indeks bellekte tutuluyor; acilista veritabanindan yeniden kurulur.
    session = SessionLocal()
    try:
        count = get_index_service().rebuild(session)
        log.info("indeks kuruldu: %s icerik", count)
    finally:
        session.close()
    yield


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
