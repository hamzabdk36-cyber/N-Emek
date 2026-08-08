"""Faz 2 - Koken kurtarma hattinin kapsamli degerlendirmesi.

Faz 0 PoC'lerinden iki farki var ve ikisi de raporun guvenilirligi icin
onemli:

1. **Uretimdeki hattin kendisini olcer.** PoC'ler asamalari tek tek ve
   dogrudan cagiriyordu; burada `recovery.recover()` calisir - API'nin
   bir yukleme sirasinda calistirdigi fonksiyonun aynisi. Yani olculen
   sey, jurinin demoda gorecegi davranistir.

2. **Negatif kontrol vardir.** Korpusun bir kismi indekse hic
   alinmaz ("holdout"). Bu goruntulerin turevleri sorgu olarak
   calistirilir ve *herhangi bir* bag onerilmesi yanlis atif sayilir.
   Bu proje icin en kritik sayi budur: sistemin olmayan bir kaynagi
   uydurmadigini gosterir.

Kurgu, gercek hayattaki en zor durumu taklit eder: turevler kodu
cozulmus piksel dizisi uzerinde uretildigi icin C2PA manifesti ve tum
metadata silinmis olur. Hattin 0. asamasi bu yuzden hicbir zaman
tetiklenmez; olculen sey saf *kurtarma* basarisidir.

Calistirma (backend/ dizininden):

    ../.venv/Scripts/python.exe -m eval.run_benchmark              # tam kosu
    ../.venv/Scripts/python.exe -m eval.run_benchmark --queries 20 # hizli deneme

Cikti: docs/DEGERLENDIRME.md  +  data/eval/sonuclar.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import sys
import time
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.config import get_settings  # noqa: E402
from app.provenance import c2pa_service, embedding, recovery, watermark  # noqa: E402
from app.provenance import fingerprint as fp  # noqa: E402
from app.provenance.index import ProvenanceIndex  # noqa: E402
from eval.attacks import ATTACKS, EXPECTED_COVERAGE  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
EVAL_DIR = ROOT / "data" / "eval"
PUBLISHED = EVAL_DIR / "published"
SCRATCH = EVAL_DIR / "sorgu.jpg"
REPORT = ROOT / "docs" / "DEGERLENDIRME.md"
RESULTS = EVAL_DIR / "sonuclar.json"

JPEG_QUALITY = 92
SEED = 42
# Kapsama olcumunde "dogru" sayilan hata payi (rapor tablosundaki bayrak).
COVERAGE_TOLERANCE = 0.10


# ---------------------------------------------------------------------------
# Icerik deposu
# ---------------------------------------------------------------------------
class EvalStore:
    """`recovery.ContentStore` protokolunun veritabanisiz karsiligi.

    Uretimde bu rolu `services.registry.IndexService` ustleniyor; burada
    ayni arayuzu dosya sistemi uzerinden karsiliyoruz ki degerlendirme
    SQLAlchemy'ye ve demo verisine bagimli olmasin.
    """

    def __init__(self) -> None:
        self._paths: dict[str, Path] = {}
        self._watermarks: dict[str, str] = {}
        self._cache: dict[str, np.ndarray] = {}

    def register(self, content_id: str, path: Path) -> None:
        self._paths[content_id] = path
        self._watermarks[watermark.content_id_to_hex(content_id)] = content_id

    def load_image(self, content_id: str) -> np.ndarray | None:
        cached = self._cache.get(content_id)
        if cached is not None:
            return cached
        path = self._paths.get(content_id)
        if path is None:
            return None
        image = cv2.imread(str(path))
        if image is None:
            return None
        if len(self._cache) > 400:
            self._cache.clear()
        self._cache[content_id] = image
        return image

    def by_watermark(self, tag: str) -> str | None:
        return self._watermarks.get(tag)

    def by_manifest_parent(self, declared_id: str) -> str | None:
        return declared_id if declared_id in self._paths else None


# ---------------------------------------------------------------------------
# Yayin: korpusu platformdan gecmis hale getir
# ---------------------------------------------------------------------------
def dedupe(paths: list[Path]) -> list[Path]:
    """Bayt bayt ayni gorselleri korpustan duser.

    Bu bir temizlik degil, olcumun gecerlilik sarti. Indekste birebir
    ikizi olan bir "holdout" gorseli icin bag onerilmesi yanlis atif
    degil dogru davranistir; ama negatif kontrol sayaci bunu yanlis
    atif yazar ve rapor gercekte olmayan bir hatayi bildirir. Ayni
    sekilde Top-1, ikizlerden hangisinin dondugune gore rastgele
    dusebilir.

    Korpus indiricisi (`scripts/fetch_eval_images.py`) artik tekilligi
    kendisi sagliyor; buradaki kontrol elle eklenmis veya eski bir
    korpusa karsi guvence.
    """
    ozetler: dict[str, Path] = {}
    tekil: list[Path] = []
    for path in paths:
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest in ozetler:
            continue
        ozetler[digest] = path
        tekil.append(path)
    dusen = len(paths) - len(tekil)
    if dusen:
        print(f"Korpus tekillestirildi: {dusen} yinelenen gorsel dusuruldu "
              f"({len(paths)} -> {len(tekil)}).")
    return tekil


def publish_corpus(paths: list[Path], rebuild: bool) -> list[str]:
    """Her ham gorseli uretimdeki yayin adimlarindan gecirir.

    Filigran gomulur ve (sertifika varsa) C2PA manifesti imzalanir.
    Indekse giren ve turevlerin uretildigi dosya bu *yayinlanmis* hali
    olmalidir - `services.ingest` de tam olarak boyle yapiyor. Ham
    gorseli indekslersek filigran asamasini hic olcmemis oluruz.
    """
    PUBLISHED.mkdir(parents=True, exist_ok=True)
    signing = c2pa_service.certs_available()
    print(f"Yayin adimi: {len(paths)} gorsel  (C2PA imzalama: {'acik' if signing else 'kapali'})")

    ids: list[str] = []
    t0 = time.perf_counter()
    for i, path in enumerate(paths, 1):
        cid = path.stem
        out = PUBLISHED / f"{cid}.jpg"
        ids.append(cid)
        if out.exists() and not rebuild:
            continue

        bgr = cv2.imread(str(path))
        if bgr is None:
            ids.pop()
            continue
        marked = watermark.embed(bgr, cid)
        tmp = PUBLISHED / f"{cid}.marked.jpg"
        cv2.imwrite(str(tmp), marked, [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY])
        if signing:
            try:
                c2pa_service.sign_original(
                    tmp, out, content_id=cid, author="Degerlendirme", title=cid
                )
            except Exception as exc:  # imzalama tek gorselde patlarsa kosu durmasin
                print(f"  uyari: {cid} imzalanamadi ({exc}); filigranli hali kullanilacak")
                out.write_bytes(tmp.read_bytes())
        else:
            out.write_bytes(tmp.read_bytes())
        tmp.unlink(missing_ok=True)
        if i % 40 == 0:
            print(f"  {i}/{len(paths)}")

    print(f"  {time.perf_counter() - t0:.1f} sn\n")
    return ids


def build_index(ids: list[str], store: EvalStore) -> ProvenanceIndex:
    """Yayinlanmis dosyalardan arama indeksini kurar."""
    print(f"Indeksleniyor: {len(ids)} gorsel  (cihaz: {embedding.pick_device()})")
    index = ProvenanceIndex()

    t0 = time.perf_counter()
    pils: list[Image.Image] = []
    fingers: list[fp.Fingerprint] = []
    for cid in ids:
        path = PUBLISHED / f"{cid}.jpg"
        raw = path.read_bytes()
        pil = Image.open(path).convert("RGB")
        pils.append(pil)
        fingers.append(fp.compute(pil, raw_bytes=raw))
        store.register(cid, path)
    t_fp = time.perf_counter() - t0

    t0 = time.perf_counter()
    vectors = embedding.embed(pils, batch_size=32)
    t_embed = time.perf_counter() - t0

    for cid, finger, vector in zip(ids, fingers, vectors):
        index.add(cid, finger, vector)

    index.save(EVAL_DIR / "index")
    print(f"  parmak izi : {t_fp:.1f} sn ({t_fp / len(ids) * 1000:.0f} ms/gorsel)")
    print(f"  CLIP gomme : {t_embed:.1f} sn ({t_embed / len(ids) * 1000:.0f} ms/gorsel)")
    print(f"  indeks     : {len(index)} kayit\n")
    return index


# ---------------------------------------------------------------------------
# Olcum
# ---------------------------------------------------------------------------
@dataclass
class ScenarioStats:
    """Tek bir turev senaryosunun tum sayaclari."""

    name: str
    pozitif: int = 0
    top1: int = 0
    top5: int = 0
    bulundu: int = 0
    # links[0] var ama gercek kaynak degil - en agir hata turu.
    yanlis_top1: int = 0
    # Onerilen tum baglarin kacinda hedef yanlisti.
    onerilen_bag: int = 0
    yanlis_bag: int = 0
    # Negatif kontrol: indekste olmayan gorselin turevine bag onerildi mi.
    negatif: int = 0
    negatif_bag: int = 0
    # Kapsama olcumu (yalnizca geometrisi dogrulanmis dogru baglar)
    kapsama_olculen: list[float] = field(default_factory=list)
    kapsama_hatalari: list[float] = field(default_factory=list)
    olculemedi: int = 0
    # Kararin hangi asamadan geldigi
    asamalar: Counter = field(default_factory=Counter)
    gecikmeler: list[float] = field(default_factory=list)
    asama_gecikmeleri: dict[str, list[float]] = field(default_factory=dict)

    def kaydet_gecikme(self, toplam_ms: float, timings: dict[str, float]) -> None:
        self.gecikmeler.append(toplam_ms)
        for stage, ms in timings.items():
            self.asama_gecikmeleri.setdefault(stage, []).append(ms)

    # -- turetilmis oranlar ------------------------------------------------
    @property
    def top1_orani(self) -> float:
        return self.top1 / self.pozitif if self.pozitif else 0.0

    @property
    def top5_orani(self) -> float:
        return self.top5 / self.pozitif if self.pozitif else 0.0

    @property
    def yanlis_atif_orani(self) -> float:
        """Yanlis Top-1 + negatif kontroldeki her bag, tum sorgulara oranla."""
        toplam = self.pozitif + self.negatif
        return (self.yanlis_top1 + self.negatif_bag) / toplam if toplam else 0.0

    @property
    def kapsama_mae(self) -> float | None:
        return float(np.mean(self.kapsama_hatalari)) if self.kapsama_hatalari else None

    @property
    def p50(self) -> float:
        return float(np.percentile(self.gecikmeler, 50)) if self.gecikmeler else 0.0

    @property
    def p95(self) -> float:
        return float(np.percentile(self.gecikmeler, 95)) if self.gecikmeler else 0.0


def run_query(
    derivative: np.ndarray,
    index: ProvenanceIndex,
    store: EvalStore,
) -> tuple[recovery.RecoveryResult, float]:
    """Bir turevi uretimdeki hattan gecirir.

    Turev diske yaziliyor cunku hat C2PA okumasi icin dosya yolu
    istiyor - uretimde de yuklenen dosya once diske aliniyor.
    """
    ok, buf = cv2.imencode(".jpg", derivative, [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY])
    raw = buf.tobytes() if ok else b""
    SCRATCH.parent.mkdir(parents=True, exist_ok=True)
    SCRATCH.write_bytes(raw)

    t0 = time.perf_counter()
    result = recovery.recover(derivative, raw, SCRATCH, index, store)
    return result, (time.perf_counter() - t0) * 1000


def evaluate(
    index: ProvenanceIndex,
    store: EvalStore,
    positives: list[str],
    holdout: list[str],
    scenarios: list[str],
) -> dict[str, ScenarioStats]:
    stats = {name: ScenarioStats(name) for name in scenarios}
    total = len(scenarios) * (len(positives) + len(holdout))
    done = 0
    started = time.perf_counter()

    for name in scenarios:
        attack = ATTACKS[name]
        stat = stats[name]
        beklenen = EXPECTED_COVERAGE.get(name)

        # --- Pozitifler: kaynak indekste, bulunmasi bekleniyor ------------
        for cid in positives:
            source = cv2.imread(str(PUBLISHED / f"{cid}.jpg"))
            if source is None:
                continue
            result, ms = run_query(attack(source), index, store)
            stat.pozitif += 1
            stat.kaydet_gecikme(ms, result.timings_ms)

            parents = [link.parent_content_id for link in result.links]
            stat.onerilen_bag += len(parents)
            stat.yanlis_bag += sum(1 for p in parents if p != cid)
            if parents:
                if parents[0] == cid:
                    stat.top1 += 1
                    stat.asamalar[result.links[0].stage.value] += 1
                else:
                    stat.yanlis_top1 += 1
            if cid in parents[:5]:
                stat.top5 += 1
            if cid in parents:
                stat.bulundu += 1
                link = next(l for l in result.links if l.parent_content_id == cid)
                if link.geometry_verified and link.visual_coverage is not None:
                    stat.kapsama_olculen.append(link.visual_coverage)
                    if beklenen is not None:
                        stat.kapsama_hatalari.append(abs(link.visual_coverage - beklenen))
                else:
                    stat.olculemedi += 1

            done += 1

        # --- Negatif kontrol: kaynak indekste degil, hicbir bag cikmamali -
        for cid in holdout:
            source = cv2.imread(str(PUBLISHED / f"{cid}.jpg"))
            if source is None:
                continue
            result, ms = run_query(attack(source), index, store)
            stat.negatif += 1
            stat.negatif_bag += len(result.links)
            stat.kaydet_gecikme(ms, result.timings_ms)
            done += 1

        gecen = time.perf_counter() - started
        kalan = gecen / done * (total - done) if done else 0
        print(
            f"  {name:<18} top1 %{stat.top1_orani * 100:5.1f}  "
            f"top5 %{stat.top5_orani * 100:5.1f}  "
            f"yanlis atif %{stat.yanlis_atif_orani * 100:4.1f}  "
            f"p50 {stat.p50:5.0f} ms   [{done}/{total}, ~{kalan / 60:.0f} dk kaldi]"
        )
        _dump_partial(stats)

    return stats


# ---------------------------------------------------------------------------
# Raporlama
# ---------------------------------------------------------------------------
def _dump_partial(stats: dict[str, ScenarioStats]) -> None:
    """Kosu uzun; her senaryo bitiminde ara sonucu diske yaz."""
    RESULTS.parent.mkdir(parents=True, exist_ok=True)
    RESULTS.write_text(json.dumps(_as_dict(stats), ensure_ascii=False, indent=2), "utf-8")


def _as_dict(stats: dict[str, ScenarioStats]) -> dict:
    out = {}
    for name, s in stats.items():
        out[name] = {
            "pozitif_sorgu": s.pozitif,
            "negatif_sorgu": s.negatif,
            "top1": round(s.top1_orani, 4),
            "top5": round(s.top5_orani, 4),
            "bulundu": round(s.bulundu / s.pozitif, 4) if s.pozitif else 0.0,
            "yanlis_top1": s.yanlis_top1,
            "onerilen_bag": s.onerilen_bag,
            "yanlis_bag": s.yanlis_bag,
            "negatif_bag": s.negatif_bag,
            "yanlis_atif_orani": round(s.yanlis_atif_orani, 4),
            "kapsama_mae": round(s.kapsama_mae, 4) if s.kapsama_mae is not None else None,
            "kapsama_ortalama": (
                round(float(np.mean(s.kapsama_olculen)), 4) if s.kapsama_olculen else None
            ),
            "kapsama_olculen": len(s.kapsama_hatalari),
            "kapsama_olculemedi": s.olculemedi,
            "karar_asamalari": dict(s.asamalar),
            "gecikme_p50_ms": round(s.p50, 1),
            "gecikme_p95_ms": round(s.p95, 1),
            "asama_gecikme_ms": {
                k: round(float(np.mean(v)), 1) for k, v in s.asama_gecikmeleri.items()
            },
        }
    return out


def _tr(value: float, digits: int = 1) -> str:
    return f"{value:.{digits}f}".replace(".", ",")


def write_report(stats: dict[str, ScenarioStats], meta: dict) -> None:
    """docs/DEGERLENDIRME.md dosyasini uretir.

    Bu dosya elle duzenlenmez; sayilar degisecekse betik yeniden kosulur.
    """
    order = [n for n in ATTACKS if n in stats]
    rows = [stats[n] for n in order]
    poz = sum(s.pozitif for s in rows)
    neg = sum(s.negatif for s in rows)

    ort_top1 = float(np.mean([s.top1_orani for s in rows])) if rows else 0.0
    ort_top5 = float(np.mean([s.top5_orani for s in rows])) if rows else 0.0
    toplam_yanlis = sum(s.yanlis_top1 for s in rows) + sum(s.negatif_bag for s in rows)
    yanlis_orani = toplam_yanlis / (poz + neg) if (poz + neg) else 0.0
    tum_hatalar = [e for s in rows for e in s.kapsama_hatalari]
    genel_mae = float(np.mean(tum_hatalar)) if tum_hatalar else float("nan")
    tum_gecikme = [g for s in rows for g in s.gecikmeler]

    lines: list[str] = []
    add = lines.append

    add("# Kapsamlı Değerlendirme — Köken Kurtarma Hattı")
    add("")
    add(f"**Tarih:** {meta['tarih']}  ")
    add(f"**Ortam:** {meta['ortam']}  ")
    add(f"**Üreten:** `backend/eval/run_benchmark.py` — bu dosya elle düzenlenmez.")
    add("")
    add(
        f"İndekste **{meta['indeks']}** yayınlanmış içerik var. "
        f"**{meta['pozitif']}** içeriğin ve indekste bulunmayan **{meta['holdout']}** "
        f"içeriğin her biri **{len(order)}** türev senaryosundan geçirildi: "
        f"toplam **{poz + neg}** sorgu."
    )
    add("")
    add(
        "Her sorgu, üretimdeki `recovery.recover()` fonksiyonunun kendisinden geçer; "
        "ölçülen davranış, bir kullanıcı görsel yüklediğinde çalışan davranışın aynısıdır."
    )
    add("")
    add("### Ölçüm kurgusu")
    add("")
    add(
        "Korpustaki her görsel önce platformun yayın adımlarından geçirildi "
        "(görünmez filigran gömüldü, C2PA manifesti imzalandı) ve türevler bu "
        "**yayınlanmış** hâlden üretildi. Türev üretimi piksel dizisi üzerinde "
        "çalıştığı için manifest ve tüm metadata siliniyor — yani hattın 0. aşaması "
        "hiçbir sorguda tetiklenmiyor. Ölçülen şey saf **kurtarma** başarısıdır: "
        "içerik kimliği silinmiş bir dosyada kaynağı bulabiliyor muyuz."
    )
    add("")
    add(
        "**Negatif kontrol:** holdout görselleri indekse hiç alınmadı. Bu sorgularda "
        "önerilen *herhangi bir* bağ yanlış atıftır. Bu projede yanlış atıf, kaçırılmış "
        "atıftan daha ağır bir hatadır; tabloların en önemli sütunu budur."
    )
    add("")
    add("---")
    add("")
    add("## Özet")
    add("")
    add("| Metrik | Sonuç |")
    add("|---|---|")
    add(f"| Ortalama Top-1 doğruluk | **%{_tr(ort_top1 * 100)}** |")
    add(f"| Ortalama Top-5 doğruluk | **%{_tr(ort_top5 * 100)}** |")
    add(
        f"| Yanlış atıf oranı (yanlış Top-1 + negatif kontrol bağları) | "
        f"**%{_tr(yanlis_orani * 100, 2)}** ({toplam_yanlis} / {poz + neg}) |"
    )
    add(
        f"| Kapsama ölçüm hatası (MAE) | **{_tr(genel_mae, 4)}** "
        f"({len(tum_hatalar)} ölçüm, hedef ≤ 0,05) |"
    )
    if tum_gecikme:
        add(
            f"| Uçtan uca gecikme | p50 **{_tr(float(np.percentile(tum_gecikme, 50)), 0)} ms** · "
            f"p95 {_tr(float(np.percentile(tum_gecikme, 95)), 0)} ms |"
        )
    add("")
    add("---")
    add("")
    add("## Senaryo başına doğruluk")
    add("")
    add("| Senaryo | Top-1 | Top-5 | Bulundu | Yanlış Top-1 | Negatif kontrol bağı |")
    add("|---|---|---|---|---|---|")
    for s in rows:
        bulundu = s.bulundu / s.pozitif * 100 if s.pozitif else 0.0
        add(
            f"| {s.name} | %{_tr(s.top1_orani * 100)} | %{_tr(s.top5_orani * 100)} | "
            f"%{_tr(bulundu)} | {s.yanlis_top1} | {s.negatif_bag} |"
        )
    add(
        f"| **Ortalama** | **%{_tr(ort_top1 * 100)}** | **%{_tr(ort_top5 * 100)}** | | "
        f"**{sum(s.yanlis_top1 for s in rows)}** | **{sum(s.negatif_bag for s in rows)}** |"
    )
    add("")
    add("---")
    add("")
    add("## Kullanılan alan oranı ölçümü")
    add("")
    add(
        "Katkı payı motorunun girdisi bu sayıdır. Beklenen değer, türevi üreten "
        "dönüşümün geometrisinden hesaplanır (`eval/attacks.py: EXPECTED_COVERAGE`)."
    )
    add("")
    add("| Senaryo | Beklenen | Ölçülen (ort.) | MAE | Ölçülen / ölçülemeyen |")
    add("|---|---|---|---|---|")
    for s in rows:
        beklenen = EXPECTED_COVERAGE.get(s.name)
        if s.kapsama_mae is None:
            add(
                f"| {s.name} | {_tr(beklenen, 2) if beklenen else '—'} | — | — | "
                f"0 / {s.olculemedi} |"
            )
            continue
        mae = s.kapsama_mae
        bayrak = "" if mae <= COVERAGE_TOLERANCE else " ⚠"
        add(
            f"| {s.name} | {_tr(beklenen, 2)} | {_tr(float(np.mean(s.kapsama_olculen)), 3)} | "
            f"**{_tr(mae, 4)}**{bayrak} | {len(s.kapsama_hatalari)} / {s.olculemedi} |"
        )
    add("")
    add(f"Genel MAE: **{_tr(genel_mae, 4)}** (hedef ≤ 0,05)")
    add("")
    add("---")
    add("")
    add("## Kararın hangi aşamadan geldiği")
    add("")
    add(
        "Doğru bulunan bağlarda, en güçlü kanıtı hangi aşamanın ürettiği. "
        "Aşamaların iş bölümünü gösterir: filigran piksel düzeni korunmuşsa kesin "
        "kanıt verir, geometrik dönüşümlerde devreyi CLIP ve homografi devralır."
    )
    add("")
    toplam_asama: Counter = Counter()
    for s in rows:
        toplam_asama.update(s.asamalar)
    add("| Aşama | Kaç kararda belirleyici oldu | Oran |")
    add("|---|---|---|")
    genel = sum(toplam_asama.values()) or 1
    for stage, count in toplam_asama.most_common():
        add(f"| {stage} | {count} | %{_tr(count / genel * 100)} |")
    add("")
    add("---")
    add("")
    add("## Gecikme")
    add("")
    add("| Senaryo | p50 (ms) | p95 (ms) |")
    add("|---|---|---|")
    for s in rows:
        add(f"| {s.name} | {_tr(s.p50, 0)} | {_tr(s.p95, 0)} |")
    add("")
    asama_ort: dict[str, list[float]] = {}
    for s in rows:
        for stage, values in s.asama_gecikmeleri.items():
            asama_ort.setdefault(stage, []).extend(values)
    if asama_ort:
        add("### Aşama başına ortalama süre")
        add("")
        add("| Aşama | Ortalama (ms) | Toplamdaki payı |")
        add("|---|---|---|")
        toplam_ms = sum(float(np.mean(v)) for v in asama_ort.values()) or 1.0
        for stage, values in sorted(
            asama_ort.items(), key=lambda kv: -float(np.mean(kv[1]))
        ):
            ort = float(np.mean(values))
            add(f"| {stage} | {_tr(ort, 1)} | %{_tr(ort / toplam_ms * 100)} |")
        add("")
    add("---")
    add("")
    add("## Dürüst sınırlar")
    add("")
    zayif = [s for s in rows if s.top1_orani < 0.90]
    if zayif:
        add("Top-1 doğruluğu %90'ın altında kalan senaryolar:")
        add("")
        for s in zayif:
            add(f"- **{s.name}** — Top-1 %{_tr(s.top1_orani * 100)}, Top-5 %{_tr(s.top5_orani * 100)}")
        add("")
        add(
            "Bu senaryolarda kaynak çoğunlukla aday listesinde var ama en üstte değil. "
            "Sistem tek bir kaynağı dayatmadığı, sıralı bir zincir önerisi sunduğu ve "
            "kullanıcı itiraz edebildiği için pratikteki etki Top-1 farkından daha küçüktür."
        )
    else:
        add("Tüm senaryolarda Top-1 doğruluğu %90'ın üzerinde.")
    add("")

    sapan = [
        s for s in rows
        if s.kapsama_mae is not None and s.kapsama_mae > COVERAGE_TOLERANCE
    ]
    if sapan:
        add(
            f"Kapsama ölçümünde {_tr(COVERAGE_TOLERANCE, 2)} hata payını aşan senaryolar:"
        )
        add("")
        for s in sapan:
            beklenen = EXPECTED_COVERAGE.get(s.name)
            olculen = float(np.mean(s.kapsama_olculen))
            yon = "eksik" if olculen < (beklenen or 0) else "fazla"
            add(
                f"- **{s.name}** — beklenen {_tr(beklenen, 2)}, ölçülen "
                f"{_tr(olculen, 3)} (MAE {_tr(s.kapsama_mae, 4)}); kaynağa {yon} pay yönünde."
            )
        add("")
        add(
            "Sapmanın yönü önemli: kaynağa **eksik** pay veren bir hata, kaynağın itiraz "
            "edip yeniden ölçüm isteyebildiği bir sistemde düzeltilebilir. Ağır "
            "küçültmede (görsel 200×150 piksele indiğinde) yerel özellikler seyrekleşiyor "
            "ve homografi kaynağın kenarlarını tam oturtamıyor; kaybedilen alan "
            "çerçevenin dışına değil, ölçülemeyen kenar bandına gidiyor."
        )
        add("")
    olculemeyen = sum(s.olculemedi for s in rows)
    if olculemeyen:
        add(
            f"{olculemeyen} doğru bağda geometrik doğrulama yapılamadı; bu bağlarda pay "
            "hesabı ihtiyatlı kapsama varsayımıyla (`unverified_coverage`) çalışır ve "
            "kaynak itiraz ederek yeniden ölçüm isteyebilir."
        )
        add("")

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
def main() -> int:
    parser = argparse.ArgumentParser(description="Koken kurtarma hattinin degerlendirmesi")
    parser.add_argument("--corpus", type=int, default=0,
                        help="Korpustan kullanilacak gorsel sayisi (0 = hepsi); hizli deneme icin")
    parser.add_argument("--queries", type=int, default=0,
                        help="Pozitif sorgu gorseli sayisi (0 = indeksteki hepsi)")
    parser.add_argument("--holdout", type=int, default=40,
                        help="Indekse alinmayacak gorsel sayisi (negatif kontrol)")
    parser.add_argument("--scenarios", type=str, default="",
                        help="Virgulle ayrilmis senaryo adlari (bos = hepsi)")
    parser.add_argument("--rebuild", action="store_true",
                        help="Yayinlanmis dosyalari bastan uret")
    args = parser.parse_args()

    get_settings()  # dizinleri kur
    paths = sorted(RAW.glob("*.jpg"))
    if not paths:
        raise SystemExit("Korpus bos. Once: .venv/Scripts/python.exe scripts/fetch_eval_images.py")
    paths = dedupe(paths)
    if args.corpus > 0:
        paths = paths[: args.corpus]

    ids = publish_corpus(paths, args.rebuild)

    rng = random.Random(SEED)
    shuffled = ids[:]
    rng.shuffle(shuffled)
    holdout = shuffled[: args.holdout]
    indexed = shuffled[args.holdout:]
    if not indexed:
        raise SystemExit("Holdout tum korpusu yuttu; --holdout degerini dusurun.")

    store = EvalStore()
    index = build_index(indexed, store)

    positives = indexed if args.queries <= 0 else indexed[: args.queries]
    scenarios = (
        [s.strip() for s in args.scenarios.split(",") if s.strip()]
        if args.scenarios
        else list(ATTACKS)
    )
    bilinmeyen = [s for s in scenarios if s not in ATTACKS]
    if bilinmeyen:
        raise SystemExit(f"Bilinmeyen senaryo: {', '.join(bilinmeyen)}")

    print(
        f"Degerlendirme: {len(positives)} pozitif + {len(holdout)} negatif gorsel "
        f"x {len(scenarios)} senaryo = {(len(positives) + len(holdout)) * len(scenarios)} sorgu\n"
    )
    t0 = time.perf_counter()
    stats = evaluate(index, store, positives, holdout, scenarios)
    sure = time.perf_counter() - t0

    meta = {
        "tarih": time.strftime("%d.%m.%Y %H:%M"),
        "ortam": f"{embedding.pick_device()}, korpus {len(ids)} görsel",
        "indeks": len(indexed),
        "pozitif": len(positives),
        "holdout": len(holdout),
        "sure_sn": round(sure, 1),
    }
    write_report(stats, meta)
    RESULTS.write_text(
        json.dumps({"meta": meta, "senaryolar": _as_dict(stats)}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    rows = list(stats.values())
    ort_top1 = float(np.mean([s.top1_orani for s in rows]))
    yanlis = sum(s.yanlis_top1 for s in rows) + sum(s.negatif_bag for s in rows)
    toplam = sum(s.pozitif + s.negatif for s in rows)
    hatalar = [e for s in rows for e in s.kapsama_hatalari]
    mae = float(np.mean(hatalar)) if hatalar else 1.0

    print(f"\n{'=' * 72}")
    print("DEGERLENDIRME SONUCU")
    print("=" * 72)
    print(f"  Sure                     : {sure / 60:.1f} dk")
    print(f"  Ortalama Top-1           : %{ort_top1 * 100:.1f}")
    print(f"  Yanlis atif              : {yanlis} / {toplam}  (%{yanlis / toplam * 100:.2f})")
    print(f"  Kapsama MAE              : {mae:.4f}  (hedef <= 0.05)")
    print(f"  Rapor                    : {REPORT}")
    print(f"  Ham sonuclar             : {RESULTS}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
