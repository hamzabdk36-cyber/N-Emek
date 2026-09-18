"""Demo akisi icin ekibin kendi fotograflari: liste okuma ve hazirlama.

Neden var
---------
Zenginlestirme icerikleri `data/raw/` korpusundan (picsum/Unsplash) geliyordu;
profesyonel stok kareler akisi katalog gibi gosteriyordu. Bu modul
`data/demo_fotolar/` altindaki telefon fotograflarini ve basliklarini okur.
Backend'e bagimli degil; `demo_hazirla.py` de kullaniyor.

Klasor duzeni
-------------
    data/demo_fotolar/
      liste.csv          dosya,baslik,aciklama,sahip,anahtar
      zincirler.csv      (istege bagli) adim,baslik,aciklama
      *.jpg / *.png

`liste.csv` sutunlari:
- dosya     klasordeki dosya adi (jpg/jpeg/png; HEIC okunamaz, once cevirin)
- baslik    akista gorunen baslik; benzersiz
- aciklama  gonderi metni; bos olabilir
- sahip     deniz | emre | selin; bos ise sirayla dagitilir
- anahtar   bos, `ilgisiz`, ya da demo_zincirler.py'deki bir yuva adi
            (gunun, arsiv, yolda, hafta_sonu, pencereden, aksam, eski, renkler).
            `ilgisiz` satiri akisa girmez: Kaynak Bul'da "bag yok" sorgusu olur.

`zincirler.csv` bir turev adiminin basligini/aciklamasini degistirir; `adim`
demo_zincirler.py'deki `Adim.anahtar` degeridir.

Fotograflar EXIF yonune gore dondurulur, uzun kenar 1080 px'e indirilir.
JPEG yeniden kodlandigi icin EXIF (konum dahil) yuklenen dosyaya gecmez.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageOps

KOK = Path(__file__).resolve().parents[1]
VARSAYILAN_KLASOR = KOK / "data" / "demo_fotolar"
UZUN_KENAR = 1080
UZANTILAR = {".jpg", ".jpeg", ".png"}
SAHIPLER = ("deniz", "emre", "selin")
YUVALAR = ("gunun", "arsiv", "yolda", "hafta_sonu", "pencereden", "aksam", "eski", "renkler")
ILGISIZ = "ilgisiz"
# Altin icerikler basliktan bulunuyor; bu onekler baska bir baslikta gecmemeli.
YASAK_ONEKLER = ("Sabah", "Şehrin", "Bulduğum")


@dataclass(frozen=True)
class Foto:
    yol: Path
    baslik: str
    aciklama: str
    sahip: str
    anahtar: str


def foto_listesi(klasor: Path) -> list[Foto]:
    """`liste.csv`'yi okur ve dogrular. Hata varsa hepsini birden bildirir."""
    liste = klasor / "liste.csv"
    if not liste.exists():
        raise SystemExit(f"{liste} yok. Sütunlar: dosya,baslik,aciklama,sahip,anahtar")
    with liste.open(encoding="utf-8-sig", newline="") as f:
        satirlar = list(csv.DictReader(f))

    fotolar: list[Foto] = []
    hatalar: list[str] = []
    for no, s in enumerate(satirlar, start=2):
        s = {k.strip().lower(): (v or "").strip() for k, v in s.items() if k}
        if not any(s.values()):
            continue
        yol = klasor / s.get("dosya", "")
        foto = Foto(yol, s.get("baslik", ""), s.get("aciklama", ""),
                    s.get("sahip", "").lower(), s.get("anahtar", "").lower())
        if not s.get("dosya") or not yol.is_file():
            hatalar.append(f"satır {no}: dosya yok ({s.get('dosya')!r})")
        elif yol.suffix.lower() not in UZANTILAR:
            hatalar.append(f"satır {no}: {yol.name} desteklenmiyor (jpg/png olmalı)")
        if foto.anahtar != ILGISIZ:
            if not foto.baslik:
                hatalar.append(f"satır {no}: başlık boş")
            elif foto.baslik.startswith(YASAK_ONEKLER):
                hatalar.append(f"satır {no}: başlık {YASAK_ONEKLER} ile başlamamalı")
        if foto.sahip and foto.sahip not in SAHIPLER:
            hatalar.append(f"satır {no}: sahip {foto.sahip!r} tanınmıyor ({', '.join(SAHIPLER)})")
        if foto.anahtar and foto.anahtar not in (*YUVALAR, ILGISIZ):
            hatalar.append(f"satır {no}: anahtar {foto.anahtar!r} tanınmıyor")
        fotolar.append(foto)

    akis = [f for f in fotolar if f.anahtar != ILGISIZ]
    for alan in ("baslik", "anahtar"):
        degerler = [getattr(f, alan) for f in fotolar if getattr(f, alan)]
        tekrar = sorted({d for d in degerler if degerler.count(d) > 1})
        if tekrar:
            hatalar.append(f"tekrarlanan {alan}: {tekrar}")
    if not akis:
        hatalar.append("akış için hiç fotoğraf yok")
    if hatalar:
        raise SystemExit(f"{liste} hatalı:\n  - " + "\n  - ".join(hatalar))
    return fotolar


def foto_oku(yol: Path) -> np.ndarray:
    """EXIF yonunu uygular, uzun kenari UZUN_KENAR'a indirir, BGR dondurur.

    cv2.imread Windows'ta Turkce karakterli yolu acamiyor; PIL aciyor.
    """
    with Image.open(yol) as img:
        img = ImageOps.exif_transpose(img).convert("RGB")
        img.thumbnail((UZUN_KENAR, UZUN_KENAR), Image.Resampling.LANCZOS)
        return cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR)


def ilgisiz_yolu(klasor: Path = VARSAYILAN_KLASOR) -> Path | None:
    """Listede `ilgisiz` satiri varsa onun dosyasi; yoksa None."""
    if not (klasor / "liste.csv").exists():
        return None
    return next((f.yol for f in foto_listesi(klasor) if f.anahtar == ILGISIZ), None)


def zincir_ustyazilari(klasor: Path) -> dict[str, tuple[str, str]]:
    """`zincirler.csv`: adim anahtari -> (baslik, aciklama)."""
    dosya = klasor / "zincirler.csv"
    if not dosya.exists():
        return {}
    with dosya.open(encoding="utf-8-sig", newline="") as f:
        return {
            s["adim"].strip(): (s["baslik"].strip(), (s.get("aciklama") or "").strip())
            for s in csv.DictReader(f)
            if (s.get("adim") or "").strip()
        }
