"""Degerlendirme korpusunu indirir.

Kaynak: picsum.photos (Unsplash lisansi - serbest kullanim).
`/seed/<tohum>/` uc noktasi deterministiktir; ayni tohum her zaman ayni
gorseli verir, boylece benchmark tekrarlanabilir olur.

Kullanim:
    .venv/Scripts/python.exe scripts/fetch_eval_images.py [adet]
"""

from __future__ import annotations

import concurrent.futures as futures
import sys
import urllib.request
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "data" / "raw"
DEFAULT_COUNT = 320
WIDTH, HEIGHT = 800, 600
HEADERS = {"User-Agent": "N-Emek-Research/0.1"}


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


def main() -> int:
    count = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_COUNT
    OUT.mkdir(parents=True, exist_ok=True)
    ok = 0
    fail = 0
    with futures.ThreadPoolExecutor(max_workers=8) as pool:
        for i, (seed, success, note) in enumerate(pool.map(fetch, range(count)), 1):
            if success:
                ok += 1
            else:
                fail += 1
                print(f"  basarisiz seed={seed}: {note}")
            if i % 40 == 0:
                print(f"  {i}/{count} ... basarili={ok} basarisiz={fail}")
    print(f"\nTamamlandi: {ok} gorsel -> {OUT}  (basarisiz: {fail})")
    return 0 if ok > count * 0.9 else 1


if __name__ == "__main__":
    sys.exit(main())
