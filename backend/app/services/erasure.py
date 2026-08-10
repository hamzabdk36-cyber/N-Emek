"""Icerik silme - "unutulma hakki"nin karsiligi.

Neden ayri bir servis
---------------------
Bir icerigi silmek tek satirlik bir `DELETE` degil. Ayni icerikten
turemis izler bes ayri yerde duruyor ve biri kalirsa silme yarim kalir:

  1. Yayinlanan gorsel dosyasi (diskte)
  2. Bagların eslesme maskeleri (diskte, PNG)
  3. Parmak izleri ve CLIP vektoru (veritabani satirinda)
  4. Bagların kendisi ve o baglara acilmis itirazlar
  5. Bellekteki FAISS indeksi ve diskteki anlik goruntusu

Mali kayitlar neden silinmiyor
------------------------------
`Payout`, gerceklesmis bir odemenin donmus kaydi. Gelir dagitan bir
sistemde bunu silmek denetlenebilirligi yok eder; ayrica `content_id`
zorunlu bir yabanci anahtar. Bu yuzden **odemesi olan icerik
silinmiyor** ve uc bunu acik bir mesajla soyluyor.

Bu, "unutulma hakki"nin tam karsilanmadigi bir sinir ve
`docs/VERI-MODEL-ETIK.md` icinde acikca yaziyor: odeme kayitlarinin
anonimlestirilmesi ayri bir istir ve urunlesme asamasina birakildi.
"""

from __future__ import annotations

import logging
from pathlib import Path

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.entities import AttributionEdge, Content, Dispute, Payout

log = logging.getLogger("nemek.erasure")


class SilinemezIcerik(Exception):
    """Icerige odeme yapilmis; mali kayit korunmali."""


def odeme_sayisi(session: Session, content_id: str) -> int:
    stmt = select(Payout).where(
        or_(Payout.content_id == content_id, Payout.source_content_id == content_id)
    )
    return len(list(session.scalars(stmt)))


def _dosya_sil(yol: str | None) -> bool:
    if not yol:
        return False
    try:
        path = Path(yol)
        if path.exists():
            path.unlink()
            return True
    except OSError as exc:  # izin/kilit sorunu silmeyi durdurmamali
        log.warning("dosya silinemedi: %s (%s)", yol, exc)
    return False


def delete_content(session: Session, content: Content) -> dict:
    """Icerigi ve ondan turemis her izi siler.

    Cagiran taraf yetkiyi dogrulamis olmali (yalnizca sahibi).
    Odeme varsa `SilinemezIcerik` firlatir - hicbir sey silinmez.

    Returns:
        Nelerin silindiginin dokumu; uc bunu kullaniciya doner.
    """
    odemeler = odeme_sayisi(session, content.id)
    if odemeler:
        raise SilinemezIcerik(
            f"Bu içeriğe {odemeler} ödeme bağlı. Gerçekleşmiş ödemelerin kaydı "
            "silinemez; mali kayıtların bütünlüğü korunmalıdır."
        )

    content_id = content.id

    # Icerigin hem kaynak hem turev tarafindaki tum baglari.
    baglar = list(
        session.scalars(
            select(AttributionEdge).where(
                or_(
                    AttributionEdge.child_id == content_id,
                    AttributionEdge.parent_id == content_id,
                )
            )
        )
    )
    bag_kimlikleri = [b.id for b in baglar]

    # Bu baglara acilmis itirazlar once gitmeli: yabanci anahtar onlara
    # bagli ve silinmezlerse veritabaninda oksuz kayit kalir.
    itirazlar = []
    if bag_kimlikleri:
        itirazlar = list(
            session.scalars(
                select(Dispute).where(Dispute.edge_id.in_(bag_kimlikleri))
            )
        )

    silinen_maske = 0
    for bag in baglar:
        if _dosya_sil(bag.mask_path):
            silinen_maske += 1

    gorsel_silindi = _dosya_sil(content.file_path)

    for itiraz in itirazlar:
        session.delete(itiraz)
    for bag in baglar:
        session.delete(bag)
    session.delete(content)
    session.commit()

    log.info(
        "içerik silindi: %s (bağ=%s, itiraz=%s, maske=%s, görsel=%s)",
        content_id,
        len(baglar),
        len(itirazlar),
        silinen_maske,
        gorsel_silindi,
    )
    return {
        "content_id": content_id,
        "silinen_bag": len(baglar),
        "silinen_itiraz": len(itirazlar),
        "silinen_maske": silinen_maske,
        "gorsel_silindi": gorsel_silindi,
    }
