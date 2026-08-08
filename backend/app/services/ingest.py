"""Icerik alma hatti: yukleme ve remix.

Sira onemlidir ve iki kez parmak izi hesaplanmasinin sebebi budur:

  1. **Gelen dosya uzerinde koken kurtarma.** Kullanicinin getirdigi sey
     ne ise onun uzerinde calisiriz - manifesti silinmis, ekran
     goruntusu alinmis, kirpilmis hali. Kaynak arayisi burada yapilir.
  2. **Yayinlanan dosya uzerinde indeksleme.** Kendi filigranimizi
     gomup manifestimizi imzaladiktan sonra dosyanin baytlari degisir.
     Baskalari bu yayinlanmis hali indirip remixleyecegi icin indekste
     duran parmak izi de yayinlanan halin olmalidir.

Bu ayrimi atlamak, kendi yayinladigimiz iceriklerin birebir kopyasini
taniyamamamiza yol acar.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.entities import (
    AttributionEdge,
    Content,
    LinkStage,
    LinkStatus,
    User,
)
from app.provenance import c2pa_service, embedding, recovery, watermark
from app.provenance import fingerprint as fp
from app.services.registry import IndexService

JPEG_QUALITY = 92


@dataclass
class IngestResult:
    content: Content
    recovery: recovery.RecoveryResult
    created_edges: list[AttributionEdge]
    # Yayin oncesi gelen dosyada manifest var miydi.
    incoming_manifest: bool


def _new_id() -> str:
    return uuid.uuid4().hex[:16]


def _write_jpeg(path: Path, image_bgr: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(path), image_bgr, [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY])


def _save_mask(content_id: str, parent_id: str, mask: np.ndarray | None) -> str | None:
    """Eslesen bolge maskesini diske yazar (arayuzdeki vurgu katmani)."""
    if mask is None:
        return None
    settings = get_settings()
    path = settings.upload_dir / "masks" / f"{content_id}__{parent_id}.png"
    path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(path), mask)
    return str(path)


def ingest(
    session: Session,
    index_service: IndexService,
    *,
    raw_bytes: bytes,
    owner: User,
    title: str,
    caption: str = "",
    declared_parent_id: str | None = None,
    remix_actions: list[str] | None = None,
    remix_allowed: bool = True,
    commercial_remix_allowed: bool = True,
    min_source_share: float = 0.0,
    campaign_id: str | None = None,
) -> IngestResult:
    """Bir gorseli platforma alir, kokenini cozer ve yayinlar.

    Args:
        declared_parent_id: Remix studyosundan geliyorsa kaynak icerik.
            Beyan guclu bir sinyaldir ama olcumun yerine gecmez.
        remix_actions: Uygulanan C2PA eylemleri ("c2pa.cropped" vb.).
    """
    settings = get_settings()
    content_id = _new_id()
    workdir = settings.upload_dir / content_id
    workdir.mkdir(parents=True, exist_ok=True)

    # --- Gelen dosyayi diske al -------------------------------------------
    incoming_path = workdir / "incoming.jpg"
    incoming_path.write_bytes(raw_bytes)
    incoming_bgr = cv2.imdecode(np.frombuffer(raw_bytes, np.uint8), cv2.IMREAD_COLOR)
    if incoming_bgr is None:
        raise ValueError("gorsel cozulemedi")

    # --- 1. Koken kurtarma: gelen dosya uzerinde --------------------------
    result = recovery.recover(
        incoming_bgr,
        raw_bytes,
        incoming_path,
        index_service.index,
        index_service,
        declared_parent_id=declared_parent_id,
    )

    # --- 2. Yayin: filigran + manifest ------------------------------------
    marked = watermark.embed(incoming_bgr, content_id)
    marked_path = workdir / "marked.jpg"
    _write_jpeg(marked_path, marked)

    published_path = workdir / "published.jpg"
    manifest_urn: str | None = None
    if c2pa_service.certs_available():
        parent_for_manifest = _pick_manifest_parent(session, result, declared_parent_id)
        if parent_for_manifest is not None:
            manifest_urn = c2pa_service.sign_remix(
                marked_path,
                published_path,
                content_id=content_id,
                author=owner.display_name,
                title=title,
                parent_path=Path(parent_for_manifest.file_path),
                parent_title=parent_for_manifest.title,
                parent_content_id=parent_for_manifest.id,
                actions=remix_actions or ["c2pa.edited"],
                remix_allowed=remix_allowed,
            )
        else:
            manifest_urn = c2pa_service.sign_original(
                marked_path,
                published_path,
                content_id=content_id,
                author=owner.display_name,
                title=title,
                remix_allowed=remix_allowed,
                commercial_remix_allowed=commercial_remix_allowed,
                min_source_share=min_source_share,
            )
    else:
        # Sertifika yoksa yayinlanan dosya filigranli ama imzasiz olur.
        # Hat calismaya devam eder; yalnizca 0. asama devre disi kalir.
        published_path.write_bytes(marked_path.read_bytes())

    # --- 3. Yayinlanan dosya uzerinden indeksleme -------------------------
    published_bytes = published_path.read_bytes()
    published_bgr = cv2.imdecode(np.frombuffer(published_bytes, np.uint8), cv2.IMREAD_COLOR)
    published_pil = Image.fromarray(published_bgr[:, :, ::-1])
    published_finger = fp.compute(published_pil, raw_bytes=published_bytes)
    published_vector = embedding.embed_one(published_pil)

    height, width = published_bgr.shape[:2]
    content = Content(
        id=content_id,
        owner_id=owner.id,
        title=title,
        caption=caption,
        file_path=str(published_path),
        width=width,
        height=height,
        content_hash=published_finger.content_hash,
        phash=f"{published_finger.phash:016x}",
        dhash=f"{published_finger.dhash:016x}",
        whash=f"{published_finger.whash:016x}",
        manifest_present=manifest_urn is not None,
        incoming_manifest_present=result.manifest.present,
        # Kaynak, beyan veya manifest olmadan yalnizca kanitlarla bulunduysa
        # bu icerigin kokeni "yeniden kurulmus" sayilir.
        provenance_recovered=bool(result.links)
        and declared_parent_id is None
        and not result.manifest.present,
        manifest_urn=manifest_urn,
        watermark_tag=watermark.content_id_to_hex(content_id),
        remix_allowed=remix_allowed,
        commercial_remix_allowed=commercial_remix_allowed,
        min_source_share=min_source_share,
        campaign_id=campaign_id,
    )
    session.add(content)
    session.flush()

    # --- 4. Baglari kaydet -------------------------------------------------
    edges = _persist_links(session, content, result)

    session.commit()
    index_service.add(content, published_finger, published_vector)
    return IngestResult(
        content=content,
        recovery=result,
        created_edges=edges,
        incoming_manifest=result.manifest.present,
    )


def _pick_manifest_parent(
    session: Session, result: recovery.RecoveryResult, declared_parent_id: str | None
) -> Content | None:
    """Manifeste ingredient olarak yazilacak kaynak.

    Yalnizca beyan edilmis veya yuksek guvenli tek bir kaynak yazilir.
    Manifest bir *beyandir*; zayif bir benzerlik tahminini imzalayip
    kriptografik kanit gorunumu vermek dogru olmaz.
    """
    settings = get_settings()
    if declared_parent_id:
        return session.get(Content, declared_parent_id)
    for link in result.links:
        if link.confidence >= settings.auto_confirm_confidence:
            return session.get(Content, link.parent_content_id)
    return None


def _persist_links(
    session: Session, content: Content, result: recovery.RecoveryResult
) -> list[AttributionEdge]:
    settings = get_settings()
    edges: list[AttributionEdge] = []
    for link in result.links:
        if link.parent_content_id == content.id:
            continue
        status = (
            LinkStatus.CONFIRMED
            if link.confidence >= settings.auto_confirm_confidence
            else LinkStatus.PROPOSED
        )
        edge = AttributionEdge(
            child_id=content.id,
            parent_id=link.parent_content_id,
            stage=link.stage,
            status=status,
            confidence=link.confidence,
            visual_coverage=link.visual_coverage,
            source_usage=link.source_usage,
            evidence=link.evidence,
            mask_path=_save_mask(content.id, link.parent_content_id, link.mask),
        )
        session.add(edge)
        edges.append(edge)
    session.flush()
    return edges


def remeasure(
    session: Session,
    index_service: IndexService,
    edge: AttributionEdge,
) -> AttributionEdge:
    """Bir bagi yeniden olcer (itiraz sonrasi kullanilir).

    Olcum kaynak ve turev gorselleri uzerinde bastan kosar; kanit
    listesi ve kapsama guncellenir. Paylar veritabaninda tutulmadigi
    icin bu tek guncelleme tum zinciri tutarli hale getirir.
    """
    from app.provenance import geometry

    child = session.get(Content, edge.child_id)
    parent = session.get(Content, edge.parent_id)
    if child is None or parent is None:
        return edge

    child_img = cv2.imread(child.file_path)
    parent_img = cv2.imread(parent.file_path)
    if child_img is None or parent_img is None:
        return edge

    match = geometry.measure_usage(parent_img, child_img, detector="sift")
    evidence = list(edge.evidence or [])
    evidence.append(
        {
            **match.as_evidence(),
            "aciklama": "Itiraz uzerine SIFT ile yeniden olculdu.",
            "remeasured": True,
        }
    )
    edge.evidence = evidence
    if match.matched:
        edge.visual_coverage = round(match.visual_coverage, 4)
        edge.source_usage = round(match.source_usage, 4)
        edge.confidence = round(
            min(0.95, max(edge.confidence, 0.55 + 0.40 * match.inlier_ratio)), 4
        )
        edge.mask_path = _save_mask(child.id, parent.id, match.retained_mask)
    session.flush()
    return edge
