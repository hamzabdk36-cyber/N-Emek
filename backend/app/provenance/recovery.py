"""Koken kurtarma hatti - bes asamanin orkestrasyonu.

Hattin mantigi iki asamali: *ucuz aday uretimi*, ardindan *pahali
dogrulama*.

  Aday uretimi (hepsi paralel calisabilir, milisaniyeler):
    0. C2PA manifest      -> beyan edilmis kaynak, guven 0.99
    1. SHA-256            -> bit-birebir kopya, guven 0.99
    2. Filigran           -> gomulu kimlik (CRC dogrulamali), guven 0.90
    3. pHash / blok hash  -> algisal benzerlik, guven 0.45-0.80
    4. CLIP (cok bolgeli) -> semantik/yapisal benzerlik, guven 0.30-0.75

  Dogrulama (aday basina ~90 ms, bu yuzden sinirli sayida aday):
    5. Homografi + ZNCC   -> baglantiyi dogrular VE kullanilan alan
                             oranini olcer

5. asama iki is birden yapar ve ikincisi projenin ayirt edici yani:
katki payinin girdisi olan "kullanilan icerik orani" burada tahmin
edilmez, olculur.

Karar birlestirme
-----------------
Bagimsiz kanit kaynaklarini gurultulu-VEYA (noisy-OR) ile birlestiriyoruz:
`1 - PI(1 - guven_i)`. Gerekce: her asama kaynagi bagimsiz bir fiziksel
izden buluyor (metadata, piksel istatistigi, frekans alani, yerel
geometri); ayni sonuca farkli yollardan varmalari guveni artirmali.

Iki emniyet supabi var:
  * Yalnizca benzerlik asamalarindan (pHash + CLIP) gelen guven 0.80
    ile sinirlanir. Benzerlik "ayni sahne" ile "ayni icerik"i ayirmaz;
    tek basina yuksek guven vermemeli.
  * Geometrik dogrulama basarisiz olursa yalnizca benzerlikle bulunan
    adayin guveni ceza katsayisiyla dusurulur ve genelde esigin altina
    duser. Yanlis atif, kacirilmis atiftan agirdir.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Protocol

import numpy as np
from PIL import Image

from app.core.config import get_settings
from app.models.entities import LinkStage
from app.provenance import c2pa_service, embedding, geometry, regions, watermark
from app.provenance import fingerprint as fp
from app.provenance.index import ProvenanceIndex

# Yalnizca benzerlik asamalarindan gelebilecek en yuksek guven.
SIMILARITY_ONLY_CAP = 0.80
# Geometrik dogrulamayi gecemeyen benzerlik adayina uygulanan ceza.
UNVERIFIED_PENALTY = 0.40
# Manifest/hash/filigran gibi "beyan" asamalarinin guven tabani.
STRONG_STAGES = {LinkStage.C2PA, LinkStage.EXACT, LinkStage.WATERMARK, LinkStage.DECLARED}


class ContentStore(Protocol):
    """Hattin veritabanina ihtiyac duydugu asgari arayuz.

    Boylece `recovery` modulu SQLAlchemy'den bagimsiz kalir ve
    degerlendirme betiklerinde sahte bir depoyla calistirilabilir.
    """

    def load_image(self, content_id: str) -> np.ndarray | None:
        """Icerigin BGR gorselini doner."""

    def by_watermark(self, tag: str) -> str | None:
        """Filigran kimliginden icerik kimligine cozer."""

    def by_manifest_parent(self, declared_id: str) -> str | None:
        """Manifestte beyan edilen kaynak kimligini icerige cozer."""


@dataclass
class RecoveredLink:
    """Bulunmus ve (mumkunse) olculmus bir kaynak bagi."""

    parent_content_id: str
    stage: LinkStage
    confidence: float
    visual_coverage: float | None = None
    source_usage: float | None = None
    geometry_verified: bool = False
    evidence: list[dict] = field(default_factory=list)
    mask: np.ndarray | None = field(default=None, repr=False)


@dataclass
class RecoveryResult:
    """Bir icerik icin hattin tam ciktisi."""

    links: list[RecoveredLink]
    manifest: c2pa_service.ManifestInfo
    fingerprint: fp.Fingerprint
    embedding: np.ndarray
    watermark_tag: str | None
    # Her asamanin ne yaptigi - Emek Karti ve teknik rapor icin.
    stage_log: list[dict] = field(default_factory=list)
    timings_ms: dict[str, float] = field(default_factory=dict)

    @property
    def best(self) -> RecoveredLink | None:
        return self.links[0] if self.links else None


def _noisy_or(confidences: list[float]) -> float:
    """Bagimsiz kanitlarin birlesik guveni."""
    product = 1.0
    for c in confidences:
        product *= 1.0 - max(0.0, min(1.0, c))
    return 1.0 - product


@dataclass
class _Candidate:
    """Dogrulamadan once biriktirilen aday."""

    content_id: str
    stage_confidences: dict[LinkStage, float] = field(default_factory=dict)
    evidence: list[dict] = field(default_factory=list)

    def note(self, stage: LinkStage, confidence: float, detail: dict) -> None:
        # Ayni asamadan birden fazla sinyal gelirse en gucluyu tut.
        if confidence > self.stage_confidences.get(stage, 0.0):
            self.stage_confidences[stage] = confidence
        self.evidence.append(detail)

    @property
    def strongest_stage(self) -> LinkStage:
        return max(self.stage_confidences.items(), key=lambda kv: kv[1])[0]


def recover(
    image_bgr: np.ndarray,
    raw_bytes: bytes | None,
    file_path,
    index: ProvenanceIndex,
    store: ContentStore,
    *,
    declared_parent_id: str | None = None,
) -> RecoveryResult:
    """Bir icerik icin olasi kaynaklari bulur ve olcer.

    Args:
        image_bgr: Icerik gorseli (OpenCV BGR).
        raw_bytes: Yuklenen dosyanin ham baytlari (SHA-256 icin).
        file_path: Dosya yolu (C2PA okumasi icin).
        index: Aday arama indeksi.
        store: Icerik cozumleyici.
        declared_parent_id: Remix studyosundan gelen beyan. Varsa
            en guclu sinyaldir ama yine de olculur - beyan, ne kadar
            kullanildigini soylemez.
    """
    settings = get_settings()
    timings: dict[str, float] = {}
    stage_log: list[dict] = []
    candidates: dict[str, _Candidate] = {}

    def candidate(content_id: str) -> _Candidate:
        return candidates.setdefault(content_id, _Candidate(content_id))

    pil = Image.fromarray(image_bgr[:, :, ::-1])

    # --- Asama 0: C2PA manifesti -----------------------------------------
    t0 = time.perf_counter()
    manifest = c2pa_service.read(file_path)
    timings["c2pa"] = (time.perf_counter() - t0) * 1000
    if manifest.present:
        resolved = [
            cid
            for declared in manifest.parent_content_ids
            if (cid := store.by_manifest_parent(declared))
        ]
        for cid in resolved:
            candidate(cid).note(
                LinkStage.C2PA,
                c2pa_service.C2PA_CONFIDENCE,
                {
                    "stage": "c2pa",
                    "found": True,
                    "manifest_urn": manifest.urn,
                    "issuer": manifest.issuer,
                    "validation": manifest.validation_state,
                    "aciklama": "Imzali manifest bu kaynagi beyan ediyor.",
                },
            )
        stage_log.append(
            {
                "stage": "c2pa",
                "found": bool(resolved),
                "detail": f"manifest var, {len(resolved)} kaynak cozuldu",
            }
        )
    else:
        stage_log.append(
            {
                "stage": "c2pa",
                "found": False,
                "detail": manifest.error or "manifest yok",
                "aciklama": "Icerik kimligi silinmis veya hic olusturulmamis.",
            }
        )

    # Remix studyosundan gelen beyan
    if declared_parent_id:
        candidate(declared_parent_id).note(
            LinkStage.DECLARED,
            0.95,
            {
                "stage": "declared",
                "found": True,
                "aciklama": "Uretici remix studyosunda bu kaynagi secti.",
            },
        )

    # --- Asama 1: Parmak izleri ve tam eslesme ---------------------------
    t0 = time.perf_counter()
    finger = fp.compute(pil, raw_bytes=raw_bytes)
    timings["fingerprint"] = (time.perf_counter() - t0) * 1000

    exact_id = index.exact(finger.content_hash)
    if exact_id:
        candidate(exact_id).note(
            LinkStage.EXACT,
            0.99,
            {
                "stage": "exact",
                "found": True,
                "content_hash": finger.content_hash[:16] + "...",
                "aciklama": "Dosya bayt bayt ayni: birebir kopya.",
            },
        )
    stage_log.append({"stage": "exact", "found": bool(exact_id), "detail": "SHA-256"})

    # --- Asama 2: Gorunmez filigran --------------------------------------
    t0 = time.perf_counter()
    extracted = watermark.extract(image_bgr)
    timings["watermark"] = (time.perf_counter() - t0) * 1000
    wm_tag = extracted[0] if extracted else None
    wm_owner = store.by_watermark(wm_tag) if wm_tag else None
    if wm_owner:
        candidate(wm_owner).note(
            LinkStage.WATERMARK,
            watermark.WATERMARK_CONFIDENCE,
            {
                "stage": "watermark",
                "found": True,
                "tag": wm_tag,
                "vote_confidence": round(extracted[1], 3) if extracted else None,
                "aciklama": "Piksellere gomulu icerik kimligi okundu (CRC dogrulandi).",
            },
        )
    stage_log.append(
        {
            "stage": "watermark",
            "found": bool(wm_owner),
            "detail": f"kimlik={wm_tag}" if wm_tag else "filigran okunamadi",
        }
    )

    # --- Asama 3-4: Cok bolgeli benzerlik aramasi ------------------------
    t0 = time.perf_counter()
    region_items = list(regions.iter_regions(pil))
    region_vectors = embedding.embed([img for _, img in region_items], batch_size=32)
    timings["embed"] = (time.perf_counter() - t0) * 1000

    t0 = time.perf_counter()
    phash_hits = 0
    for (region_name, region_img), vector in zip(region_items, region_vectors):
        region_finger = fp.compute(region_img)
        for hit in index.search_phash(region_finger, k=5):
            phash_hits += 1
            candidate(hit.content_id).note(
                LinkStage.PHASH,
                hit.confidence,
                {
                    "stage": "phash",
                    "found": True,
                    "region": region_name,
                    "hamming": int(hit.score),
                    "esik": fp.PHASH_MATCH_THRESHOLD,
                    "aciklama": f"'{region_name}' bolgesinin algisal ozeti kaynakla ortusuyor.",
                },
            )
        if region_name == "tam":
            for hit in index.search_tiles(region_finger, k=5):
                candidate(hit.content_id).note(
                    LinkStage.PHASH,
                    hit.confidence,
                    {
                        "stage": "phash_blok",
                        "found": True,
                        "hamming": int(hit.score),
                        "aciklama": "Gorselin bloklari kaynagin bloklariyla eslesiyor.",
                    },
                )
    timings["phash_search"] = (time.perf_counter() - t0) * 1000

    t0 = time.perf_counter()
    clip_hits = 0
    for (region_name, _), vector in zip(region_items, region_vectors):
        for hit in index.search_clip(vector, k=5):
            clip_hits += 1
            candidate(hit.content_id).note(
                LinkStage.CLIP,
                hit.confidence,
                {
                    "stage": "clip",
                    "found": True,
                    "region": region_name,
                    "cosine": round(hit.score, 4),
                    "aciklama": f"'{region_name}' bolgesi kaynakla gorsel olarak benzer.",
                },
            )
    timings["clip_search"] = (time.perf_counter() - t0) * 1000
    stage_log.append({"stage": "phash", "found": phash_hits > 0, "detail": f"{phash_hits} isabet"})
    stage_log.append({"stage": "clip", "found": clip_hits > 0, "detail": f"{clip_hits} isabet"})

    # --- Asama 5: Geometrik dogrulama ve alan olcumu ---------------------
    # Adaylari on guvene gore sirala; en umit vaat edenleri dogrula.
    ordered = sorted(
        candidates.values(),
        key=lambda c: _noisy_or(list(c.stage_confidences.values())),
        reverse=True,
    )[: settings.max_geometry_candidates]

    t0 = time.perf_counter()
    links: list[RecoveredLink] = []
    for cand in ordered:
        source = store.load_image(cand.content_id)
        similarity_only = all(s not in STRONG_STAGES for s in cand.stage_confidences)

        match = None
        if source is not None:
            match = geometry.measure_usage(source, image_bgr)
            cand.evidence.append(match.as_evidence())

        similarity_conf = min(
            SIMILARITY_ONLY_CAP,
            _noisy_or(
                [c for s, c in cand.stage_confidences.items() if s not in STRONG_STAGES]
            ),
        )
        strong_conf = max(
            [c for s, c in cand.stage_confidences.items() if s in STRONG_STAGES], default=0.0
        )

        if match is not None and match.matched:
            geo_conf = min(0.95, 0.55 + 0.40 * match.inlier_ratio)
            fused = _noisy_or([similarity_conf, geo_conf])
            confidence = max(strong_conf, fused)
            coverage = match.visual_coverage
            usage = match.source_usage
            verified = True
            mask = match.retained_mask
        else:
            # Dogrulanamadi. Beyan/imza gibi guclu bir kanit varsa bag
            # ayakta kalir (kaynak silinmis veya cok agir donusmus
            # olabilir) ama alan olculemedigi icin pay hesabinda
            # varsayilan bir oran kullanilacagi isaretlenir.
            confidence = max(strong_conf, similarity_conf * UNVERIFIED_PENALTY)
            coverage = None
            usage = None
            verified = False
            mask = None
            cand.evidence.append(
                {
                    "stage": "geometry",
                    "matched": False,
                    "reason": match.reason if match else "kaynak gorseli yuklenemedi",
                    "aciklama": "Geometrik dogrulama yapilamadi; alan orani olculemedi.",
                }
            )

        if confidence < settings.min_link_confidence:
            continue

        links.append(
            RecoveredLink(
                parent_content_id=cand.content_id,
                stage=cand.strongest_stage,
                confidence=round(confidence, 4),
                visual_coverage=round(coverage, 4) if coverage is not None else None,
                source_usage=round(usage, 4) if usage is not None else None,
                geometry_verified=verified,
                evidence=cand.evidence,
                mask=mask,
            )
        )
    timings["geometry"] = (time.perf_counter() - t0) * 1000

    links.sort(key=lambda link: (-link.confidence, -(link.visual_coverage or 0.0)))
    stage_log.append(
        {
            "stage": "geometry",
            "found": any(link.geometry_verified for link in links),
            "detail": f"{len(ordered)} aday dogrulandi, {len(links)} bag kaldi",
        }
    )

    return RecoveryResult(
        links=links,
        manifest=manifest,
        fingerprint=finger,
        embedding=region_vectors[0] if len(region_vectors) else np.zeros(embedding.EMBEDDING_DIM, np.float32),
        watermark_tag=wm_tag,
        stage_log=stage_log,
        timings_ms={k: round(v, 1) for k, v in timings.items()},
    )
