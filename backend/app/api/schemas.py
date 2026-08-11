"""API istek ve yanit sozlesmeleri."""

from __future__ import annotations

from pydantic import BaseModel, Field


class UserOut(BaseModel):
    id: str
    handle: str
    display_name: str
    accent: str
    # "uye" | "moderator". Arayuz bunu rozet olarak gosteriyor: moderator
    # yetkisi isteyen dugmeler 403 verdiginde kullanicinin sebebi
    # gorebilmesi icin rolun gorunur olmasi gerekiyor.
    role: str = "uye"


class ContentOut(BaseModel):
    id: str
    title: str
    caption: str
    width: int
    height: int
    created_at: str
    revenue: float
    manifest_present: bool
    remix_allowed: bool
    owner: UserOut
    source_count: int
    derivative_count: int
    campaign_id: str | None = None


class StageLogOut(BaseModel):
    stage: str
    found: bool
    detail: str = ""
    aciklama: str = ""


class LinkOut(BaseModel):
    parent_content_id: str
    parent_title: str
    stage: str
    stage_label: str
    confidence: float
    confidence_level: str
    visual_coverage: float | None
    source_usage: float | None
    geometry_verified: bool
    evidence: list[dict]


class RecoveryOut(BaseModel):
    """Koken kurtarma hattinin ciktisi - hem yuklemede hem sorgulamada."""

    manifest_present: bool
    manifest_urn: str | None = None
    watermark_tag: str | None = None
    links: list[LinkOut]
    stage_log: list[StageLogOut]
    timings_ms: dict[str, float]


class IngestOut(BaseModel):
    content: ContentOut
    recovery: RecoveryOut


class CampaignIn(BaseModel):
    brand_name: str
    title: str
    brief: str = ""
    reward_pool: float = Field(gt=0)
    commission: float = Field(default=0.10, ge=0, le=0.5)
    source_floor: float = Field(default=0.15, ge=0, le=1)
    creator_ceiling: float = Field(default=0.85, ge=0, le=1)


class CampaignOut(BaseModel):
    id: str
    brand_name: str
    title: str
    brief: str
    reward_pool: float
    status: str
    commission: float
    source_floor: float
    creator_ceiling: float
    content_count: int


class RevenueIn(BaseModel):
    amount: float = Field(ge=0)


class OturumIn(BaseModel):
    user_id: str


class OturumOut(BaseModel):
    """Demo kimlik saglayicisinin yaniti (bkz. core/security.py)."""

    token: str
    # Unix saniye; arayuz suresi dolmadan once yeniden oturum aciyor.
    expires_at: int
    user: UserOut


class DisputeIn(BaseModel):
    # `raiser_id` kaldirildi: itirazi kimin actigi govdeden degil
    # jetondan okunuyor. Onceden herkes bir baskasinin adina itiraz
    # acabiliyordu.
    edge_id: str
    reason: str = Field(min_length=3)


class ModerationIn(BaseModel):
    accept: bool
    note: str = ""
