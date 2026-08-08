"""Arama indeksinin yasam dongusu ve icerik cozumleme.

`recovery.ContentStore` protokolunu veritabani uzerinden karsilar ve
FAISS indekslerini surecte ayakta tutar.

Indeks bellekte tutulur ve acilista veritabanindan yeniden kurulur.
Prototip olceginde (on binler) bu saniyeler surer ve kalicilik
karmasikligindan kurtarir. Uretimde indeks diske yazilip artimli
guncellenir; `ProvenanceIndex.save/load` bu yolu zaten aciyor.
"""

from __future__ import annotations

import threading
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.entities import Content
from app.provenance import embedding
from app.provenance import fingerprint as fp
from app.provenance.index import ProvenanceIndex
from app.provenance.watermark import content_id_to_hex


class IndexService:
    """Surec omurlu indeks + icerik cozumleyici."""

    def __init__(self) -> None:
        self._index = ProvenanceIndex()
        self._lock = threading.Lock()
        # content_id -> dosya yolu (geometri asamasi icin)
        self._paths: dict[str, str] = {}
        # filigran kimligi -> content_id
        self._watermarks: dict[str, str] = {}
        # gorsel onbellegi: geometri her aday icin kaynagi okur
        self._image_cache: dict[str, np.ndarray] = {}

    # -- indeks yonetimi ---------------------------------------------------
    @property
    def index(self) -> ProvenanceIndex:
        return self._index

    def rebuild(self, session: Session) -> int:
        """Veritabanindaki tum icerikten indeksi bastan kurar."""
        with self._lock:
            self._index = ProvenanceIndex()
            self._paths.clear()
            self._watermarks.clear()
            self._image_cache.clear()

            contents = list(session.scalars(select(Content)))
            if not contents:
                return 0

            images: list[Image.Image] = []
            usable: list[Content] = []
            for content in contents:
                path = Path(content.file_path)
                if not path.exists():
                    continue
                images.append(Image.open(path).convert("RGB"))
                usable.append(content)

            vectors = embedding.embed(images, batch_size=32)
            for content, pil, vector in zip(usable, images, vectors):
                finger = fp.compute(pil, raw_bytes=Path(content.file_path).read_bytes())
                self._index.add(content.id, finger, vector)
                self._register(content)
            return len(usable)

    def add(self, content: Content, finger: fp.Fingerprint, vector: np.ndarray) -> None:
        with self._lock:
            self._index.add(content.id, finger, vector)
            self._register(content)

    def _register(self, content: Content) -> None:
        self._paths[content.id] = content.file_path
        # Filigran kimligi icerik kimliginden turetildigi icin tersine
        # eslemeyi burada kurabiliyoruz; ayrica saklamaya gerek yok.
        self._watermarks[content_id_to_hex(content.id)] = content.id

    def forget_image(self, content_id: str) -> None:
        self._image_cache.pop(content_id, None)

    # -- ContentStore protokolu -------------------------------------------
    def load_image(self, content_id: str) -> np.ndarray | None:
        cached = self._image_cache.get(content_id)
        if cached is not None:
            return cached
        path = self._paths.get(content_id)
        if not path:
            return None
        image = cv2.imread(path)
        if image is None:
            return None
        # Onbellek sinirsiz buyumesin; prototipte basit bir tavan yeterli.
        if len(self._image_cache) > 256:
            self._image_cache.clear()
        self._image_cache[content_id] = image
        return image

    def by_watermark(self, tag: str) -> str | None:
        return self._watermarks.get(tag)

    def by_manifest_parent(self, declared_id: str) -> str | None:
        """Manifestteki kimlik dogrudan bizim icerik kimligimizdir."""
        return declared_id if declared_id in self._paths else None

    def __len__(self) -> int:
        return len(self._index)


_service: IndexService | None = None


def get_index_service() -> IndexService:
    global _service
    if _service is None:
        _service = IndexService()
    return _service


def reset_index_service() -> None:
    """Testler icin: surec omurlu tekili sifirlar."""
    global _service
    _service = None
    get_settings.cache_clear()
