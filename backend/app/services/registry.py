"""Arama indeksinin yasam dongusu ve icerik cozumleme.

`recovery.ContentStore` protokolunu veritabani uzerinden karsilar ve
FAISS indekslerini surecte ayakta tutar.

Acilis maliyeti - cozulen sorun
-------------------------------
Indeks eskiden her acilista **veritabanindaki her icerigin gorselini
okuyup CLIP'i yeniden calistirarak** kuruluyordu. Uc icerikle fark
yoktu; 280 icerikle acilis dakikalara cikiyordu, cunku maliyet icerik
basina bir model cikarimi. Olculmus rakamlar: `docs/ACILIS-SURESI.md`.

Uc kademeli acilis (`load_or_rebuild`):

  1. **anlik goruntu** - `data/index/` altindaki FAISS dosyalari
     okunur. Kimlik kumesi veritabaniyla ayniysa kullanilir. En hizli
     yol; model hic yuklenmez.
  2. **veritabani** - anlik goruntu yok ya da bayatsa indeks
     veritabanindaki sutunlardan kurulur: parmak izi phash/dhash/whash
     ve `tile_hashes`'ten, CLIP vektoru `clip_vector`'dan. Gorsel
     dosyalarina hic dokunulmaz, model yuklenmez.
  3. **gorseller** - yalnizca vektoru eksik icerikler icin (eski
     kayitlar, elle eklenmis veri) gorsel okunur ve CLIP calisir.
     Hesaplanan degerler veritabanina geri yazilir, yani bu yol icerik
     basina **bir kez** odenir.

Anlik goruntu bir *onbellek*, kaynak dogru degil: bayatsa sessizce
atilir ve 2. kademe devreye girer. Bu yuzden onu her yuklemede
guncellemeye gerek yok - kapanista bir kez yazmak yetiyor.
"""

from __future__ import annotations

import logging
import threading
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.entities import Content
from app.provenance import embedding
from app.provenance import fingerprint as fp
from app.provenance.index import ProvenanceIndex
from app.provenance.watermark import content_id_to_hex

log = logging.getLogger("nemek.index")


def vektor_bayta(vector: np.ndarray) -> bytes:
    """CLIP vektorunu veritabaninda saklanan ham float32 baytlara cevirir."""
    return np.asarray(vector, dtype=np.float32).reshape(-1).tobytes()


def bayttan_vektor(raw: bytes | None) -> np.ndarray | None:
    if not raw:
        return None
    vec = np.frombuffer(raw, dtype=np.float32)
    return vec if vec.size == embedding.EMBEDDING_DIM else None


def parmak_izi_satirdan(content: Content) -> fp.Fingerprint:
    """Veritabani satirindan parmak izini geri kurar - gorsel okumadan."""
    return fp.Fingerprint(
        content_hash=content.content_hash,
        phash=int(content.phash, 16),
        dhash=int(content.dhash, 16),
        whash=int(content.whash, 16),
        tiles=[int(t, 16) for t in (content.tile_hashes or [])],
    )


def tile_hex(finger: fp.Fingerprint) -> list[str]:
    return [f"{t:016x}" for t in finger.tiles]


class IndexService:
    """Surec omurlu indeks + icerik cozumleyici."""

    def __init__(self) -> None:
        self._index = ProvenanceIndex()
        self._lock = threading.Lock()
        # content_id -> dosya yolu (geometri asamasi icin)
        self._paths: dict[str, str] = {}
        # filigran kimligi -> content_id
        self._watermarks: dict[str, str] = {}
        # gorsel onbellegi: geometri her aday icin kaynagi okur
        self._image_cache: dict[str, np.ndarray] = {}

    # -- indeks yonetimi ---------------------------------------------------
    @property
    def index(self) -> ProvenanceIndex:
        return self._index

    @property
    def snapshot_dir(self) -> Path:
        return Path(get_settings().index_dir) / "snapshot"

    def load_or_rebuild(self, session: Session) -> tuple[int, str]:
        """Acilis yolu. `(icerik sayisi, kullanilan kademe)` doner.

        Kademeler icin modul basligindaki acikalamaya bakin.
        """
        contents = list(session.scalars(select(Content)))
        if not contents:
            return 0, "boş"

        if self._anlik_goruntuden_yukle(contents):
            return len(contents), "anlık görüntü"

        eksik = self.rebuild(session)
        self.save_snapshot()
        return len(contents), "görseller" if eksik else "veritabanı"

    def _anlik_goruntuden_yukle(self, contents: list[Content]) -> bool:
        """Diskteki indeksi yukler; veritabaniyla uyusmuyorsa vazgecer."""
        dizin = self.snapshot_dir
        if not (dizin / "ids.json").exists():
            return False
        try:
            index = ProvenanceIndex.load(dizin)
        except Exception as exc:  # bozuk/eski bicimli dosya
            log.warning("indeks anlık görüntüsü okunamadı, yeniden kurulacak: %s", exc)
            return False

        # Uyum olcutu kimlik kumesi: icerik eklenmis/silinmisse anlik
        # goruntu bayattir. Icerik *degismez* oldugu icin (yeni surum
        # yeni kimlik) bu kontrol yeterli.
        beklenen = {c.id for c in contents}
        if set(index.content_ids()) != beklenen:
            log.info("indeks anlık görüntüsü bayat, yeniden kurulacak")
            return False

        with self._lock:
            self._index = index
            self._paths.clear()
            self._watermarks.clear()
            self._image_cache.clear()
            for content in contents:
                self._register(content)
        return True

    def rebuild(self, session: Session) -> int:
        """Indeksi veritabanindan bastan kurar.

        Vektoru saklanmis icerikler icin gorsel hic okunmaz ve model
        yuklenmez. Eksik olanlar hesaplanip veritabanina geri yazilir.
        `int` donusu: gorselden hesaplanmak zorunda kalinan icerik sayisi.
        """
        with self._lock:
            self._index = ProvenanceIndex()
            self._paths.clear()
            self._watermarks.clear()
            self._image_cache.clear()

            contents = list(session.scalars(select(Content)))
            if not contents:
                return 0

            # 1. Hazir olanlar: yalnizca FAISS'e ekleme.
            #
            # Hazir olma olcutu yalnizca vektor. Blok hash listesinin bos
            # olmasi "hesaplanmadi" demek degil - bos da gecerli bir
            # deger. Ikisi zaten hep birlikte yaziliyor (ingest ve
            # asagidaki geri yazma), dolayisiyla tek olcut yetiyor ve
            # "bos liste" ile "hic hesaplanmadi" karismiyor.
            eksikler: list[Content] = []
            for content in contents:
                vector = bayttan_vektor(content.clip_vector)
                if vector is None:
                    eksikler.append(content)
                    continue
                self._index.add(content.id, parmak_izi_satirdan(content), vector)
                self._register(content)

            if not eksikler:
                return 0

            # 2. Eksikler: gorseli oku, hesapla, veritabanina geri yaz.
            log.info("%s içerik için parmak izi/vektör hesaplanıyor", len(eksikler))
            images: list[Image.Image] = []
            usable: list[Content] = []
            for content in eksikler:
                path = Path(content.file_path)
                if not path.exists():
                    continue
                images.append(Image.open(path).convert("RGB"))
                usable.append(content)

            if not usable:
                return 0

            vectors = embedding.embed(images, batch_size=32)
            for content, pil, vector in zip(usable, images, vectors):
                finger = fp.compute(pil, raw_bytes=Path(content.file_path).read_bytes())
                self._index.add(content.id, finger, vector)
                self._register(content)
                content.tile_hashes = tile_hex(finger)
                content.clip_vector = vektor_bayta(vector)
            session.commit()
            return len(usable)

    def save_snapshot(self) -> None:
        """Indeksi diske yazar. Hata acilisi/kapanisi engellememeli."""
        try:
            with self._lock:
                self._index.save(self.snapshot_dir)
        except Exception as exc:
            log.warning("indeks anlık görüntüsü yazılamadı: %s", exc)

    def add(self, content: Content, finger: fp.Fingerprint, vector: np.ndarray) -> None:
        with self._lock:
            self._index.add(content.id, finger, vector)
            self._register(content)

    def _register(self, content: Content) -> None:
        self._paths[content.id] = content.file_path
        # Filigran kimligi icerik kimliginden turetildigi icin tersine
        # eslemeyi burada kurabiliyoruz; ayrica saklamaya gerek yok.
        self._watermarks[content_id_to_hex(content.id)] = content.id

    def forget_image(self, content_id: str) -> None:
        self._image_cache.pop(content_id, None)

    # -- ContentStore protokolu -------------------------------------------
    def load_image(self, content_id: str) -> np.ndarray | None:
        cached = self._image_cache.get(content_id)
        if cached is not None:
            return cached
        path = self._paths.get(content_id)
        if not path:
            return None
        image = cv2.imread(path)
        if image is None:
            return None
        # Onbellek sinirsiz buyumesin; prototipte basit bir tavan yeterli.
        if len(self._image_cache) > 256:
            self._image_cache.clear()
        self._image_cache[content_id] = image
        return image

    def by_watermark(self, tag: str) -> str | None:
        return self._watermarks.get(tag)

    def by_manifest_parent(self, declared_id: str) -> str | None:
        """Manifestteki kimlik dogrudan bizim icerik kimligimizdir."""
        return declared_id if declared_id in self._paths else None

    def __len__(self) -> int:
        return len(self._index)


_service: IndexService | None = None


def get_index_service() -> IndexService:
    global _service
    if _service is None:
        _service = IndexService()
    return _service


def reset_index_service() -> None:
    """Testler icin: surec omurlu tekili sifirlar."""
    global _service
    _service = None
    get_settings.cache_clear()
