"""Canli demonun "Kaynak bul" adimini hazirlar ve sahneden once isitir.

Neden var
---------
Canli demoda juri onunde hat bir kez gercekten calistiriliyor: sisteme hic
girmemis bir turev gorsel (kaynak bulunmali) ve ilgisiz bir fotograf
(hicbir bag onerilmemeli). `/api/verify` kayit yapmadigi icin demo verisi
degismez.

Iki tuzak olcumle goruldu (15 Eyl, yerel ortam):
- Surecteki **ilk** sorgu model yuklendigi icin uzun suruyor (calisan
  sunucuda ~9,5 sn, soguk surecte ~25 sn), sonrakiler ~0,3-0,4 sn. Isitma sunucunun kendi surecinde yapilmali; bu betik ayni
  sorguyu API uzerinden gonderdigi icin isitmayi da yapmis olur.
- Windows'ta "localhost" once IPv6'yi deniyor ve her istege ~2 sn ekliyor;
  uvicorn yalnizca 127.0.0.1'i dinliyor. Varsayilan adres bu yuzden 127.0.0.1
  (Vite vekili de oyle, tarayici yolu etkilenmiyor).
- Demo verisi her `seed_demo.py --reset` ile yeniden olculuyor. Dosyalar bu
  yuzden elle degil, calisan sistemdeki "Sabah isigi" iceriginden uretilir.

Kullanim (backend calisirken)
-----------------------------
    .venv/Scripts/python.exe scripts/demo_hazirla.py            # uret + isit + denetle
    .venv/Scripts/python.exe scripts/demo_hazirla.py --api http://127.0.0.1:8765

Ciktilar `data/demo/` altina yazilir (depoda degil). Beklenti tutmazsa
cikis kodu 1: o durumda dosyalar sahnede kullanilmaz.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
import uuid
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import cv2
import numpy as np

import demo_fotolar

KOK = Path(__file__).resolve().parents[1]
HEDEF = KOK / "data" / "demo"
KORPUS = KOK / "data" / "raw"
KAYNAK_BASLIK = "Sabah ışığı"
TUREV = "kaynak-bul-turev.jpg"
ILGISIZ = "kaynak-bul-ilgisiz.jpg"
# Korpusun 4. gorseli (indeks 3) altin senaryonun kaynagi; 11. gorsel demo
# verisinde indekslenmiyor. Docker 24 gorsel indirdigi icin ikisi de orada da var.
ILGISIZ_SIRA = 10
# data/demo_fotolar/liste.csv'de `ilgisiz` satiri varsa korpus yerine o kare
# kullanilir: sahnede stok fotograf degil telefon fotografi sorgulanir.
# Isitilmis sorgunun ust siniri. Olculen 0,3-0,4 sn; 1,5 sn'yi asmasi bir
# seylerin ters gittigini gosterir (or. "localhost" gecikmesi, CPU'ya dusus).
ISINMIS_SINIR_MS = 1500


def _ms(sure: float) -> str:
    return f"{sure:,.0f} ms".replace(",", ".")


def _getir(url: str) -> bytes:
    with urllib.request.urlopen(url, timeout=30) as yanit:
        return yanit.read()


def _sorgula(api: str, ad: str, veri: bytes) -> tuple[dict, float]:
    sinir = uuid.uuid4().hex
    govde = (
        f"--{sinir}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{ad}"\r\n'
        "Content-Type: image/jpeg\r\n\r\n"
    ).encode() + veri + f"\r\n--{sinir}--\r\n".encode()
    istek = urllib.request.Request(
        f"{api}/api/verify",
        data=govde,
        headers={"Content-Type": f"multipart/form-data; boundary={sinir}"},
        method="POST",
    )
    basla = time.perf_counter()
    # Ilk sorgu modeli yukluyor; sabirli bekle.
    with urllib.request.urlopen(istek, timeout=180) as yanit:
        sonuc = json.loads(yanit.read())
    return sonuc, (time.perf_counter() - basla) * 1000


def turev_uret(gorsel: np.ndarray) -> np.ndarray:
    """Remix studyosunun yapacagi turden: kirpma + ust yazi bandi + olcekleme."""
    h, w = gorsel.shape[:2]
    kirpik = gorsel[int(h * 0.10) : int(h * 0.85), int(w * 0.20) : int(w * 0.95)].copy()
    cv2.rectangle(kirpik, (0, 0), (kirpik.shape[1], 40), (30, 30, 30), -1)
    cv2.putText(kirpik, "JURI DEMO", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    return cv2.resize(kirpik, None, fx=0.8, fy=0.8)


def ilgisiz_gorsel(korpus: list[Path]) -> np.ndarray:
    yol = demo_fotolar.ilgisiz_yolu()
    return demo_fotolar.foto_oku(yol) if yol else cv2.imread(str(korpus[ILGISIZ_SIRA]))


def jpeg(gorsel: np.ndarray) -> bytes:
    ok, tampon = cv2.imencode(".jpg", gorsel, [cv2.IMWRITE_JPEG_QUALITY, 88])
    if not ok:
        raise RuntimeError("JPEG kodlanamadi")
    return tampon.tobytes()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--api", default="http://127.0.0.1:8000")
    args = ap.parse_args()
    api = args.api.rstrip("/")

    try:
        saglik = json.loads(_getir(f"{api}/api/health"))
        akis = json.loads(_getir(f"{api}/api/feed"))
    except (urllib.error.URLError, OSError) as hata:
        print(f"API'ye ulaşılamadı ({api}): {hata}")
        print("  Önce backend'i başlatın.")
        return 2
    print(f"API: {saglik['indexed_contents']} içerik indeksli, cihaz {saglik['device']}")

    kaynak = next((c for c in akis if c["title"] == KAYNAK_BASLIK), None)
    if kaynak is None:
        print(f"Akışta \"{KAYNAK_BASLIK}\" yok. Demo verisi kurulu mu? (scripts/seed_demo.py)")
        return 1
    korpus = sorted(KORPUS.glob("*.jpg"))
    if len(korpus) <= ILGISIZ_SIRA:
        print(f"İlgisiz görsel için korpus eksik ({KORPUS}). Önce: scripts/fetch_eval_images.py")
        return 1

    ham = np.frombuffer(_getir(f"{api}/api/contents/{kaynak['id']}/image"), np.uint8)
    kaynak_gorsel = cv2.imdecode(ham, cv2.IMREAD_COLOR)
    HEDEF.mkdir(parents=True, exist_ok=True)
    dosyalar = {
        TUREV: jpeg(turev_uret(kaynak_gorsel)),
        ILGISIZ: jpeg(ilgisiz_gorsel(korpus)),
    }
    for ad, veri in dosyalar.items():
        (HEDEF / ad).write_bytes(veri)
    print(f"Dosyalar: {HEDEF}")

    sorun: list[str] = []
    for tur in ("ısıtma", "kontrol"):
        for ad, veri in dosyalar.items():
            sonuc, sure = _sorgula(api, ad, veri)
            baglar = sonuc["links"]
            basliklar = [b["parent_title"] for b in baglar]
            alanlar = ", ".join(
                f"{b['parent_title']} %{b['visual_coverage'] * 100:.1f}".replace(".", ",")
                for b in baglar
                if b["visual_coverage"] is not None
            )
            print(f"  [{tur}] {ad}: {_ms(sure)} · {len(baglar)} kaynak"
                  + (f" · {alanlar}" if alanlar else ""))
            if tur != "kontrol":
                continue
            if ad == TUREV and KAYNAK_BASLIK not in basliklar:
                sorun.append(f"türevde \"{KAYNAK_BASLIK}\" bulunmadı: {basliklar}")
            if ad == ILGISIZ and baglar:
                sorun.append(f"ilgisiz görselde bağ önerildi: {basliklar}")
            if sure > ISINMIS_SINIR_MS:
                sorun.append(f"{ad} ısıtmadan sonra {_ms(sure)} sürdü")

    if sorun:
        print("\nHAZIR DEĞİL:")
        for s in sorun:
            print(f"  - {s}")
        return 1
    print("\nHazır: iki dosya da beklendiği gibi; model ısındı.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
