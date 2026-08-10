"""API uc noktalarinin sozlesme testleri.

Mevcut 35 testin hepsi *iceriden* calisiyor: pay motorunu ve servis
katmanini dogrudan cagiriyorlar. Bu dosya disaridan calisir - gercek
HTTP istekleri atar ve `routes.py` ile `schemas.py` katmanini olcer.

Sorulan soru "hesap dogru mu" degil (o zaten 22 degismez testiyle
sabitlendi), "**dogru hesabi dogru bicimde disari veriyor muyum**".
Arayuz bu bicime guvenerek yazildi; bir alan adi degisirse mevcut
testlerin hepsi yesil kalir ama arayuz sessizce kirilir.

Iki tur test var:

  * **Bicim**: uc, sozunu verdigi alanlari dondurmus mu.
  * **Hatali girdi**: olmayan kimlik, bozuk dosya, izinsiz islem.
    Juri prototipi kendi kurcalayacak; beklenmedik girdide 500 donen
    bir uc "calisan prototip" izlenimini bozar.

Testler hizli tutuldu: agir koken kurtarma hatti yalnizca iki testte
calisir, geri kalani dogrudan yazilmis kayitlar uzerinden gider.
"""

from __future__ import annotations

import time
from pathlib import Path

import cv2
import numpy as np
import pytest
from fastapi.testclient import TestClient

from app.core.database import SessionLocal, create_schema
from app.models.entities import (
    AttributionEdge,
    Campaign,
    Content,
    LinkStage,
    LinkStatus,
    User,
)
from app.provenance import fingerprint as fp
from PIL import Image

from tests.conftest import gorsel_korpusu


def _jpeg(image: np.ndarray, quality: int = 92) -> bytes:
    ok, buf = cv2.imencode(".jpg", image, [cv2.IMWRITE_JPEG_QUALITY, quality])
    assert ok
    return buf.tobytes()


@pytest.fixture(scope="module")
def ortam(tmp_path_factory):
    """Uygulamayi ayaga kaldirir ve asgari veriyi dogrudan yazar.

    Icerik `ingest` hattindan gecirilmez: amac ucun bicimini olcmek,
    kurtarma hattini yeniden olcmek degil. Hattin kendisi zaten
    `test_e2e_altin_senaryo.py` ile ve 6.400 sorgulu degerlendirmeyle
    olculuyor.
    """
    from app.main import app

    photos = gorsel_korpusu()

    create_schema()
    session = SessionLocal()

    ayse = User(handle="api_ayse", display_name="Ayşe Yılmaz", accent="#E8A838")
    burak = User(handle="api_burak", display_name="Burak Demir", accent="#5B8DEF")
    session.add_all([ayse, burak])
    session.flush()

    kampanya = Campaign(
        brand_name="Anadolu Kahve",
        title="Test Kampanyası",
        brief="Sözleşme testleri için.",
        reward_pool=10_000.0,
    )
    session.add(kampanya)
    session.flush()

    # Diske gercek bir gorsel yaz: /image ucu dosyayi okuyor.
    dizin = tmp_path_factory.mktemp("api-icerik")
    yol = dizin / "published.jpg"
    bgr = cv2.imread(str(photos[0]))
    yol.write_bytes(_jpeg(bgr))
    finger = fp.compute(Image.open(yol).convert("RGB"), raw_bytes=yol.read_bytes())

    icerik = Content(
        id="apitesticerik01",
        owner_id=ayse.id,
        title="Sözleşme testi içeriği",
        caption="API testleri için.",
        file_path=str(yol),
        width=bgr.shape[1],
        height=bgr.shape[0],
        content_hash=finger.content_hash,
        phash=f"{finger.phash:016x}",
        dhash=f"{finger.dhash:016x}",
        whash=f"{finger.whash:016x}",
        manifest_present=True,
        revenue=1000.0,
        campaign_id=kampanya.id,
    )
    kilitli = Content(
        id="apitestkilitli1",
        owner_id=burak.id,
        title="Remixe kapalı içerik",
        file_path=str(yol),
        width=bgr.shape[1],
        height=bgr.shape[0],
        content_hash=finger.content_hash + "x",
        phash=f"{finger.phash:016x}",
        dhash=f"{finger.dhash:016x}",
        whash=f"{finger.whash:016x}",
        remix_allowed=False,
    )
    session.add_all([icerik, kilitli])
    session.flush()

    # Yetki testleri icin gercek bir bag: kaynak Ayse'nin, turev
    # Burak'in. Payin sahibi Ayse oldugu icin itiraz hakki da onun.
    bag = AttributionEdge(
        child_id=kilitli.id,
        parent_id=icerik.id,
        stage=LinkStage.CLIP,
        status=LinkStatus.CONFIRMED,
        confidence=0.9,
        visual_coverage=0.6,
        source_usage=0.5,
    )
    session.add(bag)
    session.commit()

    veri = {
        "ayse_id": ayse.id,
        "burak_id": burak.id,
        "kampanya_id": kampanya.id,
        "icerik_id": icerik.id,
        "kilitli_id": kilitli.id,
        "bag_id": bag.id,
        "foto": photos[0],
    }
    session.close()

    with TestClient(app) as client:
        yield client, veri


@pytest.fixture()
def client(ortam):
    return ortam[0]


@pytest.fixture()
def veri(ortam):
    return ortam[1]


@pytest.fixture()
def basliklar(client):
    """Verilen kullanici adina oturum acip Authorization basligini doner.

    Testler jetonu elle uretmiyor, gercek ucu cagiriyor: boylece
    sozlesme testi imzalama ayrintisina degil ucun kendisine bagli
    kaliyor.
    """

    def uret(user_id: str) -> dict[str, str]:
        r = client.post("/api/oturum", json={"user_id": user_id})
        assert r.status_code == 200, r.text
        return {"Authorization": f"Bearer {r.json()['token']}"}

    return uret


def alanlar(govde: dict, *beklenen: str) -> None:
    """Sozlesmenin vaat ettigi alanlar gercekten var mi."""
    eksik = [a for a in beklenen if a not in govde]
    assert not eksik, f"cevapta eksik alan: {eksik} (gelen: {sorted(govde)})"


# ---------------------------------------------------------------------------
# Saglik ve kullanicilar
# ---------------------------------------------------------------------------
def test_kok_uc_yonlendirme_bilgisi_doner(client):
    r = client.get("/")
    assert r.status_code == 200
    alanlar(r.json(), "name", "docs", "api")


def test_health_indeks_ve_cihaz_bildirir(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    govde = r.json()
    alanlar(govde, "status", "indexed_contents", "device", "c2pa_signing")
    assert govde["status"] == "ok"
    assert isinstance(govde["indexed_contents"], int)


def test_kullanici_listesi_bicimi(client):
    r = client.get("/api/users")
    assert r.status_code == 200
    kullanicilar = r.json()
    assert isinstance(kullanicilar, list) and kullanicilar
    alanlar(kullanicilar[0], "id", "handle", "display_name", "accent")


def test_kazanc_ucu_rollere_ayirir(client, veri):
    r = client.get(f"/api/users/{veri['ayse_id']}/earnings")
    assert r.status_code == 200
    alanlar(r.json(), "total", "as_creator", "as_source")


def test_olmayan_kullanicinin_kazanci_404(client):
    r = client.get("/api/users/yokboylekullanici/earnings")
    assert r.status_code == 404


# ---------------------------------------------------------------------------
# Icerik okuma
# ---------------------------------------------------------------------------
def test_akis_kart_icin_gereken_alanlari_verir(client):
    r = client.get("/api/feed")
    assert r.status_code == 200
    akis = r.json()
    assert isinstance(akis, list) and akis
    kart = akis[0]
    # Arayuzdeki kart birebir bu alanlari okuyor.
    alanlar(
        kart, "id", "title", "caption", "width", "height", "created_at", "revenue",
        "manifest_present", "remix_allowed", "owner", "source_count",
        "derivative_count", "campaign_id",
    )
    alanlar(kart["owner"], "id", "handle", "display_name", "accent")


def test_akis_limit_parametresine_uyar(client):
    r = client.get("/api/feed", params={"limit": 1})
    assert r.status_code == 200
    assert len(r.json()) == 1


def test_icerik_detayi_akisla_ayni_bicimde(client, veri):
    r = client.get(f"/api/contents/{veri['icerik_id']}")
    assert r.status_code == 200
    assert r.json()["id"] == veri["icerik_id"]


def test_olmayan_icerik_404_doner_500_degil(client):
    """Juri adres cubuguna rastgele bir kimlik yazarsa ham hata gormemeli."""
    r = client.get("/api/contents/yokboyleicerik")
    assert r.status_code == 404
    assert "detail" in r.json()


def test_icerik_gorseli_jpeg_doner(client, veri):
    r = client.get(f"/api/contents/{veri['icerik_id']}/image")
    assert r.status_code == 200
    assert r.headers["content-type"] == "image/jpeg"
    assert len(r.content) > 1000


def test_olmayan_icerigin_gorseli_404(client):
    assert client.get("/api/contents/yokboyle/image").status_code == 404


# ---------------------------------------------------------------------------
# Emek Karti
# ---------------------------------------------------------------------------
def test_emek_karti_tum_bolumleri_icerir(client, veri):
    """Demonun kapak ekrani; arayuz bu alt sozluklerin hepsini okuyor."""
    r = client.get(f"/api/contents/{veri['icerik_id']}/labour-card")
    assert r.status_code == 200
    kart = r.json()
    alanlar(kart, "content", "provenance", "chain", "distribution", "rules")
    alanlar(kart["chain"], "nodes", "edges")
    alanlar(
        kart["distribution"],
        "gross_revenue", "commission_amount", "distributable", "parties",
    )
    taraflar = kart["distribution"]["parties"]
    assert taraflar, "en az uretici ve platform bulunmali"
    alanlar(taraflar[0], "user_name", "role", "share_pct", "amount")


def test_emek_kartinda_paylar_yuzde_olarak_gelir(client, veri):
    """`share_pct` 0-1 arasi oran degil, yuzde; arayuz oyle basiyor."""
    kart = client.get(f"/api/contents/{veri['icerik_id']}/labour-card").json()
    toplam = sum(
        p["share_pct"] for p in kart["distribution"]["parties"] if p["role"] != "platform"
    )
    assert 99.0 <= toplam <= 101.0, f"paylar yuzde olarak 100'e toplanmali, geldi: {toplam}"


def test_olmayan_icerigin_emek_karti_404(client):
    assert client.get("/api/contents/yokboyle/labour-card").status_code == 404


def test_olmayan_bagin_maskesi_404(client):
    assert client.get("/api/edges/yokboylebag/mask").status_code == 404


# ---------------------------------------------------------------------------
# Oturum ve yetki
#
# Bu boluümün varlik sebebi: once `owner_id` form alanindan geliyordu,
# yani herkes herkes adina icerik yukleyebiliyor, baskasinin payina
# itiraz edebiliyor ve baskasinin icerigi uzerinde gelir
# degistirebiliyordu. Asagidaki testler o kapinin kapali kaldigini
# sinar.
# ---------------------------------------------------------------------------
def test_oturum_jeton_ve_kullanici_doner(client, veri):
    r = client.post("/api/oturum", json={"user_id": veri["ayse_id"]})
    assert r.status_code == 200
    govde = r.json()
    alanlar(govde, "token", "expires_at", "user")
    assert govde["user"]["id"] == veri["ayse_id"]
    assert govde["token"].count(".") == 1, "jeton govde.imza biciminde olmali"
    assert govde["expires_at"] > time.time()


def test_olmayan_kullaniciyla_oturum_404(client):
    assert client.post("/api/oturum", json={"user_id": "yokboyle"}).status_code == 404


@pytest.mark.parametrize(
    "baslik",
    [
        pytest.param(None, id="baslik-yok"),
        pytest.param({"Authorization": "Bearer uydurma.jeton"}, id="imza-tutmuyor"),
        pytest.param({"Authorization": "Basic abc"}, id="yanlis-sema"),
        pytest.param({"Authorization": "Bearer"}, id="jeton-eksik"),
    ],
)
def test_jetonsuz_yukleme_401(client, veri, baslik):
    bgr = cv2.imread(str(veri["foto"]))
    r = client.post(
        "/api/contents",
        files={"file": ("a.jpg", _jpeg(bgr), "image/jpeg")},
        data={"title": "Jetonsuz"},
        headers=baslik,
    )
    assert r.status_code == 401


def test_jetonsuz_itiraz_401(client, veri):
    r = client.post(
        "/api/disputes", json={"edge_id": veri["bag_id"], "reason": "deneme"}
    )
    assert r.status_code == 401


def test_jetonsuz_gelir_degisikligi_401(client, veri):
    r = client.post(
        f"/api/contents/{veri['icerik_id']}/revenue", json={"amount": 999.0}
    )
    assert r.status_code == 401


def test_baskasinin_payina_itiraz_403(client, veri, basliklar):
    """Bagin kaynagi Ayse'nin; pay ona odendigi icin itiraz hakki da onun."""
    r = client.post(
        "/api/disputes",
        json={"edge_id": veri["bag_id"], "reason": "Payım düşük hesaplandı."},
        headers=basliklar(veri["burak_id"]),
    )
    assert r.status_code == 403


def test_payin_sahibi_itiraz_acabilir(client, veri, basliklar):
    r = client.post(
        "/api/disputes",
        json={"edge_id": veri["bag_id"], "reason": "Payım düşük hesaplandı."},
        headers=basliklar(veri["ayse_id"]),
    )
    assert r.status_code == 200, r.text
    alanlar(r.json(), "id", "status")


def test_baskasinin_icerigine_gelir_403(client, veri, basliklar):
    r = client.post(
        f"/api/contents/{veri['icerik_id']}/revenue",
        json={"amount": 999.0},
        headers=basliklar(veri["burak_id"]),
    )
    assert r.status_code == 403
    # Gelir gercekten degismemis olmali.
    assert client.get(f"/api/contents/{veri['icerik_id']}").json()["revenue"] != 999.0


def test_suresi_dolmus_jeton_401(client, veri, basliklar, monkeypatch):
    """Jetonun omru gercekten kontrol ediliyor mu."""
    from app.core import security

    kimlik = basliklar(veri["ayse_id"])

    # Saat ileri aliniyor. `time` modulunun kendisi degil, yalnizca
    # `security` icindeki referansi degistiriliyor: global `time.time`
    # yamalanirsa test sirasinda calisan her sey etkilenirdi.
    ileri = time.time() + 10 * 60 * 60

    class _IleriSaat:
        @staticmethod
        def time() -> float:
            return ileri

    monkeypatch.setattr(security, "time", _IleriSaat)
    r = client.post(
        f"/api/contents/{veri['icerik_id']}/revenue",
        json={"amount": 123.0},
        headers=kimlik,
    )
    assert r.status_code == 401


@pytest.mark.slow
def test_yuklenen_icerigin_sahibi_jetondan_geliyor(client, veri, basliklar):
    """Govdedeki owner_id yok sayilir; sahip yalnizca jetondan gelir.

    `slow`: bu test koken kurtarma hattinin tamamini calistiriyor.
    """
    bgr = cv2.imread(str(veri["foto"]))
    r = client.post(
        "/api/contents",
        files={"file": ("a.jpg", _jpeg(bgr), "image/jpeg")},
        data={"title": "Jetonla yüklendi", "owner_id": veri["burak_id"]},
        headers=basliklar(veri["ayse_id"]),
    )
    assert r.status_code == 200, r.text
    assert r.json()["content"]["owner"]["id"] == veri["ayse_id"]


# ---------------------------------------------------------------------------
# Gelir ve dagitim
# ---------------------------------------------------------------------------
def test_gelir_ayarlanir_ve_geri_okunur(client, veri, basliklar):
    r = client.post(
        f"/api/contents/{veri['icerik_id']}/revenue",
        json={"amount": 2500.0},
        headers=basliklar(veri["ayse_id"]),
    )
    assert r.status_code == 200
    assert r.json()["revenue"] == 2500.0
    assert client.get(f"/api/contents/{veri['icerik_id']}").json()["revenue"] == 2500.0


def test_gelir_govdesi_dogrulanir(client, veri, basliklar):
    """Eksik veya yanlis tipte govde 422 olmali - sunucu hatasi degil."""
    kimlik = basliklar(veri["ayse_id"])
    r = client.post(
        f"/api/contents/{veri['icerik_id']}/revenue", json={}, headers=kimlik
    )
    assert r.status_code == 422
    r = client.post(
        f"/api/contents/{veri['icerik_id']}/revenue",
        json={"amount": "elli lira"},
        headers=kimlik,
    )
    assert r.status_code == 422


def test_dagitim_tutarlari_ve_kural_gunlugu_doner(client, veri, basliklar):
    client.post(
        f"/api/contents/{veri['icerik_id']}/revenue",
        json={"amount": 1000.0},
        headers=basliklar(veri["ayse_id"]),
    )
    r = client.post(f"/api/contents/{veri['icerik_id']}/distribute")
    assert r.status_code == 200
    govde = r.json()
    alanlar(
        govde,
        "content_id", "gross_revenue", "commission_amount", "distributable",
        "rules_log", "payouts", "payout_ids",
    )
    assert govde["gross_revenue"] == 1000.0
    odenen = sum(p["amount"] for p in govde["payouts"])
    assert abs(odenen - 1000.0) < 0.05, "odemeler brut gelire esit olmali"


def test_olmayan_icerigin_dagitimi_404(client):
    assert client.post("/api/contents/yokboyle/distribute").status_code == 404


# ---------------------------------------------------------------------------
# Kampanyalar
# ---------------------------------------------------------------------------
def test_kampanya_listesi_bicimi(client):
    r = client.get("/api/campaigns")
    assert r.status_code == 200
    kampanyalar = r.json()
    assert kampanyalar
    alanlar(
        kampanyalar[0],
        "id", "brand_name", "title", "brief", "reward_pool", "status",
        "commission", "source_floor", "creator_ceiling", "content_count",
    )


def test_kampanya_olusturulur_ve_listede_gorunur(client):
    onceki = len(client.get("/api/campaigns").json())
    r = client.post(
        "/api/campaigns",
        json={
            "brand_name": "Test Marka",
            "title": "Yeni Kampanya",
            "brief": "Deneme.",
            "reward_pool": 5000.0,
            "commission": 0.1,
            "source_floor": 0.15,
            "creator_ceiling": 0.8,
        },
    )
    assert r.status_code == 200
    assert r.json()["content_count"] == 0
    assert len(client.get("/api/campaigns").json()) == onceki + 1


def test_eksik_alanli_kampanya_reddedilir(client):
    assert client.post("/api/campaigns", json={"brand_name": "Yalniz marka"}).status_code == 422


def test_olmayan_kampanyanin_dagitimi_404(client):
    assert client.post("/api/campaigns/yokboyle/distribute").status_code == 404


def test_kampanya_dagitimi_havuzu_raporlar(client, veri):
    r = client.post(f"/api/campaigns/{veri['kampanya_id']}/distribute")
    assert r.status_code == 200
    alanlar(
        r.json(), "campaign_id", "reward_pool", "total_paid", "platform_total", "per_content"
    )


# ---------------------------------------------------------------------------
# Itiraz ve moderasyon
# ---------------------------------------------------------------------------
def test_itiraz_kuyrugu_liste_doner(client):
    r = client.get("/api/disputes/queue")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_olmayan_baga_itiraz_404(client, veri, basliklar):
    """Olmayan bag icin 404: yanit hangi baglarin var oldugunu sizdirmasin."""
    r = client.post(
        "/api/disputes",
        json={"edge_id": "yokboylebag", "reason": "deneme"},
        headers=basliklar(veri["ayse_id"]),
    )
    assert r.status_code == 404


def test_olmayan_itirazin_cozumu_404(client):
    assert client.post("/api/disputes/yokboyle/resolve").status_code == 404


def test_olmayan_itirazin_moderasyonu_404(client):
    r = client.post(
        "/api/disputes/yokboyle/moderate", json={"accept": True, "note": "deneme"}
    )
    assert r.status_code == 404


# ---------------------------------------------------------------------------
# Yukleme ve dogrulama - hattin tamami calisir, bu ikisi yavas
# ---------------------------------------------------------------------------
def test_bozuk_dosya_400_doner(client, veri, basliklar):
    """Gorsel olmayan bir dosya sunucu hatasina yol acmamali."""
    r = client.post(
        "/api/contents",
        files={"file": ("not.txt", b"bu bir gorsel degil", "text/plain")},
        data={"title": "Bozuk"},
        headers=basliklar(veri["ayse_id"]),
    )
    assert r.status_code == 400


def test_remixe_kapali_icerik_403_doner(client, veri, basliklar):
    """Ureticinin remix tercihi API katmaninda da uygulanmali."""
    bgr = cv2.imread(str(veri["foto"]))
    r = client.post(
        f"/api/contents/{veri['kilitli_id']}/remix",
        files={"file": ("a.jpg", _jpeg(bgr), "image/jpeg")},
        data={"title": "İzinsiz remix"},
        headers=basliklar(veri["ayse_id"]),
    )
    assert r.status_code == 403


def test_olmayan_kaynaga_remix_404(client, veri, basliklar):
    bgr = cv2.imread(str(veri["foto"]))
    r = client.post(
        "/api/contents/yokboyle/remix",
        files={"file": ("a.jpg", _jpeg(bgr), "image/jpeg")},
        data={"title": "Deneme"},
        headers=basliklar(veri["ayse_id"]),
    )
    assert r.status_code == 404


def test_dogrula_ucu_bozuk_gorselde_400(client):
    r = client.post(
        "/api/verify", files={"file": ("not.txt", b"gorsel degil", "text/plain")}
    )
    assert r.status_code == 400


@pytest.mark.slow
def test_yukleme_icerik_ve_kurtarma_ciktisini_birlikte_doner(client, veri):
    """Tam hat: yukleme cevabi hem icerigi hem hattin ne yaptigini tasir."""
    bgr = cv2.imread(str(veri["foto"]))
    r = client.post(
        "/api/contents",
        files={"file": ("yeni.jpg", _jpeg(bgr), "image/jpeg")},
        data={"owner_id": veri["ayse_id"], "title": "API'den yüklendi"},
    )
    assert r.status_code == 200
    govde = r.json()
    alanlar(govde, "content", "recovery")
    alanlar(govde["content"], "id", "title", "owner")
    alanlar(
        govde["recovery"],
        "manifest_present", "manifest_urn", "watermark_tag", "links",
        "stage_log", "timings_ms",
    )
    # Hat bes asamayi da gunlukler; arayuzdeki zaman cizelgesi bunu okuyor.
    asamalar = {a["stage"] for a in govde["recovery"]["stage_log"]}
    assert {"c2pa", "exact", "watermark", "phash", "clip", "geometry"} <= asamalar


@pytest.mark.slow
def test_dogrula_ucu_kaydetmeden_kanit_doner(client, veri):
    onceki = len(client.get("/api/feed").json())
    bgr = cv2.imread(str(veri["foto"]))
    r = client.post("/api/verify", files={"file": ("s.jpg", _jpeg(bgr), "image/jpeg")})
    assert r.status_code == 200
    alanlar(r.json(), "manifest_present", "links", "stage_log", "timings_ms")
    # "Kaydetmeden" sozu tutulmali.
    assert len(client.get("/api/feed").json()) == onceki
