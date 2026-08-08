"""Icerik parmak izleri: kriptografik ve algisal.

Uc katman:
  * `content_hash`  - SHA-256. Bit-birebir kopyayi kesin tespit eder.
  * `perceptual`    - pHash/dHash/wHash. Yeniden sikistirma, olcekleme,
                      parlaklik/renk oynamasina dayaniklidir.
  * `tiled`         - gorseli 3x3 bloga bolup her bloga pHash uygular.
                      Kirpilmis turevlerde tek bir global pHash coker;
                      blok hash'lerinden en az birinin eslesmesi
                      kirpmaya karsi dayaniklilik saglar.

Tum algisal hash'ler 64 bit ve `numpy.uint64` olarak paketlenir; FAISS
`IndexBinaryFlat` ile Hamming aramasi bu format uzerinden yapilir.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field

import imagehash
import numpy as np
from PIL import Image

# 64 bitlik pHash'te bu mesafeye kadar "ayni icerik" kabul edilir.
PHASH_MATCH_THRESHOLD = 12
# Blok hash'lerinde daha siki esik kullanilir (blok basina daha az bilgi var).
TILE_MATCH_THRESHOLD = 8
TILE_GRID = 3


@dataclass
class Fingerprint:
    """Bir gorselin tum parmak izleri."""

    content_hash: str
    phash: int
    dhash: int
    whash: int
    tiles: list[int] = field(default_factory=list)

    def phash_bytes(self) -> np.ndarray:
        return _int_to_bits(self.phash)

    def tile_bytes(self) -> np.ndarray:
        if not self.tiles:
            return np.zeros((0, 8), dtype=np.uint8)
        return np.vstack([_int_to_bits(t) for t in self.tiles])

    def as_evidence(self) -> dict:
        return {
            "content_hash": self.content_hash[:16] + "...",
            "phash": f"{self.phash:016x}",
            "dhash": f"{self.dhash:016x}",
        }


def _int_to_bits(value: int) -> np.ndarray:
    """64 bit tamsayiyi FAISS binary indeksinin bekledigi 8 bayta cevirir."""
    return np.frombuffer(int(value).to_bytes(8, "big"), dtype=np.uint8).reshape(1, 8)


def _hash_to_int(h: imagehash.ImageHash) -> int:
    bits = h.hash.flatten()
    out = 0
    for bit in bits:
        out = (out << 1) | int(bool(bit))
    return out


def hamming(a: int, b: int) -> int:
    """Iki 64 bit hash arasindaki Hamming mesafesi."""
    return int(a ^ b).bit_count()


def content_hash(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def compute(image: Image.Image, raw_bytes: bytes | None = None) -> Fingerprint:
    """Bir PIL gorseli icin tum parmak izlerini uretir.

    Args:
        image: Kaynak gorsel.
        raw_bytes: Dosyanin ham baytlari. Verilirse SHA-256 bunun uzerinden
            hesaplanir (bit-birebir kopya tespiti icin dogrusu budur).
            Verilmezse yeniden kodlanmis piksellerden hesaplanir.
    """
    rgb = image.convert("RGB")
    digest = content_hash(raw_bytes if raw_bytes is not None else rgb.tobytes())

    tiles: list[int] = []
    w, h = rgb.size
    tw, th = w // TILE_GRID, h // TILE_GRID
    if tw >= 16 and th >= 16:
        for gy in range(TILE_GRID):
            for gx in range(TILE_GRID):
                box = (gx * tw, gy * th, (gx + 1) * tw, (gy + 1) * th)
                tiles.append(_hash_to_int(imagehash.phash(rgb.crop(box))))

    return Fingerprint(
        content_hash=digest,
        phash=_hash_to_int(imagehash.phash(rgb)),
        dhash=_hash_to_int(imagehash.dhash(rgb)),
        whash=_hash_to_int(imagehash.whash(rgb)),
        tiles=tiles,
    )


def phash_confidence(distance: int) -> float:
    """Hamming mesafesini 0-1 guven skoruna cevirir.

    0 mesafe -> 0.80 (kesin degil; algisal hash carpismasi mumkundur)
    esik     -> 0.45 (sinirda)
    esik ustu -> 0.0
    """
    if distance > PHASH_MATCH_THRESHOLD:
        return 0.0
    span = PHASH_MATCH_THRESHOLD
    return round(0.80 - 0.35 * (distance / span), 4)
