"""Veri modeli.

Tasarim ilkesi: *olcum* ile *karar* ayri saklanir.

`AttributionEdge` bir olcumdur - hangi asama neyi buldu, kullanilan alan
orani ne, guven ne. Bu kayit degismez (itiraz sonrasi yeniden olculurse
yeni bir surum yazilir). Paylar bu olcumlerden her seferinde yeniden
*hesaplanir*; veritabaninda donmus pay tutulmaz. Boylece bir itiraz
kabul edildiginde tum zincir tutarli sekilde guncellenir.

Tek istisna: `Payout`. Para dagitildigi an hesap dondurulur, cunku
odenen bir tutarin gerekcesi sonradan degismemelidir.
"""

from __future__ import annotations

import datetime as dt
import enum
import uuid

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    LargeBinary,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.types import JSON


def _uid() -> str:
    return uuid.uuid4().hex[:16]


def _now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


class Base(DeclarativeBase):
    pass


# ---------------------------------------------------------------------------
# Sabit kumeler
# ---------------------------------------------------------------------------
class LinkStage(str, enum.Enum):
    """Bagi kuran koken kurtarma asamasi."""

    C2PA = "c2pa"  # imzali manifest - en guclu kanit
    EXACT = "exact"  # SHA-256 tam eslesme
    WATERMARK = "watermark"  # gomulu kimlik
    PHASH = "phash"  # algisal hash
    CLIP = "clip"  # gorsel gomme benzerligi
    DECLARED = "declared"  # kullanici beyani (remix studyosundan)


class LinkStatus(str, enum.Enum):
    PROPOSED = "proposed"  # sistem onerdi, onay bekliyor
    CONFIRMED = "confirmed"  # otomatik veya kullanici onayiyla kesinlesti
    DISPUTED = "disputed"  # itiraz var, insan incelemesinde
    REJECTED = "rejected"  # inceleme sonucu reddedildi


class DisputeStatus(str, enum.Enum):
    OPEN = "open"
    RESOLVED_ACCEPTED = "resolved_accepted"
    RESOLVED_REJECTED = "resolved_rejected"
    ESCALATED = "escalated"  # insan moderatore yonlendirildi


class CampaignStatus(str, enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    DISTRIBUTED = "distributed"


# ---------------------------------------------------------------------------
# Varliklar
# ---------------------------------------------------------------------------
class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(16), primary_key=True, default=_uid)
    handle: Mapped[str] = mapped_column(String(40), unique=True)
    display_name: Mapped[str] = mapped_column(String(80))
    # Arayuzde avatar yerine kullanilan renk (demo verisi icin yeterli).
    accent: Mapped[str] = mapped_column(String(9), default="#5B8DEF")
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=_now)

    contents: Mapped[list["Content"]] = relationship(back_populates="owner")


class Content(Base):
    """Platformdaki bir gorsel gonderi."""

    __tablename__ = "contents"

    id: Mapped[str] = mapped_column(String(16), primary_key=True, default=_uid)
    owner_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    title: Mapped[str] = mapped_column(String(200), default="")
    caption: Mapped[str] = mapped_column(Text, default="")
    file_path: Mapped[str] = mapped_column(String(400))
    width: Mapped[int] = mapped_column(Integer)
    height: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=_now)

    # --- Koken kimligi ----------------------------------------------------
    content_hash: Mapped[str] = mapped_column(String(64), index=True)
    # Algisal hash'ler 64 bit *isaretsiz*; SQLite'in isaretli INTEGER'ina
    # sigmaz (ust bit setliyken tasar). Onaltilik dizge olarak saklanir.
    phash: Mapped[str] = mapped_column(String(16))
    dhash: Mapped[str] = mapped_column(String(16))
    whash: Mapped[str] = mapped_column(String(16))
    # Yayinlanan dosyada C2PA manifesti var mi (biz imzaladiysak True).
    manifest_present: Mapped[bool] = mapped_column(Boolean, default=False)
    # *Yuklenen* dosyada manifest var miydi. Bu ikisini ayirmak sart:
    # her yayinladigimiz icerigi imzaladigimiz icin `manifest_present`
    # neredeyse hep True olur ve "kimlik silinmisti, biz yeniden kurduk"
    # durumunu gizler. Emek Karti'nda gosterilen sey bu alandir.
    incoming_manifest_present: Mapped[bool] = mapped_column(Boolean, default=False)
    # Kaynak, kullanici beyani veya manifest olmadan yalnizca kanitlarla
    # mi bulundu? Demo anlatisinin ve arayuz rozetinin dayanagi.
    provenance_recovered: Mapped[bool] = mapped_column(Boolean, default=False)
    # Bizim imzaladigimiz manifestin URN'i (varsa).
    manifest_urn: Mapped[str | None] = mapped_column(String(80), nullable=True)
    # Gomulu filigranin onaltilik kimligi (varsa).
    watermark_tag: Mapped[str | None] = mapped_column(String(16), nullable=True)

    # --- Uretici tercihleri ----------------------------------------------
    remix_allowed: Mapped[bool] = mapped_column(Boolean, default=True)
    commercial_remix_allowed: Mapped[bool] = mapped_column(Boolean, default=True)
    # Ureticinin kendi icin talep ettigi asgari kaynak payi (kampanya
    # kurallariyla birlikte degerlendirilir).
    min_source_share: Mapped[float] = mapped_column(Float, default=0.0)

    campaign_id: Mapped[str | None] = mapped_column(ForeignKey("campaigns.id"), nullable=True)
    # Gonderinin urettigi ham gelir (kampanya disi; bahsis, reklam payi vb.).
    revenue: Mapped[float] = mapped_column(Float, default=0.0)

    # --- Indeks kaliciligi ------------------------------------------------
    # Parmak izinin indekste kullanilan ama yukaridaki sutunlarda
    # karsiligi olmayan parcasi: 3x3 blok hash'leri, onaltilik dizge
    # listesi olarak (phash gibi; isaretsiz 64 bit SQLite'in isaretli
    # INTEGER'ina sigmaz).
    tile_hashes: Mapped[list] = mapped_column(JSON, default=list)
    # CLIP gommesi, float32 ham baytlar (512 x 4 = 2048 bayt).
    #
    # Neden saklaniyor: acilista indeks veritabanindan kuruluyor ve bu,
    # her icerik icin CLIP'i yeniden calistirmak demekti. Vektor burada
    # durunca acilis, model hic yuklenmeden yalnizca FAISS'e ekleme
    # maliyetine iniyor (bkz. services/registry.py, docs/ACILIS-SURESI.md).
    clip_vector: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)

    owner: Mapped[User] = relationship(back_populates="contents")
    campaign: Mapped["Campaign | None"] = relationship(back_populates="contents")
    # Bu icerigin kaynaklarina giden baglar.
    parent_links: Mapped[list["AttributionEdge"]] = relationship(
        back_populates="child",
        foreign_keys="AttributionEdge.child_id",
        cascade="all, delete-orphan",
    )


class AttributionEdge(Base):
    """Bir turev ile kaynagi arasindaki olculmus bag.

    Bu tablo bir *olcum kaydidir*. Pay hesabi buradan turetilir ama
    burada saklanmaz.
    """

    __tablename__ = "attribution_edges"
    __table_args__ = (UniqueConstraint("child_id", "parent_id", name="uq_edge"),)

    id: Mapped[str] = mapped_column(String(16), primary_key=True, default=_uid)
    child_id: Mapped[str] = mapped_column(ForeignKey("contents.id"), index=True)
    parent_id: Mapped[str] = mapped_column(ForeignKey("contents.id"), index=True)

    stage: Mapped[LinkStage] = mapped_column(Enum(LinkStage))
    status: Mapped[LinkStatus] = mapped_column(Enum(LinkStatus), default=LinkStatus.PROPOSED)
    confidence: Mapped[float] = mapped_column(Float)

    # Geometri asamasinin olcumleri. Geometri calismadiysa None.
    visual_coverage: Mapped[float | None] = mapped_column(Float, nullable=True)
    source_usage: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Her asamanin ne bulduğunun tam dokumu - Emek Karti bunu gosterir.
    evidence: Mapped[list] = mapped_column(JSON, default=list)
    # Eslesen bolge maskesinin PNG yolu (arayuzde vurgu katmani).
    mask_path: Mapped[str | None] = mapped_column(String(400), nullable=True)

    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), default=_now, onupdate=_now
    )

    child: Mapped[Content] = relationship(back_populates="parent_links", foreign_keys=[child_id])
    parent: Mapped[Content] = relationship(foreign_keys=[parent_id])

    @property
    def counts_for_share(self) -> bool:
        """Bu bag pay hesabina giriyor mu."""
        return self.status in (LinkStatus.PROPOSED, LinkStatus.CONFIRMED)


class Campaign(Base):
    """Marka sponsorlu remix kampanyasi."""

    __tablename__ = "campaigns"

    id: Mapped[str] = mapped_column(String(16), primary_key=True, default=_uid)
    brand_name: Mapped[str] = mapped_column(String(120))
    title: Mapped[str] = mapped_column(String(200))
    brief: Mapped[str] = mapped_column(Text, default="")
    reward_pool: Mapped[float] = mapped_column(Float)
    status: Mapped[CampaignStatus] = mapped_column(
        Enum(CampaignStatus), default=CampaignStatus.ACTIVE
    )

    # --- Kampanyaya ozel paylasim kurallari -------------------------------
    # Bunlar varsayilan ayarlari ezer; Emek Karti hangisinin uygulandigini yazar.
    commission: Mapped[float] = mapped_column(Float, default=0.10)
    source_floor: Mapped[float] = mapped_column(Float, default=0.15)  # kaynaklara asgari
    creator_ceiling: Mapped[float] = mapped_column(Float, default=0.85)

    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=_now)
    ends_at: Mapped[dt.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    contents: Mapped[list[Content]] = relationship(back_populates="campaign")
    payouts: Mapped[list["Payout"]] = relationship(back_populates="campaign")


class Payout(Base):
    """Dagitilmis odeme. Gerekcesiyle birlikte dondurulmus kayit."""

    __tablename__ = "payouts"

    id: Mapped[str] = mapped_column(String(16), primary_key=True, default=_uid)
    campaign_id: Mapped[str | None] = mapped_column(ForeignKey("campaigns.id"), nullable=True)
    # Odemeyi doguran gonderi (zincirin ucundaki icerik).
    content_id: Mapped[str] = mapped_column(ForeignKey("contents.id"), index=True)
    # Odemeyi alan taraf. Platform payinda None.
    user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    # Payin hangi icerikten dogdugu (zincirdeki hangi halka).
    source_content_id: Mapped[str | None] = mapped_column(
        ForeignKey("contents.id"), nullable=True
    )

    share: Mapped[float] = mapped_column(Float)
    amount: Mapped[float] = mapped_column(Float)
    is_platform_fee: Mapped[bool] = mapped_column(Boolean, default=False)
    # Hesabin tam dokumu - odeme aninda dondurulur.
    rationale: Mapped[dict] = mapped_column(JSON, default=dict)

    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=_now)

    campaign: Mapped["Campaign | None"] = relationship(back_populates="payouts")


class Dispute(Base):
    """Bir baga yapilan itiraz."""

    __tablename__ = "disputes"

    id: Mapped[str] = mapped_column(String(16), primary_key=True, default=_uid)
    edge_id: Mapped[str] = mapped_column(ForeignKey("attribution_edges.id"), index=True)
    raiser_id: Mapped[str] = mapped_column(ForeignKey("users.id"))

    reason: Mapped[str] = mapped_column(Text)
    # Itiraz sahibinin sundugu ek kanit (orijinal dosya, daha eski surum).
    evidence_path: Mapped[str | None] = mapped_column(String(400), nullable=True)

    status: Mapped[DisputeStatus] = mapped_column(Enum(DisputeStatus), default=DisputeStatus.OPEN)
    # Sistemin yeniden olcum sonucu ve karari.
    resolution: Mapped[dict] = mapped_column(JSON, default=dict)

    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=_now)
    resolved_at: Mapped[dt.datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    edge: Mapped[AttributionEdge] = relationship()
    raiser: Mapped[User] = relationship()
