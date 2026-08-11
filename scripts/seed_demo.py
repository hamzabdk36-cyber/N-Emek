"""Altin senaryoyu bastan sona kurar ve anlatir.

Bu betik ayni zamanda juri demosunun senaryosudur:

  1. Ayse ozgun bir fotograf yukler        -> C2PA imzalanir, filigran gomulur
  2. Burak remixler (kirpma + yazi)        -> zincir kurulur, alan olculur
  3. Ceyda ekran goruntusu alip yukler     -> C2PA SILINIR, sistem yine bulur
  4. Marka kampanyasi odul havuzunu dagitir
  5. Ayse itiraz eder                      -> yeniden olcum, paylar guncellenir

Calistirma:
    .venv/Scripts/python.exe scripts/seed_demo.py [--reset]
"""

from __future__ import annotations

import sys

# Windows konsolu varsayilan olarak cp1254 kullaniyor; Turkce ciktinin
# bozulmamasi icin akisi UTF-8'e sabitliyoruz.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.attribution.explain import build_labour_card  # noqa: E402
from app.core.config import get_settings  # noqa: E402
from app.core.database import SessionLocal, create_schema, engine  # noqa: E402
from app.models.entities import (  # noqa: E402
    AttributionEdge,
    Base,
    Campaign,
    User,
)
from app.services import dispute as dispute_service  # noqa: E402
from app.services import ingest as ingest_service  # noqa: E402
from app.services import payout as payout_service  # noqa: E402
from app.services.registry import get_index_service  # noqa: E402

RAW = ROOT / "data" / "raw"


# ---------------------------------------------------------------------------
# Gorsel donusumleri (remix studyosunun yapacagi islerin betik karsiligi)
# ---------------------------------------------------------------------------
def jpeg_bytes(image: np.ndarray, quality: int = 92) -> bytes:
    ok, buf = cv2.imencode(".jpg", image, [cv2.IMWRITE_JPEG_QUALITY, quality])
    if not ok:
        raise RuntimeError("JPEG kodlanamadi")
    return buf.tobytes()


def burak_remix(source: np.ndarray) -> np.ndarray:
    """Kirpma + alt yazi bandi + kendi cizimi."""
    h, w = source.shape[:2]
    out = source[int(h * 0.12) : int(h * 0.88), int(w * 0.10) : int(w * 0.90)].copy()
    oh, ow = out.shape[:2]
    band = int(oh * 0.16)
    cv2.rectangle(out, (0, oh - band), (ow, oh), (24, 20, 18), -1)
    cv2.putText(
        out, "SEHRIN RENKLERI", (int(ow * 0.04), oh - band // 3),
        cv2.FONT_HERSHEY_SIMPLEX, oh / 620, (255, 255, 255), 2, cv2.LINE_AA,
    )
    # Burak'in ekledigi ozgun unsur
    cv2.circle(out, (int(ow * 0.85), int(oh * 0.18)), int(min(oh, ow) * 0.09), (60, 200, 250), -1)
    cv2.circle(out, (int(ow * 0.85), int(oh * 0.18)), int(min(oh, ow) * 0.09), (20, 20, 20), 3)
    return out


def ceyda_screenshot(source: np.ndarray) -> np.ndarray:
    """Ekran goruntusu benzetimi: kenar kirpma, olcekleme, yeniden sikistirma.

    Bu adim C2PA manifestini ve filigrani yok eder - senaryonun kritik ani.
    """
    h, w = source.shape[:2]
    out = source[int(h * 0.05) : int(h * 0.95), int(w * 0.04) : int(w * 0.96)]
    out = cv2.resize(out, None, fx=0.82, fy=0.82, interpolation=cv2.INTER_AREA)
    return cv2.imdecode(np.frombuffer(jpeg_bytes(out, 58), np.uint8), cv2.IMREAD_COLOR)


# ---------------------------------------------------------------------------
def banner(step: str, text: str) -> None:
    print(f"\n{'=' * 74}\n{step}  {text}\n{'=' * 74}")


def show_recovery(result) -> None:
    print("  Köken kurtarma hattı:")
    for entry in result.stage_log:
        mark = "BULDU " if entry["found"] else "yok   "
        print(f"    [{mark}] {entry['stage']:<10} {entry['detail']}")
    if not result.links:
        print("    → kaynak bulunamadı (özgün içerik)")
        return
    print("  Bulunan kaynaklar:")
    for link in result.links:
        coverage = (
            f"kullanılan alan %{link.visual_coverage * 100:.1f}"
            if link.visual_coverage is not None
            else "alan ölçülemedi"
        )
        print(
            f"    - {link.parent_content_id}  asama={link.stage.value:<9} "
            f"guven={link.confidence:.2f}  {coverage}"
        )
    toplam = sum(result.timings_ms.values())
    print(f"  Toplam süre: {toplam:.0f} ms  ({result.timings_ms})")


def show_card(session, content_id: str) -> dict:
    card = build_labour_card(session, content_id)
    dist = card["distribution"]
    print(f"\n  EMEK KARTI - {card['content']['title']}")
    print(f"  Brüt gelir: {dist['gross_revenue']:.2f} TL   "
          f"Komisyon: {dist['commission_amount']:.2f} TL   "
          f"Dağıtılan: {dist['distributable']:.2f} TL")
    print(f"  {'taraf':<22}{'rol':<10}{'pay':>8}{'tutar':>12}")
    print("  " + "-" * 52)
    for party in dist["parties"]:
        print(
            f"  {party['user_name']:<22}{party['role']:<10}"
            f"{party['share_pct']:>7.1f}%{party['amount']:>11.2f} TL"
        )
        for note in party["rules_applied"][:2]:
            print(f"      . {note}")
        for row in party["evidence"][:3]:
            if row["found"]:
                print(f"      + {row['label']}: {row['aciklama']}")
    if card["rules"]["log"]:
        print("  Uygulanan kurallar:")
        for line in card["rules"]["log"]:
            print(f"      . {line}")
    return card


def reset_database() -> None:
    Base.metadata.drop_all(engine)
    settings = get_settings()
    uploads = settings.upload_dir
    if uploads.exists():
        import shutil

        shutil.rmtree(uploads)
    uploads.mkdir(parents=True, exist_ok=True)


def main() -> int:
    if "--reset" in sys.argv:
        reset_database()
        print("Veritabanı ve yüklemeler sıfırlandı.")
    create_schema()

    photos = sorted(RAW.glob("*.jpg"))
    if not photos:
        raise SystemExit("Once gorsel korpusu indirin: python scripts/fetch_eval_images.py")

    session = SessionLocal()
    index = get_index_service()
    index.rebuild(session)

    # --- Aktorler ---------------------------------------------------------
    # Kimlik renkleri, temanin anlam yukledigi renklerden ayri tutulur.
    # Onceki degerler (#E8A838, #5B8DEF, #4CC38A) sirasiyla altin, zincir
    # mavisi ve dogrulama yesiliydi: Emek Karti'nda Ayse'nin pay serisi
    # para altiniyla, Ceyda'ninki "dogrulandi" yesiliyle ayni tonu
    # paylasiyordu ve renk artik bir sey soylemiyordu. Mor/turkuaz/pembe
    # hicbir durum rengiyle karismiyor.
    ayse = User(handle="ayse", display_name="Ayşe Yılmaz", accent="#B47AE0")
    burak = User(handle="burak", display_name="Burak Demir", accent="#5CC9C4")
    # Ceyda ayni zamanda moderator: insan incelemesine dusen itirazi karara
    # baglayan ve kampanya havuzunu dagitan uclar moderator yetkisi istiyor.
    # Demo verisinde atanmis moderator olmadiginda o iki ekrandaki dugmeler
    # 403 veriyordu. Dorduncu bir kullanici eklemek yerine mevcut birine rol
    # verildi; kullanici secici uc kisi kaliyor.
    ceyda = User(
        handle="ceyda", display_name="Ceyda Aksoy", accent="#E87BA8", role="moderator"
    )
    session.add_all([ayse, burak, ceyda])

    campaign = Campaign(
        brand_name="Anadolu Kahve",
        title="Şehrin Renkleri Remix Kampanyası",
        brief="Şehrinizin renklerini yakalayan içerikleri remixleyin.",
        reward_pool=50_000.0,
        commission=0.10,
        source_floor=0.15,
        creator_ceiling=0.80,
    )
    session.add(campaign)
    session.commit()

    # --- 1. Ayse ozgun icerik yukler --------------------------------------
    banner("1/5", "Ayşe özgün fotoğrafını yüklüyor")
    original_bgr = cv2.imread(str(photos[3]))
    ayse_result = ingest_service.ingest(
        session, index,
        raw_bytes=jpeg_bytes(original_bgr),
        owner=ayse,
        title="Sabah ışığı",
        caption="Kendi çektiğim kare.",
        min_source_share=0.10,
        campaign_id=campaign.id,
    )
    show_recovery(ayse_result.recovery)
    print(f"  Yayınlandı: manifest={'var' if ayse_result.content.manifest_present else 'yok'}, "
          f"filigran={ayse_result.content.watermark_tag}")

    # --- 2. Burak remixler -------------------------------------------------
    banner("2/5", "Burak remixliyor: kırpma + yazı bandı + kendi çizimi")
    ayse_published = cv2.imread(ayse_result.content.file_path)
    burak_result = ingest_service.ingest(
        session, index,
        raw_bytes=jpeg_bytes(burak_remix(ayse_published)),
        owner=burak,
        title="Şehrin Renkleri",
        caption="Ayşe'nin karesinden yola çıkarak.",
        declared_parent_id=ayse_result.content.id,
        remix_actions=["c2pa.cropped", "c2pa.drawing"],
        campaign_id=campaign.id,
    )
    show_recovery(burak_result.recovery)

    # --- 3. Ceyda ekran goruntusu alip yukluyor ---------------------------
    banner("3/5", "Ceyda ekran görüntüsü alıyor — C2PA manifesti siliniyor")
    burak_published = cv2.imread(burak_result.content.file_path)
    stripped = ceyda_screenshot(burak_published)
    print("  Ceyda'nın yüklediği dosyada içerik kimliği yok. Kaynak beyanı da yok.")
    ceyda_result = ingest_service.ingest(
        session, index,
        raw_bytes=jpeg_bytes(stripped),
        owner=ceyda,
        title="Bulduğum kare",
        caption="Akışta gördüm, paylaşıyorum.",
        campaign_id=campaign.id,
    )
    show_recovery(ceyda_result.recovery)

    # --- 4. Gelir ve dagitim ----------------------------------------------
    banner("4/5", "Kampanya ödül havuzu dağıtılıyor")
    for content, revenue in (
        (ayse_result.content, 1200.0),
        (burak_result.content, 2600.0),
        (ceyda_result.content, 4200.0),
    ):
        content.revenue = revenue
    session.commit()

    card_before = show_card(session, ceyda_result.content.id)

    campaign_result = payout_service.distribute_campaign(session, campaign.id)
    print(f"\n  Havuz {campaign_result.reward_pool:,.0f} TL dagitildi. "
          f"Platform payi {campaign_result.platform_total:,.2f} TL.")
    for row in campaign_result.per_content:
        print(f"    {row['title']:<22} agirlik %{row['weight'] * 100:.1f} "
              f"-> {row['allocation']:,.2f} TL  ({row['basis']})")

    # --- 5. Ayse itiraz ediyor --------------------------------------------
    banner("5/5", "Ayşe payına itiraz ediyor")
    ayse_edge = next(
        (
            e
            for e in session.query(AttributionEdge).filter(
                AttributionEdge.child_id == ceyda_result.content.id
            )
            if e.parent_id == ayse_result.content.id
        ),
        None,
    )
    if ayse_edge is None:
        print("  Ayse'nin Ceyda'nin icerigiyle dogrudan bagi yok; "
              "zincir uzerinden Burak araciligiyla pay aliyor.")
        ayse_edge = (
            session.query(AttributionEdge)
            .filter(AttributionEdge.parent_id == ayse_result.content.id)
            .first()
        )

    if ayse_edge is not None:
        print(f"  Itiraz edilen bag: {ayse_edge.parent_id} -> {ayse_edge.child_id}  "
              f"(kapsama %{(ayse_edge.visual_coverage or 0) * 100:.1f}, "
              f"guven {ayse_edge.confidence:.2f})")
        dispute = dispute_service.open_dispute(
            session,
            edge_id=ayse_edge.id,
            raiser=ayse,
            reason="Orijinalimin daha geniş bir bölümü kullanılmış; pay düşük hesaplandı.",
        )
        outcome = dispute_service.resolve(session, index, dispute.id)
        print(f"  Sonuc: {outcome.dispute.status.value}")
        print(f"  {outcome.summary}")
        show_card(session, ceyda_result.content.id)

    # --- Kazanc ozeti -----------------------------------------------------
    banner("ÖZET", "Kullanıcı kazançları")
    for user in (ayse, burak, ceyda):
        earnings = payout_service.earnings_for_user(session, user.id)
        print(f"  {user.display_name:<18} toplam {earnings['total']:>10,.2f} TL   "
              f"(uretici {earnings['as_creator']:,.2f} / kaynak {earnings['as_source']:,.2f})")

    session.close()
    print(f"\nVeritabani: {get_settings().database_url}")
    print("API'yi baslatmak icin: .venv/Scripts/python.exe -m uvicorn app.main:app --reload --app-dir backend")
    return 0


if __name__ == "__main__":
    sys.exit(main())
