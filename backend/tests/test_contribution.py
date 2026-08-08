"""Katki payi motorunun degismez kurallari.

Bu testler formulun matematiksel ozelliklerini sabitler. Esikler
degistiginde bu testler kirilmali - degerlerin degismesi normaldir ama
"paylar 1.0'a toplanir" veya "derin kaynak daha az alir" gibi kurallar
asla bozulmamalidir.
"""

from __future__ import annotations

import pytest

from app.attribution.contribution import (
    ChainNode,
    Distribution,
    LeafInfo,
    Rules,
    compute_shares,
)

LEAF = LeafInfo(content_id="leaf", owner_id="u_ceyda", owner_name="Ceyda")


def rules(**overrides) -> Rules:
    base = Rules(
        commission=0.10,
        creator_floor=0.20,
        creator_ceiling=0.85,
        source_floor=0.0,
        min_payout_share=0.01,
        chain_damping=0.50,
        coverage_exponent=1.0,
        confidence_exponent=1.0,
        unverified_coverage=0.35,
    )
    for key, value in overrides.items():
        setattr(base, key, value)
    return base


def node(content_id="src", depth=1, coverage=0.5, confidence=1.0, **kw) -> ChainNode:
    return ChainNode(
        content_id=content_id,
        owner_id=f"u_{content_id}",
        owner_name=content_id.title(),
        depth=depth,
        coverage=coverage,
        confidence=confidence,
        **kw,
    )


def assert_sums_to_one(dist: Distribution) -> None:
    """Platform komisyonu haric tum paylar tam olarak 1.0'a toplanmali."""
    assert dist.total_share() == pytest.approx(1.0, abs=1e-6)


# ---------------------------------------------------------------------------
# Temel davranis
# ---------------------------------------------------------------------------
def test_kaynak_yoksa_uretici_tamamini_alir():
    dist = compute_shares(LEAF, [], revenue=1000.0, rules=rules())
    assert dist.creator.share == pytest.approx(1.0)
    assert dist.sources == []
    assert_sums_to_one(dist)


def test_uretici_tavani_kaynak_yokken_uygulanmaz():
    """Tavan, kaynak payini korumak icin var. Kaynak yoksa anlamsizdir."""
    dist = compute_shares(LEAF, [], revenue=1000.0, rules=rules(creator_ceiling=0.85))
    assert dist.creator.share == pytest.approx(1.0)


def test_tek_kaynak_agirligi_carpimsal_formulden_gelir():
    dist = compute_shares(
        LEAF, [node(coverage=0.40, confidence=0.90, depth=1)], 1000.0, rules()
    )
    # 0.40 * 0.90 * 0.5^0 = 0.36
    assert dist.sources[0].share == pytest.approx(0.36, abs=1e-6)
    assert dist.creator.share == pytest.approx(0.64, abs=1e-6)
    assert_sums_to_one(dist)


@pytest.mark.parametrize(
    "chain",
    [
        [],
        [node()],
        [node("a", coverage=0.9), node("b", depth=2, coverage=0.8)],
        [node(f"s{i}", coverage=0.7, depth=i + 1) for i in range(5)],
        [node("tiny", coverage=0.001, confidence=0.4)],
    ],
)
def test_paylar_her_zaman_bire_toplanir(chain):
    dist = compute_shares(LEAF, chain, 1000.0, rules())
    assert_sums_to_one(dist)
    assert all(p.share >= 0 for p in dist.parties)


# ---------------------------------------------------------------------------
# Zincir sonumlemesi
# ---------------------------------------------------------------------------
def test_derin_kaynak_daha_az_alir():
    """Ayni kapsama ve guvende, zincirde geride olan kaynak daha az almali."""
    chain = [
        node("yakin", depth=1, coverage=0.5),
        node("orta", depth=2, coverage=0.5),
        node("uzak", depth=3, coverage=0.5),
    ]
    dist = compute_shares(LEAF, chain, 1000.0, rules())
    shares = {p.content_id: p.share for p in dist.sources}
    assert shares["yakin"] > shares["orta"] > shares["uzak"]
    # Her adimda tam olarak sonumleme katsayisi kadar azalmali.
    # Tolerans, paylarin 6 basamaga yuvarlanmasindan gelen sapmayi kapsar.
    assert shares["orta"] == pytest.approx(shares["yakin"] * 0.5, abs=1e-5)
    assert shares["uzak"] == pytest.approx(shares["orta"] * 0.5, abs=1e-5)


def test_sonumleme_kapatilabilir():
    chain = [node("a", depth=1, coverage=0.3), node("b", depth=2, coverage=0.3)]
    dist = compute_shares(LEAF, chain, 1000.0, rules(chain_damping=1.0))
    shares = [p.share for p in dist.sources]
    assert shares[0] == pytest.approx(shares[1])


# ---------------------------------------------------------------------------
# Tabanlar ve tavanlar
# ---------------------------------------------------------------------------
def test_uretici_tabani_asla_ihlal_edilmez():
    """Kaynaklar ne kadar cok yer kaplarsa kaplasin uretici tabanini alir."""
    chain = [node(f"s{i}", coverage=1.0, confidence=1.0, depth=1) for i in range(4)]
    dist = compute_shares(LEAF, chain, 1000.0, rules(creator_floor=0.20))
    assert dist.creator.share == pytest.approx(0.20, abs=1e-6)
    assert_sums_to_one(dist)
    assert any("taban" in line for line in dist.rules_log)


def test_uretici_tavani_kucuk_kaynagi_korur():
    """Kaynak varken uretici tavani asamaz; fark kaynaga gider."""
    dist = compute_shares(
        LEAF, [node(coverage=0.02, confidence=0.5)], 1000.0, rules(creator_ceiling=0.85)
    )
    assert dist.creator.share == pytest.approx(0.85, abs=1e-6)
    assert dist.sources[0].share == pytest.approx(0.15, abs=1e-6)
    assert any("tavan" in line for line in dist.rules_log)


def test_kampanya_kaynak_tabani_uygulanir():
    r = rules(source_floor=0.30, creator_ceiling=1.0)
    dist = compute_shares(LEAF, [node(coverage=0.10, confidence=0.5)], 1000.0, r)
    assert dist.sources[0].share == pytest.approx(0.30, abs=1e-6)
    assert any("Kampanya kuralı" in line for line in dist.rules_log)


def test_kampanya_tabani_birden_fazla_kaynaga_oranli_dagilir():
    r = rules(source_floor=0.40, creator_ceiling=1.0)
    chain = [node("buyuk", coverage=0.20), node("kucuk", coverage=0.10)]
    dist = compute_shares(LEAF, chain, 1000.0, r)
    shares = {p.content_id: p.share for p in dist.sources}
    assert sum(shares.values()) == pytest.approx(0.40, abs=1e-6)
    # Oran korunmali: buyuk kaynak kucugun iki kati almali.
    assert shares["buyuk"] == pytest.approx(shares["kucuk"] * 2, abs=1e-5)


# ---------------------------------------------------------------------------
# Guven ve belirsizlik
# ---------------------------------------------------------------------------
def test_dusuk_guven_kaynagin_payini_dusurur_fark_ureticide_kalir():
    """Belirsizlik ureticide kalir; kaynak itiraz edip kanit sunabilir."""
    yuksek = compute_shares(LEAF, [node(coverage=0.6, confidence=0.99)], 1000.0, rules())
    dusuk = compute_shares(LEAF, [node(coverage=0.6, confidence=0.45)], 1000.0, rules())
    assert dusuk.sources[0].share < yuksek.sources[0].share
    assert dusuk.creator.share > yuksek.creator.share


def test_olculemeyen_kapsama_ihtiyatli_tavani_asamaz():
    r = rules(unverified_coverage=0.35)
    dist = compute_shares(
        LEAF, [node(coverage=0.95, confidence=1.0, geometry_verified=False)], 1000.0, r
    )
    # Olcum yoksa beyan edilen 0.95 gecmez, ihtiyatli tavan uygulanir.
    assert dist.sources[0].share == pytest.approx(0.35, abs=1e-6)
    assert any("ölçülemedi" in n for n in dist.sources[0].factors["notlar"])


def test_olculemeyen_zincirde_ihtiyatli_varsayim_iki_kez_inmez():
    """Cok adimli zincirde chain katmani zaten ihtiyatli carpani uygulamis
    olabilir; contribution bunu tekrar uygulamamali, yalnizca tavanlamali."""
    r = rules(unverified_coverage=0.35)
    # 0.5 (olculmus adim) x 0.35 (olculememis adim) = 0.175 gelmis olsun.
    dist = compute_shares(
        LEAF,
        [node(coverage=0.175, confidence=1.0, depth=1, geometry_verified=False)],
        1000.0,
        r,
    )
    assert dist.sources[0].share == pytest.approx(0.175, abs=1e-6)


# ---------------------------------------------------------------------------
# Uretici beyani ve eleme
# ---------------------------------------------------------------------------
def test_kaynagin_asgari_pay_beyani_uygulanir():
    chain = [node(coverage=0.05, confidence=0.9, min_source_share=0.25)]
    dist = compute_shares(LEAF, chain, 1000.0, rules(creator_ceiling=1.0))
    assert dist.sources[0].share == pytest.approx(0.25, abs=1e-6)
    assert any("asgari" in n for n in dist.sources[0].factors["notlar"])


def test_asgari_pay_beyani_uretici_tabanini_ezemez():
    """Kaynagin talebi, ureticinin garantili tabanindan once gelemez."""
    chain = [
        node("a", coverage=0.5, confidence=1.0),
        node("b", coverage=0.3, confidence=1.0, min_source_share=0.60),
    ]
    dist = compute_shares(LEAF, chain, 1000.0, rules(creator_floor=0.20))
    assert dist.creator.share >= 0.20 - 1e-9
    assert_sums_to_one(dist)


def test_cok_kucuk_paylar_elenir():
    chain = [node("normal", coverage=0.5), node("kirinti", coverage=0.001, confidence=0.5)]
    dist = compute_shares(LEAF, chain, 1000.0, rules(min_payout_share=0.01))
    ids = {p.content_id for p in dist.sources}
    assert "kirinti" not in ids
    assert_sums_to_one(dist)
    assert any("eşiği" in line for line in dist.rules_log)


# ---------------------------------------------------------------------------
# Para
# ---------------------------------------------------------------------------
def test_komisyon_brut_gelirden_dusulur_ve_tutarlar_tutar():
    r = rules(commission=0.10)
    dist = compute_shares(LEAF, [node(coverage=0.4, confidence=1.0)], 1000.0, r)
    assert dist.commission_amount == pytest.approx(100.0)
    assert dist.distributable == pytest.approx(900.0)
    odenen = sum(p.amount for p in dist.parties if p.role != "platform")
    assert odenen == pytest.approx(900.0, abs=0.02)
    toplam = sum(p.amount for p in dist.parties)
    assert toplam == pytest.approx(1000.0, abs=0.02)


def test_gelir_sifirsa_paylar_yine_hesaplanir():
    """Pay dagilimi gelirden bagimsizdir; henuz kazanc yokken de gosterilir."""
    dist = compute_shares(LEAF, [node(coverage=0.4)], 0.0, rules())
    assert_sums_to_one(dist)
    assert all(p.amount == 0.0 for p in dist.parties)
