"""Cok bolgeli sorgu bolgeleri.

Sorun: kaynak icerik turevin yalnizca bir parcasini kapliyorsa (kolaj,
meme seritleri, kirpma + yazi bandi), gorselin tamamindan hesaplanan
global pHash ve global CLIP vektoru kaynaga benzemez. Deney sonuclari
bunu net gosterdi: kolajda %42, meme'de %25 geri getirme.

Cozum: sorgu gorselini sabit bir bolge kumesine ayirip her bolgeyi ayri
ayri aramak. Bolgelerden biri kaynagin tamamiyla ortusuyorsa eslesme
yakalanir. Indeks tarafi degismez (yalnizca tam gorsel saklanir), bu
yuzden maliyet yalnizca sorgu aninda ve tek bir GPU yiginina sigar.

Ayrica `trim_uniform_border`, meme seritleri gibi duz renkli cerceveleri
olcumden once kirpar; bu tek basina bircok durumu cozer.
"""

from __future__ import annotations

import cv2
import numpy as np
from PIL import Image

# (isim, x0, y0, x1, y1) - oransal kutular
REGIONS: list[tuple[str, float, float, float, float]] = [
    ("tam", 0.00, 0.00, 1.00, 1.00),
    ("merkez", 0.15, 0.15, 0.85, 0.85),
    ("sol", 0.00, 0.00, 0.50, 1.00),
    ("sag", 0.50, 0.00, 1.00, 1.00),
    ("ust", 0.00, 0.00, 1.00, 0.50),
    ("alt", 0.00, 0.50, 1.00, 1.00),
    ("sol_ust", 0.00, 0.00, 0.55, 0.55),
    ("sag_ust", 0.45, 0.00, 1.00, 0.55),
    ("sol_alt", 0.00, 0.45, 0.55, 1.00),
    ("sag_alt", 0.45, 0.45, 1.00, 1.00),
]

# Bir kenar seridinin "duz" sayilmasi icin izin verilen renk sapmasi.
BORDER_TOLERANCE = 10.0
# Bu boyutun altina dusen bolgeler atlanir.
MIN_REGION_SIDE = 48


def trim_uniform_border(image: Image.Image) -> tuple[Image.Image, tuple[int, int, int, int]]:
    """Duz renkli cerceveyi (meme seritleri, letterbox) kirpar.

    Returns:
        (kirpilmis gorsel, kullanilan kutu). Cerceve yoksa gorsel aynen doner.
    """
    arr = np.asarray(image.convert("RGB"), dtype=np.float32)
    h, w = arr.shape[:2]

    def flat_rows(rows: np.ndarray) -> np.ndarray:
        """Her satir icin: satir boyunca renk sapmasi tolerans altinda mi."""
        return rows.reshape(rows.shape[0], -1, 3).std(axis=1).max(axis=1) < BORDER_TOLERANCE

    row_flat = flat_rows(arr)
    col_flat = flat_rows(arr.transpose(1, 0, 2))

    top = 0
    while top < h - MIN_REGION_SIDE and row_flat[top]:
        top += 1
    bottom = h
    while bottom > top + MIN_REGION_SIDE and row_flat[bottom - 1]:
        bottom -= 1
    left = 0
    while left < w - MIN_REGION_SIDE and col_flat[left]:
        left += 1
    right = w
    while right > left + MIN_REGION_SIDE and col_flat[right - 1]:
        right -= 1

    box = (left, top, right, bottom)
    if box == (0, 0, w, h):
        return image, box
    return image.crop(box), box


def iter_regions(image: Image.Image, include_trimmed: bool = True):
    """Sorgu bolgelerini (isim, gorsel) ciftleri olarak uretir."""
    w, h = image.size
    seen: set[tuple[int, int, int, int]] = set()

    for name, fx0, fy0, fx1, fy1 in REGIONS:
        box = (int(fx0 * w), int(fy0 * h), int(fx1 * w), int(fy1 * h))
        if box[2] - box[0] < MIN_REGION_SIDE or box[3] - box[1] < MIN_REGION_SIDE:
            continue
        if box in seen:
            continue
        seen.add(box)
        yield name, image.crop(box)

    if include_trimmed:
        trimmed, box = trim_uniform_border(image)
        if box not in seen and trimmed.size[0] >= MIN_REGION_SIDE:
            yield "cerceve_kirpilmis", trimmed
