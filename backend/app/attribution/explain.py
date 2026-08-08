"""Emek Karti - acilanabilirlik katmani.

Bir sayi gostermek yetmez. Kullanicinin sormasi gereken her soruya
ayni ekranda cevap verilmeli:

    "Bu icerik 4.200 TL kazandi. Neden bana 1.430 TL geldi?"
      -> icerigin %41'i senin gonderinden geliyor (olculdu)
      -> bu bagdan %92 eminiz (hangi kanitla?)
      -> zincirde bir adim gerideysin, sonumleme %50
      -> kampanya kaynaklara en az %15 ayiriyor
      -> katilmiyorsan itiraz et, kanit yukle

Bu modul o ekranin verisini uretir. Hicbir sayi gerekcesiz gelmez.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.attribution import chain as chain_builder
from app.attribution.contribution import Distribution, LeafInfo, Rules, compute_shares
from app.models.entities import AttributionEdge, Campaign, Content, LinkStatus, User

# Guven duzeyinin insan okuyabilir karsiligi.
CONFIDENCE_BANDS = [
    (0.85, "yuksek", "Kanitlar guclu ve birbirini destekliyor."),
    (0.60, "orta", "Kaynak buyuk olasilikla dogru; itiraza acik."),
    (0.0, "dusuk", "Zayif kanit. Bu bag bir oneridir, kesin karar degildir."),
]

STAGE_LABELS = {
    "c2pa": "Imzali icerik kimligi (C2PA)",
    "exact": "Birebir dosya eslesmesi",
    "watermark": "Piksele gomulu kimlik",
    "phash": "Algisal parmak izi",
    "phash_blok": "Blok bazli algisal parmak izi",
    "clip": "Gorsel benzerlik modeli",
    "declared": "Uretici beyani",
    "geometry": "Geometrik dogrulama ve alan olcumu",
}


def confidence_band(value: float) -> dict:
    for threshold, label, note in CONFIDENCE_BANDS:
        if value >= threshold:
            return {"level": label, "score": round(value, 4), "note": note}
    return {"level": "dusuk", "score": round(value, 4), "note": ""}


def rules_for(content: Content, campaign: Campaign | None) -> Rules:
    """Bu icerige uygulanacak kural kumesi."""
    base = Rules.from_settings()
    if campaign is None:
        return base
    return base.with_campaign(
        commission=campaign.commission,
        source_floor=campaign.source_floor,
        creator_ceiling=campaign.creator_ceiling,
        label=f"{campaign.brand_name} - {campaign.title} kampanya kurallari",
    )


def _evidence_rows(edge: AttributionEdge) -> list[dict]:
    """Bir bagin kanit satirlarini arayuz icin duzenler."""
    rows: list[dict] = []
    for item in edge.evidence or []:
        stage = item.get("stage", "")
        row = {
            "stage": stage,
            "label": STAGE_LABELS.get(stage, stage),
            "found": item.get("found", item.get("matched", False)),
            "aciklama": item.get("aciklama", ""),
            "detay": {
                k: v
                for k, v in item.items()
                if k not in {"stage", "found", "matched", "aciklama"}
            },
        }
        rows.append(row)
    return rows


def _edge_between(session: Session, child_id: str, parent_id: str) -> AttributionEdge | None:
    stmt = select(AttributionEdge).where(
        AttributionEdge.child_id == child_id, AttributionEdge.parent_id == parent_id
    )
    return session.scalars(stmt).first()


def _direct_edge_for_ancestor(
    session: Session, leaf_id: str, ancestor_id: str
) -> AttributionEdge | None:
    """Ata dogrudan kaynaksa bagi doner; degilse en yakin halkayi arar."""
    direct = _edge_between(session, leaf_id, ancestor_id)
    if direct:
        return direct
    stmt = select(AttributionEdge).where(AttributionEdge.parent_id == ancestor_id)
    return session.scalars(stmt).first()


def build_labour_card(session: Session, content_id: str, revenue: float | None = None) -> dict:
    """Bir icerik icin tam Emek Karti verisi."""
    content = session.get(Content, content_id)
    if content is None:
        raise ValueError(f"icerik bulunamadi: {content_id}")
    owner = session.get(User, content.owner_id)
    campaign = session.get(Campaign, content.campaign_id) if content.campaign_id else None

    nodes = chain_builder.build_chain(session, content_id)
    rules = rules_for(content, campaign)
    gross = content.revenue if revenue is None else revenue

    distribution = compute_shares(
        LeafInfo(
            content_id=content.id,
            owner_id=content.owner_id,
            owner_name=owner.display_name if owner else "bilinmiyor",
        ),
        nodes,
        gross,
        rules,
    )

    return {
        "content": _content_summary(session, content),
        "provenance": _provenance_summary(session, content),
        "chain": _chain_graph(session, content_id, nodes),
        "distribution": _distribution_payload(session, content_id, distribution),
        "rules": {
            "label": distribution.rules_label,
            "commission": rules.commission,
            "creator_floor": rules.creator_floor,
            "creator_ceiling": rules.creator_ceiling,
            "source_floor": rules.source_floor,
            "chain_damping": rules.chain_damping,
            "log": distribution.rules_log,
        },
        "campaign": _campaign_summary(campaign),
    }


def _content_summary(session: Session, content: Content) -> dict:
    owner = session.get(User, content.owner_id)
    return {
        "id": content.id,
        "title": content.title,
        "caption": content.caption,
        "width": content.width,
        "height": content.height,
        "created_at": content.created_at.isoformat(),
        "revenue": content.revenue,
        "owner": {
            "id": content.owner_id,
            "name": owner.display_name if owner else "bilinmiyor",
            "handle": owner.handle if owner else "",
            "accent": owner.accent if owner else "#5B8DEF",
        },
        "remix_allowed": content.remix_allowed,
        "min_source_share": content.min_source_share,
    }


def _provenance_summary(session: Session, content: Content) -> dict:
    """Icerigin kimlik durumu: manifest var mi, nasil bulundu."""
    edges = list(
        session.scalars(select(AttributionEdge).where(AttributionEdge.child_id == content.id))
    )
    best = max((e.confidence for e in edges), default=0.0)

    if content.provenance_recovered:
        durum = "yeniden_kuruldu"
        aciklama = (
            "Yuklenen dosyada icerik kimligi yoktu ve kaynak beyan edilmemisti. "
            "Koken, kanit zinciriyle yeniden kuruldu."
        )
    elif content.incoming_manifest_present:
        durum = "kimlik_korundu"
        aciklama = "Yuklenen dosyada icerik kimligi korunmustu; koken manifestten okundu."
    elif edges:
        durum = "beyan_dogrulandi"
        aciklama = (
            "Yuklenen dosyada icerik kimligi yoktu; uretici kaynagi beyan etti ve "
            "beyan olcumle dogrulandi."
        )
    else:
        durum = "ozgun"
        aciklama = "Kaynak bulunamadi; icerik ozgun kabul edildi."

    return {
        "durum": durum,
        # Yuklenen dosyada kimlik var miydi (anlatinin dayanagi).
        "incoming_manifest_present": content.incoming_manifest_present,
        # Yayinlanan dosyaya bizim ekledigimiz kimlik.
        "manifest_present": content.manifest_present,
        "manifest_urn": content.manifest_urn,
        "watermark_tag": content.watermark_tag,
        "content_hash": content.content_hash[:16] + "...",
        "link_count": len(edges),
        "confidence": confidence_band(best) if edges else None,
        "aciklama": aciklama,
    }


def _chain_graph(session: Session, leaf_id: str, nodes) -> dict:
    """Zincir gorunumu (DAG) icin dugum ve kenar listesi."""
    graph_nodes = []
    graph_edges = []
    seen = {leaf_id}

    leaf = session.get(Content, leaf_id)
    leaf_owner = session.get(User, leaf.owner_id) if leaf else None
    graph_nodes.append(
        {
            "id": leaf_id,
            "depth": 0,
            "role": "leaf",
            "title": leaf.title if leaf else "",
            "owner": leaf_owner.display_name if leaf_owner else "",
            "accent": leaf_owner.accent if leaf_owner else "#5B8DEF",
        }
    )

    for node in nodes:
        content = session.get(Content, node.content_id)
        owner = session.get(User, node.owner_id)
        if node.content_id not in seen:
            graph_nodes.append(
                {
                    "id": node.content_id,
                    "depth": node.depth,
                    "role": "source",
                    "title": content.title if content else "",
                    "owner": owner.display_name if owner else "",
                    "accent": owner.accent if owner else "#5B8DEF",
                }
            )
            seen.add(node.content_id)

    # Kenarlar: zincirdeki tum icerikler arasindaki gercek baglar
    ids = list(seen)
    stmt = select(AttributionEdge).where(
        AttributionEdge.child_id.in_(ids), AttributionEdge.parent_id.in_(ids)
    )
    for edge in session.scalars(stmt):
        graph_edges.append(
            {
                "id": edge.id,
                "from": edge.parent_id,
                "to": edge.child_id,
                "stage": edge.stage.value,
                "stage_label": STAGE_LABELS.get(edge.stage.value, edge.stage.value),
                "status": edge.status.value,
                "confidence": confidence_band(edge.confidence),
                "visual_coverage": edge.visual_coverage,
                "source_usage": edge.source_usage,
                "mask_path": edge.mask_path,
            }
        )

    return {"nodes": graph_nodes, "edges": graph_edges}


def _distribution_payload(session: Session, leaf_id: str, dist: Distribution) -> dict:
    parties = []
    for party in dist.parties:
        entry = {
            "role": party.role,
            "user_id": party.user_id,
            "user_name": party.user_name,
            "content_id": party.content_id,
            "share": party.share,
            "share_pct": round(party.share * 100, 1),
            "amount": party.amount,
            "factors": party.factors,
            "rules_applied": party.rules_applied,
            "evidence": [],
        }
        if party.role == "source" and party.content_id:
            edge = _direct_edge_for_ancestor(session, leaf_id, party.content_id)
            if edge is not None:
                entry["evidence"] = _evidence_rows(edge)
                entry["edge_id"] = edge.id
                entry["edge_status"] = edge.status.value
                entry["disputable"] = edge.status in (
                    LinkStatus.PROPOSED,
                    LinkStatus.CONFIRMED,
                )
        parties.append(entry)

    return {
        "gross_revenue": dist.gross_revenue,
        "commission_amount": dist.commission_amount,
        "distributable": dist.distributable,
        "parties": parties,
    }


def _campaign_summary(campaign: Campaign | None) -> dict | None:
    if campaign is None:
        return None
    return {
        "id": campaign.id,
        "brand_name": campaign.brand_name,
        "title": campaign.title,
        "brief": campaign.brief,
        "reward_pool": campaign.reward_pool,
        "status": campaign.status.value,
        "commission": campaign.commission,
        "source_floor": campaign.source_floor,
        "creator_ceiling": campaign.creator_ceiling,
    }
