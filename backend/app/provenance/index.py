"""Aday kaynak arama indeksleri.

Iki FAISS indeksi bir arada tutulur:
  * `IndexBinaryFlat(64)`  - pHash ve blok hash'leri icin Hamming aramasi
  * `IndexFlatIP(512)`     - L2-normalize CLIP vektorleri icin kosinus aramasi

Her ikisi de "flat" (kaba kuvvet) indekstir. Prototip olcegi (on binler)
icin fazlasiyla hizli ve %100 geri getirme garantili. Milyonlara cikildiginda
IVF-PQ / HNSW'ye gecis, indeks arayuzu ayni kalarak yapilabilir - bu
tercih teknik raporda olceklenebilirlik bolumunde gerekcelendirilir.
"""

from __future__ import annotations

import json
import pickle
from dataclasses import dataclass
from pathlib import Path

import faiss
import numpy as np

from . import fingerprint as fp
from .embedding import EMBEDDING_DIM


@dataclass
class Candidate:
    """Bir arama sonucundaki aday kaynak."""

    content_id: str
    source: str  # "phash" | "tile" | "clip"
    score: float  # phash/tile icin Hamming mesafesi, clip icin kosinus
    confidence: float


class ProvenanceIndex:
    """Icerik parmak izlerini ve gommelerini saklayan birlesik indeks."""

    def __init__(self) -> None:
        self.phash_index = faiss.IndexBinaryFlat(64)
        self.tile_index = faiss.IndexBinaryFlat(64)
        self.clip_index = faiss.IndexFlatIP(EMBEDDING_DIM)
        # FAISS satir numarasi -> content_id eslemeleri
        self._phash_ids: list[str] = []
        self._tile_ids: list[str] = []
        self._clip_ids: list[str] = []
        # Tam kopya tespiti icin
        self._by_content_hash: dict[str, str] = {}

    # -- ekleme ------------------------------------------------------------
    def add(
        self,
        content_id: str,
        finger: fp.Fingerprint,
        embedding: np.ndarray | None = None,
    ) -> None:
        self._by_content_hash[finger.content_hash] = content_id

        self.phash_index.add(finger.phash_bytes())
        self._phash_ids.append(content_id)

        tiles = finger.tile_bytes()
        if len(tiles):
            self.tile_index.add(tiles)
            self._tile_ids.extend([content_id] * len(tiles))

        if embedding is not None:
            vec = np.asarray(embedding, dtype=np.float32).reshape(1, -1)
            self.clip_index.add(vec)
            self._clip_ids.append(content_id)

    # -- arama -------------------------------------------------------------
    def exact(self, content_hash: str) -> str | None:
        return self._by_content_hash.get(content_hash)

    def search_phash(self, finger: fp.Fingerprint, k: int = 10) -> list[Candidate]:
        if self.phash_index.ntotal == 0:
            return []
        k = min(k, self.phash_index.ntotal)
        dists, idxs = self.phash_index.search(finger.phash_bytes(), k)
        out = []
        for dist, idx in zip(dists[0], idxs[0]):
            if idx < 0 or dist > fp.PHASH_MATCH_THRESHOLD:
                continue
            out.append(
                Candidate(self._phash_ids[idx], "phash", float(dist), fp.phash_confidence(int(dist)))
            )
        return out

    def search_tiles(self, finger: fp.Fingerprint, k: int = 5) -> list[Candidate]:
        """Kirpilmis turevler icin: turevin bloklari kaynagin bloklariyla eslesir."""
        tiles = finger.tile_bytes()
        if self.tile_index.ntotal == 0 or not len(tiles):
            return []
        k = min(k, self.tile_index.ntotal)
        dists, idxs = self.tile_index.search(tiles, k)
        # Ayni kaynaktan gelen birden fazla blok eslesmesi guveni artirir.
        best: dict[str, int] = {}
        hits: dict[str, int] = {}
        for row_d, row_i in zip(dists, idxs):
            for dist, idx in zip(row_d, row_i):
                if idx < 0 or dist > fp.TILE_MATCH_THRESHOLD:
                    continue
                cid = self._tile_ids[idx]
                hits[cid] = hits.get(cid, 0) + 1
                best[cid] = min(best.get(cid, 64), int(dist))
        out = []
        for cid, dist in best.items():
            # Blok sayisi arttikca guven yukselir, tavan 0.70.
            conf = min(0.70, 0.30 + 0.12 * hits[cid])
            out.append(Candidate(cid, "tile", float(dist), round(conf, 4)))
        return sorted(out, key=lambda c: -c.confidence)

    def search_clip(self, embedding: np.ndarray, k: int = 10) -> list[Candidate]:
        from .embedding import clip_confidence

        if self.clip_index.ntotal == 0:
            return []
        k = min(k, self.clip_index.ntotal)
        vec = np.asarray(embedding, dtype=np.float32).reshape(1, -1)
        sims, idxs = self.clip_index.search(vec, k)
        out = []
        for sim, idx in zip(sims[0], idxs[0]):
            if idx < 0:
                continue
            conf = clip_confidence(float(sim))
            if conf <= 0:
                continue
            out.append(Candidate(self._clip_ids[idx], "clip", float(sim), conf))
        return out

    # -- kalicilik ---------------------------------------------------------
    def save(self, directory: Path) -> None:
        directory.mkdir(parents=True, exist_ok=True)
        faiss.write_index_binary(self.phash_index, str(directory / "phash.faiss"))
        faiss.write_index_binary(self.tile_index, str(directory / "tile.faiss"))
        faiss.write_index(self.clip_index, str(directory / "clip.faiss"))
        (directory / "ids.json").write_text(
            json.dumps(
                {
                    "phash": self._phash_ids,
                    "tile": self._tile_ids,
                    "clip": self._clip_ids,
                    "content_hash": self._by_content_hash,
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

    @classmethod
    def load(cls, directory: Path) -> "ProvenanceIndex":
        obj = cls()
        obj.phash_index = faiss.read_index_binary(str(directory / "phash.faiss"))
        obj.tile_index = faiss.read_index_binary(str(directory / "tile.faiss"))
        obj.clip_index = faiss.read_index(str(directory / "clip.faiss"))
        meta = json.loads((directory / "ids.json").read_text(encoding="utf-8"))
        obj._phash_ids = meta["phash"]
        obj._tile_ids = meta["tile"]
        obj._clip_ids = meta["clip"]
        obj._by_content_hash = meta["content_hash"]
        return obj

    def __len__(self) -> int:
        return self.phash_index.ntotal
