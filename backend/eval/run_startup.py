"""Acilis suresi olcumu: indeks kaliciligi ne kazandiriyor.

Sistemin "olceklenir" iddiasinin acilis tarafindaki sayisal dayanagi.

Olculen uc kademe (bkz. app/services/registry.py):

  gorseller     her icerigin gorseli okunur, parmak izi ve CLIP
                gommesi yeniden hesaplanir. Kalicilik eklenmeden
                onceki tek yol buydu.
  veritabani    parmak izi ve vektor veritabanindaki sutunlardan
                okunur; gorsel dosyalarina dokunulmaz, model yuklenmez.
  anlik goruntu diskteki FAISS dosyalari okunur.

Model yukleme maliyeti bilerek olcum disinda: her uc kademede de
onbellekten gelirdi ve "gorseller" kademesinin lehine yanilti olurdu.
Karsilastirilan sey icerik basina odenen is.

Kullanim:
    cd backend
    ../.venv/Scripts/python.exe -m eval.run_startup            # 280 icerik
    ../.venv/Scripts/python.exe -m eval.run_startup --icerik 40 --tekrar 2

Cikti: docs/ACILIS-SURESI.md  +  data/eval/acilis.json
Bu dosyalar elle duzenlenmez; sayilar degistiyse betik yeniden kosulur.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import statistics
import sys
import tempfile
import time
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

_TMP = Path(tempfile.mkdtemp(prefix="nemek-acilis-"))
os.environ["NEMEK_DATA_DIR"] = str(_TMP)
os.environ["NEMEK_UPLOAD_DIR"] = str(_TMP / "uploads")
os.environ["NEMEK_INDEX_DIR"] = str(_TMP / "index")
os.environ["NEMEK_DATABASE_URL"] = f"sqlite:///{(_TMP / 'acilis.db').as_posix()}"

import cv2  # noqa: E402
from PIL import Image  # noqa: E402

from app.core.database import SessionLocal, create_schema  # noqa: E402
from app.models.entities import Content, User  # noqa: E402
from app.provenance import embedding  # noqa: E402
from app.provenance import fingerprint as fp  # noqa: E402
from app.services.registry import IndexService  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
REPORT = ROOT / "docs" / "ACILIS-SURESI.md"
RESULTS = ROOT / "data" / "eval" / "acilis.json"

KADEMELER = [
    (
        "gorseller",
        "Görseller",
        "her içeriğin görseli okunur, parmak izi ve CLIP gömmesi yeniden hesaplanır",
    ),
    (
        "veritabani",
        "Veritabanı",
        "parmak izi ve vektör sütunlardan okunur; görsele ve modele dokunulmaz",
    ),
    (
        "anlik_goruntu",
        "Anlık görüntü",
        "diskteki FAISS dosyaları okunur",
    ),
]


# ---------------------------------------------------------------------------
def korpusu_yaz(session, sayi: int) -> int:
    """Veritabanina `sayi` kadar icerik yazar - vektor sutunlari bos."""
    paths = sorted(RAW.glob("*.jpg"))[:sayi]
    if len(paths) < sayi:
        raise SystemExit(
            f"Korpusta {len(paths)} görsel var, {sayi} isteniyor.\n"
            f"Önce: .venv/Scripts/python.exe scripts/fetch_eval_images.py {sayi}"
        )

    korpus = User(handle="korpus", display_name="Korpus")
    session.add(korpus)
    session.flush()

    for path in paths:
        image = cv2.imread(str(path))
        if image is None:
            continue
        h, w = image.shape[:2]
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
                # Bilerek bos: "gorseller" kademesi tam da bu durumu olcuyor.
            )
        )
    session.commit()
    return len(paths)


def sutunlari_bosalt(session) -> None:
    for content in session.query(Content).all():
        content.tile_hashes = []
        content.clip_vector = None
    session.commit()


def sure_olc(fn) -> float:
    basla = time.perf_counter()
    fn()
    return (time.perf_counter() - basla) * 1000


# ---------------------------------------------------------------------------
def olc(sayi: int, tekrar: int) -> dict:
    create_schema()
    session = SessionLocal()
    yazilan = korpusu_yaz(session, sayi)
    print(f"korpus hazir: {yazilan} icerik\n")

    # Model onbellege alinsin: olculen sey icerik basina yapilan is,
    # tek seferlik model yukleme degil.
    embedding.embed_one(Image.open(sorted(RAW.glob('*.jpg'))[0]).convert("RGB"))

    olcum: dict[str, list[float]] = {k: [] for k, _, _ in KADEMELER}

    for tur in range(1, tekrar + 1):
        print(f"tur {tur}/{tekrar}")

        # 1. Gorseller: sutunlar bos, indeks sifirdan.
        sutunlari_bosalt(session)
        servis = IndexService()
        sure = sure_olc(lambda: servis.rebuild(session))
        olcum["gorseller"].append(sure)
        print(f"  görseller     {sure:8.0f} ms")

        # 2. Veritabani: sutunlar artik dolu (rebuild geri yazdi).
        servis = IndexService()
        sure = sure_olc(lambda: servis.rebuild(session))
        olcum["veritabani"].append(sure)
        print(f"  veritabanı    {sure:8.0f} ms")

        # 3. Anlik goruntu: diske yaz, yeni servisle geri yukle.
        servis.save_snapshot()
        servis = IndexService()
        sure = sure_olc(lambda: servis.load_or_rebuild(session))
        olcum["anlik_goruntu"].append(sure)
        print(f"  anlık görüntü {sure:8.0f} ms\n")

        assert len(servis) == yazilan, "indeks eksik kuruldu"

    session.close()
    return {
        "icerik": yazilan,
        "tekrar": tekrar,
        "olcum": olcum,
        "medyan": {k: statistics.median(v) for k, v in olcum.items()},
    }


# ---------------------------------------------------------------------------
def rapor_yaz(sonuc: dict) -> None:
    medyan = sonuc["medyan"]
    taban = medyan["gorseller"]
    n = sonuc["icerik"]

    lines: list[str] = []
    add = lines.append

    add("# Açılış Süresi — İndeks Kalıcılığı")
    add("")
    add(f"**Tarih:** {date.today().isoformat()}  ")
    add(f"**Ortam:** {platform.system()} {platform.machine()}, "
        f"Python {platform.python_version()}, cihaz `{embedding.pick_device()}`  ")
    add("**Üreten:** `backend/eval/run_startup.py` — bu dosya elle düzenlenmez.")
    add("")
    add(
        f"**{n}** içerikli bir veritabanıyla, açılışta indeksin kurulma süresi. "
        f"Her kademe **{sonuc['tekrar']}** kez ölçüldü; tabloda medyan var. "
        "Model yükleme maliyeti ölçüm dışında: her kademede önbellekten gelirdi ve "
        "en yavaş kademenin lehine yanıltırdı. Karşılaştırılan şey **içerik başına "
        "ödenen iş**."
    )
    add("")
    add("| Kademe | Medyan | İçerik başına | Hızlanma | Ne yapılıyor |")
    add("|---|--:|--:|--:|---|")
    for anahtar, baslik, aciklama in KADEMELER:
        ms = medyan[anahtar]
        hiz = taban / ms if ms > 0 else float("inf")
        basina = f"{ms / n:.2f}".replace(".", ",")
        add(
            f"| {baslik} | {_ms(ms)} | {basina} ms | "
            f"{'—' if anahtar == 'gorseller' else f'{hiz:.0f}×'} | {aciklama} |"
        )
    add("")
    add("## Ne değişti")
    add("")
    add(
        "Önce indeks her açılışta **görsellerden** kuruluyordu: her içerik için dosya "
        "okunuyor, parmak izi çıkarılıyor ve CLIP gömmesi yeniden hesaplanıyordu. "
        "Maliyet içerik başına bir model çıkarımı olduğu için açılış, içerik sayısıyla "
        "doğrusal büyüyordu."
    )
    add("")
    add(
        "Artık vektör ve blok hash'leri `contents` tablosunda saklanıyor, indeks de "
        "`data/index/snapshot/` altına yazılıyor. Açılışta önce anlık görüntü deneniyor; "
        "bayatsa veritabanı sütunlarından kuruluyor. Görsel okumak ve model çalıştırmak "
        "yalnızca vektörü eksik içerikler için gerekiyor — yani içerik başına **bir kez**."
    )
    add("")
    add(
        f"Ölçülen kazanç: {n} içerikte açılış {_ms(taban)} yerine "
        f"{_ms(medyan['anlik_goruntu'])} sürüyor."
    )
    add("")
    add("## Dürüst sınır")
    add("")
    add(
        "Anlık görüntü bir **önbellek**, kaynak doğru değil. Veritabanıyla kimlik kümesi "
        "uyuşmuyorsa sessizce atılıyor ve indeks veritabanından kuruluyor. Süreç aniden "
        "öldürülürse anlık görüntü bayat kalır; bu durumda açılış veritabanı kademesine "
        "düşer — hâlâ görsellerden hızlı, ama en hızlısı değil."
    )
    add("")

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    RESULTS.parent.mkdir(parents=True, exist_ok=True)
    RESULTS.write_text(json.dumps(sonuc, ensure_ascii=False, indent=2), encoding="utf-8")


def _ms(value: float) -> str:
    if value >= 1000:
        return f"{value / 1000:.1f} sn".replace(".", ",")
    return f"{value:.0f} ms"


# ---------------------------------------------------------------------------
def main() -> int:
    parser = argparse.ArgumentParser(description="Acilis suresi olcumu")
    parser.add_argument("--icerik", type=int, default=280, help="Veritabanindaki icerik sayisi")
    parser.add_argument("--tekrar", type=int, default=3, help="Her kademenin kac kez olculecegi")
    args = parser.parse_args()

    print("ACILIS SURESI OLCUMU")
    print(f"  icerik: {args.icerik}  tekrar: {args.tekrar}\n")

    sonuc = olc(args.icerik, args.tekrar)
    rapor_yaz(sonuc)

    medyan = sonuc["medyan"]
    print("MEDYANLAR")
    for anahtar, baslik, _ in KADEMELER:
        print(f"  {baslik:<14} {medyan[anahtar]:8.0f} ms")
    print(f"\nHizlanma: {medyan['gorseller'] / medyan['anlik_goruntu']:.0f}x")
    print(f"Rapor: {REPORT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
