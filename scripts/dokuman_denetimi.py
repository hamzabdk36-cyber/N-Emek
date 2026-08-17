"""Dokumanlardaki sayisal iddialari gercekle karsilastirir.

Neden var
---------
Projenin kurali su: hicbir performans sayisi elle yazilmaz, hepsi bir
betigin ciktisidir. Ama dokumanlarin *kendi* sayilari - "118 test",
"21 uc" - elle yaziliyordu ve tekrar tekrar kaydi. Tek bir gelistirme
oturumunda dort kez eskidiler; her seferinde biri fark edip elle
duzeltti. Kaymayi yakalayan bir sey yoktu.

Bu betik o boslugu kapatiyor: sayilari olcuyor, dokumanlardaki
iddialarla karsilastiriyor, uyusmazlikta dosya:satir vererek sifirdan
farkli cikiyor.

Isaretleme
----------
Bir dokumandaki her sayisal iddia, hangi olcume ait oldugunu kendisi
soyler. Isaret HTML yorumu (Markdown'da gorunmez) ya da YAML yorumu
olarak yazilir:

    118 test <!-- sayim: backend -->
    name: Testler (115 test)  # sayim: backend

Gecerli isaretler:

    sayim: backend              tum backend testleri
    sayim: backend-hizli        `slow` isaretli olmayanlar (CI'nin kostugu)
    sayim: backend/<dosya>      tek bir test dosyasindaki testler
    sayim: arayuz               tum arayuz testleri
    sayim: uc                   API uc noktasi sayisi
    sayim: tarihsel             gecmise dair anlati, kontrol edilmez

Bir satirda birden fazla sayi varsa isaretler virgulle sirayla yazilir:

    Backend 125 test, arayüz 95 test. <!-- sayim: backend, arayuz -->

Isaret bir sonraki satirda da olabilir. Mermaid ve kod bloklarinda yorum
kendi satirinda durmak zorunda:

    subgraph api["FastAPI — 22 uç"]
        %% sayim: uc

**Isaretsiz bir sayi iddiasi da hatadir.** Yeni yazilan "42 test"
cumlesi, isaretlenmedigi surece burada yakalanir; boylece denetim
kendisi eskimez.

Kullanim
--------
    python scripts/dokuman_denetimi.py
    python scripts/dokuman_denetimi.py --atla arayuz      # node yoksa
    python scripts/dokuman_denetimi.py --atla backend

`--atla` bilincli bir tercihtir ve raporda yaziyor. Olcum
yapilamadiginda betik *sessizce gecmez*, durur - CI'da sessiz atlama bu
projeyi bir kez zaten yanilltti (bkz. .github/workflows/ci.yml).
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[1]

# Depoda olmayan, bilincli olarak disarida tutulan dosyalar. Yerelde
# duruyorlar ama CI'da yoklar; taranirlarsa denetim iki ortamda farkli
# sonuc verirdi.
DEPO_DISI = {"N-Emek-Plani.md"}


# Taranan dosyalar: kok dizindeki Markdown, docs/ altindaki Markdown ve
# CI is akisi (adim adlarinda da test sayisi yaziyor).
def taranan_dosyalar() -> list[Path]:
    dosyalar = [p for p in sorted(ROOT.glob("*.md")) if p.name not in DEPO_DISI]
    dosyalar += sorted((ROOT / "docs").glob("*.md"))
    # Teknik raporun kaynak metni. Jurinin okuyacagi tek belge burasi;
    # sayilarin dogrulanmadigi tek yer olmasi anlamsiz olurdu.
    dosyalar += sorted((ROOT / "docs" / "RAPOR").glob("*.md"))
    akis = ROOT / ".github" / "workflows" / "ci.yml"
    if akis.exists():
        dosyalar.append(akis)
    return dosyalar


# Sayi + "test"/"uc" kalibi. `test\w*` "testi", "testler" gibi ekleri de
# yakalar. `uc` icin kelime siniri sart: "uctan uca" bir sayim degil.
#
# Ondeki `(?<![\w.])`: "CC0 test görselleri" ve "6.400 test" gibi
# dizilerde sayinin ortasindan yakalamayi engelliyor.
IDDIA = re.compile(r"(?<![\w.])(\d+)\s+(test\w*|uç)\b", re.IGNORECASE)
# `sayim: a, b` -> ["a", "b"]. Bir satirda birden fazla sayi olabiliyor
# (ornegin "125 test ... 95 test"); isaretler sirayla eslesiyor.
ISARET = re.compile(r"sayim:\s*([\w./,\s-]+?)\s*(?:-->|#|$)")


def isaret_listesi(satir: str) -> list[str]:
    eslesme = ISARET.search(satir)
    if not eslesme:
        return []
    return [ad.strip() for ad in eslesme.group(1).split(",") if ad.strip()]


# ---------------------------------------------------------------------------
# Olcum
# ---------------------------------------------------------------------------
def uc_sayisi() -> int:
    """routes.py icindeki `@router.<metod>` bezeyicileri.

    Metin sayimi; uygulamayi ice aktarmayi gerektirmiyor, dolayisiyla
    backend bagimliliklari kurulu olmadan da calisiyor.
    """
    kaynak = (ROOT / "backend" / "app" / "api" / "routes.py").read_text(encoding="utf-8")
    return len(re.findall(r"^@router\.", kaynak, re.MULTILINE))


def _pytest_toplar(*ek_args: str) -> dict[str, int]:
    """`pytest --collect-only -q` ciktisindan dosya bazinda test sayisi.

    Cikti satirlari `tests/test_x.py: 65` bicimindedir. Toplam da
    burada hesaplaniyor; pytest'in ozet satirini ayrica ayristirmaya
    gerek yok.
    """
    sonuc = subprocess.run(
        [sys.executable, "-m", "pytest", "--collect-only", "-q", *ek_args],
        cwd=ROOT / "backend",
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if sonuc.returncode != 0:
        raise RuntimeError(
            "pytest --collect-only başarısız oldu:\n" + (sonuc.stdout + sonuc.stderr)[-2000:]
        )

    sayilar: dict[str, int] = {}
    for satir in sonuc.stdout.splitlines():
        eslesme = re.match(r"^(tests[/\\][\w.]+\.py):\s*(\d+)\s*$", satir.strip())
        if eslesme:
            dosya = eslesme.group(1).replace("\\", "/").split("/")[-1]
            sayilar[dosya] = int(eslesme.group(2))
    if not sayilar:
        raise RuntimeError("pytest çıktısından test sayısı okunamadı.")
    sayilar["__toplam__"] = sum(sayilar.values())
    return sayilar


def backend_sayilari() -> tuple[dict[str, int], int]:
    """Doner: (dosya bazinda tum testler, `slow` haric toplam).

    CI yalnizca hizli testleri kosuyor ve adim adinda o sayi yaziyor;
    dokuman toplamiyla ayni degil. Ikisi ayri olculuyor ki hangisinin
    kaydigi belli olsun.
    """
    hepsi = _pytest_toplar()
    hizli = _pytest_toplar("-m", "not slow")
    return hepsi, hizli["__toplam__"]


def arayuz_sayisi() -> int:
    """`vitest run --reporter=json` ciktisindan toplam test sayisi.

    Testler statik olarak sayilamiyor: `it.each` tek satirdan birden
    fazla test uretiyor. Kosucuya sormak tek dogru yol.
    """
    sonuc = subprocess.run(
        ["npx", "--no-install", "vitest", "run", "--reporter=json"],
        cwd=ROOT / "frontend",
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        shell=sys.platform == "win32",
    )
    # JSON, gunlugun icine gomulu gelebiliyor; ilk `{` ile son `}` arasi.
    bas = sonuc.stdout.find("{")
    son = sonuc.stdout.rfind("}")
    if bas < 0 or son < bas:
        raise RuntimeError(
            "vitest JSON çıktısı okunamadı:\n" + (sonuc.stdout + sonuc.stderr)[-2000:]
        )
    rapor = json.loads(sonuc.stdout[bas : son + 1])
    toplam = rapor.get("numTotalTests")
    if not isinstance(toplam, int):
        raise RuntimeError("vitest raporunda numTotalTests yok.")
    return toplam


# ---------------------------------------------------------------------------
# Tarama
# ---------------------------------------------------------------------------
class Bulgu:
    def __init__(self, dosya: Path, satir_no: int, mesaj: str, metin: str):
        self.dosya = dosya
        self.satir_no = satir_no
        self.mesaj = mesaj
        self.metin = metin

    def __str__(self) -> str:
        yol = self.dosya.relative_to(ROOT).as_posix()
        return f"{yol}:{self.satir_no}: {self.mesaj}\n    {self.metin.strip()}"


def denetle(gercek: dict[str, int | None]) -> tuple[list[Bulgu], int, int]:
    """Dokumanlari tarar. Doner: (bulgular, dogrulanan, atlanan)."""
    bulgular: list[Bulgu] = []
    dogrulanan = 0
    atlanan = 0

    for dosya in taranan_dosyalar():
        satirlar = dosya.read_text(encoding="utf-8").splitlines()
        for indis, satir in enumerate(satirlar):
            satir_no = indis + 1
            iddialar = IDDIA.findall(satir)
            if not iddialar:
                continue

            # Isaretler iddialarla *sirayla* eslesiyor: bir satirda iki
            # sayi varsa isaret de iki tane olmali.
            #
            # Isaret bir sonraki satirda da olabilir: mermaid ve kod
            # bloklarinda yorum kendi satirinda durmak zorunda
            # (`%% sayim: uc`), satir sonuna eklenemiyor.
            isaretler = isaret_listesi(satir)
            if not isaretler and indis + 1 < len(satirlar):
                sonraki = satirlar[indis + 1]
                if not IDDIA.search(sonraki):
                    isaretler = isaret_listesi(sonraki)
            if len(isaretler) < len(iddialar):
                bulgular.append(
                    Bulgu(
                        dosya,
                        satir_no,
                        f"{len(iddialar)} sayı iddiası var, {len(isaretler)} işaret — "
                        "satır sonuna `<!-- sayim: backend|backend-hizli|arayuz|uc|"
                        "tarihsel -->` ekleyin",
                        satir,
                    )
                )
                continue

            for (yazan_metin, _), ad in zip(iddialar, isaretler):
                if ad == "tarihsel":
                    continue

                beklenen = gercek.get(ad, "BILINMIYOR")
                if beklenen == "BILINMIYOR":
                    bulgular.append(
                        Bulgu(dosya, satir_no, f"tanınmayan işaret: sayim: {ad}", satir)
                    )
                    continue
                if beklenen is None:
                    atlanan += 1
                    continue

                yazan = int(yazan_metin)
                if yazan != beklenen:
                    bulgular.append(
                        Bulgu(
                            dosya,
                            satir_no,
                            f"{ad}: dokümanda {yazan}, gerçekte {beklenen}",
                            satir,
                        )
                    )
                else:
                    dogrulanan += 1

    return bulgular, dogrulanan, atlanan


# ---------------------------------------------------------------------------
def main() -> int:
    ayristirici = argparse.ArgumentParser(description=__doc__)
    ayristirici.add_argument(
        "--atla",
        default="",
        help="Ölçülmeyecek gruplar, virgülle: backend, arayuz",
    )
    args = ayristirici.parse_args()
    atlananlar = {a.strip() for a in args.atla.split(",") if a.strip()}

    bilinmeyen = atlananlar - {"backend", "arayuz"}
    if bilinmeyen:
        print(f"Atlanamayan grup: {', '.join(sorted(bilinmeyen))}")
        return 2

    # `uc` her zaman ölçülüyor: metin sayımı, hiçbir bağımlılık istemiyor.
    gercek: dict[str, int | None] = {"uc": uc_sayisi()}
    print(f"ölçüldü · uc = {gercek['uc']}")

    if "backend" in atlananlar:
        gercek["backend"] = None
        gercek["backend-hizli"] = None
        print("atlandı  · backend (--atla)")
    else:
        try:
            sayilar, hizli = backend_sayilari()
        except (RuntimeError, OSError) as hata:
            print(f"backend ölçülemedi: {hata}")
            return 2
        gercek["backend"] = sayilar["__toplam__"]
        gercek["backend-hizli"] = hizli
        for dosya, adet in sayilar.items():
            if dosya != "__toplam__":
                gercek[f"backend/{dosya}"] = adet
        print(f"ölçüldü · backend = {gercek['backend']} (hızlı: {hizli})")

    if "arayuz" in atlananlar:
        gercek["arayuz"] = None
        print("atlandı  · arayuz (--atla)")
    else:
        try:
            gercek["arayuz"] = arayuz_sayisi()
        except (RuntimeError, OSError, json.JSONDecodeError) as hata:
            print(f"arayüz ölçülemedi: {hata}")
            return 2
        print(f"ölçüldü · arayuz = {gercek['arayuz']}")

    # Atlanan grubun alt dosya işaretleri de atlanmış sayılır.
    if gercek.get("backend") is None:
        for dosya in (ROOT / "backend" / "tests").glob("test_*.py"):
            gercek[f"backend/{dosya.name}"] = None

    bulgular, dogrulanan, atlanan = denetle(gercek)

    print()
    if bulgular:
        print(f"{len(bulgular)} uyuşmazlık:\n")
        for bulgu in bulgular:
            print(bulgu)
            print()
        return 1

    ek = f", {atlanan} atlandı" if atlanan else ""
    print(f"Tutarlı: {dogrulanan} iddia doğrulandı{ek}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
