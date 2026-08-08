"""Faz 0 PoC - Aday kaynak bulma hattinin geri getirme basarisi.

320 gorsellik korpus indekslenir, ardindan 40 gorselin 20 farkli
donusturulmus turevi sorgu olarak calistirilir. Her asamanin
(tam hash / pHash / blok hash / CLIP) o senaryoda gercek kaynagi
bulup bulmadigi olculur.

Bu tablo teknik raporun "yontem dogrulamasi" bolumune girecek.

Calistirma:  .venv/Scripts/python.exe backend/poc/poc_similarity.py
"""

from __future__ import annotations

import random
import sys
import time
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.provenance import embedding, fingerprint as fp, regions  # noqa: E402
from app.provenance.index import ProvenanceIndex  # noqa: E402
from eval.attacks import ATTACKS  # noqa: E402

RAW = Path(__file__).resolve().parents[2] / "data" / "raw"
QUERY_COUNT = 40
SEED = 42


def bgr_to_pil(img: np.ndarray) -> Image.Image:
    return Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))


def build_index() -> tuple[ProvenanceIndex, list[str], dict[str, np.ndarray]]:
    paths = sorted(RAW.glob("*.jpg"))
    if not paths:
        raise SystemExit("Korpus bos. Once: python scripts/fetch_eval_images.py")

    print(f"Korpus indeksleniyor: {len(paths)} gorsel  (cihaz: {embedding.pick_device()})")
    images: dict[str, np.ndarray] = {}
    fingers: dict[str, fp.Fingerprint] = {}

    t0 = time.perf_counter()
    pil_batch: list[Image.Image] = []
    ids: list[str] = []
    for path in paths:
        raw = path.read_bytes()
        bgr = cv2.imdecode(np.frombuffer(raw, np.uint8), cv2.IMREAD_COLOR)
        if bgr is None:
            continue
        cid = path.stem
        images[cid] = bgr
        pil = bgr_to_pil(bgr)
        fingers[cid] = fp.compute(pil, raw_bytes=raw)
        pil_batch.append(pil)
        ids.append(cid)
    t_fingerprint = time.perf_counter() - t0

    t0 = time.perf_counter()
    vectors = embedding.embed(pil_batch, batch_size=32)
    t_embed = time.perf_counter() - t0

    index = ProvenanceIndex()
    for cid, vec in zip(ids, vectors):
        index.add(cid, fingers[cid], vec)

    print(f"  parmak izi : {t_fingerprint:.1f} sn  ({t_fingerprint / len(ids) * 1000:.0f} ms/gorsel)")
    print(f"  CLIP gomme : {t_embed:.1f} sn  ({t_embed / len(ids) * 1000:.0f} ms/gorsel)")
    print(f"  indeks     : {len(index)} kayit\n")
    return index, ids, images


def main() -> int:
    index, ids, images = build_index()
    rng = random.Random(SEED)
    queries = rng.sample(ids, min(QUERY_COUNT, len(ids)))

    attack_names = list(ATTACKS.keys())
    # sonuc[senaryo][asama] = dogru bulunan sorgu sayisi
    hits: dict[str, dict[str, int]] = {
        a: {"tam": 0, "phash": 0, "blok": 0, "clip": 0, "birlesik": 0} for a in attack_names
    }
    latency: dict[str, float] = {a: 0.0 for a in attack_names}

    for attack in attack_names:
        derivatives = [ATTACKS[attack](images[cid]) for cid in queries]
        pils = [bgr_to_pil(d) for d in derivatives]

        # Cok bolgeli sorgu: her turev icin bolge kumesi cikarilir ve
        # tek bir GPU yigininda gomulur.
        region_sets = [list(regions.iter_regions(p)) for p in pils]
        flat = [img for rset in region_sets for _, img in rset]
        flat_vectors = embedding.embed(flat, batch_size=64)

        t0 = time.perf_counter()
        cursor = 0
        for cid, derivative, pil, rset in zip(queries, derivatives, pils, region_sets):
            vecs = flat_vectors[cursor : cursor + len(rset)]
            cursor += len(rset)

            ok, buf = cv2.imencode(".jpg", derivative, [cv2.IMWRITE_JPEG_QUALITY, 92])
            finger = fp.compute(pil, raw_bytes=buf.tobytes() if ok else None)

            found = set()
            if index.exact(finger.content_hash) == cid:
                hits[attack]["tam"] += 1
                found.add("tam")

            # pHash: her bolgenin global hash'i, kaynagin global hash'ine karsi
            for _, region_img in rset:
                rfinger = fp.compute(region_img)
                if any(c.content_id == cid for c in index.search_phash(rfinger, k=5)):
                    hits[attack]["phash"] += 1
                    found.add("phash")
                    break

            if any(c.content_id == cid for c in index.search_tiles(finger, k=5)):
                hits[attack]["blok"] += 1
                found.add("blok")

            if any(
                c.content_id == cid
                for vec in vecs
                for c in index.search_clip(vec, k=5)
            ):
                hits[attack]["clip"] += 1
                found.add("clip")

            if found:
                hits[attack]["birlesik"] += 1
        latency[attack] = (time.perf_counter() - t0) / len(queries) * 1000

    # --- Tablo ---------------------------------------------------------------
    n = len(queries)
    header = f"{'senaryo':<18}{'tam':>7}{'pHash':>8}{'blok':>7}{'CLIP':>7}{'BIRLESIK':>10}{'gecikme':>10}"
    print(f"Sorgu basina geri getirme (%), n={n} gorsel/senaryo, top-5")
    print(header)
    print("-" * len(header))
    for attack in attack_names:
        h = hits[attack]
        birlesik = h["birlesik"] / n * 100
        flag = "" if birlesik >= 90 else ("  <- zayif" if birlesik >= 50 else "  <- BASARISIZ")
        print(
            f"{attack:<18}{h['tam'] / n * 100:>6.0f}%{h['phash'] / n * 100:>7.0f}%"
            f"{h['blok'] / n * 100:>6.0f}%{h['clip'] / n * 100:>6.0f}%"
            f"{birlesik:>9.0f}%{latency[attack]:>8.0f}ms{flag}"
        )

    overall = np.mean([hits[a]["birlesik"] / n for a in attack_names]) * 100
    zayif = [a for a in attack_names if hits[a]["birlesik"] / n < 0.9]
    print("-" * len(header))
    print(f"{'ORTALAMA':<18}{'':>7}{'':>8}{'':>7}{'':>7}{overall:>9.0f}%")

    print("\n" + "=" * 72)
    print("PoC SONUCU")
    print("=" * 72)
    print(f"  Ortalama birlesik geri getirme : {overall:.1f}%")
    print(f"  Hedefin altinda kalan senaryolar: {', '.join(zayif) if zayif else 'yok'}")
    ok = overall >= 90
    print(f"\n  RISK 2 (aday bulma) {'KAPANDI' if ok else 'ACIK - hat guclendirilmeli'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
