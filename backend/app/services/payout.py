"""Gelir dagitimi.

Paylar veritabaninda tutulmaz, her seferinde olcumlerden hesaplanir.
Tek istisna buradaki `Payout` kaydidir: para dagitildigi an hesap
dondurulur, cunku odenen bir tutarin gerekcesi sonradan degismemelidir.

Yeniden dagitim *degistirir*, eklemez
-------------------------------------
Ilk yazimda dagitim uclari idempotent degildi: ayni gonderi iki kez
dagitilinca ikinci kosum yeni `Payout` satirlari yaziyor, eskiler
duruyordu. Sonuc `GET /users/{id}/earnings` icin iki kat kazanc, kampanya
icin havuzu asan bir toplamdi - yani para ile ilgili bir doğruluk
hatasi. Dugmeye iki kez basmak bunu tetiklemeye yetiyordu.

Simdi her dagitim, o gonderinin onceki odemelerini silip yerine yenisini
yaziyor: **bir gonderi, bir odeme kumesi** (`_kapsam_temizle`).

Bu bir denetim izi kaybi degil: dagitilan tutarin *gerekcesi*
donduruluyor, ama "en son ne dagitildi" tek bir gercek olmali. Odeme
gecmisinin surumlenmesi (kim ne zaman neyi yeniden dagitti) urunlesme
isi ve `docs/VERI-MODEL-ETIK.md` icinde kayitli.
"""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.attribution import chain as chain_builder
from app.attribution.contribution import Distribution, LeafInfo, compute_shares
from app.attribution.explain import rules_for
from app.models.entities import Campaign, CampaignStatus, Content, Payout, User


@dataclass
class CampaignDistribution:
    campaign_id: str
    reward_pool: float
    # Havuzun gonderilere nasil bolundugu
    per_content: list[dict]
    payouts: list[Payout]
    total_paid: float
    platform_total: float


def _kapsam_temizle(session: Session, content_id: str) -> int:
    """Bu gonderinin onceki odemelerini siler ve sayisini doner.

    Kural tek cumle: **bir gonderi, bir odeme kumesi.** Kampanyaya gore
    daraltmak da denenebilirdi ama bir gonderinin odemeleri zaten tek bir
    kampanyaya ait - `distribute_content` kampanyayi gonderinin kendi
    `campaign_id` alanindan cozuyor. Daraltma, yalnizca gonderinin
    kampanyasi degistiginde eski odemelerin oksuz kalmasi riskini
    eklerdi.

    `source_content_id` uzerinden gelen odemeler bilerek disarida: onlar
    *baska* bir gonderinin dagitimina ait ve o dagitim yeniden
    kosuldugunda kendi kapsaminda temizlenir.
    """
    stmt = select(Payout).where(Payout.content_id == content_id)
    eskiler = list(session.scalars(stmt))
    for odeme in eskiler:
        session.delete(odeme)
    if eskiler:
        # Silmeler sonraki `add`'lerden once veritabanina insin: ayni
        # oturumda once ekleyip sonra silmek, silinmesi gerekenlerin
        # yerine yenilerini silme riskini tasiyor.
        session.flush()
    return len(eskiler)


def distribute_content(
    session: Session, content_id: str, revenue: float, campaign: Campaign | None = None
) -> tuple[Distribution, list[Payout]]:
    """Tek bir gonderinin gelirini zincire dagitir.

    Idempotent: ayni kapsamdaki onceki odemeler silinip yerine yenisi
    yazilir. Iki kez cagirmak odemeleri ikiye katlamaz.
    """
    content = session.get(Content, content_id)
    if content is None:
        raise ValueError(f"İçerik bulunamadı: {content_id}")
    owner = session.get(User, content.owner_id)
    campaign = campaign or (
        session.get(Campaign, content.campaign_id) if content.campaign_id else None
    )

    nodes = chain_builder.build_chain(session, content_id)
    distribution = compute_shares(
        LeafInfo(
            content_id=content.id,
            owner_id=content.owner_id,
            owner_name=owner.display_name if owner else "bilinmiyor",
        ),
        nodes,
        revenue,
        rules_for(content, campaign),
    )

    _kapsam_temizle(session, content_id)

    payouts: list[Payout] = []
    for party in distribution.parties:
        if party.amount <= 0 and party.role != "platform":
            continue
        payout = Payout(
            campaign_id=campaign.id if campaign else None,
            content_id=content_id,
            user_id=party.user_id,
            source_content_id=party.content_id if party.role == "source" else None,
            share=party.share,
            amount=party.amount,
            is_platform_fee=party.role == "platform",
            rationale={
                "role": party.role,
                "factors": party.factors,
                "rules_applied": party.rules_applied,
                "rules_label": distribution.rules_label,
                "rules_log": distribution.rules_log,
            },
        )
        session.add(payout)
        payouts.append(payout)

    session.flush()
    return distribution, payouts


def distribute_campaign(session: Session, campaign_id: str) -> CampaignDistribution:
    """Kampanya odul havuzunu katilan gonderilere ve zincirlerine dagitir.

    Havuz once gonderiler arasinda bolunur. Bolusme olcutu, gonderinin
    kendi urettigi gelir (etkilesim/gorunurluk vekili); hicbir gonderi
    gelir uretmediyse havuz esit bolunur. Ardindan her gonderinin payi
    kendi atif zincirine dagitilir.
    """
    campaign = session.get(Campaign, campaign_id)
    if campaign is None:
        raise ValueError(f"Kampanya bulunamadı: {campaign_id}")

    contents = list(
        session.scalars(select(Content).where(Content.campaign_id == campaign_id))
    )
    if not contents:
        return CampaignDistribution(campaign_id, campaign.reward_pool, [], [], 0.0, 0.0)

    # Havuz butun olarak yeniden bolunuyor, dolayisiyla temizlik de butun
    # olmali. `distribute_content` yalnizca kendi gonderisinin kapsamini
    # temizler; kampanyadan cikarilmis bir gonderinin eski odemesi orada
    # yakalanmaz. Havuzun asilmamasini garanti eden sey bu satir.
    eski = list(session.scalars(select(Payout).where(Payout.campaign_id == campaign_id)))
    for odeme in eski:
        session.delete(odeme)
    if eski:
        session.flush()

    total_signal = sum(c.revenue for c in contents)
    per_content: list[dict] = []
    all_payouts: list[Payout] = []
    platform_total = 0.0
    paid_total = 0.0

    for content in contents:
        if total_signal > 0:
            weight = content.revenue / total_signal
            basis = "gönderi geliri oranı"
        else:
            weight = 1.0 / len(contents)
            basis = "eşit bölüşme (henüz gelir yok)"
        allocation = campaign.reward_pool * weight

        distribution, payouts = distribute_content(session, content.id, allocation, campaign)
        all_payouts.extend(payouts)
        platform_total += distribution.commission_amount
        paid_total += distribution.distributable

        per_content.append(
            {
                "content_id": content.id,
                "title": content.title,
                "weight": round(weight, 4),
                "basis": basis,
                "allocation": round(allocation, 2),
                "parties": [
                    {
                        "role": p.role,
                        "user_name": p.user_name,
                        "share_pct": round(p.share * 100, 1),
                        "amount": p.amount,
                    }
                    for p in distribution.parties
                ],
            }
        )

    campaign.status = CampaignStatus.DISTRIBUTED
    session.commit()

    return CampaignDistribution(
        campaign_id=campaign_id,
        reward_pool=campaign.reward_pool,
        per_content=per_content,
        payouts=all_payouts,
        total_paid=round(paid_total, 2),
        platform_total=round(platform_total, 2),
    )


def earnings_for_user(session: Session, user_id: str) -> dict:
    """Bir kullanicinin tum kazanclari, kaynagina gore ayrilmis."""
    rows = list(session.scalars(select(Payout).where(Payout.user_id == user_id)))
    as_creator = sum(r.amount for r in rows if r.rationale.get("role") == "creator")
    as_source = sum(r.amount for r in rows if r.rationale.get("role") == "source")
    return {
        "user_id": user_id,
        "total": round(as_creator + as_source, 2),
        "as_creator": round(as_creator, 2),
        "as_source": round(as_source, 2),
        "payout_count": len(rows),
    }
