"""Indeks kaliciligi ve acilis yolu.

Sinanan iddia: **acilista CLIP yeniden calismaz.** Bu, olculebilir ama
gozle gorulemez bir ozellik - indeks her iki yolda da dogru kuruluyor,
fark yalnizca surede. Dolayisiyla bir gerileme (or. vektorun
saklanmayi birakmasi) hicbir testi kirmadan gecebilir ve ancak juri
demosunda 280 icerikle acilis dakikalara ciktiginda fark edilirdi.

Testler modelin *cagrilip cagrilmadigini* dogrudan sinar: `embedding.embed`
patlayacak sekilde degistirilir. Cagrilirsa test kirmizi olur.

Olcum: `backend/eval/run_startup.py` -> `docs/ACILIS-SURESI.md`
"""

from __future__ import annotations

import shutil

import numpy as np
import pytest
from PIL import Image
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import get_settings
from app.models.entities import Base, Content, User
from app.provenance import embedding
from app.provenance import fingerprint as fp
from app.services.registry import (
    IndexService,
    bayttan_vektor,
    parmak_izi_satirdan,
    tile_hex,
    vektor_bayta,
)
from tests.conftest import gorsel_korpusu


@pytest.fixture(scope="module")
def foto():
    return gorsel_korpusu()[0]


@pytest.fixture()
def session(tmp_path):
    """Bu modul icin ayri bir veritabani.

    Paylasilan test veritabani kullanilamaz: `rebuild` *butun* icerigi
    okuyor, yani diger test modullerinin yazdigi kayitlar da olcume
    girerdi.
    """
    engine = create_engine(f"sqlite:///{(tmp_path / 'indeks.db').as_posix()}")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, expire_on_commit=False)
    oturum = Session()
    yield oturum
    oturum.close()


@pytest.fixture(autouse=True)
def temiz_anlik_goruntu():
    """Her test kendi anlik goruntusuyle bassin."""
    dizin = IndexService().snapshot_dir
    shutil.rmtree(dizin, ignore_errors=True)
    yield
    shutil.rmtree(dizin, ignore_errors=True)


@pytest.fixture()
def model_yasak(monkeypatch):
    """CLIP cagrilirsa test patlasin."""

    def _patla(*args, **kwargs):
        raise AssertionError("CLIP çalıştırıldı: vektör veritabanından okunmalıydı")

    monkeypatch.setattr(embedding, "embed", _patla)
    monkeypatch.setattr(embedding, "embed_one", _patla)


# ---------------------------------------------------------------------------
def icerik_yaz(session, foto, sayi: int = 3, *, vektorlu: bool = True) -> list[Content]:
    """Veritabanina icerik yazar; `vektorlu=False` eski kayitlari taklit eder."""
    sahip = session.get(User, "sahip01") or User(
        id="sahip01", handle="sahip", display_name="Sahip"
    )
    session.add(sahip)
    session.flush()

    pil = Image.open(foto).convert("RGB")
    finger = fp.compute(pil, raw_bytes=foto.read_bytes())
    vector = np.random.default_rng(0).standard_normal(embedding.EMBEDDING_DIM).astype(
        np.float32
    )

    yazilan = []
    for i in range(sayi):
        content = Content(
            id=f"kalici{i:09d}",
            owner_id=sahip.id,
            title=f"İçerik {i}",
            file_path=str(foto),
            width=pil.width,
            height=pil.height,
            # content_hash benzersiz olmali: tam kopya tespiti bunu kullaniyor.
            content_hash=f"{finger.content_hash[:-2]}{i:02x}",
            phash=f"{finger.phash:016x}",
            dhash=f"{finger.dhash:016x}",
            whash=f"{finger.whash:016x}",
            tile_hashes=tile_hex(finger) if vektorlu else [],
            clip_vector=vektor_bayta(vector) if vektorlu else None,
        )
        session.add(content)
        yazilan.append(content)
    session.commit()
    return yazilan


# ---------------------------------------------------------------------------
class TestVektorDonusumu:
    def test_vektor_gidip_geliyor(self):
        vector = np.random.default_rng(1).standard_normal(
            embedding.EMBEDDING_DIM
        ).astype(np.float32)

        geri = bayttan_vektor(vektor_bayta(vector))

        assert geri is not None
        np.testing.assert_allclose(geri, vector, rtol=0, atol=0)

    def test_bos_ve_bozuk_vektor_none_doner(self):
        assert bayttan_vektor(None) is None
        assert bayttan_vektor(b"") is None
        # Yanlis boyut: eski bir kayit ya da bozuk bayt dizisi.
        assert bayttan_vektor(np.zeros(8, dtype=np.float32).tobytes()) is None

    def test_parmak_izi_satirdan_geri_kuruluyor(self, session, foto):
        [content] = icerik_yaz(session, foto, sayi=1)
        pil = Image.open(foto).convert("RGB")
        beklenen = fp.compute(pil, raw_bytes=foto.read_bytes())

        geri = parmak_izi_satirdan(content)

        assert geri.phash == beklenen.phash
        assert geri.dhash == beklenen.dhash
        assert geri.whash == beklenen.whash
        assert geri.tiles == beklenen.tiles


class TestAcilisKademeleri:
    def test_vektor_saklanmissa_model_calismiyor(self, session, foto, model_yasak):
        icerik_yaz(session, foto, sayi=3)
        servis = IndexService()

        eksik = servis.rebuild(session)

        assert eksik == 0, "hiçbir içerik görselden hesaplanmamalıydı"
        assert len(servis) == 3

    def test_vektoru_eksik_icerik_hesaplanip_geri_yaziliyor(
        self, session, foto, monkeypatch
    ):
        """Eski kayitlar bir kez hesaplanir ve bir daha hesaplanmaz."""
        icerikler = icerik_yaz(session, foto, sayi=2, vektorlu=False)
        sahte = np.ones((2, embedding.EMBEDDING_DIM), dtype=np.float32)
        cagri = {"sayi": 0}

        def _embed(images, **kwargs):
            cagri["sayi"] += 1
            return sahte[: len(images)]

        monkeypatch.setattr(embedding, "embed", _embed)

        servis = IndexService()
        eksik = servis.rebuild(session)

        assert eksik == 2
        assert cagri["sayi"] == 1
        # Sutunlar geri yazilmis olmali.
        for content in icerikler:
            session.refresh(content)
            assert content.clip_vector, "vektör veritabanına yazılmadı"
            assert content.tile_hashes, "blok hash'leri veritabanına yazılmadı"

        # Ikinci kurulumda model artik gerekmiyor.
        monkeypatch.setattr(
            embedding,
            "embed",
            lambda *a, **k: pytest.fail("ikinci kurulumda CLIP çalıştırıldı"),
        )
        assert IndexService().rebuild(session) == 0

    def test_anlik_goruntu_yazilip_okunuyor(self, session, foto, model_yasak):
        icerik_yaz(session, foto, sayi=3)
        kuran = IndexService()
        kuran.rebuild(session)
        kuran.save_snapshot()

        yeni = IndexService()
        sayi, kademe = yeni.load_or_rebuild(session)

        assert kademe == "anlık görüntü"
        assert sayi == 3
        assert len(yeni) == 3

    def test_bayat_anlik_goruntu_atiliyor(self, session, foto, model_yasak):
        icerik_yaz(session, foto, sayi=2)
        kuran = IndexService()
        kuran.rebuild(session)
        kuran.save_snapshot()

        # Anlik goruntu alindiktan sonra icerik eklenirse bayatlar.
        yeni_icerik = Content(
            id="kalicisonradan",
            owner_id="sahip01",
            title="Sonradan eklendi",
            file_path=str(foto),
            width=10,
            height=10,
            content_hash="sonradan-eklenen-benzersiz-ozet",
            phash="0" * 16,
            dhash="0" * 16,
            whash="0" * 16,
            tile_hashes=[],
            clip_vector=vektor_bayta(
                np.zeros(embedding.EMBEDDING_DIM, dtype=np.float32)
            ),
        )
        session.add(yeni_icerik)
        session.commit()

        yeni = IndexService()
        sayi, kademe = yeni.load_or_rebuild(session)

        assert kademe != "anlık görüntü", "bayat anlık görüntü kullanılmamalı"
        assert sayi == 3

    def test_bozuk_anlik_goruntu_cokme_yerine_yeniden_kuruyor(
        self, session, foto, model_yasak
    ):
        icerik_yaz(session, foto, sayi=2)
        servis = IndexService()
        servis.rebuild(session)
        servis.save_snapshot()

        # Dosyayi boz: okunamayan anlik goruntu acilisi durdurmamali.
        (servis.snapshot_dir / "clip.faiss").write_bytes(b"bozuk")

        sayi, kademe = IndexService().load_or_rebuild(session)

        assert kademe == "veritabanı"
        assert sayi == 2

    def test_bos_veritabaninda_cokmiyor(self, session, model_yasak):
        sayi, kademe = IndexService().load_or_rebuild(session)

        assert (sayi, kademe) == (0, "boş")

    def test_yuklenen_indeks_arama_yapabiliyor(self, session, foto, model_yasak):
        """Anlik goruntudan gelen indeks yalnizca dolu degil, ise yariyor."""
        [ilk, *_] = icerik_yaz(session, foto, sayi=3)
        kuran = IndexService()
        kuran.rebuild(session)
        kuran.save_snapshot()

        yeni = IndexService()
        yeni.load_or_rebuild(session)

        # Tam kopya tespiti ve algisal arama yuklenen indeksten calismali.
        assert yeni.index.exact(ilk.content_hash) == ilk.id
        adaylar = yeni.index.search_phash(parmak_izi_satirdan(ilk))
        assert {c.content_id for c in adaylar} >= {ilk.id}
        # Filigran ve dosya yolu eslemeleri veritabanindan kuruluyor.
        assert yeni.load_image(ilk.id) is not None
