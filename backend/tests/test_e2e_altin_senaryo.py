"""Uctan uca altin senaryo.

Juriye gosterilecek akisin tamamini calistirir ve her adimda projenin
iddia ettigi seyin gerceklestigini dogrular:

  Ayse yukler -> Burak remixler -> Ceyda ekran goruntusu alir (icerik
  kimligi silinir) -> sistem zinciri yine de kurar -> paylar olculmus
  alan oranlarina gore dagitilir -> Ayse itiraz eder.

Bu test yavastir (CLIP modeli ve geometri calisir) ama demonun
kirilmadigini garanti eden tek sey budur.
"""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
import pytest

from app.attribution import chain as chain_builder
from app.attribution.explain import build_labour_card
from app.core.database import SessionLocal, create_schema
from app.models.entities import AttributionEdge, Campaign, LinkStatus, User
from app.services import dispute as dispute_service
from app.services import ingest as ingest_service
from app.services import payout as payout_service
from app.services.registry import IndexService

RAW = Path(__file__).resolve().parents[2] / "data" / "raw"


def jpeg(image: np.ndarray, quality: int = 92) -> bytes:
    ok, buf = cv2.imencode(".jpg", image, [cv2.IMWRITE_JPEG_QUALITY, quality])
    assert ok
    return buf.tobytes()


def remix(source: np.ndarray) -> np.ndarray:
    """Burak: kirpma + yazi bandi + kendi cizimi."""
    h, w = source.shape[:2]
    out = source[int(h * 0.12) : int(h * 0.88), int(w * 0.10) : int(w * 0.90)].copy()
    oh, ow = out.shape[:2]
    band = int(oh * 0.16)
    cv2.rectangle(out, (0, oh - band), (ow, oh), (24, 20, 18), -1)
    cv2.putText(out, "REMIX", (20, oh - band // 3), cv2.FONT_HERSHEY_SIMPLEX,
                oh / 620, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.circle(out, (int(ow * 0.85), int(oh * 0.18)), int(min(oh, ow) * 0.09), (60, 200, 250), -1)
    return out


def screenshot(source: np.ndarray) -> np.ndarray:
    """Ceyda: kenar kirpma + olcekleme + agir yeniden sikistirma."""
    h, w = source.shape[:2]
    out = source[int(h * 0.05) : int(h * 0.95), int(w * 0.04) : int(w * 0.96)]
    out = cv2.resize(out, None, fx=0.82, fy=0.82, interpolation=cv2.INTER_AREA)
    return cv2.imdecode(np.frombuffer(jpeg(out, 58), np.uint8), cv2.IMREAD_COLOR)


@pytest.fixture(scope="module")
def senaryo():
    """Altin senaryoyu bir kez kurar; testler sonucu paylasir."""
    photos = sorted(RAW.glob("*.jpg"))
    if not photos:
        pytest.skip("gorsel korpusu yok: python scripts/fetch_eval_images.py")

    create_schema()
    session = SessionLocal()
    index = IndexService()

    ayse = User(handle="t_ayse", display_name="Ayse", accent="#E8A838")
    burak = User(handle="t_burak", display_name="Burak", accent="#5B8DEF")
    ceyda = User(handle="t_ceyda", display_name="Ceyda", accent="#4CC38A")
    campaign = Campaign(
        brand_name="Test Marka", title="Test Kampanya", reward_pool=10_000.0,
        commission=0.10, source_floor=0.15, creator_ceiling=0.80,
    )
    session.add_all([ayse, burak, ceyda, campaign])
    session.commit()

    original = cv2.imread(str(photos[3]))
    r_ayse = ingest_service.ingest(
        session, index, raw_bytes=jpeg(original), owner=ayse,
        title="Orijinal", campaign_id=campaign.id,
    )
    r_burak = ingest_service.ingest(
        session, index, raw_bytes=jpeg(remix(cv2.imread(r_ayse.content.file_path))),
        owner=burak, title="Remix", declared_parent_id=r_ayse.content.id,
        remix_actions=["c2pa.cropped"], campaign_id=campaign.id,
    )
    r_ceyda = ingest_service.ingest(
        session, index, raw_bytes=jpeg(screenshot(cv2.imread(r_burak.content.file_path))),
        owner=ceyda, title="Ekran goruntusu", campaign_id=campaign.id,
    )

    for content, revenue in ((r_ayse.content, 1200.0), (r_burak.content, 2600.0),
                             (r_ceyda.content, 4200.0)):
        content.revenue = revenue
    session.commit()

    yield {
        "session": session, "index": index, "campaign": campaign,
        "ayse": ayse, "burak": burak, "ceyda": ceyda,
        "r_ayse": r_ayse, "r_burak": r_burak, "r_ceyda": r_ceyda,
    }
    session.close()


# ---------------------------------------------------------------------------
# 1. Ozgun icerik
# ---------------------------------------------------------------------------
def test_ozgun_icerik_kaynak_bulmaz_ve_kimlikle_yayinlanir(senaryo):
    result = senaryo["r_ayse"]
    assert result.recovery.links == [], "ozgun icerige kaynak atanmamali"
    assert result.content.manifest_present, "yayinlanan icerikte C2PA manifesti olmali"
    assert result.content.watermark_tag, "filigran gomulmus olmali"


# ---------------------------------------------------------------------------
# 2. Remix
# ---------------------------------------------------------------------------
def test_remix_kaynagina_baglanir_ve_alan_olculur(senaryo):
    result = senaryo["r_burak"]
    assert len(result.recovery.links) >= 1
    link = next(
        l for l in result.recovery.links
        if l.parent_content_id == senaryo["r_ayse"].content.id
    )
    assert link.geometry_verified, "geometri dogrulamasi calismali"
    # Kirpma + yazi bandi + cizim sonrasi kaynagin buyuk kismi duruyor
    # ama tamami degil.
    assert 0.60 < link.visual_coverage < 0.98, (
        f"olculen kapsama makul araligin disinda: {link.visual_coverage}"
    )
    assert link.confidence > 0.85


# ---------------------------------------------------------------------------
# 3. Kritik an: kimlik silinmis icerik
# ---------------------------------------------------------------------------
def test_ekran_goruntusunde_icerik_kimligi_kayboluyor(senaryo):
    """Senaryonun on kabulu: manifest gercekten siliniyor."""
    assert not senaryo["r_ceyda"].incoming_manifest, (
        "ekran goruntusu benzetimi manifesti silmeliydi; silmediyse senaryo "
        "sistemin asil yetenegini gostermiyor demektir"
    )


def test_kimlik_silinmis_icerikte_zincir_yeniden_kurulur(senaryo):
    result = senaryo["r_ceyda"]
    bulunanlar = {l.parent_content_id for l in result.recovery.links}
    assert senaryo["r_burak"].content.id in bulunanlar, "dogrudan kaynak bulunmali"
    assert any(l.geometry_verified for l in result.recovery.links)
    assert result.content.provenance_recovered, (
        "beyan ve manifest olmadan bulunan koken 'yeniden kuruldu' olarak "
        "isaretlenmeli - arayuzdeki rozet ve demo anlatisi buna dayaniyor"
    )


def test_emek_karti_kimligin_silindigini_dogru_anlatir(senaryo):
    """Yayinlarken biz imzaladigimiz icin manifest her zaman vardir;
    kart bunu 'kimlik korunmustu' diye sunmamali."""
    card = build_labour_card(senaryo["session"], senaryo["r_ceyda"].content.id)
    prov = card["provenance"]
    assert prov["durum"] == "yeniden_kuruldu"
    assert prov["incoming_manifest_present"] is False
    assert prov["manifest_present"] is True, "yayinlanan surum imzalanmis olmali"
    assert "yeniden kuruldu" in prov["aciklama"]


def test_zincir_geciski_indirgeme_ile_dogru_derinlige_yerlesir(senaryo):
    """Ayse, dogrudan degil Burak uzerinden sayilmali.

    Geometri Ayse'yi Ceyda'nin icerigainde de bulur (pikselleri oraya
    Burak araciligiyla ulasmistir). Bu dogrudan bag pay hesabina
    girerse ayni pikseller iki kez odullendirilir.
    """
    session = senaryo["session"]
    leaf = senaryo["r_ceyda"].content.id
    nodes = {n.content_id: n for n in chain_builder.build_chain(session, leaf)}

    ayse_id = senaryo["r_ayse"].content.id
    burak_id = senaryo["r_burak"].content.id
    assert burak_id in nodes and nodes[burak_id].depth == 1
    assert ayse_id in nodes, "Ayse zincirde olmali"
    assert nodes[ayse_id].depth == 2, "Ayse Burak uzerinden, derinlik 2'de sayilmali"


def test_ozel_kapsamalar_bire_toplanir(senaryo):
    """Ozel kapsamalar gorselin tam bir bolutlemesi olmali."""
    session = senaryo["session"]
    leaf = senaryo["r_ceyda"].content.id
    nodes = chain_builder.build_chain(session, leaf)
    kaynaklar = sum(n.coverage for n in nodes)
    assert kaynaklar <= 1.0 + 1e-6, (
        f"ozel kapsamalar toplami 1.0'i asamaz, {kaynaklar} bulundu - "
        "ic ice gecmis alanlar cift sayiliyor olabilir"
    )
    assert kaynaklar > 0.5, "zincirin buyuk bolumu kaynaklardan gelmeli"


# ---------------------------------------------------------------------------
# 4. Paylar ve odeme
# ---------------------------------------------------------------------------
def test_emek_karti_her_payi_gerekcelendirir(senaryo):
    card = build_labour_card(senaryo["session"], senaryo["r_ceyda"].content.id)
    parties = card["distribution"]["parties"]
    roles = {p["role"] for p in parties}
    assert {"creator", "source", "platform"} <= roles

    for party in parties:
        if party["role"] == "source":
            assert party["factors"]["kapsama"] >= 0
            assert party["factors"]["guven"] > 0
            assert party["evidence"], "her kaynak payinin kaniti olmali"
            assert any(row["aciklama"] for row in party["evidence"])

    toplam = sum(p["share"] for p in parties if p["role"] != "platform")
    assert toplam == pytest.approx(1.0, abs=1e-4)


def test_orijinal_uretici_zincirin_ucundan_pay_alir(senaryo):
    """Projenin varlik sebebi: Ayse, hic tanimadigi Ceyda'nin
    gonderisinden pay almali."""
    card = build_labour_card(senaryo["session"], senaryo["r_ceyda"].content.id)
    ayse_pay = next(
        (
            p
            for p in card["distribution"]["parties"]
            if p["content_id"] == senaryo["r_ayse"].content.id
        ),
        None,
    )
    assert ayse_pay is not None, "Ayse dagilimda yer almali"
    assert ayse_pay["share"] > 0.10, (
        f"Ayse'nin payi anlamli olmali, {ayse_pay['share']} bulundu"
    )
    assert ayse_pay["amount"] > 0


def test_kampanya_havuzu_tamamen_dagitilir(senaryo):
    result = payout_service.distribute_campaign(
        senaryo["session"], senaryo["campaign"].id
    )
    assert result.total_paid + result.platform_total == pytest.approx(
        result.reward_pool, abs=1.0
    )
    assert len(result.per_content) == 3


def test_kazanclar_role_gore_ayrilir(senaryo):
    session = senaryo["session"]
    ayse = payout_service.earnings_for_user(session, senaryo["ayse"].id)
    ceyda = payout_service.earnings_for_user(session, senaryo["ceyda"].id)
    assert ayse["as_source"] > 0, "Ayse kaynak olarak kazanmali"
    assert ceyda["as_creator"] > 0, "Ceyda uretici olarak kazanmali"


# ---------------------------------------------------------------------------
# 5. Itiraz
# ---------------------------------------------------------------------------
def test_itiraz_yeniden_olcum_tetikler_ve_sonuclanir(senaryo):
    session = senaryo["session"]
    edge = (
        session.query(AttributionEdge)
        .filter(AttributionEdge.parent_id == senaryo["r_ayse"].content.id)
        .first()
    )
    assert edge is not None

    dispute = dispute_service.open_dispute(
        session, edge_id=edge.id, raiser=senaryo["ayse"],
        reason="Orijinalimin daha genis bolumu kullanilmis.",
    )
    assert edge.status == LinkStatus.DISPUTED

    outcome = dispute_service.resolve(session, senaryo["index"], dispute.id)
    assert outcome.dispute.resolution["summary"]
    assert "before" in outcome.dispute.resolution
    assert "after" in outcome.dispute.resolution
    # Itiraz cozuldukten sonra bag artik "itirazli" durumda kalmamali.
    assert edge.status != LinkStatus.DISPUTED or outcome.dispute.status.value == "escalated"


def test_cozulemeyen_itiraz_insan_incelemesine_dusebilir(senaryo):
    """Kuyruk uc noktasi calismali (bos olabilir)."""
    kuyruk = dispute_service.review_queue(senaryo["session"])
    assert isinstance(kuyruk, list)
