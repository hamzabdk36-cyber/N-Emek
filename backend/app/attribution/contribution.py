"""Katki payi motoru.

Bu modulun tek isi: olculmus bir icerik zincirini, gerekcesi satir satir
yazilmis bir pay dagilimina cevirmek.

Tasarim kurallari
-----------------
1. **Saf fonksiyon.** Hesap, veritabanindan bagimsiz calisir
   (`compute_shares`). Boylece birim testlerle sinanabilir ve
   degerlendirme betikleri zincirleri elle kurup formulu dogrulayabilir.
2. **Her kural loglanir.** Bir tabana takilan, tavana carpan veya
   elenen her pay icin insan okuyabilir bir satir uretilir. Emek Karti
   bu satirlari gosterir; "sistem boyle hesapladi" demek yetmez.
3. **Belirsizlik ureticide kalir.** Guven dustukce kaynagin payi duser
   ve fark son ureticide kalir. Bu, icerik kimligini korumayi odullendirir
   ve kaynaga itiraz etme yolunu acik birakir - kanit sunulunca yeniden
   olculur ve pay yukselir.

Hesap sirasi (sira onemlidir, her adim bir oncekinin ciktisini kisitlar)
------------------------------------------------------------------------
  1. Her kaynak icin ham agirlik = kapsama^a x guven^b x sonumleme^(d-1)
  2. Kaynaklarin toplam agirligi, uretici tabanini asamayacak sekilde
     oranli olarak kisilir
  3. Kampanyanin kaynak tabani uygulanir (kaynak varsa)
  4. Ureticinin tavani uygulanir
  5. Kaynaklarin kendi asgari pay talepleri (yalnizca yuksek guvenli
     baglarda) uygulanir
  6. Cok kucuk paylar elenir, tutar oranli dagitilir
  7. Platform komisyonu brut gelirden dusulur, kalan paylara bolunur
"""

from __future__ import annotations

from dataclasses import dataclass, field

from app.core.config import Settings, get_settings


@dataclass
class ChainNode:
    """Zincirdeki bir kaynak halkasi (yaprak icerik haric)."""

    content_id: str
    owner_id: str
    owner_name: str
    # Yapraga uzaklik: dogrudan kaynak = 1, onun kaynagi = 2 ...
    depth: int
    # Kaynagin yaprak icerikte *kendi kattigi* alan orani (ozel kapsama).
    # Zincirdeki tum dugumlerin ozel kapsamalari 1.0'a toplanir; bkz.
    # chain.build_chain. Pay hesabinin temeli budur.
    coverage: float
    # Yapraga giden yol boyunca birlesik guven.
    confidence: float
    # Kaynagin yaprakta gorunen *toplam* alani (kendi kaynaklarindan
    # gelenler dahil). Yalnizca Emek Karti'nda gosterilir, hesaba girmez.
    total_coverage: float | None = None
    geometry_verified: bool = True
    # Ureticinin kendi manifestinde beyan ettigi asgari pay talebi.
    min_source_share: float = 0.0
    stage: str = ""


@dataclass
class LeafInfo:
    """Geliri doguran icerik ve sahibi."""

    content_id: str
    owner_id: str
    owner_name: str


@dataclass
class Rules:
    """Bu hesapta gecerli kurallar. Kampanya varsa varsayilanlari ezer."""

    commission: float
    creator_floor: float
    creator_ceiling: float
    source_floor: float
    min_payout_share: float
    chain_damping: float
    coverage_exponent: float
    confidence_exponent: float
    unverified_coverage: float
    source_label: str = "varsayılan kurallar"

    @classmethod
    def from_settings(cls, settings: Settings | None = None) -> "Rules":
        s = settings or get_settings()
        return cls(
            commission=s.platform_commission,
            creator_floor=s.creator_floor,
            creator_ceiling=s.creator_ceiling,
            source_floor=0.0,
            min_payout_share=s.min_payout_share,
            chain_damping=s.chain_damping,
            coverage_exponent=s.coverage_exponent,
            confidence_exponent=s.confidence_exponent,
            unverified_coverage=s.unverified_coverage,
        )

    def with_campaign(
        self, *, commission: float, source_floor: float, creator_ceiling: float, label: str
    ) -> "Rules":
        return Rules(
            commission=commission,
            creator_floor=self.creator_floor,
            creator_ceiling=creator_ceiling,
            source_floor=source_floor,
            min_payout_share=self.min_payout_share,
            chain_damping=self.chain_damping,
            coverage_exponent=self.coverage_exponent,
            confidence_exponent=self.confidence_exponent,
            unverified_coverage=self.unverified_coverage,
            source_label=label,
        )


@dataclass
class Party:
    """Dagilimda pay alan bir taraf."""

    role: str  # "creator" | "source" | "platform"
    user_id: str | None
    user_name: str
    content_id: str | None
    share: float
    amount: float = 0.0
    # Payin nasil olustugunun sayisal dokumu.
    factors: dict = field(default_factory=dict)
    # Bu paya uygulanan kurallarin insan okuyabilir listesi.
    rules_applied: list[str] = field(default_factory=list)


@dataclass
class Distribution:
    """Tam dagilim ve gerekcesi."""

    content_id: str
    gross_revenue: float
    commission_amount: float
    distributable: float
    parties: list[Party]
    # Dagilimin tamamina uygulanan kurallarin gunlugu.
    rules_log: list[str] = field(default_factory=list)
    rules_label: str = ""

    @property
    def creator(self) -> Party:
        return next(p for p in self.parties if p.role == "creator")

    @property
    def sources(self) -> list[Party]:
        return [p for p in self.parties if p.role == "source"]

    def total_share(self) -> float:
        return sum(p.share for p in self.parties if p.role != "platform")


def _pct(value: float) -> str:
    """Orani Turkce yazim kurallarina gore bicimlendirir.

    Ondalik ayraci virguldur. Yuzde isareti sayidan once gelir ve
    bitisik yazilir: %12,5
    """
    return f"%{value * 100:.1f}".replace(".", ",")


def compute_shares(
    leaf: LeafInfo,
    chain: list[ChainNode],
    revenue: float,
    rules: Rules | None = None,
) -> Distribution:
    """Zinciri pay dagilimina cevirir.

    Paylar her zaman 1.0'a toplanir (platform komisyonu haric; komisyon
    brut gelirden ayri dusulur).
    """
    rules = rules or Rules.from_settings()
    log: list[str] = []

    # --- 1. Ham agirliklar ------------------------------------------------
    weights: dict[str, float] = {}
    factors: dict[str, dict] = {}
    for node in chain:
        coverage = node.coverage
        node_notes: list[str] = []
        if not node.geometry_verified:
            # Ikame degil *tavan*: zincirin bir halkasi olculemediyse
            # gelen deger zaten ihtiyatli carpanlari icermis olabilir
            # (bkz. chain.build_chain). Tavan uygulamak hem cok adimli
            # zincirde varsayimin iki kez inmesini onler hem de yuksek
            # bir kapsamanin dogrulanmadan gecmesini engeller.
            capped = min(coverage, rules.unverified_coverage)
            node_notes.append(
                f"Alan oranı ölçülemedi; ihtiyatlı tavan {_pct(rules.unverified_coverage)} "
                f"uygulandı, kapsama {_pct(capped)} alındı."
            )
            coverage = capped

        damping = rules.chain_damping ** (node.depth - 1)
        weight = (
            (coverage**rules.coverage_exponent)
            * (node.confidence**rules.confidence_exponent)
            * damping
        )
        weights[node.content_id] = weight
        factors[node.content_id] = {
            "kapsama": round(coverage, 4),
            "toplam_kapsama": (
                round(node.total_coverage, 4) if node.total_coverage is not None else None
            ),
            "guven": round(node.confidence, 4),
            "derinlik": node.depth,
            "sonumleme": round(damping, 4),
            "ham_agirlik": round(weight, 4),
            "notlar": node_notes,
        }

    sources_total = sum(weights.values())

    # --- 2. Uretici tabani ------------------------------------------------
    max_sources = 1.0 - rules.creator_floor
    if sources_total > max_sources and sources_total > 0:
        scale = max_sources / sources_total
        weights = {k: v * scale for k, v in weights.items()}
        # Apostrofla ek almaktan kaciniliyor (bkz. CLAUDE.md): "%80,0'e"
        # hem imla kurali disinda hem de ondalik virgulunun hemen
        # ardindan geldigi icin okunmasi zor.
        log.append(
            f"Kaynakların toplamı {_pct(sources_total)} idi; üreticiye bırakılan "
            f"{_pct(rules.creator_floor)} taban için oranlı olarak "
            f"{_pct(max_sources)} düzeyine çekildi."
        )
        sources_total = max_sources

    # --- 3. Kampanyanin kaynak tabani ------------------------------------
    if chain and rules.source_floor > 0 and sources_total < rules.source_floor:
        if sources_total > 0:
            scale = rules.source_floor / sources_total
            weights = {k: v * scale for k, v in weights.items()}
        else:
            # Olculebilir agirlik yok ama kaynak var: tabani esit bol.
            weights = {n.content_id: rules.source_floor / len(chain) for n in chain}
        log.append(
            f"Kampanya kuralı: kaynaklara en az {_pct(rules.source_floor)} ayrılır. "
            f"Hesaplanan {_pct(sources_total)} bu tabana yükseltildi."
        )
        sources_total = rules.source_floor

    # --- 4. Uretici tavani ------------------------------------------------
    creator_share = 1.0 - sources_total
    if chain and creator_share > rules.creator_ceiling:
        needed = 1.0 - rules.creator_ceiling
        if sources_total > 0:
            scale = needed / sources_total
            weights = {k: v * scale for k, v in weights.items()}
        else:
            weights = {n.content_id: needed / len(chain) for n in chain}
        log.append(
            f"Üretici tavanı {_pct(rules.creator_ceiling)}; kaynakların payı "
            f"{_pct(sources_total)} yerine {_pct(needed)} olarak alındı."
        )
        sources_total = needed
        creator_share = rules.creator_ceiling

    # --- 5. Kaynagin kendi asgari pay talebi -----------------------------
    for node in chain:
        if node.min_source_share <= 0:
            continue
        current = weights.get(node.content_id, 0.0)
        if current >= node.min_source_share:
            continue
        gap = node.min_source_share - current
        # Farki ureticiden al; uretici tabaninin altina inmeyecek kadar.
        available = max(0.0, (1.0 - sum(weights.values())) - rules.creator_floor)
        granted = min(gap, available)
        if granted <= 0:
            factors[node.content_id]["notlar"].append(
                f"Üretici beyan ettiği asgari {_pct(node.min_source_share)} payı talep etti "
                f"ancak üretici tabanı nedeniyle uygulanamadı."
            )
            continue
        weights[node.content_id] = current + granted
        factors[node.content_id]["notlar"].append(
            f"Üretici manifestinde asgari {_pct(node.min_source_share)} pay beyan etmişti; "
            f"pay {_pct(current)} yerine {_pct(current + granted)} olarak ayarlandı."
        )

    creator_share = 1.0 - sum(weights.values())

    # --- 6. Cok kucuk paylari ele -----------------------------------------
    dropped = {k: v for k, v in weights.items() if v < rules.min_payout_share}
    if dropped:
        freed = sum(dropped.values())
        for k in dropped:
            weights.pop(k)
        log.append(
            f"{len(dropped)} kaynağın payı ödeme eşiği {_pct(rules.min_payout_share)} "
            f"altında kaldı; toplam {_pct(freed)} kalan taraflara dağıtıldı."
        )
        creator_share += freed

    # --- 7. Komisyon ve tutarlar ------------------------------------------
    commission_amount = revenue * rules.commission
    distributable = revenue - commission_amount

    parties: list[Party] = [
        Party(
            role="creator",
            user_id=leaf.owner_id,
            user_name=leaf.owner_name,
            content_id=leaf.content_id,
            share=round(creator_share, 6),
            amount=round(distributable * creator_share, 2),
            factors={"aciklama": "Kaynaklara ayrılan pay düşüldükten sonra kalan."},
            rules_applied=[
                f"Üretici tabanı {_pct(rules.creator_floor)}, tavanı {_pct(rules.creator_ceiling)}."
            ],
        )
    ]

    by_id = {n.content_id: n for n in chain}
    for content_id, weight in sorted(weights.items(), key=lambda kv: -kv[1]):
        node = by_id[content_id]
        parties.append(
            Party(
                role="source",
                user_id=node.owner_id,
                user_name=node.owner_name,
                content_id=content_id,
                share=round(weight, 6),
                amount=round(distributable * weight, 2),
                factors=factors[content_id],
                rules_applied=list(factors[content_id]["notlar"]),
            )
        )

    parties.append(
        Party(
            role="platform",
            user_id=None,
            user_name=get_settings().platform_name,
            content_id=None,
            share=round(rules.commission, 6),
            amount=round(commission_amount, 2),
            factors={"aciklama": "Kampanya yönetimi ve analiz hizmeti komisyonu."},
            rules_applied=[f"Brüt gelir üzerinden {_pct(rules.commission)} oranında."],
        )
    )

    return Distribution(
        content_id=leaf.content_id,
        gross_revenue=round(revenue, 2),
        commission_amount=round(commission_amount, 2),
        distributable=round(distributable, 2),
        parties=parties,
        rules_log=log,
        rules_label=rules.source_label,
    )
