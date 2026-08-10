"""HTTP uclari."""

from __future__ import annotations

import tempfile
from pathlib import Path

import cv2
import numpy as np
from fastapi import APIRouter, Depends, File, Form, Header, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.schemas import (
    CampaignIn,
    CampaignOut,
    ContentOut,
    DisputeIn,
    IngestOut,
    LinkOut,
    ModerationIn,
    OturumIn,
    OturumOut,
    RecoveryOut,
    RevenueIn,
    UserOut,
)
from app.attribution.explain import STAGE_LABELS, build_labour_card, confidence_band
from app.core.config import get_settings
from app.core.database import get_session
from app.core.security import TokenError, decode_token, encode_token
from app.models.entities import (
    AttributionEdge,
    Campaign,
    Content,
    LinkStatus,
    User,
)
from app.provenance import recovery
from app.services import dispute as dispute_service
from app.services import ingest as ingest_service
from app.services import payout as payout_service
from app.services.registry import IndexService, get_index_service

router = APIRouter(prefix="/api")


def index_dep() -> IndexService:
    return get_index_service()


# ---------------------------------------------------------------------------
# Yardimcilar
# ---------------------------------------------------------------------------
def _user_out(user: User) -> UserOut:
    return UserOut(
        id=user.id, handle=user.handle, display_name=user.display_name, accent=user.accent
    )


def _content_out(session: Session, content: Content) -> ContentOut:
    owner = session.get(User, content.owner_id)
    sources = session.scalar(
        select(func.count())
        .select_from(AttributionEdge)
        .where(
            AttributionEdge.child_id == content.id,
            AttributionEdge.status != LinkStatus.REJECTED,
        )
    )
    derivatives = session.scalar(
        select(func.count())
        .select_from(AttributionEdge)
        .where(
            AttributionEdge.parent_id == content.id,
            AttributionEdge.status != LinkStatus.REJECTED,
        )
    )
    return ContentOut(
        id=content.id,
        title=content.title,
        caption=content.caption,
        width=content.width,
        height=content.height,
        created_at=content.created_at.isoformat(),
        revenue=content.revenue,
        manifest_present=content.manifest_present,
        remix_allowed=content.remix_allowed,
        owner=_user_out(owner),
        source_count=int(sources or 0),
        derivative_count=int(derivatives or 0),
        campaign_id=content.campaign_id,
    )


def _recovery_out(session: Session, result: recovery.RecoveryResult) -> RecoveryOut:
    links = []
    for link in result.links:
        parent = session.get(Content, link.parent_content_id)
        band = confidence_band(link.confidence)
        links.append(
            LinkOut(
                parent_content_id=link.parent_content_id,
                parent_title=parent.title if parent else "",
                stage=link.stage.value,
                stage_label=STAGE_LABELS.get(link.stage.value, link.stage.value),
                confidence=link.confidence,
                confidence_level=band["level"],
                visual_coverage=link.visual_coverage,
                source_usage=link.source_usage,
                geometry_verified=link.geometry_verified,
                evidence=link.evidence,
            )
        )
    return RecoveryOut(
        manifest_present=result.manifest.present,
        manifest_urn=result.manifest.urn,
        watermark_tag=result.watermark_tag,
        links=links,
        stage_log=result.stage_log,
        timings_ms=result.timings_ms,
    )


def _require_user(session: Session, user_id: str) -> User:
    user = session.get(User, user_id)
    if user is None:
        raise HTTPException(404, f"Kullanıcı bulunamadı: {user_id}")
    return user


async def _read_upload(file: UploadFile) -> bytes:
    """Yuklemeyi sinirli okur.

    `await file.read()` dosyanin tamamini bellege aliyordu ve boyut
    sinirinin tek uygulandigi yer Docker'daki nginx'ti - yani yerel
    calistirmada hicbir sinir yoktu ve tek bir istek sunucunun belleğini
    tuketebiliyordu. Parca parca okuyup sinir asilinca durduruyoruz;
    bellege alinan miktar hicbir zaman sinirdan fazla olmuyor.
    """
    limit_mb = get_settings().max_upload_mb
    limit = limit_mb * 1024 * 1024
    parcalar: list[bytes] = []
    toplam = 0
    while True:
        parca = await file.read(1024 * 1024)
        if not parca:
            break
        toplam += len(parca)
        if toplam > limit:
            raise HTTPException(
                413, f"Dosya çok büyük: en fazla {limit_mb} MB kabul ediliyor."
            )
        parcalar.append(parca)
    return b"".join(parcalar)


def _require_content(session: Session, content_id: str) -> Content:
    content = session.get(Content, content_id)
    if content is None:
        raise HTTPException(404, f"İçerik bulunamadı: {content_id}")
    return content


# ---------------------------------------------------------------------------
# Oturum ve yetki
# ---------------------------------------------------------------------------
def current_user(
    authorization: str | None = Header(default=None),
    session: Session = Depends(get_session),
) -> User:
    """`Authorization: Bearer <jeton>` basligindan kullaniciyi cozer.

    Jeton yoksa, bozuksa ya da suresi dolmussa 401. Jeton gecerli ama
    kullanici silinmisse de 401: istemci acisindan yapilacak sey ayni,
    yeniden oturum acmak.
    """
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(401, "Bu işlem için oturum gerekli.")

    try:
        payload = decode_token(authorization.split(" ", 1)[1].strip())
    except TokenError as exc:
        raise HTTPException(401, str(exc)) from exc

    user = session.get(User, payload.user_id)
    if user is None:
        raise HTTPException(401, "Oturum açan kullanıcı artık kayıtlı değil.")
    return user


@router.post("/oturum", response_model=OturumOut)
def oturum_ac(body: OturumIn, session: Session = Depends(get_session)):
    """Demo kimlik saglayicisi: kullanici kimligi -> imzali jeton.

    **Parola sorulmuyor ve bu bilincli.** N-Emek N'Sosyal'in icine giren
    bir emek katmani; kimlik dogrulama ana platformun isi. Gercek
    dagitimda bu ucun yerini N'Sosyal'in kimlik saglayicisi alir ve geri
    kalan uclar aynen calisir, cunku onlar jetonun nereden geldigini
    degil gecerli olup olmadigini soruyor. Ayrintili gerekce:
    `app/core/security.py`.
    """
    user = _require_user(session, body.user_id)
    token, expires_at = encode_token(user.id)
    return OturumOut(token=token, expires_at=expires_at, user=_user_out(user))


# ---------------------------------------------------------------------------
# Saglik ve kullanicilar
# ---------------------------------------------------------------------------
@router.get("/health")
def health(index: IndexService = Depends(index_dep)) -> dict:
    from app.provenance import c2pa_service, embedding

    return {
        "status": "ok",
        "indexed_contents": len(index),
        "device": embedding.pick_device(),
        "c2pa_signing": c2pa_service.certs_available(),
    }


@router.get("/users", response_model=list[UserOut])
def list_users(session: Session = Depends(get_session)):
    return [_user_out(u) for u in session.scalars(select(User))]


@router.get("/users/{user_id}/earnings")
def user_earnings(user_id: str, session: Session = Depends(get_session)):
    _require_user(session, user_id)
    return payout_service.earnings_for_user(session, user_id)


# ---------------------------------------------------------------------------
# Icerik
# ---------------------------------------------------------------------------
@router.get("/feed", response_model=list[ContentOut])
def feed(session: Session = Depends(get_session), limit: int = 50):
    stmt = select(Content).order_by(Content.created_at.desc()).limit(limit)
    return [_content_out(session, c) for c in session.scalars(stmt)]


@router.get("/contents/{content_id}", response_model=ContentOut)
def get_content(content_id: str, session: Session = Depends(get_session)):
    return _content_out(session, _require_content(session, content_id))


@router.get("/contents/{content_id}/image")
def get_content_image(content_id: str, session: Session = Depends(get_session)):
    content = _require_content(session, content_id)
    path = Path(content.file_path)
    if not path.exists():
        raise HTTPException(404, "Dosya bulunamadı.")
    return FileResponse(path, media_type="image/jpeg")


@router.post("/contents", response_model=IngestOut)
async def create_content(
    file: UploadFile = File(...),
    title: str = Form(...),
    caption: str = Form(""),
    remix_allowed: bool = Form(True),
    commercial_remix_allowed: bool = Form(True),
    min_source_share: float = Form(0.0),
    campaign_id: str | None = Form(None),
    session: Session = Depends(get_session),
    index: IndexService = Depends(index_dep),
    owner: User = Depends(current_user),
):
    """Yeni icerik yukler. Koken kurtarma hatti otomatik calisir.

    Kullanici "bu benim ozgun icerigim" dese bile hat calisir - iddia
    dogrulanir. Zaten sistemin varlik sebebi bu.

    Sahip artik form alanindan degil jetondan geliyor: onceden herkes
    herkes adina icerik yukleyebiliyordu.
    """
    raw = await _read_upload(file)
    try:
        result = ingest_service.ingest(
            session,
            index,
            raw_bytes=raw,
            owner=owner,
            title=title,
            caption=caption,
            remix_allowed=remix_allowed,
            commercial_remix_allowed=commercial_remix_allowed,
            min_source_share=min_source_share,
            campaign_id=campaign_id or None,
        )
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc

    return IngestOut(
        content=_content_out(session, result.content),
        recovery=_recovery_out(session, result.recovery),
    )


@router.post("/contents/{parent_id}/remix", response_model=IngestOut)
async def create_remix(
    parent_id: str,
    file: UploadFile = File(...),
    title: str = Form(...),
    caption: str = Form(""),
    actions: str = Form("c2pa.edited"),
    campaign_id: str | None = Form(None),
    session: Session = Depends(get_session),
    index: IndexService = Depends(index_dep),
    owner: User = Depends(current_user),
):
    """Remix stüdyosundan gelen turevi yayinlar.

    Args:
        actions: Virgulle ayrilmis C2PA eylemleri (c2pa.cropped, c2pa.edited...).
    """
    parent = _require_content(session, parent_id)
    if not parent.remix_allowed:
        raise HTTPException(403, "Bu içerik remixlenemez: üretici remix iznini kapatmış.")
    raw = await _read_upload(file)

    result = ingest_service.ingest(
        session,
        index,
        raw_bytes=raw,
        owner=owner,
        title=title,
        caption=caption,
        declared_parent_id=parent_id,
        remix_actions=[a.strip() for a in actions.split(",") if a.strip()],
        campaign_id=campaign_id or parent.campaign_id,
    )
    return IngestOut(
        content=_content_out(session, result.content),
        recovery=_recovery_out(session, result.recovery),
    )


@router.post("/verify", response_model=RecoveryOut)
async def verify(
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
    index: IndexService = Depends(index_dep),
):
    """Bir gorselin kaynagini bulur - yayinlamadan.

    "Bu icerik kimden geliyor?" sorusunun tek adimlik cevabi. Platforma
    kaydetmez, yalnizca hatti calistirip kanitlari doner.
    """
    raw = await _read_upload(file)
    image = cv2.imdecode(np.frombuffer(raw, np.uint8), cv2.IMREAD_COLOR)
    if image is None:
        raise HTTPException(400, "Görsel çözülemedi.")

    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
        tmp.write(raw)
        tmp_path = Path(tmp.name)
    try:
        result = recovery.recover(image, raw, tmp_path, index.index, index)
    finally:
        tmp_path.unlink(missing_ok=True)
    return _recovery_out(session, result)


# ---------------------------------------------------------------------------
# Atif, Emek Karti, gelir
# ---------------------------------------------------------------------------
@router.get("/contents/{content_id}/labour-card")
def labour_card(content_id: str, session: Session = Depends(get_session)):
    """Emek Karti: payin hangi gerekcelerle olustugunun tam dokumu."""
    _require_content(session, content_id)
    return build_labour_card(session, content_id)


@router.get("/edges/{edge_id}/mask")
def edge_mask(edge_id: str, session: Session = Depends(get_session)):
    """Eslesen bolge maskesi - arayuzdeki vurgu katmani."""
    edge = session.get(AttributionEdge, edge_id)
    if edge is None or not edge.mask_path:
        raise HTTPException(404, "Bu bağ için maske üretilmedi.")
    path = Path(edge.mask_path)
    if not path.exists():
        raise HTTPException(404, "Maske dosyası bulunamadı.")
    return FileResponse(path, media_type="image/png")


@router.post("/contents/{content_id}/revenue")
def set_revenue(
    content_id: str,
    body: RevenueIn,
    session: Session = Depends(get_session),
    user: User = Depends(current_user),
):
    """Gonderinin urettigi geliri ayarlar (demo icin).

    Yetki: yalnizca icerigin sahibi. Gelir tum zincirin paylarini
    belirledigi icin baskasinin gonderisinde degistirilebilir olmasi,
    zincirdeki herkesin odemesini oynatabilmek demekti.
    """
    content = _require_content(session, content_id)
    if content.owner_id != user.id:
        raise HTTPException(
            403, "Geliri yalnızca içeriğin sahibi değiştirebilir."
        )
    content.revenue = body.amount
    session.commit()
    return {"content_id": content_id, "revenue": content.revenue}


@router.post("/contents/{content_id}/distribute")
def distribute(content_id: str, session: Session = Depends(get_session)):
    """Gonderinin gelirini zincire dagitir ve odemeleri kaydeder."""
    content = _require_content(session, content_id)
    distribution, payouts = payout_service.distribute_content(
        session, content_id, content.revenue
    )
    session.commit()
    return {
        "content_id": content_id,
        "gross_revenue": distribution.gross_revenue,
        "commission_amount": distribution.commission_amount,
        "distributable": distribution.distributable,
        "rules_log": distribution.rules_log,
        "payouts": [
            {
                "user_name": p.user_name,
                "role": p.role,
                "share_pct": round(p.share * 100, 1),
                "amount": p.amount,
            }
            for p in distribution.parties
        ],
        "payout_ids": [p.id for p in payouts],
    }


# ---------------------------------------------------------------------------
# Kampanyalar
# ---------------------------------------------------------------------------
@router.get("/campaigns", response_model=list[CampaignOut])
def list_campaigns(session: Session = Depends(get_session)):
    out = []
    for campaign in session.scalars(select(Campaign)):
        count = session.scalar(
            select(func.count())
            .select_from(Content)
            .where(Content.campaign_id == campaign.id)
        )
        out.append(
            CampaignOut(
                id=campaign.id,
                brand_name=campaign.brand_name,
                title=campaign.title,
                brief=campaign.brief,
                reward_pool=campaign.reward_pool,
                status=campaign.status.value,
                commission=campaign.commission,
                source_floor=campaign.source_floor,
                creator_ceiling=campaign.creator_ceiling,
                content_count=int(count or 0),
            )
        )
    return out


@router.post("/campaigns", response_model=CampaignOut)
def create_campaign(body: CampaignIn, session: Session = Depends(get_session)):
    campaign = Campaign(
        brand_name=body.brand_name,
        title=body.title,
        brief=body.brief,
        reward_pool=body.reward_pool,
        commission=body.commission,
        source_floor=body.source_floor,
        creator_ceiling=body.creator_ceiling,
    )
    session.add(campaign)
    session.commit()
    return CampaignOut(
        id=campaign.id,
        brand_name=campaign.brand_name,
        title=campaign.title,
        brief=campaign.brief,
        reward_pool=campaign.reward_pool,
        status=campaign.status.value,
        commission=campaign.commission,
        source_floor=campaign.source_floor,
        creator_ceiling=campaign.creator_ceiling,
        content_count=0,
    )


@router.post("/campaigns/{campaign_id}/distribute")
def distribute_campaign(campaign_id: str, session: Session = Depends(get_session)):
    """Odul havuzunu katilan gonderilere ve zincirlerine dagitir."""
    try:
        result = payout_service.distribute_campaign(session, campaign_id)
    except ValueError as exc:
        raise HTTPException(404, str(exc)) from exc
    return {
        "campaign_id": result.campaign_id,
        "reward_pool": result.reward_pool,
        "total_paid": result.total_paid,
        "platform_total": result.platform_total,
        "per_content": result.per_content,
    }


# ---------------------------------------------------------------------------
# Itirazlar
# ---------------------------------------------------------------------------
@router.post("/disputes")
def create_dispute(
    body: DisputeIn,
    session: Session = Depends(get_session),
    raiser: User = Depends(current_user),
):
    """Bir baga itiraz acar.

    Yetki: itirazi yalnizca o payin sahibi acabilir - yani bagin
    *kaynak* tarafindaki icerigin sahibi. Pay ona odendigi icin olcumun
    dusuk ciktigini one surme hakki da onun.

    Bag once yukleniyor: olmayan bir bag icin 403 degil 404 donmeli,
    yoksa yanit hangi baglarin var oldugunu sizdirirdi.
    """
    edge = session.get(AttributionEdge, body.edge_id)
    if edge is None:
        raise HTTPException(404, f"Bağ bulunamadı: {body.edge_id}")

    kaynak = session.get(Content, edge.parent_id)
    if kaynak is None or kaynak.owner_id != raiser.id:
        raise HTTPException(403, "Bu paya yalnızca payın sahibi itiraz edebilir.")

    try:
        dispute = dispute_service.open_dispute(
            session, edge_id=body.edge_id, raiser=raiser, reason=body.reason
        )
    except ValueError as exc:
        raise HTTPException(404, str(exc)) from exc
    return {"id": dispute.id, "status": dispute.status.value}


@router.post("/disputes/{dispute_id}/resolve")
def resolve_dispute(
    dispute_id: str,
    session: Session = Depends(get_session),
    index: IndexService = Depends(index_dep),
):
    """Itirazi otomatik degerlendirir: daha hassas dedektorle yeniden olcer."""
    try:
        outcome = dispute_service.resolve(session, index, dispute_id)
    except ValueError as exc:
        raise HTTPException(404, str(exc)) from exc
    return {
        "id": outcome.dispute.id,
        "status": outcome.dispute.status.value,
        "changed": outcome.changed,
        "summary": outcome.summary,
        "resolution": outcome.dispute.resolution,
    }


@router.get("/disputes/queue")
def dispute_queue(session: Session = Depends(get_session)):
    """Insan moderatore dusen itirazlar."""
    return dispute_service.review_queue(session)


@router.post("/disputes/{dispute_id}/moderate")
def moderate_dispute(
    dispute_id: str, body: ModerationIn, session: Session = Depends(get_session)
):
    try:
        dispute = dispute_service.moderator_decision(
            session, dispute_id, accept=body.accept, note=body.note
        )
    except ValueError as exc:
        raise HTTPException(404, str(exc)) from exc
    return {"id": dispute.id, "status": dispute.status.value, "resolution": dispute.resolution}
