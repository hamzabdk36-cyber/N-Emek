"""Emek Karti uretiminin maliyeti.

Buradaki iddialar gozle gorulemez: kart her iki halde de ayni sayilari
uretiyor, fark yalnizca kac kez hesaplandigi ve kac sorgu atildigi.
Dolayisiyla bir gerileme (alt grafigin yine iki kez toplanmasi, ya da
dugum basina `session.get` donusu) hicbir ciktiyi bozmadan geri
gelebilir ve ancak zincir uzadiginda fark edilirdi.

Iki sey sinaniyor:
  * alt grafik ve gecisli indirgeme istek basina **bir kez** hesaplaniyor
  * icerik/kullanici sorgulari zincir uzunluguyla **artmiyor** (N+1 yok)
"""

from __future__ import annotations

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker

from app.attribution import chain as chain_builder
from app.attribution.explain import build_labour_card
from app.models.entities import (
    AttributionEdge,
    Base,
    Content,
    LinkStage,
    LinkStatus,
    User,
)


@pytest.fixture(scope="module")
def motor(tmp_path_factory):
    """Bu modul icin ayri veritabani - sorgu sayimi baska verilerle kirlenmesin."""
    yol = tmp_path_factory.mktemp("maliyet") / "maliyet.db"
    return create_engine(f"sqlite:///{yol.as_posix()}")


@pytest.fixture(scope="module")
def zincirler(motor):
    """İki zincir kurar: kısa (3 kaynak) ve uzun (8 kaynak).

    Duz zincir: k0 <- k1 <- ... <- kN, yaprak k0.
    """
    Base.metadata.create_all(motor)
    Session_ = sessionmaker(bind=motor, expire_on_commit=False)
    session = Session_()

    kimlikler = {}
    for ad, uzunluk in (("kisa", 3), ("uzun", 8)):
        sahipler = []
        for i in range(uzunluk + 1):
            kullanici = User(handle=f"{ad}_u{i}", display_name=f"{ad} kullanıcı {i}")
            session.add(kullanici)
            sahipler.append(kullanici)
        session.flush()

        icerikler = []
        for i in range(uzunluk + 1):
            content = Content(
                id=f"{ad}icerik{i:06d}",
                owner_id=sahipler[i].id,
                title=f"{ad} içerik {i}",
                file_path=f"/yok/{ad}-{i}.jpg",
                width=800,
                height=600,
                content_hash=f"{ad}-ozet-{i}",
                phash="0" * 16,
                dhash="0" * 16,
                whash="0" * 16,
            )
            session.add(content)
            icerikler.append(content)
        session.flush()

        # k0 <- k1 <- k2 ... (cocuk, ebeveyn)
        for i in range(uzunluk):
            session.add(
                AttributionEdge(
                    child_id=icerikler[i].id,
                    parent_id=icerikler[i + 1].id,
                    stage=LinkStage.CLIP,
                    status=LinkStatus.CONFIRMED,
                    confidence=0.9,
                    visual_coverage=0.8,
                    source_usage=0.7,
                )
            )
        kimlikler[ad] = icerikler[0].id

    session.commit()
    session.close()
    return kimlikler


def yeni_oturum(motor) -> Session:
    """Her olcum temiz bir oturumla: kimlik haritasi sayimi bozmasin."""
    return sessionmaker(bind=motor, expire_on_commit=False)(),


@pytest.fixture()
def sorgu_sayaci(motor):
    """Belirli bir tabloya atilan SELECT sayisini olcer."""

    def olc(tablo: str, fn) -> int:
        sayac = {"n": 0}

        def dinle(conn, cursor, statement, params, context, executemany):
            if f"FROM {tablo}" in statement:
                sayac["n"] += 1

        event.listen(motor, "before_cursor_execute", dinle)
        try:
            fn()
        finally:
            event.remove(motor, "before_cursor_execute", dinle)
        return sayac["n"]

    return olc


# ---------------------------------------------------------------------------
class TestTekrarlananHesap:
    def test_alt_grafik_istek_basina_bir_kez_toplanıyor(
        self, motor, zincirler, monkeypatch
    ):
        """`build_chain` ve zincir görünümü aynı alt grafiği paylaşıyor."""
        cagri = {"toplama": 0, "indirgeme": 0}
        orij_toplama = chain_builder._collect_subgraph
        orij_indirgeme = chain_builder._redundant_edges

        def sayan_toplama(*a, **k):
            cagri["toplama"] += 1
            return orij_toplama(*a, **k)

        def sayan_indirgeme(*a, **k):
            cagri["indirgeme"] += 1
            return orij_indirgeme(*a, **k)

        monkeypatch.setattr(chain_builder, "_collect_subgraph", sayan_toplama)
        monkeypatch.setattr(chain_builder, "_redundant_edges", sayan_indirgeme)

        (session,) = yeni_oturum(motor)
        try:
            build_labour_card(session, zincirler["uzun"])
        finally:
            session.close()

        assert cagri["toplama"] == 1, "alt grafik birden fazla kez toplandı"
        assert cagri["indirgeme"] == 1, "geçişli indirgeme birden fazla kez koşuldu"

    def test_indirgenmis_kume_yeniden_hesaplanmiyor(self, motor, zincirler):
        """`Subgraph.reduced` önbellekli: her erişimde yeniden filtrelenmiyor."""
        (session,) = yeni_oturum(motor)
        try:
            alt = chain_builder.collect(session, zincirler["kisa"])
            assert alt.reduced is alt.reduced
        finally:
            session.close()

    def test_paylasilan_alt_grafik_sonucu_degistirmiyor(self, motor, zincirler):
        """Hızlandırma davranışı değiştirmemeli: iki yol aynı kartı üretmeli."""
        (session,) = yeni_oturum(motor)
        try:
            paylasimli = build_labour_card(session, zincirler["uzun"])
        finally:
            session.close()

        (session,) = yeni_oturum(motor)
        try:
            # Alt grafigi vermeden: her cagri kendi hesabini yapar.
            nodes = chain_builder.build_chain(session, zincirler["uzun"])
        finally:
            session.close()

        assert [n["id"] for n in paylasimli["chain"]["nodes"]]
        assert {n.content_id for n in nodes} == {
            n["id"]
            for n in paylasimli["chain"]["nodes"]
            if n["contributes"] and n["role"] == "source"
        }


class TestSorguSayisi:
    def test_icerik_sorgulari_zincir_uzunluguyla_artmiyor(
        self, motor, zincirler, sorgu_sayaci
    ):
        """N+1 koruması: düğüm başına `session.get` dönerse bu test kırılır."""

        def kart(leaf_id):
            (session,) = yeni_oturum(motor)
            try:
                build_labour_card(session, leaf_id)
            finally:
                session.close()

        kisa = sorgu_sayaci("contents", lambda: kart(zincirler["kisa"]))
        uzun = sorgu_sayaci("contents", lambda: kart(zincirler["uzun"]))

        assert uzun == kisa, (
            f"içerik sorgusu zincirle büyüyor: 3 kaynakta {kisa}, "
            f"8 kaynakta {uzun} sorgu"
        )

    def test_kullanici_sorgulari_zincir_uzunluguyla_artmiyor(
        self, motor, zincirler, sorgu_sayaci
    ):
        def kart(leaf_id):
            (session,) = yeni_oturum(motor)
            try:
                build_labour_card(session, leaf_id)
            finally:
                session.close()

        kisa = sorgu_sayaci("users", lambda: kart(zincirler["kisa"]))
        uzun = sorgu_sayaci("users", lambda: kart(zincirler["uzun"]))

        assert uzun == kisa, (
            f"kullanıcı sorgusu zincirle büyüyor: 3 kaynakta {kisa}, "
            f"8 kaynakta {uzun} sorgu"
        )

    def test_toplu_cekim_tek_sorgu_atiyor(self, motor, zincirler, sorgu_sayaci):
        (session,) = yeni_oturum(motor)
        try:
            alt = chain_builder.collect(session, zincirler["uzun"])
            kimlikler = list(alt.edges)

            icerikler = {}

            def cek():
                icerikler.update(chain_builder.fetch_contents(session, kimlikler))

            sayi = sorgu_sayaci("contents", cek)

            assert len(kimlikler) > 1
            assert sayi == 1, f"{len(kimlikler)} kimlik için {sayi} sorgu atıldı"
            assert len(icerikler) == len(kimlikler)
        finally:
            session.close()

    def test_bos_listede_sorgu_atilmiyor(self, motor, sorgu_sayaci):
        (session,) = yeni_oturum(motor)
        try:
            assert sorgu_sayaci("contents", lambda: chain_builder.fetch_contents(session, [])) == 0
            assert sorgu_sayaci("users", lambda: chain_builder.fetch_owners(session, [])) == 0
        finally:
            session.close()
