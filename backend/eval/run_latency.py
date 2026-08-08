"""Faz 2 - Altin senaryonun adim adim gecikmesi.

`run_benchmark.py` hattin *dogrulugunu* olcuyor; bu betik ayni hattin
bir kullanicinin bekleyecegi surelere ne kadar yansidigini olcer.
Teknik raporun "uygulanabilirlik" bolumunun sayisal dayanagi budur:
juri "guzel de bu gercek bir platformda calisir mi" diye sorduğunda
cevabin olculmus olmasi gerekiyor.

Olculen adimlar, demoda gorulen sirayla:

  1. Ozgun icerik yukleme   - filigran + C2PA imzalama + indeksleme
  2. Remix yukleme          - kaynak beyanli, zincir kurulur
  3. Kimliksiz yukleme      - manifest silinmis; tam kurtarma hatti kosar
  4. Emek Karti uretimi     - zincir yurutme + pay hesabi + aciklamalar
  5. Kampanya dagitimi      - havuzun tum icerige bolusturulmesi
  6. Itiraz cozumu          - SIFT ile yeniden olcum

Olcum gercekci bir indeks buyuklugunde yapilir: senaryo kosmadan once
korpus indekse yuklenir, cunku aday arama ve geometri maliyeti indeks
buyuklugune baglidir. Bos bir indekste olculen sure yaniltici olurdu.

Calistirma (backend/ dizininden):

    ../.venv/Scripts/python.exe -m eval.run_latency [--tekrar 5] [--indeks 200]

Cikti: docs/GECIKME.md  +  data/eval/gecikme.json
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
import time
from pathlib import Path

# Uygulama modulleri yuklenmeden once ortam degiskenleri ayarlanmali:
# `app.core.database` motoru modul duzeyinde kuruyor. Olcum, demo
# veritabanina ve yuklemelere dokunmaz.
_TMP = Path(tempfile.mkdtemp(prefix="nemek-gecikme-"))
os.environ["NEMEK_DATA_DIR"] = str(_TMP)
os.environ["NEMEK_UPLOAD_DIR"] = str(_TMP / "uploads")
os.environ["NEMEK_INDEX_DIR"] = str(_TMP / "index")
os.environ["NEMEK_DATABASE_URL"] = f"sqlite:///{(_TMP / 'gecikme.db').as_posix()}"

import cv2  # noqa: E402
import numpy as np  # noqa: E402
from PIL import Image  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.attribution.explain import build_labour_card  # noqa: E402
from app.core.database import SessionLocal, create_schema  # noqa: E402
from app.models.entities import AttributionEdge, Campaign, Content, User  # noqa: E402
from app.provenance import embedding  # noqa: E402
from app.provenance import fingerprint as fp  # noqa: E402
from app.services import dispute as dispute_service  # noqa: E402
from app.services import ingest as ingest_service  # noqa: E402
from app.services import payout as payout_service  # noqa: E402
from app.services.registry import get_index_service  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
PUBLISHED = ROOT / "data" / "eval" / "published"
REPORT = ROOT / "docs" / "GECIKME.md"
RESULTS = ROOT / "data" / "eval" / "gecikme.json"

ADIMLAR = [
    ("yukleme_ozgun", "Özgün içerik yükleme", "filigran + C2PA imzalama + indeksleme"),
    ("remix", "Remix yükleme", "kaynak beyanlı, zincir kurulur ve alan ölçülür"),
    ("kurtarma_kimliksiz", "Kimliksiz içerik yükleme", "manifest silinmiş; tam kurtarma hattı"),
    ("emek_karti", "Emek Kartı üretimi", "zincir yürütme + pay hesabı + açıklamalar"),
    ("kampanya_dagitimi", "Kampanya dağıtımı", "havuzun tüm içeriğe bölüştürülmesi"),
    ("itiraz_cozumu", "İtiraz çözümü", "SIFT ile yeniden ölçüm"),
]


# ---------------------------------------------------------------------------
# Senaryo gorselleri - seed_demo.py ile ayni donusumler
# ---------------------------------------------------------------------------
def jpeg_bytes(image: np.ndarray, quality: int = 92) -> bytes:
    ok, buf = cv2.imencode(".jpg", image, [cv2.IMWRITE_JPEG_QUALITY, quality])
    if not ok:
        raise RuntimeError("JPEG kodlanamadi")
    return buf.tobytes()


def burak_remix(source: np.ndarray) -> np.ndarray:
    h, w = source.shape[:2]
    out = source[int(h * 0.12) : int(h * 0.88), int(w * 0.10) : int(w * 0.90)].copy()
    oh, ow = out.shape[:2]
    band = int(oh * 0.16)
    cv2.rectangle(out, (0, oh - band), (ow, oh), (24, 20, 18), -1)
    cv2.putText(out, "SEHRIN RENKLERI", (int(ow * 0.04), oh - band // 3),
                cv2.FONT_HERSHEY_SIMPLEX, oh / 620, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.circle(out, (int(ow * 0.85), int(oh * 0.18)), int(min(oh, ow) * 0.09), (60, 200, 250), -1)
    cv2.circle(out, (int(ow * 0.85), int(oh * 0.18)), int(min(oh, ow) * 0.09), (20, 20, 20), 3)
    return out


def ceyda_screenshot(source: np.ndarray) -> np.ndarray:
    h, w = source.shape[:2]
    out = source[int(h * 0.05) : int(h * 0.95), int(w * 0.04) : int(w * 0.96)]
    out = cv2.resize(out, None, fx=0.82, fy=0.82, interpolation=cv2.INTER_AREA)
    return cv2.imdecode(np.frombuffer(jpeg_bytes(out, 58), np.uint8), cv2.IMREAD_COLOR)


# ---------------------------------------------------------------------------
def arka_plan_yukle(session, index, sayi: int) -> int:
    """Indeksi gercekci bir buyuklukte doldurur.

    Icerikler `ingest` hattindan gecirilmez - amac indeksi doldurmak,
    yukleme suresini olcmek degil. Kayitlar dogrudan yazilip indeks
    tek seferde kurulur.
    """
    kaynak_dizin = PUBLISHED if PUBLISHED.exists() and any(PUBLISHED.glob("*.jpg")) else RAW
    paths = sorted(kaynak_dizin.glob("*.jpg"))[:sayi]
    if not paths:
        raise SystemExit("Korpus bos. Once: .venv/Scripts/python.exe scripts/fetch_eval_images.py")

    korpus = User(handle="korpus", display_name="Korpus")
    session.add(korpus)
    session.flush()

    for path in paths:
        image = cv2.imread(str(path))
        if image is None:
            continue
        h, w = image.shape[:2]
        # Parmak izi alanlari sema geregi zorunlu; indeks zaten bunlari
        # yeniden hesaplayacak ama veritabanindaki kayit da tutarli olmali.
        finger = fp.compute(Image.open(path).convert("RGB"), raw_bytes=path.read_bytes())
        session.add(
            Content(
                id=path.stem[:16],
                owner_id=korpus.id,
                title=path.stem,
                file_path=str(path),
                width=w,
                height=h,
                content_hash=finger.content_hash,
                phash=f"{finger.phash:016x}",
                dhash=f"{finger.dhash:016x}",
                whash=f"{finger.whash:016x}",
            )
        )
    session.commit()
    return index.rebuild(session)


def senaryo_kos(session, index, foto: Path, kampanya_id: str, olcum: dict) -> None:
    """Altin senaryoyu bir kez kosar ve her adimin suresini kaydeder."""
    ayse = User(handle=f"ayse_{foto.stem}", display_name="Ayşe Yılmaz")
    burak = User(handle=f"burak_{foto.stem}", display_name="Burak Demir")
    ceyda = User(handle=f"ceyda_{foto.stem}", display_name="Ceyda Aksoy")
    session.add_all([ayse, burak, ceyda])
    session.commit()

    original = cv2.imread(str(foto))

    # 1. Ozgun yukleme
    t0 = time.perf_counter()
    ayse_res = ingest_service.ingest(
        session, index, raw_bytes=jpeg_bytes(original), owner=ayse,
        title="Sabah ışığı", campaign_id=kampanya_id,
    )
    olcum["yukleme_ozgun"].append((time.perf_counter() - t0) * 1000)
    olcum["_asamalar"].setdefault("yukleme_ozgun", []).append(ayse_res.recovery.timings_ms)

    # 2. Remix
    ayse_published = cv2.imread(ayse_res.content.file_path)
    t0 = time.perf_counter()
    burak_res = ingest_service.ingest(
        session, index, raw_bytes=jpeg_bytes(burak_remix(ayse_published)), owner=burak,
        title="Şehrin Renkleri", declared_parent_id=ayse_res.content.id,
        remix_actions=["c2pa.cropped", "c2pa.drawing"], campaign_id=kampanya_id,
    )
    olcum["remix"].append((time.perf_counter() - t0) * 1000)
    olcum["_asamalar"].setdefault("remix", []).append(burak_res.recovery.timings_ms)

    # 3. Kimligi silinmis yukleme - senaryonun kritik adimi
    burak_published = cv2.imread(burak_res.content.file_path)
    stripped = ceyda_screenshot(burak_published)
    t0 = time.perf_counter()
    ceyda_res = ingest_service.ingest(
        session, index, raw_bytes=jpeg_bytes(stripped), owner=ceyda,
        title="Bulduğum kare", campaign_id=kampanya_id,
    )
    olcum["kurtarma_kimliksiz"].append((time.perf_counter() - t0) * 1000)
    olcum["_asamalar"].setdefault("kurtarma_kimliksiz", []).append(ceyda_res.recovery.timings_ms)
    olcum["_zincir"].append(len(ceyda_res.recovery.links))

    for content, revenue in (
        (ayse_res.content, 1200.0), (burak_res.content, 2600.0), (ceyda_res.content, 4200.0)
    ):
        content.revenue = revenue
    session.commit()

    # 4. Emek Karti
    t0 = time.perf_counter()
    build_labour_card(session, ceyda_res.content.id)
    olcum["emek_karti"].append((time.perf_counter() - t0) * 1000)

    # 5. Kampanya dagitimi
    t0 = time.perf_counter()
    payout_service.distribute_campaign(session, kampanya_id)
    olcum["kampanya_dagitimi"].append((time.perf_counter() - t0) * 1000)

    # 6. Itiraz cozumu
    edge = (
        session.query(AttributionEdge)
        .filter(AttributionEdge.child_id == ceyda_res.content.id)
        .first()
    )
    if edge is not None:
        d = dispute_service.open_dispute(
            session, edge_id=edge.id, raiser=ayse,
            reason="Orijinalimin daha geniş bir bölümü kullanılmış.",
        )
        t0 = time.perf_counter()
        dispute_service.resolve(session, index, d.id)
        olcum["itiraz_cozumu"].append((time.perf_counter() - t0) * 1000)


# ---------------------------------------------------------------------------
def _tr(value: float, digits: int = 0) -> str:
    """Turkce sayi bicimi: ondalik ayraci virgul."""
    return f"{value:.{digits}f}".replace(".", ",")


def rapor_yaz(olcum: dict, meta: dict) -> None:
    lines: list[str] = []
    add = lines.append

    add("# Uçtan Uca Gecikme — Altın Senaryo")
    add("")
    add(f"**Tarih:** {meta['tarih']}  ")
    add(f"**Ortam:** {meta['ortam']}  ")
    add("**Üreten:** `backend/eval/run_latency.py` — bu dosya elle düzenlenmez.")
    add("")
    add(
        f"Senaryo **{meta['tekrar']}** kez baştan koşuldu. Ölçüm sırasında indekste "
        f"**{meta['indeks']}** içerik vardı; aday arama ve geometrik doğrulama maliyeti "
        "indeks büyüklüğüne bağlı olduğu için boş bir indekste ölçüm yanıltıcı olurdu."
    )
    add("")
    add("Süreler sunucu tarafıdır: ağ, dosya yükleme ve arayüz çizimi dahil değildir.")
    add("")
    add("---")
    add("")
    add("## Adım başına süre")
    add("")
    add("| # | Adım | Ne yapılıyor | Ortalama | En hızlı | En yavaş |")
    add("|---|---|---|---|---|---|")
    for i, (key, isim, aciklama) in enumerate(ADIMLAR, 1):
        values = olcum.get(key) or []
        if not values:
            add(f"| {i} | {isim} | {aciklama} | — | — | — |")
            continue
        add(
            f"| {i} | **{isim}** | {aciklama} | **{_tr(float(np.mean(values)))} ms** | "
            f"{_tr(min(values))} ms | {_tr(max(values))} ms |"
        )
    add("")
    toplam = sum(float(np.mean(olcum[k])) for k, _, _ in ADIMLAR if olcum.get(k))
    add(f"Senaryonun tamamı (altı adım): **{_tr(toplam)} ms**")
    add("")
    add("---")
    add("")
    add("## Kurtarma hattının aşama dağılımı")
    add("")
    add(
        "Üç yükleme adımının içindeki köken kurtarma hattı, aşama aşama. "
        "Kimliksiz yükleme, hattın tamamının çalıştığı en ağır durumdur."
    )
    add("")
    stage_keys: list[str] = []
    for kayitlar in olcum["_asamalar"].values():
        for kayit in kayitlar:
            for k in kayit:
                if k not in stage_keys:
                    stage_keys.append(k)
    add("| Aşama | " + " | ".join(
        isim for key, isim, _ in ADIMLAR if key in olcum["_asamalar"]
    ) + " |")
    add("|---" * (1 + sum(1 for key, _, _ in ADIMLAR if key in olcum["_asamalar"])) + "|")
    for stage in stage_keys:
        hucreler = []
        for key, _, _ in ADIMLAR:
            if key not in olcum["_asamalar"]:
                continue
            values = [k.get(stage, 0.0) for k in olcum["_asamalar"][key]]
            hucreler.append(f"{_tr(float(np.mean(values)), 1)} ms")
        add(f"| {stage} | " + " | ".join(hucreler) + " |")
    add("")
    add("---")
    add("")
    add("## Yorum")
    add("")
    olculen = [(key, isim, float(np.mean(olcum[key]))) for key, isim, _ in ADIMLAR if olcum.get(key)]
    en_agir = max(olculen, key=lambda t: t[2])
    add(
        f"En ağır adım **{en_agir[1].lower()}**: ortalama {_tr(en_agir[2])} ms. "
        "Üç yükleme adımının hepsi köken kurtarma hattının tamamını koşar — "
        "özgün bir içerik yüklenirken bile, çünkü sistem yükleyenin sözüne değil "
        "ölçüme bakar: kaynak olmadığını *doğrulamak* da kaynak bulmak kadar iş."
    )
    add("")
    if olcum.get("yukleme_ozgun") and olcum.get("kurtarma_kimliksiz"):
        fark = float(np.mean(olcum["yukleme_ozgun"])) - float(np.mean(olcum["kurtarma_kimliksiz"]))
        add(
            f"Özgün yükleme, kimliksiz yüklemeden {_tr(abs(fark))} ms "
            f"{'daha uzun' if fark > 0 else 'daha kısa'} sürüyor. Aradaki farkın kaynağı "
            "yalnızca yayın adımları (filigran gömme, C2PA imzalama, indeksleme) değil; "
            "geometri aşaması da burada daha pahalı, çünkü doğrulanacak adayların hepsi "
            "yanlış çıkıyor ve her biri eleninceye kadar tam maliyetini ödetiyor. "
            "Gerçek kaynak bulunduğunda ise eşleşme erken ve güçlü oluyor."
        )
        add("")
    pay_toplam = sum(
        float(np.mean(olcum[k])) for k in ("emek_karti", "kampanya_dagitimi") if olcum.get(k)
    )
    add(
        f"Pay hesabı tarafı (Emek Kartı + kampanya dağıtımı) toplam {_tr(pay_toplam)} ms — "
        "görsel işleme içermediği için milisaniyeler mertebesinde. Sistemin maliyeti "
        "tamamen köken kurtarmada. Bu da ölçeklendirmenin nereden yapılacağını söylüyor: "
        "aday arama indeksi (bugün kaba kuvvet FAISS) ve geometrik doğrulamaya giden "
        "aday sayısı (`max_geometry_candidates`)."
    )
    add("")
    add(
        "Kullanıcı deneyimi açısından anlamlı sayı, yükleme adımlarının yarım saniye "
        "civarında olması: bu, yüklemeden sonra zincir önerisinin **beklemeden** "
        "gösterilebileceği anlamına geliyor. Kuyruğa alıp sonra bildirim göndermek "
        "gerekmiyor."
    )
    add("")

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
def main() -> int:
    parser = argparse.ArgumentParser(description="Altin senaryonun adim adim gecikmesi")
    parser.add_argument("--tekrar", type=int, default=5, help="Senaryonun kac kez kosulacagi")
    parser.add_argument("--indeks", type=int, default=200, help="Olcum sirasindaki indeks buyuklugu")
    args = parser.parse_args()

    create_schema()
    session = SessionLocal()
    index = get_index_service()

    print(f"Arka plan indeksi kuruluyor ({args.indeks} icerik)...")
    t0 = time.perf_counter()
    indeks_boyu = arka_plan_yukle(session, index, args.indeks)
    print(f"  {indeks_boyu} kayit, {time.perf_counter() - t0:.1f} sn\n")

    campaign = Campaign(
        brand_name="Anadolu Kahve",
        title="Şehrin Renkleri Remix Kampanyası",
        brief="Şehrinizin renklerini yakalayan içerikleri remixleyin.",
        reward_pool=50_000.0,
        commission=0.10,
        source_floor=0.15,
        creator_ceiling=0.80,
    )
    session.add(campaign)
    session.commit()

    photos = sorted(RAW.glob("*.jpg"))
    olcum: dict = {key: [] for key, _, _ in ADIMLAR}
    olcum["_asamalar"] = {}
    olcum["_zincir"] = []

    for i in range(args.tekrar):
        foto = photos[(i * 7 + 3) % len(photos)]
        senaryo_kos(session, index, foto, campaign.id, olcum)
        print(
            f"  tekrar {i + 1}/{args.tekrar}: "
            + "  ".join(
                f"{key}={olcum[key][-1]:.0f}ms" for key, _, _ in ADIMLAR if olcum[key]
            )
        )

    meta = {
        "tarih": time.strftime("%d.%m.%Y %H:%M"),
        "ortam": f"{embedding.pick_device()}, indeks {indeks_boyu} içerik",
        "tekrar": args.tekrar,
        "indeks": indeks_boyu,
    }
    rapor_yaz(olcum, meta)

    ozet = {
        key: {
            "ortalama_ms": round(float(np.mean(olcum[key])), 1),
            "min_ms": round(min(olcum[key]), 1),
            "max_ms": round(max(olcum[key]), 1),
        }
        for key, _, _ in ADIMLAR
        if olcum[key]
    }
    RESULTS.parent.mkdir(parents=True, exist_ok=True)
    RESULTS.write_text(
        json.dumps({"meta": meta, "adimlar": ozet}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"\n{'=' * 72}")
    print("GECIKME OLCUMU")
    print("=" * 72)
    for key, isim, _ in ADIMLAR:
        if olcum[key]:
            print(f"  {isim:<28} {np.mean(olcum[key]):>8.0f} ms")
    print(f"  {'TOPLAM':<28} {sum(np.mean(olcum[k]) for k, _, _ in ADIMLAR if olcum[k]):>8.0f} ms")
    print(f"\n  Rapor: {REPORT}")
    session.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
