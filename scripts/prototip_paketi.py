"""Calisan prototipin temiz bir kopyasini uretir.

Neden var
---------
Depo yalnizca uygulamadan olusmuyor: teknik rapor, olcum dokumanlari,
degerlendirme duzenegi, 100 MB'lik test korpusu ve rapor uretim
betikleri de burada. Prototipi birine vermek gerektiginde bunlarin
hepsi gurultu.

Bu betik **yalnizca uygulamayi** ayri bir klasore cikarir: `docker
compose up --build` ile ayaga kalkan sey, fazlasi degil.

Ilke: hicbir dosya **degistirilmez**, yalnizca secilir. Kopyadaki
uygulama depodakiyle bayt bayt ayni; boylece "prototipte baska bir
surum vardi" durumu olusamaz.

Neyin disarida kaldigi ve nedeni
--------------------------------
    docs/                rapor ve dokumanlar - uygulama degil
    backend/eval/        degerlendirme duzenegi - uygulama degil
    backend/poc/         faz 0 kavram kanitlari - uygulama degil
    backend/tests/       `conftest.py` korpusa bagimli (data/raw), korpus
                         kopyalanmiyor; testler orada zaten kosamazdi
    data/                korpus, yuklemeler, indeks, veritabani - hepsi
                         kapsayici acilisinda uretiliyor
    backend/certs/       imzalama anahtarlari; kapsayici kendi uretir
    node_modules/, dist/, .venv/, __pycache__/   uretilen
    scripts/rapor_*      rapor uretim betikleri - uygulamanin parcasi degil

`frontend/src/test/setup.ts` disarida **birakilmiyor**: `vite.config.ts`
ona atif yapiyor ve dosyayi silmek yapilandirmayi bozuk birakirdi.
Yapilandirmayi degistirmek ise "hicbir dosya degistirilmez" ilkesini
bozardi.

Kullanim
--------
    .venv/Scripts/python.exe scripts/prototip_paketi.py
    .venv/Scripts/python.exe scripts/prototip_paketi.py --hedef D:/bir/yer
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[1]
VARSAYILAN_HEDEF = Path.home() / "Desktop" / "N-Emek-Prototip"

# Kok dizinden birebir kopyalanan dosyalar.
DOSYALAR = [
    "docker-compose.yml",
    ".dockerignore",
    ".env.example",
    "LICENSE",
]

# (kaynak dizin, hedef dizin, disarida birakilacak alt yollar)
DIZINLER = [
    ("backend/app", "backend/app", []),
    ("frontend/src", "frontend/src", []),
    ("frontend/public", "frontend/public", []),
    ("docker", "docker", []),
]

# Dizin icinden tek tek secilen dosyalar.
SECILI = [
    "backend/requirements.txt",
    "backend/Dockerfile",
    "frontend/index.html",
    "frontend/package.json",
    "frontend/package-lock.json",
    "frontend/tsconfig.json",
    "frontend/vite.config.ts",
    "frontend/nginx.conf",
    "frontend/Dockerfile",
    # Kapsayici acilis betiginin (docker/entrypoint.sh) cagirdiklari.
    # Bunlar olmadan sertifika, korpus ve demo verisi olusmaz.
    "scripts/gen_dev_certs.py",
    "scripts/fetch_eval_images.py",
    "scripts/seed_demo.py",
    # Demoda bir kullaniciyi moderator yapmak icin; kucuk ve isleve ait.
    "scripts/set_role.py",
]

# Kopyalanan agacta hicbir yerde bulunmamasi gerekenler. Denetim bunlari
# arar: elle bir sey eklendiginde ya da depo yapisi degistiginde
# paketin sessizce kirlenmesini engelliyor.
YASAK_KALIP = [
    "*.md",       # OKUBENI.txt disinda metin dosyasi istenmedi
    "*.pdf",
    "*.docx",
    "*.db",
    "*.pem",
    "*.key",
    "__pycache__",
    "node_modules",
    ".venv",
    "tsconfig.tsbuildinfo",
]

# Uretilen dosyalari kopyalamamak icin.
ATLA = {"__pycache__", "node_modules", ".venv", ".pytest_cache", "dist"}

OKUBENI = """N-Emek — Prototip
=================

Bu klasor yalnizca calisan uygulamadir. Teknik rapor, olcum dokumanlari
ve degerlendirme duzenegi bilerek disarida birakildi.


CALISTIRMA
----------

Onkosul: Docker Desktop kurulu ve calisir durumda.

    docker compose up --build

Ardindan tarayicida:   http://localhost:5173

Ilk acilis 10-15 dakika surer. Bunun sebebi indirme:

  * Python ve Node bagimliliklari kurulur
  * CLIP gorsel modeli iner (~600 MB)
  * C2PA imzalama sertifikalari uretilir
  * Test gorseli korpusu iner ve demo senaryosu kurulur

Sonraki acilislar saniyeler icinde olur; uretilen her sey Docker
biriminde (volume) kalici.


SIFIRLAMA
---------

Demo verisini bastan kurmak icin:

    docker compose down -v
    docker compose up --build


NE GORECEKSINIZ
---------------

Acilista demo senaryosu kurulu gelir: uc kullanici, uc gonderi ve bir
marka kampanyasi. Akistaki ucuncu gonderi, ikincisinin ekran goruntusu
alinarak uretilmis ve icerik kimligi silinmis olanidir; sistem kaynagini
olcerek geri bulur.

Bir gonderiye girip "Emek Karti"ni acin: her payin altinda gerekcesi,
olculen kapsama orani ve kanit satirlari durur.

Backend ayrica dogrudan kullanilabilir:  http://localhost:8000/docs


GPU
---

Varsayilan kurulum CPU uzerinde calisir; GPU gerekmez, yalnizca daha
yavastir. GPU kullanmak isterseniz docker-compose.yml dosyasinin
sonundaki nota bakin.
"""


def kopyala(hedef: Path) -> tuple[int, int]:
    """Doner: (dosya sayisi, toplam bayt)."""
    adet = 0
    boyut = 0

    def kopyala_dosya(kaynak: Path, varis: Path) -> None:
        nonlocal adet, boyut
        varis.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(kaynak, varis)
        adet += 1
        boyut += kaynak.stat().st_size

    for yol in DOSYALAR + SECILI:
        kaynak = ROOT / yol
        if not kaynak.exists():
            raise SystemExit(f"kaynak dosya yok: {yol}")
        kopyala_dosya(kaynak, hedef / yol)

    for kaynak_dizin, hedef_dizin, haric in DIZINLER:
        temel = ROOT / kaynak_dizin
        if not temel.is_dir():
            raise SystemExit(f"kaynak dizin yok: {kaynak_dizin}")
        for kaynak in temel.rglob("*"):
            if not kaynak.is_file():
                continue
            if ATLA & set(kaynak.relative_to(temel).parts):
                continue
            goreli = kaynak.relative_to(temel)
            if any(goreli.match(k) for k in haric):
                continue
            kopyala_dosya(kaynak, hedef / hedef_dizin / goreli)

    return adet, boyut


def denetle(hedef: Path) -> list[str]:
    """Pakete girmemesi gereken bir sey girmis mi, gereken bir sey eksik mi."""
    sorunlar: list[str] = []

    for kalip in YASAK_KALIP:
        for yol in hedef.rglob(kalip):
            if yol.name == "OKUBENI.txt":
                continue
            sorunlar.append(f"pakette olmamaliydi: {yol.relative_to(hedef).as_posix()}")

    # Docker yapilandirmasinin adiyla andigi her sey yerinde mi. Eksik
    # bir dosya ancak 10-15 dakikalik derlemenin ortasinda fark edilirdi.
    gerekli = [
        "docker-compose.yml",
        "backend/Dockerfile",
        "backend/requirements.txt",
        "backend/app/main.py",
        "docker/entrypoint.sh",
        "scripts/gen_dev_certs.py",
        "scripts/fetch_eval_images.py",
        "scripts/seed_demo.py",
        "frontend/Dockerfile",
        "frontend/nginx.conf",
        "frontend/package.json",
        "frontend/package-lock.json",
        "frontend/index.html",
        "frontend/vite.config.ts",
        "frontend/src/main.tsx",
        "frontend/src/test/setup.ts",
    ]
    for yol in gerekli:
        if not (hedef / yol).exists():
            sorunlar.append(f"eksik: {yol}")

    return sorunlar


def main() -> int:
    ayristirici = argparse.ArgumentParser(description=__doc__)
    ayristirici.add_argument("--hedef", type=Path, default=VARSAYILAN_HEDEF)
    args = ayristirici.parse_args()
    hedef: Path = args.hedef

    if hedef.exists():
        # Bilincli olarak once siliniyor: uzerine yazmak, bir onceki
        # paketten kalan dosyalari sessizce tasirdi.
        print(f"var olan klasör siliniyor: {hedef}")
        shutil.rmtree(hedef)

    hedef.mkdir(parents=True)
    adet, boyut = kopyala(hedef)
    (hedef / "OKUBENI.txt").write_text(OKUBENI, encoding="utf-8")
    adet += 1

    sorunlar = denetle(hedef)

    print(f"\n✓ {hedef}")
    print(f"  {adet} dosya · {boyut / 1024 / 1024:.1f} MB")
    for ust in sorted(p for p in hedef.iterdir()):
        if ust.is_dir():
            ic = sum(1 for _ in ust.rglob("*") if _.is_file())
            print(f"    {ust.name}/  ({ic} dosya)")
        else:
            print(f"    {ust.name}")

    if sorunlar:
        print(f"\n{len(sorunlar)} sorun:")
        for s in sorunlar:
            print(f"  · {s}")
        return 1

    print("\nDenetim temiz: fazlalık yok, Docker'ın istediği her dosya yerinde.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
