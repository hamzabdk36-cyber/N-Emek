"""Degerlendirme korpusunu indirir.

Kaynak: picsum.photos (Unsplash lisansi - serbest kullanim).
`/seed/<tohum>/` uc noktasi deterministiktir; ayni tohum her zaman ayni
gorseli verir, boylece benchmark tekrarlanabilir olur.

**Tekillik zorunlu.** picsum farkli tohumlari ayni fotografa
esleyebiliyor - ilk kosumuzda 320 dosyanin yalnizca 276'si benzersiz
cikti. Yinelenen bir gorsel degerlendirmeyi bozar: indekste birebir
ikizi olan bir "holdout" gorseli icin bag bulmak yanlis atif degil,
dogru davranistir; ama sayac bunu yanlis atif olarak yazar. Bu yuzden
betik indirdigi her dosyanin SHA-256 ozetini tutar, yinelenenleri siler
ve hedef sayiya ulasana kadar yeni tohumlarla devam eder.

Kullanim:
    .venv/Scripts/python.exe scripts/fetch_eval_images.py [adet]
"""

from __future__ import annotations

import concurrent.futures as futures
import hashlib
import sys
import urllib.request
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "data" / "raw"
DEFAULT_COUNT = 320
WIDTH, HEIGHT = 800, 600
HEADERS = {"User-Agent": "N-Emek-Research/0.1"}
# Yinelenenler yuzunden hedefe ulasilamazsa sonsuz donguye girmemek icin.
MAX_SEED_FACTOR = 4


def fetch(seed: int) -> tuple[int, bool, str]:
    dest = OUT / f"img_{seed:04d}.jpg"
    if dest.exists() and dest.stat().st_size > 5000:
        return seed, True, "atlandi"
    url = f"https://picsum.photos/seed/nemek{seed}/{WIDTH}/{HEIGHT}"
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        data = urllib.request.urlopen(req, timeout=30).read()
        if len(data) < 5000:
            return seed, False, "cok kucuk"
        dest.write_bytes(data)
        return seed, True, "indirildi"
    except Exception as exc:
        return seed, False, f"{type(exc).__name__}"


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    count = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_COUNT
    OUT.mkdir(parents=True, exist_ok=True)

    # Zaten indirilmis dosyalari tara; yinelenenleri simdi temizle.
    ozetler: dict[str, str] = {}
    yinelenen = 0
    for path in sorted(OUT.glob("*.jpg")):
        digest = _digest(path)
        if digest in ozetler:
            path.unlink()
            yinelenen += 1
        else:
            ozetler[digest] = path.stem
    if yinelenen:
        print(f"Yinelenen {yinelenen} dosya silindi; elde {len(ozetler)} benzersiz gorsel var.")

    seed = 0
    fail = 0
    sinir = count * MAX_SEED_FACTOR
    with futures.ThreadPoolExecutor(max_workers=8) as pool:
        while len(ozetler) < count and seed < sinir:
            parti = range(seed, min(seed + 64, sinir))
            seed += 64
            for s, success, note in pool.map(fetch, parti):
                if not success:
                    fail += 1
                    print(f"  basarisiz seed={s}: {note}")
                    continue
                path = OUT / f"img_{s:04d}.jpg"
                digest = _digest(path)
                if digest in ozetler and ozetler[digest] != path.stem:
                    # picsum bu tohumu daha once gordugumuz bir fotografa esledi.
                    path.unlink()
                    continue
                ozetler[digest] = path.stem
            print(f"  tohum {seed} ... benzersiz={len(ozetler)}/{count} basarisiz={fail}")

    if len(ozetler) < count:
        print(f"\nUYARI: hedef {count}, elde edilen {len(ozetler)}. "
              "picsum havuzu tukenmis olabilir; MAX_SEED_FACTOR artirilabilir.")
    elif len(ozetler) > count:
        # Partiler 64'luk oldugu icin hedefi asabiliyoruz. Korpusun
        # tam olarak istenen boyutta olmasi, olcumlerin tekrarlanabilir
        # olmasi icin onemli.
        fazla = sorted(OUT.glob("*.jpg"))[count:]
        for path in fazla:
            path.unlink()
        print(f"Hedef asildi; {len(fazla)} fazla dosya silindi.")
        ozetler = {d: s for d, s in ozetler.items() if (OUT / f"{s}.jpg").exists()}
    print(f"\nTamamlandi: {len(ozetler)} benzersiz gorsel -> {OUT}  (basarisiz istek: {fail})")
    return 0 if len(ozetler) >= count * 0.9 else 1


if __name__ == "__main__":
    sys.exit(main())
