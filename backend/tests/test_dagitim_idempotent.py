"""Yeniden dagitim degistirir, eklemez.

Neden ayri bir dosya
--------------------
Bu, para ile ilgili bir dogruluk sorusu ve cevabi *veritabaninda*:
dagitim uclarinin dondugu govde, satirlar ikiye katlansa bile aynen
ayni goruntuyu verir. Dolayisiyla olculecek sey yanit degil, `Payout`
tablosunun kendisi.

Testler koken kurtarma hattini hic calistirmiyor: `Content` satirlari
dogrudan yaziliyor, gorsel dosyasi yok. Dagitim yalnizca baglari ve
sahipleri okuyor, dolayisiyla korpus da gerekmiyor - bu dosya korpussuz
bir makinede de kosuyor.
"""

from __future__ import annotations

import uuid

import pytest
from sqlalchemy import select

from app.core.database import SessionLocal, create_schema
from app.models.entities import (
    AttributionEdge,
    Campaign,
    Content,
    LinkStage,
    LinkStatus,
    Payout,
    User,
)
from app.services import payout as payout_service


def _icerik(owner_id: str, ident: str, **ek) -> Content:
    """Asgari gecerli `Content`. Parmak izi alanlari dolduruluyor cunku
    sutunlar zorunlu; degerleri bu testlerde okunmuyor."""
    return Content(
        id=ident,
        owner_id=owner_id,
        title=f"{ident} başlık",
        file_path=f"/yok/{ident}.jpg",
        width=800,
        height=600,
        content_hash=ident.ljust(64, "0"),
        phash="0" * 16,
        dhash="0" * 16,
        whash="0" * 16,
        **ek,
    )


@pytest.fixture()
def zincir():
    """Ayse -> Burak zinciri, tek kampanya. Her testte temiz kurulur.

    Testler ayni veritabanini paylasiyor (conftest tek bir gecici dosya
    kuruyor), bu yuzden her kimlik benzersiz uretiliyor: kullanicilar,
    icerikler ve kampanya testler arasi hicbir sey paylasmiyor.
    """
    create_schema()
    session = SessionLocal()
    ek = uuid.uuid4().hex[:8]

    ayse = User(handle=f"idem_ayse_{ek}", display_name="Ayşe Kaynak")
    burak = User(handle=f"idem_burak_{ek}", display_name="Burak Türev")
    session.add_all([ayse, burak])
    session.flush()

    kampanya = Campaign(
        brand_name="Idempotent Marka",
        title="Tekrar dağıtım testi",
        reward_pool=10_000.0,
    )
    session.add(kampanya)
    session.flush()

    kaynak = _icerik(ayse.id, f"idkaynak{ek}")
    turev = _icerik(
        burak.id,
        f"idturev_{ek}",
        revenue=1000.0,
        campaign_id=kampanya.id,
    )
    session.add_all([kaynak, turev])
    session.flush()

    session.add(
        AttributionEdge(
            child_id=turev.id,
            parent_id=kaynak.id,
            stage=LinkStage.CLIP,
            status=LinkStatus.CONFIRMED,
            confidence=0.9,
            visual_coverage=0.6,
            source_usage=0.5,
        )
    )
    session.commit()

    try:
        yield session, {
            "ayse": ayse.id,
            "burak": burak.id,
            "kampanya": kampanya.id,
            "kaynak": kaynak.id,
            "turev": turev.id,
        }
    finally:
        session.close()


def _odemeler(session, **filtre) -> list[Payout]:
    stmt = select(Payout)
    for alan, deger in filtre.items():
        stmt = stmt.where(getattr(Payout, alan) == deger)
    return list(session.scalars(stmt))


# ---------------------------------------------------------------------------
# Gonderi dagitimi
# ---------------------------------------------------------------------------
def test_ayni_gonderi_iki_kez_dagitilinca_odemeler_katlanmiyor(zincir):
    session, v = zincir

    payout_service.distribute_content(session, v["turev"], 1000.0)
    session.commit()
    ilk = _odemeler(session, content_id=v["turev"])

    payout_service.distribute_content(session, v["turev"], 1000.0)
    session.commit()
    ikinci = _odemeler(session, content_id=v["turev"])

    assert len(ikinci) == len(ilk)
    assert sum(o.amount for o in ikinci) == pytest.approx(
        sum(o.amount for o in ilk)
    )
    # Satirlar gercekten yenilendi - eskiler silinip yerine yazildi.
    assert {o.id for o in ikinci}.isdisjoint({o.id for o in ilk})


def test_yeniden_dagitim_kazanci_ikiye_katlamiyor(zincir):
    """`GET /users/{id}/earnings` bu tabloyu topluyor."""
    session, v = zincir

    payout_service.distribute_content(session, v["turev"], 1000.0)
    session.commit()
    ilk = payout_service.earnings_for_user(session, v["ayse"])
    assert ilk["total"] > 0, "kaynak zaten pay almalı"

    payout_service.distribute_content(session, v["turev"], 1000.0)
    session.commit()
    ikinci = payout_service.earnings_for_user(session, v["ayse"])

    assert ikinci == ilk


def test_yeniden_dagitim_yeni_geliri_yansitiyor(zincir):
    """Silip yeniden yazmak, *guncellemeyi* de yapmali.

    Sadece "ikinci cagri hicbir sey yapmasin" seklinde cozulseydi bu
    test kirmizi olurdu; demo akisi gelirin degistirilip yeniden
    dagitilmasina dayaniyor.
    """
    session, v = zincir

    payout_service.distribute_content(session, v["turev"], 1000.0)
    session.commit()
    dusuk = payout_service.earnings_for_user(session, v["ayse"])["total"]

    payout_service.distribute_content(session, v["turev"], 4000.0)
    session.commit()
    yuksek = payout_service.earnings_for_user(session, v["ayse"])["total"]

    assert yuksek == pytest.approx(dusuk * 4, rel=0.02)


def test_temizlik_baska_gonderinin_odemesine_dokunmuyor(zincir):
    """Temizlik gonderi kapsaminda kalmali.

    "Yeniden dagitimda tabloyu temizle" en kaba haliyle yazilirsa
    (`delete from payouts`) yukaridaki testlerin hepsi yesil kalir ama
    her dagitim, ilgisiz gonderilerin odemelerini silerdi.
    """
    session, v = zincir

    payout_service.distribute_content(session, v["turev"], 1000.0)
    session.commit()
    turev_odemeleri = {o.id for o in _odemeler(session, content_id=v["turev"])}
    assert turev_odemeleri

    # Ayni sahibin, ayni veritabanindaki bagimsiz bir gonderisi.
    bagimsiz = _icerik(v["ayse"], f"idbagim_{uuid.uuid4().hex[:8]}", revenue=300.0)
    session.add(bagimsiz)
    session.commit()

    payout_service.distribute_content(session, bagimsiz.id, 300.0)
    session.commit()

    assert {o.id for o in _odemeler(session, content_id=v["turev"])} == turev_odemeleri
    assert _odemeler(session, content_id=bagimsiz.id)


# ---------------------------------------------------------------------------
# Kampanya dagitimi
# ---------------------------------------------------------------------------
def test_kampanya_iki_kez_dagitilinca_havuz_asilmiyor(zincir):
    session, v = zincir

    payout_service.distribute_campaign(session, v["kampanya"])
    ilk = payout_service.earnings_for_user(session, v["ayse"])

    payout_service.distribute_campaign(session, v["kampanya"])
    ikinci = payout_service.earnings_for_user(session, v["ayse"])

    assert ikinci == ilk

    odenen = sum(
        o.amount for o in _odemeler(session, campaign_id=v["kampanya"])
    )
    kampanya = session.get(Campaign, v["kampanya"])
    assert odenen <= kampanya.reward_pool + 0.05


def test_kampanyadan_cikarilmis_gonderinin_odemesi_temizleniyor(zincir):
    """Gonderi bazli temizlik burada yetmiyor.

    Kampanyadan cikarilan gonderi ikinci dagitimda hic ziyaret
    edilmiyor; eski odemesi kampanya toplaminda asili kaliyor ve havuz
    asiliyor. Bu yuzden `distribute_campaign` kampanyanin *tum*
    odemelerini basta siliyor.
    """
    session, v = zincir

    payout_service.distribute_campaign(session, v["kampanya"])
    assert _odemeler(session, campaign_id=v["kampanya"], content_id=v["turev"])

    # Gonderi kampanyadan cikariliyor, yerine baskasi giriyor.
    turev = session.get(Content, v["turev"])
    turev.campaign_id = None
    yeni = _icerik(
        v["burak"],
        f"idyeni_{uuid.uuid4().hex[:8]}",
        revenue=1000.0,
        campaign_id=v["kampanya"],
    )
    session.add(yeni)
    session.commit()

    payout_service.distribute_campaign(session, v["kampanya"])

    assert not _odemeler(session, campaign_id=v["kampanya"], content_id=v["turev"])
    odenen = sum(o.amount for o in _odemeler(session, campaign_id=v["kampanya"]))
    kampanya = session.get(Campaign, v["kampanya"])
    assert odenen <= kampanya.reward_pool + 0.05
