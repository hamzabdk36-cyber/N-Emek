"""Zenginlestirme iceriklerine altin senaryoya dokunmadan turev zincirleri ekler.

Neden var
---------
`demo_zenginlestir.py` akisa 20 ozgun, bagsiz icerik ekledi; Emek Kartlari bos
duruyordu (tek taraf: icerigin kendisi). Bu betik o iceriklerden yedi zincir
kurar ki akista altin uclunun disinda da dolu Emek Karti olan gonderiler olsun:
beyanli remix, beyansiz ekran goruntusu, uc halkali zincir, iki kaynakli kolaj.

Degismemesi gerekenler, once ve sonra olculup karsilastirilir:
- altin senaryonun baglari, uc kartin dagitimi ve zinciri
- tum odemeler ve Ayse/Burak/Ceyda kazanclari (kampanya dagitimi)
- akisin ustundeki uc gonderi
- `demo_hazirla.py` beklentisi; demo turevinde yalnizca altin icerikler bulunur

Biri tutmazsa betik aldigi yedegi geri yukler.

Turevlere kucuk gelir (`content.revenue`) yazilir; Emek Karti tutarlari bundan
anlik hesaplar. Odeme satiri yazilmaz, dagitim cagrilmaz.

Kullanim (backend kapaliyken)
-----------------------------
    .venv/Scripts/python.exe scripts/demo_zincirler.py
"""

from __future__ import annotations

import datetime as dt
import json
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
sys.path.insert(0, str(ROOT / "scripts"))

from sqlalchemy import or_, select  # noqa: E402

from app.attribution.explain import build_labour_card  # noqa: E402
from app.core.config import get_settings  # noqa: E402
from app.core.database import SessionLocal, create_schema  # noqa: E402
from app.models.entities import (  # noqa: E402
    AttributionEdge,
    Campaign,
    Content,
    Dispute,
    Payout,
    User,
)
from app.services import ingest as ingest_service  # noqa: E402
from app.services import payout as payout_service  # noqa: E402
from app.services.registry import get_index_service  # noqa: E402
from eval import attacks  # noqa: E402

import demo_hazirla  # noqa: E402
from demo_zenginlestir import (  # noqa: E402
    ALTIN_BASLIKLAR,
    _backend_calisiyor,
    _jpeg,
    _sorgula,
    canli_demo_kontrolu,
    geri_yukle,
    yedekle,
)

RAW = ROOT / "data" / "raw"
EK_KULLANICILAR = ("deniz", "emre", "selin")


# ---------------------------------------------------------------------------
# Donusumler (remix studyosunun yapacagi islerin betik karsiligi)
# ---------------------------------------------------------------------------
def yazi_bandi(img: np.ndarray, metin: str) -> np.ndarray:
    """Kirpma + alt yazi bandi. OpenCV Turkce harf cizemedigi icin metin ASCII."""
    out = attacks._crop_area(img, 0.64).copy()
    h, w = out.shape[:2]
    band = int(h * 0.15)
    cv2.rectangle(out, (0, h - band), (w, h), (22, 20, 18), -1)
    cv2.putText(out, metin, (int(w * 0.04), h - band // 3),
                cv2.FONT_HERSHEY_SIMPLEX, h / 640, (255, 255, 255), 2, cv2.LINE_AA)
    return out


def iki_kaynak_kolaj(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Iki gorsel ayni yukseklikte, aralarinda beyaz serit, tek tuvalde."""
    h = min(a.shape[0], b.shape[0])
    a = cv2.resize(a, (int(a.shape[1] * h / a.shape[0]), h), interpolation=cv2.INTER_AREA)
    b = cv2.resize(b, (int(b.shape[1] * h / b.shape[0]), h), interpolation=cv2.INTER_AREA)
    ara = np.full((h, max(8, h // 40), 3), 255, np.uint8)
    return np.hstack([a, ara, b])


def meme(img: np.ndarray) -> np.ndarray:
    return attacks._meme(img)


def ekran_goruntusu(img: np.ndarray) -> np.ndarray:
    return attacks._screenshot(img)


def cikartma(img: np.ndarray) -> np.ndarray:
    return attacks._sticker(img)


def kirp_yaz(img: np.ndarray) -> np.ndarray:
    return attacks._crop_and_text(img)


# ---------------------------------------------------------------------------
# Zincir tanimlari
# ---------------------------------------------------------------------------
@dataclass
class Adim:
    anahtar: str             # sonraki adimlarin kaynak olarak anacagi ad
    baslik: str
    aciklama: str
    kaynaklar: tuple[str, ...]  # zenginlestirme basligi ya da onceki adimin anahtari
    donusum: object
    beyanli: bool            # remix studyosundan: kaynak beyani + C2PA remix manifesti
    eylemler: tuple[str, ...] = ()
    gelir: float = 0.0
    dakika: int = 20         # kaynaginin kac dakika sonrasina tarihlenir
    icerik: Content | None = field(default=None, repr=False)


ADIMLAR = (
    Adim("gunun", "Günün karesi, benim yorumum", "Akışta gördüğüm kareyi kırpıp yazı ekledim.",
         ("Günün karesi",), lambda g: yazi_bandi(g[0], "BENIM YORUMUM"),
         beyanli=True, eylemler=("c2pa.cropped", "c2pa.edited"), gelir=640.0),
    Adim("arsiv", "Akıştan kaydettim", "Ekran görüntüsü aldım, çok güzeldi.",
         ("Arşivden",), lambda g: ekran_goruntusu(g[0]),
         beyanli=False, gelir=380.0),
    Adim("yolda_meme", "Yolda ama komik", "Klasik şablon.",
         ("Yolda",), lambda g: meme(g[0]),
         beyanli=True, eylemler=("c2pa.edited",), gelir=520.0),
    Adim("yolda_ss", "Güldüren kare", "Arkadaştan geldi, paylaşıyorum.",
         ("yolda_meme",), lambda g: ekran_goruntusu(g[0]),
         beyanli=False, gelir=870.0, dakika=20),
    Adim("kolaj", "Hafta sonu kolajı", "İki kareyi yan yana koydum.",
         ("Hafta sonu", "Pencereden"), lambda g: iki_kaynak_kolaj(g[0], g[1]),
         beyanli=False, gelir=450.0),
    Adim("aksam", "Akşamüstü, çıkartmalı", "Üstüne küçük bir çizim ekledim.",
         ("Akşamüstü",), lambda g: cikartma(g[0]),
         beyanli=True, eylemler=("c2pa.drawing",), gelir=260.0),
    Adim("eski", "Eski bir kareden kesit", "Bir köşesini alıp yazı ekledim.",
         ("Eski bir kare",), lambda g: kirp_yaz(g[0]),
         beyanli=False, gelir=190.0),
    Adim("renkler", "Renkler ama şaka", "Klasik şablon, kaynak belli.",
         ("Renkler",), lambda g: meme(g[0]),
         beyanli=True, eylemler=("c2pa.edited",), gelir=330.0),
)


# Kaynaklarinin hepsi ozgun zenginlestirme icerigi olan adim yeni bir zincir baslatir.
ZINCIR_SAYISI = sum(all(k not in {a.anahtar for a in ADIMLAR} for k in a.kaynaklar) for a in ADIMLAR)


# ---------------------------------------------------------------------------
# Degismemesi gerekenler
# ---------------------------------------------------------------------------
def olc(session, altin: dict[str, Content]) -> dict:
    """Altin senaryonun sayisal izi. Yalnizca altin iceriklere degen baglar."""
    altin_id = {c.id for c in altin.values()}
    baglar = sorted(
        (e.parent_id, e.child_id, e.stage.value, e.status.value,
         round(e.confidence, 6), None if e.visual_coverage is None else round(e.visual_coverage, 6))
        for e in session.scalars(select(AttributionEdge))
        if e.parent_id in altin_id or e.child_id in altin_id
    )
    odemeler = sorted(
        (p.content_id, p.user_id or "", round(p.share, 6), round(p.amount, 2))
        for p in session.scalars(select(Payout))
    )
    kazanclar = {
        u.handle: payout_service.earnings_for_user(session, u.id)
        for u in session.scalars(select(User))
        if u.handle in {"ayse", "burak", "ceyda"}
    }
    kartlar = {}
    for baslik, icerik in altin.items():
        kart = build_labour_card(session, icerik.id)
        kartlar[baslik] = {"distribution": kart["distribution"], "chain": kart["chain"]}
    kampanya = {
        c.id: session.query(Content).filter(Content.campaign_id == c.id).count()
        for c in session.scalars(select(Campaign))
    }
    return json.loads(json.dumps({
        "baglar": baglar,
        "odemeler": odemeler,
        "kazanclar": kazanclar,
        "kartlar": kartlar,
        "kampanya_icerik": kampanya,
        "itiraz": session.query(Dispute).count(),
    }, default=str))


def _atalar(session, icerik_id: str) -> set[str]:
    """Bir icerigin baglar uzerinden ulasilan tum kaynaklari."""
    gorulen: set[str] = set()
    sira = [icerik_id]
    while sira:
        cocuk = sira.pop()
        for e in session.scalars(select(AttributionEdge).where(AttributionEdge.child_id == cocuk)):
            if e.parent_id not in gorulen:
                gorulen.add(e.parent_id)
                sira.append(e.parent_id)
    return gorulen


def _pct(x: float) -> str:
    return f"%{x * 100:.1f}".replace(".", ",")


def _tl(x: float) -> str:
    return "₺" + f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


# ---------------------------------------------------------------------------
def main() -> int:
    settings = get_settings()
    if _backend_calisiyor():
        print("Backend çalışıyor (127.0.0.1:8000). Önce sunucuyu kapatın.")
        return 2

    create_schema()
    session = SessionLocal()
    altin: dict[str, Content] = {}
    for baslik in ALTIN_BASLIKLAR:
        icerik = session.scalar(select(Content).where(Content.title == baslik))
        if icerik is None:
            print(f"\"{baslik}\" yok. Önce altın senaryo: scripts/seed_demo.py")
            return 1
        altin[baslik] = icerik
    basliklar = [a.baslik for a in ADIMLAR]
    if session.scalar(select(Content).where(Content.title.in_(basliklar))) is not None:
        print("Zaten eklenmiş: türev başlıkları veritabanında var. Bir şey yapılmadı.")
        return 0
    kullanicilar = {u.handle: u for u in session.scalars(select(User).where(User.handle.in_(EK_KULLANICILAR)))}
    if len(kullanicilar) != len(EK_KULLANICILAR):
        print("Ek kullanıcılar yok. Önce: scripts/demo_zenginlestir.py")
        return 1
    ek_icerikler = {
        c.title: c for c in session.scalars(
            select(Content).where(Content.owner_id.in_([u.id for u in kullanicilar.values()]))
        )
    }
    eksik = {k for a in ADIMLAR for k in a.kaynaklar if k not in ek_icerikler and k not in {b.anahtar for b in ADIMLAR}}
    if eksik:
        print(f"Kaynak içerik bulunamadı: {sorted(eksik)}")
        return 1

    print(f"Veritabanı: {settings.database_url}")
    yedek = yedekle(settings)
    print(f"Yedek: {yedek}")

    index = get_index_service()
    index.rebuild(session)
    once = olc(session, altin)
    print(f"Önce: {len(once['baglar'])} altın bağ, {len(once['odemeler'])} ödeme, indekste {len(index)} içerik\n")

    korpus = sorted(RAW.glob("*.jpg"))
    sorun: list[str] = []
    eklenen: list[Content] = []
    anahtarla: dict[str, Content] = {}
    sahip_sirasi = list(EK_KULLANICILAR)
    try:
        basla = time.perf_counter()
        for sira, adim in enumerate(ADIMLAR):
            kaynaklar = [anahtarla.get(k) or ek_icerikler[k] for k in adim.kaynaklar]
            gorseller = [cv2.imread(k.file_path) for k in kaynaklar]
            veri = _jpeg(adim.donusum(gorseller))

            # Sahip: kaynaklarin hicbirinin sahibi olmayan ilk ek kullanici (donusumlu).
            kaynak_sahipler = {k.owner_id for k in kaynaklar}
            adaylar = sahip_sirasi[sira % 3:] + sahip_sirasi[: sira % 3]
            sahip = next(kullanicilar[h] for h in adaylar if kullanicilar[h].id not in kaynak_sahipler)

            sonuc = ingest_service.ingest(
                session, index,
                raw_bytes=veri,
                owner=sahip,
                title=adim.baslik,
                caption=adim.aciklama,
                declared_parent_id=kaynaklar[0].id if adim.beyanli else None,
                remix_actions=list(adim.eylemler) or None,
                campaign_id=None,
            )
            icerik = sonuc.content
            icerik.revenue = adim.gelir
            icerik.created_at = max(k.created_at for k in kaynaklar) + dt.timedelta(minutes=adim.dakika)
            session.commit()
            adim.icerik = icerik
            anahtarla[adim.anahtar] = icerik
            eklenen.append(icerik)

            # Bag denetimi: beklenen kaynaklar var, fazlasi yalnizca onlarin atasi.
            beklenen = {k.id for k in kaynaklar}
            izinli = set(beklenen)
            for k in kaynaklar:
                izinli |= _atalar(session, k.id)
            bulunan = {e.parent_id for e in session.scalars(
                select(AttributionEdge).where(AttributionEdge.child_id == icerik.id))}
            if not beklenen <= bulunan:
                eksik_ad = [k.title for k in kaynaklar if k.id not in bulunan]
                sorun.append(f"\"{adim.baslik}\": kaynak bulunamadı {eksik_ad}")
            if bulunan - izinli:
                sorun.append(f"\"{adim.baslik}\": beklenmeyen bağ {len(bulunan - izinli)} adet")

            # Emek Karti: her beklenen kaynak sifirdan buyuk payla dagilimda.
            kart = build_labour_card(session, icerik.id)
            taraflar = kart["distribution"]["parties"]
            paylar = {p["content_id"]: p for p in taraflar if p["role"] == "source"}
            for k in kaynaklar:
                if paylar.get(k.id, {}).get("share", 0) <= 0:
                    sorun.append(f"\"{adim.baslik}\": Emek Kartı'nda \"{k.title}\" payı yok")
            ozet = " · ".join(f"{p['user_name']} {_pct(p['share'])} {_tl(p['amount'])}" for p in taraflar)
            tur = "remix" if adim.beyanli else "beyansız"
            print(f"  + {adim.baslik:<30} {sahip.display_name:<12} {tur:<9} {ozet}")
            if sorun:
                break
        print(f"\nEkleme: {len(eklenen)} içerik, {time.perf_counter() - basla:.0f} sn")

        # --- Sonra dogrulama ----------------------------------------------
        if not sorun:
            session.expire_all()
            sonra = olc(session, altin)
            sorun += [f"değişti: {a}" for a in once if once[a] != sonra.get(a)]
            yeni = {c.id for c in eklenen}
            altin_id = {c.id for c in altin.values()}
            bag = session.scalar(select(AttributionEdge).where(or_(
                AttributionEdge.child_id.in_(altin_id) & AttributionEdge.parent_id.in_(yeni),
                AttributionEdge.parent_id.in_(altin_id) & AttributionEdge.child_id.in_(yeni),
            )))
            if bag is not None:
                sorun.append("altın içerikle yeni içerik arasında bağ var")
            ust = list(session.scalars(select(Content).order_by(Content.created_at.desc()).limit(3)))
            if {c.title for c in ust} != set(ALTIN_BASLIKLAR):
                sorun.append(f"akışın üstü değişti: {[c.title for c in ust]}")
            sorun += canli_demo_kontrolu(index, altin, korpus)
            kaynak = cv2.imread(altin[demo_hazirla.KAYNAK_BASLIK].file_path)
            turev = _sorgula(index, _jpeg(demo_hazirla.turev_uret(kaynak)))
            yabanci = {l.parent_content_id for l in turev.links} - altin_id
            if yabanci:
                sorun.append(f"demo türevinde altın dışı {len(yabanci)} kaynak çıktı")
    except Exception as hata:  # yedege donmeden cikilmasin
        sorun.append(f"hata: {hata!r}")

    session.close()
    if sorun:
        geri_yukle(settings, yedek)
        print("\nGERİ ALINDI (yedek yüklendi):")
        for s in sorun:
            print(f"  - {s}")
        return 1

    index.save_snapshot()
    print(
        f"\nTamam: {len(eklenen)} türev, {len(ADIMLAR) - 1} zincir; indekste {len(index)} içerik. "
        "Altın senaryo sayıları aynı."
    )
    print(f"Geri dönmek gerekirse (backend kapalıyken) yedek: {yedek}")
    print("Sıradaki: demo_baslat.bat")
    return 0


if __name__ == "__main__":
    sys.exit(main())
