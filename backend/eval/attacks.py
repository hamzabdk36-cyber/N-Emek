"""Turev uretim senaryolari ("saldirilar").

Gercek hayatta bir icerigin kaynagini gizleyen donusumleri taklit eder.
Hem Faz 0 PoC'lerinde hem de Faz 2 kapsamli degerlendirmesinde ayni
tanimlar kullanilir; boylece raporda verilen sayilar tek bir kaynaktan
uretilmis olur.

Her senaryo (isim, fonksiyon) ciftidir; fonksiyon BGR numpy dizisi alir,
BGR numpy dizisi doner.
"""

from __future__ import annotations

from collections.abc import Callable

import cv2
import numpy as np

Attack = Callable[[np.ndarray], np.ndarray]


def _jpeg(img: np.ndarray, quality: int) -> np.ndarray:
    ok, buf = cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, quality])
    return cv2.imdecode(buf, cv2.IMREAD_COLOR) if ok else img


def _crop_area(img: np.ndarray, keep_area: float) -> np.ndarray:
    """Alanin `keep_area` oranini merkezden korur."""
    h, w = img.shape[:2]
    f = float(np.sqrt(keep_area))
    ch, cw = int(h * f), int(w * f)
    y0, x0 = (h - ch) // 2, (w - cw) // 2
    return img[y0 : y0 + ch, x0 : x0 + cw]


def _rotate(img: np.ndarray, degrees: float) -> np.ndarray:
    h, w = img.shape[:2]
    m = cv2.getRotationMatrix2D((w / 2, h / 2), degrees, 1.0)
    return cv2.warpAffine(img, m, (w, h), borderMode=cv2.BORDER_REPLICATE)


def _text_overlay(img: np.ndarray) -> np.ndarray:
    out = img.copy()
    h, w = out.shape[:2]
    band = int(h * 0.16)
    cv2.rectangle(out, (0, h - band), (w, h), (16, 16, 16), -1)
    cv2.putText(out, "REMIX 2026", (int(w * 0.04), h - band // 3),
                cv2.FONT_HERSHEY_SIMPLEX, h / 420, (255, 255, 255), 2, cv2.LINE_AA)
    return out


def _sticker(img: np.ndarray) -> np.ndarray:
    out = img.copy()
    h, w = out.shape[:2]
    cv2.circle(out, (int(w * 0.78), int(h * 0.25)), int(min(h, w) * 0.16), (40, 220, 250), -1)
    cv2.circle(out, (int(w * 0.78), int(h * 0.25)), int(min(h, w) * 0.16), (20, 20, 20), 3)
    return out


def _heavy_color(img: np.ndarray) -> np.ndarray:
    lut = np.clip(np.linspace(0, 255, 256) ** 1.35 / 255 ** 0.35, 0, 255).astype(np.uint8)
    out = cv2.LUT(img, lut)
    hsv = cv2.cvtColor(out, cv2.COLOR_BGR2HSV).astype(np.int16)
    hsv[..., 0] = (hsv[..., 0] + 25) % 180
    hsv[..., 1] = np.clip(hsv[..., 1] * 1.4, 0, 255)
    return cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)


def _grayscale(img: np.ndarray) -> np.ndarray:
    return cv2.cvtColor(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), cv2.COLOR_GRAY2BGR)


def _screenshot(img: np.ndarray) -> np.ndarray:
    """Ekran goruntusu benzetimi: kenar kirpma, olcekleme, hafif bulanikl., JPEG."""
    h, w = img.shape[:2]
    out = img[int(h * 0.04) : int(h * 0.96), int(w * 0.03) : int(w * 0.97)]
    out = cv2.resize(out, None, fx=0.75, fy=0.75, interpolation=cv2.INTER_AREA)
    out = cv2.GaussianBlur(out, (3, 3), 0.6)
    return _jpeg(out, 55)


def _collage(img: np.ndarray) -> np.ndarray:
    """Kaynak, iki kat genislikteki tuvalin sol yarisinda; sag yari gurultu."""
    h, w = img.shape[:2]
    rng = np.random.default_rng(int(img[:8, :8].sum()) % 9999)
    canvas = rng.integers(0, 255, (h, w * 2, 3), dtype=np.uint8)
    canvas = cv2.GaussianBlur(canvas, (0, 0), 6)
    canvas[:, :w] = img
    return canvas


def _crop_and_text(img: np.ndarray) -> np.ndarray:
    return _text_overlay(_crop_area(img, 0.45))


def _meme(img: np.ndarray) -> np.ndarray:
    """Klasik meme formati: ust ve alt beyaz seritler + yazi."""
    h, w = img.shape[:2]
    pad = int(h * 0.14)
    out = cv2.copyMakeBorder(img, pad, pad, 0, 0, cv2.BORDER_CONSTANT, value=(255, 255, 255))
    cv2.putText(out, "UST YAZI", (int(w * 0.1), int(pad * 0.72)),
                cv2.FONT_HERSHEY_SIMPLEX, h / 500, (0, 0, 0), 2, cv2.LINE_AA)
    cv2.putText(out, "ALT YAZI", (int(w * 0.1), out.shape[0] - int(pad * 0.3)),
                cv2.FONT_HERSHEY_SIMPLEX, h / 500, (0, 0, 0), 2, cv2.LINE_AA)
    return _jpeg(out, 70)


# Senaryo kaydi. Sira, raporlardaki tablo sirasini belirler.
ATTACKS: dict[str, Attack] = {
    "orijinal": lambda img: img.copy(),
    "jpeg_q50": lambda img: _jpeg(img, 50),
    "jpeg_q30": lambda img: _jpeg(img, 30),
    "olcek_%50": lambda img: cv2.resize(img, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA),
    "olcek_%25": lambda img: cv2.resize(img, None, fx=0.25, fy=0.25, interpolation=cv2.INTER_AREA),
    "kirpma_%90": lambda img: _crop_area(img, 0.90),
    "kirpma_%70": lambda img: _crop_area(img, 0.70),
    "kirpma_%50": lambda img: _crop_area(img, 0.50),
    "kirpma_%30": lambda img: _crop_area(img, 0.30),
    "yazi_bandi": _text_overlay,
    "sticker": _sticker,
    "meme": _meme,
    "agir_renk": _heavy_color,
    "gri_ton": _grayscale,
    "dondurme_5d": lambda img: _rotate(img, 5),
    "dondurme_15d": lambda img: _rotate(img, 15),
    "ayna": lambda img: cv2.flip(img, 1),
    "ekran_goruntusu": _screenshot,
    "kolaj": _collage,
    "kirpma+yazi": _crop_and_text,
}

# Bu senaryolarda kaynagin turevdeki gorunur alan orani (yaklasik dogru cevap).
# Geometri asamasinin `visual_coverage` ciktisi bunlarla karsilastirilir.
EXPECTED_COVERAGE: dict[str, float] = {
    "orijinal": 1.00,
    "jpeg_q50": 1.00,
    "jpeg_q30": 1.00,
    "olcek_%50": 1.00,
    "olcek_%25": 1.00,
    "kirpma_%90": 1.00,
    "kirpma_%70": 1.00,
    "kirpma_%50": 1.00,
    "kirpma_%30": 1.00,
    "yazi_bandi": 0.84,
    "sticker": 0.92,
    "meme": 0.78,
    "agir_renk": 1.00,
    "gri_ton": 1.00,
    "dondurme_5d": 1.00,
    "dondurme_15d": 1.00,
    "ayna": 1.00,
    "ekran_goruntusu": 1.00,
    "kolaj": 0.50,
    "kirpma+yazi": 0.84,
}
