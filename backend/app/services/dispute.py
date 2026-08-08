"""Itiraz ve insan incelemesi.

Sistem "sahibi budur" demez, "kanitlar bunu gosteriyor" der. Bu iddianin
karsiligi, itirazin gercek bir sonuc dogurmasidir: itiraz aciklan bag
yeniden olculur, karar degisirse zincir ve tum paylar guncellenir.

Uc sonuc mumkun:
  * kabul   - yeniden olcum itirazi dogruladi, bag guclendi/duzeldi
  * ret     - olcum ayni sonucu verdi, itiraz reddedildi
  * yukselt - olcum kararsiz kaldi, insan moderatore gonderildi

Otomatik karar veremedigimiz durumu gizlemek yerine acikca isaretlemek,
sistemin guvenilirliginin parcasi.
"""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.entities import (
    AttributionEdge,
    Dispute,
    DisputeStatus,
    LinkStatus,
    User,
)
from app.services import ingest
from app.services.registry import IndexService

# Yeniden olcumde bu kadar degisim "anlamli" sayilir.
MATERIAL_CHANGE = 0.05


@dataclass
class DisputeOutcome:
    dispute: Dispute
    edge: AttributionEdge
    changed: bool
    summary: str


def open_dispute(
    session: Session,
    *,
    edge_id: str,
    raiser: User,
    reason: str,
    evidence_path: str | None = None,
) -> Dispute:
    edge = session.get(AttributionEdge, edge_id)
    if edge is None:
        raise ValueError(f"Bağ bulunamadı: {edge_id}")

    dispute = Dispute(
        edge_id=edge_id,
        raiser_id=raiser.id,
        reason=reason,
        evidence_path=evidence_path,
    )
    edge.status = LinkStatus.DISPUTED
    session.add(dispute)
    session.commit()
    return dispute


def resolve(
    session: Session, index_service: IndexService, dispute_id: str
) -> DisputeOutcome:
    """Itirazi otomatik olarak degerlendirir.

    Yeniden olcum, ilk gecistekinden daha hassas bir dedektorle (SIFT)
    yapilir. Ilk gecis hizli olmak zorundadir - yukleme aninda calisir;
    itiraz ise seyrek ve gecikmeye toleranslidir, orada dogruluk once
    gelir.
    """
    settings = get_settings()
    dispute = session.get(Dispute, dispute_id)
    if dispute is None:
        raise ValueError(f"İtiraz bulunamadı: {dispute_id}")
    edge = session.get(AttributionEdge, dispute.edge_id)
    if edge is None:
        raise ValueError("İtiraza konu bağ silinmiş.")

    before = {
        "confidence": edge.confidence,
        "visual_coverage": edge.visual_coverage,
    }
    ingest.remeasure(session, index_service, edge)
    after = {
        "confidence": edge.confidence,
        "visual_coverage": edge.visual_coverage,
    }

    coverage_delta = (after["visual_coverage"] or 0.0) - (before["visual_coverage"] or 0.0)
    confidence_delta = after["confidence"] - before["confidence"]
    changed = abs(coverage_delta) >= MATERIAL_CHANGE or abs(confidence_delta) >= MATERIAL_CHANGE

    if after["visual_coverage"] is None:
        # Olcum yine yapilamadi: makine karar veremez.
        dispute.status = DisputeStatus.ESCALATED
        edge.status = LinkStatus.DISPUTED
        summary = (
            "Yeniden ölçüm de sonuç vermedi. Bağ insan incelemesine yönlendirildi; "
            "karar verilene kadar mevcut pay geçerli."
        )
    elif changed:
        dispute.status = DisputeStatus.RESOLVED_ACCEPTED
        edge.status = (
            LinkStatus.CONFIRMED
            if after["confidence"] >= settings.auto_confirm_confidence
            else LinkStatus.PROPOSED
        )
        yon = "yükseldi" if coverage_delta > 0 else "düştü"
        onceki = f"%{(before['visual_coverage'] or 0) * 100:.1f}".replace(".", ",")
        sonraki = f"%{(after['visual_coverage'] or 0) * 100:.1f}".replace(".", ",")
        summary = (
            f"İtiraz kabul edildi. Yeniden ölçümde kullanılan alan oranı "
            f"{onceki} yerine {sonraki} çıktı ({yon}). Paylar güncellendi."
        )
    else:
        dispute.status = DisputeStatus.RESOLVED_REJECTED
        edge.status = (
            LinkStatus.CONFIRMED
            if after["confidence"] >= settings.auto_confirm_confidence
            else LinkStatus.PROPOSED
        )
        summary = (
            "İtiraz reddedildi. Daha hassas dedektörle yapılan yeniden ölçüm "
            "aynı sonucu verdi; anlamlı bir değişiklik yok."
        )

    dispute.resolution = {
        "before": before,
        "after": after,
        "coverage_delta": round(coverage_delta, 4),
        "confidence_delta": round(confidence_delta, 4),
        "material_change_threshold": MATERIAL_CHANGE,
        "summary": summary,
    }
    from datetime import datetime, timezone

    dispute.resolved_at = datetime.now(timezone.utc)
    session.commit()

    return DisputeOutcome(dispute=dispute, edge=edge, changed=changed, summary=summary)


def review_queue(session: Session) -> list[dict]:
    """Insan moderatore dusen itirazlar."""
    stmt = select(Dispute).where(
        Dispute.status.in_([DisputeStatus.OPEN, DisputeStatus.ESCALATED])
    )
    out = []
    for dispute in session.scalars(stmt):
        edge = session.get(AttributionEdge, dispute.edge_id)
        raiser = session.get(User, dispute.raiser_id)
        out.append(
            {
                "id": dispute.id,
                "status": dispute.status.value,
                "reason": dispute.reason,
                "raiser": raiser.display_name if raiser else "",
                "created_at": dispute.created_at.isoformat(),
                "edge": {
                    "id": edge.id if edge else None,
                    "child_id": edge.child_id if edge else None,
                    "parent_id": edge.parent_id if edge else None,
                    "confidence": edge.confidence if edge else None,
                    "visual_coverage": edge.visual_coverage if edge else None,
                },
                "resolution": dispute.resolution,
            }
        )
    return out


def moderator_decision(
    session: Session, dispute_id: str, *, accept: bool, note: str
) -> Dispute:
    """Insan moderatorun nihai karari."""
    dispute = session.get(Dispute, dispute_id)
    if dispute is None:
        raise ValueError(f"İtiraz bulunamadı: {dispute_id}")
    edge = session.get(AttributionEdge, dispute.edge_id)

    if accept:
        dispute.status = DisputeStatus.RESOLVED_ACCEPTED
        if edge is not None:
            edge.status = LinkStatus.REJECTED
    else:
        dispute.status = DisputeStatus.RESOLVED_REJECTED
        if edge is not None:
            edge.status = LinkStatus.CONFIRMED

    resolution = dict(dispute.resolution or {})
    resolution["moderator"] = {"accepted": accept, "note": note}
    dispute.resolution = resolution

    from datetime import datetime, timezone

    dispute.resolved_at = datetime.now(timezone.utc)
    session.commit()
    return dispute
