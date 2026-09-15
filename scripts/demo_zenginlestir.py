"""Demo verisine altin senaryoya dokunmadan ilgisiz icerik ekler.

Neden var
---------
`seed_demo.py` yalnizca altin senaryonun uc icerigini kurar. Canli
"Kaynak bul" sorgusu uc gorselin icinden kaynak buldugunda juri "bunu
bulmak kolay" diyebilir; akis da uc gonderiyle gelistirici demosu gibi
duruyor. Bu betik mevcut veritabaninin **ustune** kampanya disi, gelirsiz
icerikler ve birkac kullanici ekler. Sifirlama yapmaz.

Degismemesi gerekenler, once ve sonra olculup karsilastirilir:
- altin senaryonun baglari (kapsama, guven, durum)
- odemeler ve kullanici kazanclari (10. sayfa kampanya dagitimi)
- uc icerigin Emek Karti dagitimi ve zinciri
- `demo_hazirla.py` beklentisi: turevde "Sabah isigi" bulunur, ilgisiz
  gorselde bag onerilmez

Biri tutmazsa betik aldigi yedegi geri yukler.

Dikkat edilen uc nokta:
- Her aday **yuklemeden once** kurtarma hattindan gecirilir; herhangi bir
  bag cikarsa atlanir. Yeni icerik ne altin zincire ne birbirine baglanir.
- Akis `created_at`'e gore yeniden eskiye siralaniyor. Yeni icerikler
  Ayse'nin iceriginden daha eskiye tarihlenir; yoksa en uste cikip demonun
  "uc gonderi, tek zincir" adimini asagi iterlerdi.
- Backend calisirken kosulmaz: SQLite'a iki surec yazar ve calisan
  sunucunun bellekteki indeksi yeni icerikleri gormez.

Kullanim (backend kapaliyken)
-----------------------------
    .venv/Scripts/python.exe scripts/demo_zenginlestir.py            # 20 icerik
    .venv/Scripts/python.exe scripts/demo_zenginlestir.py --adet 15
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import shutil
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from sqlalchemy import or_, select  # noqa: E402

from app.attribution.explain import build_labour_card  # noqa: E402
from app.core.config import get_settings  # noqa: E402
from app.core.database import SessionLocal, create_schema, engine  # noqa: E402
from app.models.entities import (  # noqa: E402
    AttributionEdge,
    Campaign,
    Content,
    Dispute,
    Payout,
    User,
)
from app.provenance import recovery  # noqa: E402
from app.services import ingest as ingest_service  # noqa: E402
from app.services import payout as payout_service  # noqa: E402
from app.services.registry import get_index_service  # noqa: E402

import demo_hazirla  # noqa: E402

RAW = ROOT / "data" / "raw"
ALTIN_BASLIKLAR = ("Sabah ışığı", "Şehrin Renkleri", "Bulduğum kare")
# seed_demo.py altin senaryonun kaynagini photos[3]'ten aliyor.
ALTIN_KAYNAK_SIRA = 3

# Kimlik renkleri seed_demo.py'deki kurala uyar: temanin anlam renklerinden
# (altin, dogrulama yesili, zincir mavisi, uyari turuncusu, alarm kirmizisi)
# ve altin uclunun mor/turkuaz/pembesinden ayrik. Ikincil kullanicilar
# olduklari icin bilerek soluk tonlar.
KULLANICILAR = (
    ("deniz", "Deniz Kaya", "#9AA5B4"),
    ("emre", "Emre Şahin", "#B08A63"),
    ("selin", "Selin Arslan", "#A3A35C"),
)
# Gorselin ne gosterdigini bilmedigimiz icin icerige gonderme yapmayan
# basliklar. "Sabah", "Şehrin", "Bulduğum" gecmemeli: ekran_goruntuleri.py
# ve demo_hazirla.py altin icerikleri basliktan buluyor.
BASLIKLAR = (
    "Günün karesi", "Arşivden", "Yolda", "Hafta sonu", "Pencereden",
    "Akşamüstü", "Eski bir kare", "Deneme çekimi", "Yürüyüşten",
    "Sessiz bir an", "Bugün gördüğüm", "Renkler", "Işık denemesi",
    "Uzaktan", "Yakın plan", "Mevsim", "Kısa bir mola", "Kenardan",
    "Dönüş yolunda", "Bir köşe", "Tatilden", "Haftanın karesi",
    "Rastgele", "Not defterinden",
)
ACIKLAMALAR = ("", "Telefonla çekildi.", "Arşivimden bir kare.", "Paylaşmak istedim.")


def _jpeg(gorsel: np.ndarray) -> bytes:
    ok, tampon = cv2.imencode(".jpg", gorsel, [cv2.IMWRITE_JPEG_QUALITY, 92])
    if not ok:
        raise RuntimeError("JPEG kodlanamadi")
    return tampon.tobytes()


def _sorgula(index, veri: bytes) -> recovery.RecoveryResult:
    """`POST /api/verify` ile ayni cagri: kayit yapmadan hatti calistirir."""
    gorsel = cv2.imdecode(np.frombuffer(veri, np.uint8), cv2.IMREAD_COLOR)
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
        tmp.write(veri)
        yol = Path(tmp.name)
    try:
        return recovery.recover(gorsel, veri, yol, index.index, index)
    finally:
        yol.unlink(missing_ok=True)


def _backend_calisiyor() -> bool:
    try:
        with urllib.request.urlopen("http://127.0.0.1:8000/api/health", timeout=2):
            return True
    except OSError:
        return False


# ---------------------------------------------------------------------------
# Yedek
# ---------------------------------------------------------------------------
def yedekle(settings) -> Path:
    hedef = settings.data_dir / "yedek" / dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    hedef.mkdir(parents=True)
    db = Path(settings.database_url.removeprefix("sqlite:///"))
    shutil.copy2(db, hedef / db.name)
    for klasor in (settings.upload_dir, settings.index_dir):
        if klasor.exists():
            shutil.copytree(klasor, hedef / klasor.name)
    return hedef


def geri_yukle(settings, yedek: Path) -> None:
    # Windows acik dosyayi ezdirmez; once baglantilar birakilir.
    engine.dispose()
    db = Path(settings.database_url.removeprefix("sqlite:///"))
    shutil.copy2(yedek / db.name, db)
    for klasor in (settings.upload_dir, settings.index_dir):
        if klasor.exists():
            shutil.rmtree(klasor)
        if (yedek / klasor.name).exists():
            shutil.copytree(yedek / klasor.name, klasor)


# ---------------------------------------------------------------------------
# Degismemesi gerekenler
# ---------------------------------------------------------------------------
def olc(session, altin: dict[str, Content]) -> dict:
    """Altin senaryonun sayisal izi. Once ve sonra birebir ayni olmali."""
    baglar = sorted(
        (e.parent_id, e.child_id, e.stage.value, e.status.value,
         round(e.confidence, 6), None if e.visual_coverage is None else round(e.visual_coverage, 6))
        for e in session.scalars(select(AttributionEdge))
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


def fark(once: dict, sonra: dict) -> list[str]:
    return [anahtar for anahtar in once if once[anahtar] != sonra.get(anahtar)]


def canli_demo_kontrolu(index, altin: dict[str, Content], korpus: list[Path]) -> list[str]:
    """demo_hazirla.py'nin API uzerinden bekledigini surec icinde dogrular."""
    sorun = []
    kaynak = cv2.imread(altin[demo_hazirla.KAYNAK_BASLIK].file_path)
    turev = _sorgula(index, _jpeg(demo_hazirla.turev_uret(kaynak)))
    if altin[demo_hazirla.KAYNAK_BASLIK].id not in {l.parent_content_id for l in turev.links}:
        sorun.append(f"türevde \"{demo_hazirla.KAYNAK_BASLIK}\" bulunmadı")
    ilgisiz = _sorgula(index, _jpeg(cv2.imread(str(korpus[demo_hazirla.ILGISIZ_SIRA]))))
    if ilgisiz.links:
        sorun.append(f"ilgisiz görselde {len(ilgisiz.links)} bağ önerildi")
    return sorun


# ---------------------------------------------------------------------------
def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--adet", type=int, default=20, help="eklenecek içerik sayısı")
    args = ap.parse_args()
    settings = get_settings()

    # --- On kosullar ------------------------------------------------------
    if _backend_calisiyor():
        print("Backend çalışıyor (127.0.0.1:8000). Önce sunucuyu kapatın.")
        return 2
    korpus = sorted(RAW.glob("*.jpg"))
    haric = {ALTIN_KAYNAK_SIRA, demo_hazirla.ILGISIZ_SIRA}
    adaylar = [yol for sira, yol in enumerate(korpus) if sira not in haric]
    if len(korpus) <= demo_hazirla.ILGISIZ_SIRA or len(adaylar) < args.adet:
        print(f"Korpus yetersiz ({len(korpus)} görsel, {RAW}). Önce: scripts/fetch_eval_images.py")
        return 1

    create_schema()
    session = SessionLocal()
    altin = {}
    for baslik in ALTIN_BASLIKLAR:
        icerik = session.scalar(select(Content).where(Content.title == baslik))
        if icerik is None:
            print(f"\"{baslik}\" yok. Önce altın senaryo: scripts/seed_demo.py")
            return 1
        altin[baslik] = icerik
    handles = [h for h, _, _ in KULLANICILAR]
    if session.scalar(select(User).where(User.handle.in_(handles))) is not None:
        print("Zaten eklenmiş: ek kullanıcılar veritabanında var. Bir şey yapılmadı.")
        return 0

    print(f"Veritabanı: {settings.database_url}")
    yedek = yedekle(settings)
    print(f"Yedek: {yedek}")

    index = get_index_service()
    index.rebuild(session)
    once = olc(session, altin)
    print(f"Önce: {len(once['baglar'])} bağ, {len(once['odemeler'])} ödeme, indekste {len(index)} içerik")

    # --- Ekleme -----------------------------------------------------------
    sorun: list[str] = []
    eklenen: list[Content] = []
    atlanan: list[str] = []
    try:
        kullanicilar = [User(handle=h, display_name=ad, accent=renk) for h, ad, renk in KULLANICILAR]
        session.add_all(kullanicilar)
        session.commit()

        en_eski = min(c.created_at for c in altin.values())
        basla = time.perf_counter()
        for yol in adaylar:
            if len(eklenen) >= args.adet:
                break
            veri = _jpeg(cv2.imread(str(yol)))
            on = _sorgula(index, veri)
            if on.links:
                atlanan.append(f"{yol.name} ({len(on.links)} bağ)")
                continue
            sira = len(eklenen)
            sonuc = ingest_service.ingest(
                session, index,
                raw_bytes=veri,
                owner=kullanicilar[sira % len(kullanicilar)],
                title=BASLIKLAR[sira % len(BASLIKLAR)],
                caption=ACIKLAMALAR[sira % len(ACIKLAMALAR)],
                campaign_id=None,
            )
            if sonuc.created_edges:
                sorun.append(f"{yol.name} yüklenirken bağ kuruldu")
                break
            sonuc.content.created_at = en_eski - dt.timedelta(hours=sira + 1)
            session.commit()
            eklenen.append(sonuc.content)
            print(f"  + {sonuc.content.title:<18} {yol.name}")
        print(f"Ekleme: {len(eklenen)} içerik, {time.perf_counter() - basla:.0f} sn")

        # --- Sonra dogrulama ----------------------------------------------
        if len(eklenen) < args.adet and not sorun:
            sorun.append(f"yalnızca {len(eklenen)} uygun aday bulundu")
        session.expire_all()
        sonra = olc(session, altin)
        sorun += [f"değişti: {anahtar}" for anahtar in fark(once, sonra)]
        yeni = [c.id for c in eklenen]
        bag = session.scalar(
            select(AttributionEdge).where(
                or_(AttributionEdge.child_id.in_(yeni), AttributionEdge.parent_id.in_(yeni))
            )
        )
        if bag is not None:
            sorun.append("yeni içeriklerden birinde bağ var")
        ust = list(session.scalars(select(Content).order_by(Content.created_at.desc()).limit(3)))
        if {c.title for c in ust} != set(ALTIN_BASLIKLAR):
            sorun.append(f"akışın üstü değişti: {[c.title for c in ust]}")
        sorun += canli_demo_kontrolu(index, altin, korpus)
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
    if atlanan:
        print(f"Atlanan adaylar (bağ çıktı): {', '.join(atlanan)}")
    print(
        f"\nTamam: {len(eklenen)} içerik ve {len(KULLANICILAR)} kullanıcı eklendi, "
        f"indekste {len(index)} içerik. Altın senaryo sayıları aynı."
    )
    print(f"Geri dönmek gerekirse (backend kapalıyken) yedek: {yedek}")
    print("Sıradaki: backend'i başlatıp scripts/demo_hazirla.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
