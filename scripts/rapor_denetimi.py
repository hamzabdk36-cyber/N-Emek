"""Uretilen teknik raporu teslim edilebilir mi diye denetler.

Neden var
---------
Sartname tek cumlede ozetliyor: "sablona uymayan, eksik veya gec
yuklenen raporlar degerlendirmeye alinmaz ve ilgili takimlar
yarismadan elenir." Bicim hatasinin bedeli puan kaybi degil, eleme.

Bu betik gozle yakalanmasi zor olan seyleri sayiyla yakalar: silinmesi
gereken sayfanin kalmasi, kaynakcada karsiligi olmayan bir atif,
doldurulmayi bekleyen bir yer tutucu, gövdeye sizmis Calibri.

Sayfa sayisi burada **olculmuyor** - onu ancak Word cizerek bilir
(`scripts/rapor_word.ps1`).

Denetimler
----------
1. Sablonun sekiz ana basligi, sirasiyla ve birebir metinle duruyor mu
2. "PUANLAMA VE DEĞERLENDİRME ESASLARI" bolumu silinmis mi
3. Bos kalan baslik var mi
4. Metin ici `[n]` atiflari kaynakcayla eslesiyor mu - iki yonlu
5. Govdede Arial disi yazi tipi ya da beklenmeyen punto var mi
6. Yer tutucu (`___`) kalmis mi
7. Isaretsiz sayisal iddia var mi (`dokuman_denetimi.py` kurali)

Kullanim
--------
    .venv/Scripts/python.exe scripts/rapor_denetimi.py
    .venv/Scripts/python.exe scripts/rapor_denetimi.py --taslak

`--taslak` yazim surerken kullanilir: bos bolum ve yer tutucu uyari
olarak yazilir, hata sayilmaz. Teslim oncesi **bayraksiz** kosulur.
"""

from __future__ import annotations

import argparse
import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[1]
KAYNAK_DIZIN = ROOT / "docs" / "RAPOR"
BELGE = KAYNAK_DIZIN / "N-Emek-Teknik-Rapor.docx"
KAYNAKCA_DOSYASI = KAYNAK_DIZIN / "09-kaynakca.md"

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"

ANA_BASLIKLAR = [
    "PROJE ÖZETİ",
    "KATMA DEĞER VE YENİLİKÇİLİK",
    "TEKNOLOJİ KULLANIMI",
    "UYGULANABİLİRLİK",
    "YAYGIN ETKİ",
    "SÜRDÜRÜLEBİLİRLİK",
    "PROJE TAKVİMİ",
    "TAKIM YAPISI",
    "KAYNAKÇA",
]

ALT_BASLIKLAR = [
    "1.1. Proje Konusu ve amacı",
    "1.2. Proje Kapsamı ve Yöntemi",
    "2.1. Problem Tanımı ve Mevcut Çözümler",
    "2.2. Çözüm Fikri, Özgünlük ve Yerlilik",
    "3.1. İzlenecek Yöntem, altyapı ve Sürüm Kontrolü",
    "3.2. Model ve Veri Doğrulama",
    "3.3. Kullanıcı Deneyimi (UI/UX) Tasarımı",
    "4.1. Verimlilik ve Etkinlik",
    "4.2. Hedef Kitle",
    "4.3. Teknolojik Yenilik ve Uygulanabilirlik",
    "5.1. Toplumsal Fayda ve Erişim Potansiyeli",
    "6.1. Ticarileştirme Potansiyeli ve İş Modeli",
    "6.2. Finansal, Teknik ve Sosyal Sürdürülebilirlik",
    "7.1. İş Paketleri ve Zamanlama",
    "8.1. Takım Organizasyonu ve Roller",
]

YASAK_METIN = "PUANLAMA VE DEĞERLENDİRME ESASLARI"

# Govdede kabul edilen yazi tipleri. "Arial Black" basliklarin,
# "Consolas" kod parcalarinin; ikisi de bilincli.
IZINLI_YAZI_TIPI = {"Arial", "Arial Black", "Consolas"}
# Yarim punto cinsinden: 24 = 12 pt govde, 28 = 14 pt baslik,
# 20 = 10 pt tablo ve altyazi, 21 = 10,5 pt satir ici kod.
IZINLI_PUNTO = {20, 21, 24, 28}

# `[3]`, `[4,7]`, `[5-11]` - ama `[metin](bag)` degil.
ATIF = re.compile(r"\[(\d+(?:\s*[,\-–]\s*\d+)*)\]")
KAYNAK_SATIRI = re.compile(r"^\[(\d+)\]\s+(.+)$")

# Sayi iddiasi kalibi ve isaret ayristirmasi `dokuman_denetimi.py`'den
# **ice aktariliyor**, kopyalanmiyor. Ilk yazimda kopyalanmisti ve iki
# kural hemen ayristi: oradaki "isaret bir sonraki satirda da olabilir"
# istisnasi burada yoktu, dolayisiyla denetim gecerli bir isareti hata
# sandi. Tek kaynak olmasi gerekiyor.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from dokuman_denetimi import IDDIA, isaret_listesi  # noqa: E402


class Sonuc:
    def __init__(self) -> None:
        self.hatalar: list[str] = []
        self.uyarilar: list[str] = []
        self.notlar: list[str] = []

    def hata(self, mesaj: str) -> None:
        self.hatalar.append(mesaj)

    def uyari(self, mesaj: str) -> None:
        self.uyarilar.append(mesaj)

    def notu(self, mesaj: str) -> None:
        self.notlar.append(mesaj)


# ---------------------------------------------------------------------------
# Belgeyi okuma
# ---------------------------------------------------------------------------
def paragraflari_oku(yol: Path) -> list[tuple[str, str]]:
    """Doner: (stil, metin) listesi. Tablo hucreleri dahil, kapak haric.

    Kapak bir metin kutusu; sablonun tasarimi ve elle dolduruluyor.
    Govde denetimlerine karistirilmasi, her kosuda kapagi "sablon
    yonergesi kalmis" diye isaretlerdi.
    """
    with zipfile.ZipFile(yol) as arsiv:
        kok = ET.fromstring(arsiv.read("word/document.xml"))

    cikti: list[tuple[str, str]] = []

    def gez(dugum) -> None:
        for cocuk in dugum:
            if cocuk.tag in ATLANAN_ALT_AGAC:
                continue
            if cocuk.tag == W + "p":
                metin = "".join(t.text or "" for t in cocuk.iter(W + "t")).strip()
                ppr = cocuk.find(W + "pPr")
                stil = ""
                if ppr is not None:
                    s = ppr.find(W + "pStyle")
                    if s is not None:
                        stil = s.get(W + "val") or ""
                cikti.append((stil, metin))
            gez(cocuk)

    gez(kok.find(W + "body"))
    return cikti


# Denetim disi birakilan iki alt agac:
#
# Kapak bir metin kutusu ve sablonun kendi tasarimi (20 pt baslik,
# 11 pt alan adlari); ona dokunmuyoruz, dolayisiyla bicim denetimine de
# sokmuyoruz - yoksa denetim her kosuda kendi sablonunu sikayet ederdi.
#
# Icindekiler (`w:sdt`) Word'un urettigi bir alan: baslik ve girdiler
# 11 punto, kendi ic stiliyle. Bunlari "beklenmeyen punto" saymak,
# denetimi Word'un cikti bicimiyle kavga ettirirdi.
ATLANAN_ALT_AGAC = {
    "{http://schemas.openxmlformats.org/markup-compatibility/2006}AlternateContent",
    W + "drawing",
    W + "pict",
    W + "sdt",
}


def yazi_tiplerini_oku(yol: Path) -> tuple[dict[str, int], dict[int, int]]:
    with zipfile.ZipFile(yol) as arsiv:
        kok = ET.fromstring(arsiv.read("word/document.xml"))

    tipler: dict[str, int] = {}
    puntolar: dict[int, int] = {}

    def gez(dugum) -> None:
        for cocuk in dugum:
            if cocuk.tag in ATLANAN_ALT_AGAC:
                continue
            if cocuk.tag == W + "r":
                metin = "".join(t.text or "" for t in cocuk.iter(W + "t"))
                rpr = cocuk.find(W + "rPr")
                if metin.strip() and rpr is not None:
                    fonts = rpr.find(W + "rFonts")
                    if fonts is not None and fonts.get(W + "ascii"):
                        ad = fonts.get(W + "ascii")
                        tipler[ad] = tipler.get(ad, 0) + 1
                    sz = rpr.find(W + "sz")
                    if sz is not None and sz.get(W + "val"):
                        deger = int(sz.get(W + "val"))
                        puntolar[deger] = puntolar.get(deger, 0) + 1
            gez(cocuk)

    gez(kok.find(W + "body"))
    return tipler, puntolar


# ---------------------------------------------------------------------------
# Denetimler
# ---------------------------------------------------------------------------
def basliklari_denetle(paragraflar: list[tuple[str, str]], sonuc: Sonuc) -> None:
    metinler = [m for _, m in paragraflar]

    sira = 0
    for baslik in ANA_BASLIKLAR:
        try:
            sira = metinler.index(baslik, sira) + 1
        except ValueError:
            sonuc.hata(f"ana başlık eksik ya da sırası bozuk: {baslik}")
            return

    eksik = [b for b in ALT_BASLIKLAR if b not in metinler]
    for b in eksik:
        sonuc.hata(f"alt başlık eksik: {b}")

    if any(m.startswith(YASAK_METIN) for m in metinler):
        sonuc.hata(
            f"'{YASAK_METIN}' bölümü belgede duruyor — şablon bu sayfaların "
            "rapora konmamasını istiyor"
        )


def kendi_sayfasi_denetle(yol: Path, sonuc: Sonuc) -> None:
    """Kaynakca kendi sayfasinda basliyor mu.

    Sablonun format notu: "Kapak, Icindekiler ve Kaynakca icin 3 ayri
    sayfa ayrilmalidir." Kapak ve icindekiler sablonun kendi sayfa
    sonlariyla ayrilmis durumda; kaynakca ise govdenin devami olarak
    akiyor ve tedbir alinmazsa takim bolumuyle ayni sayfayi paylasiyor.
    """
    with zipfile.ZipFile(yol) as arsiv:
        kok = ET.fromstring(arsiv.read("word/document.xml"))
    for p in kok.iter(W + "p"):
        if "".join(t.text or "" for t in p.iter(W + "t")).strip() != "KAYNAKÇA":
            continue
        ppr = p.find(W + "pPr")
        if ppr is not None and ppr.find(W + "pageBreakBefore") is not None:
            sonuc.notu("kaynakça kendi sayfasında başlıyor")
            return
    sonuc.hata(
        "KAYNAKÇA başlığında sayfa sonu yok — şablon kapak, içindekiler ve "
        "kaynakça için ayrı sayfa istiyor"
    )


def bos_bolumleri_denetle(paragraflar: list[tuple[str, str]], sonuc: Sonuc, taslak: bool) -> None:
    """Bir baslikla bir sonraki arasinda hic metin yoksa bolum bos demektir."""
    capalar = set(ANA_BASLIKLAR) | set(ALT_BASLIKLAR)
    konumlar = [i for i, (_, m) in enumerate(paragraflar) if m in capalar]

    for sira, indis in enumerate(konumlar):
        ad = paragraflar[indis][1]
        if ad in ANA_BASLIKLAR and ad != "KAYNAKÇA":
            continue  # ana basliklarin kendi govdesi olmayabilir
        son = konumlar[sira + 1] if sira + 1 < len(konumlar) else len(paragraflar)
        govde = [m for _, m in paragraflar[indis + 1 : son] if m]
        if not govde:
            (sonuc.uyari if taslak else sonuc.hata)(f"bölüm boş: {ad}")


def yonergeleri_denetle(paragraflar: list[tuple[str, str]], sonuc: Sonuc, taslak: bool) -> None:
    """Sablonun kendi aciklamalari belgede kalmis mi.

    Sablondaki her alt basligin altinda, o bolumde ne anlatilacagini
    soyleyen bir yonerge paragrafi var. Bunlar juriye degil yazana
    yazilmis. Bos kalan bir bolum, "bos" gorunmez - sablonun metniyle
    dolu gorunur, ve dikkatsiz bir teslimde jurinin okuyacagi sey
    sablonun kendi talimati olur.

    Yonerge listesi sablondan okunuyor; sablon guncellenirse denetim
    kendiliginden guncelleniyor.
    """
    sablon = ROOT / "docs" / "NSosyal_Inovasyon_2026_-_Proje_Teknik_Raporu_1_u6IVb.docx"
    if not sablon.exists():
        sonuc.uyari("şablon bulunamadı; yönerge denetimi atlandı")
        return

    capalar = set(ANA_BASLIKLAR) | set(ALT_BASLIKLAR)
    yonergeler = set()
    for _, metin in paragraflari_oku(sablon):
        if not metin or metin in capalar or metin.startswith(YASAK_METIN):
            continue
        if len(metin) > 60:  # kisa parcalar (baslik kirintilari) sayilmaz
            yonergeler.add(metin)

    # Kapak ve icindekiler denetim disinda: kapak sablonun tasarimi,
    # icindekiler bir Word alani. Yonerge aramasi ilk ana basliktan
    # sonra basliyor.
    metinler = [m for _, m in paragraflar]
    try:
        bas = metinler.index(ANA_BASLIKLAR[0])
    except ValueError:
        bas = 0
    kalanlar = [m for m in metinler[bas:] if m in yonergeler]
    for metin in kalanlar:
        (sonuc.uyari if taslak else sonuc.hata)(
            "şablon yönergesi belgede duruyor: " + metin[:70] + "…"
        )
    if not kalanlar:
        sonuc.notu("şablon yönergelerinin tamamı içerikle değişmiş")


def kaynakcayi_denetle(sonuc: Sonuc, taslak: bool) -> None:
    if not KAYNAKCA_DOSYASI.exists():
        (sonuc.uyari if taslak else sonuc.hata)(f"kaynakça dosyası yok: {KAYNAKCA_DOSYASI.name}")
        return

    kaynaklar: dict[int, str] = {}
    for satir in KAYNAKCA_DOSYASI.read_text(encoding="utf-8").splitlines():
        eslesme = KAYNAK_SATIRI.match(satir.strip())
        if eslesme:
            kaynaklar[int(eslesme.group(1))] = eslesme.group(2)

    if not kaynaklar:
        (sonuc.uyari if taslak else sonuc.hata)(
            "kaynakçada `[n] ...` biçiminde kayıt bulunamadı"
        )
        return

    beklenen = set(range(1, max(kaynaklar) + 1))
    bosluk = sorted(beklenen - set(kaynaklar))
    if bosluk:
        sonuc.hata(f"kaynakça numaraları atlamalı: {bosluk} yok")

    anilan: set[int] = set()
    for dosya in sorted(KAYNAK_DIZIN.glob("*.md")):
        if dosya.name.startswith("_") or dosya == KAYNAKCA_DOSYASI:
            continue
        metin = dosya.read_text(encoding="utf-8")
        for satir_no, satir in enumerate(metin.splitlines(), 1):
            for grup in ATIF.findall(satir):
                for parca in re.split(r"\s*,\s*", grup):
                    aralik = re.match(r"^(\d+)\s*[-–]\s*(\d+)$", parca)
                    numaralar = (
                        range(int(aralik.group(1)), int(aralik.group(2)) + 1)
                        if aralik
                        else [int(parca)]
                    )
                    for n in numaralar:
                        anilan.add(n)
                        if n not in kaynaklar:
                            sonuc.hata(
                                f"{dosya.name}:{satir_no}: [{n}] atfının kaynakçada "
                                "karşılığı yok"
                            )

    hic_anilmayan = sorted(set(kaynaklar) - anilan)
    if hic_anilmayan:
        (sonuc.uyari if taslak else sonuc.hata)(
            "kaynakçada olup metinde hiç anılmayan kaynak: "
            + ", ".join(f"[{n}]" for n in hic_anilmayan)
        )

    sonuc.notu(f"kaynakça: {len(kaynaklar)} kayıt, {len(anilan)} tanesi metinde anılıyor")


def bicimi_denetle(yol: Path, sonuc: Sonuc) -> None:
    tipler, puntolar = yazi_tiplerini_oku(yol)
    yabanci = {ad: adet for ad, adet in tipler.items() if ad not in IZINLI_YAZI_TIPI}
    if yabanci:
        sonuc.hata(
            "gövdede izinsiz yazı tipi: "
            + ", ".join(f"{ad} ({adet} çalıştırma)" for ad, adet in sorted(yabanci.items()))
        )
    yabanci_punto = {p: adet for p, adet in puntolar.items() if p not in IZINLI_PUNTO}
    if yabanci_punto:
        sonuc.hata(
            "beklenmeyen punto: "
            + ", ".join(f"{p / 2:g} pt ({adet})" for p, adet in sorted(yabanci_punto.items()))
        )

    with zipfile.ZipFile(yol) as arsiv:
        kok = ET.fromstring(arsiv.read("word/document.xml"))
    kenar = kok.find(f"{W}body/{W}sectPr/{W}pgMar")
    if kenar is not None:
        # 2,5 cm = 1417 twip. Sablon dogru geliyor ama biri Word'de
        # elle degistirirse burada gorulur.
        for yon in ("top", "bottom", "left", "right"):
            deger = int(kenar.get(W + yon, "0"))
            if abs(deger - 1417) > 20:
                sonuc.hata(f"kenar boşluğu {yon}: {deger / 567:.2f} cm (olması gereken 2,50)")


def yer_tutuculari_denetle(sonuc: Sonuc, taslak: bool) -> None:
    toplam = 0
    for dosya in sorted(KAYNAK_DIZIN.glob("*.md")):
        if dosya.name.startswith("_"):
            continue
        for satir_no, satir in enumerate(dosya.read_text(encoding="utf-8").splitlines(), 1):
            if "___" in satir:
                toplam += 1
                (sonuc.uyari if taslak else sonuc.hata)(
                    f"{dosya.name}:{satir_no}: doldurulmamış yer tutucu"
                )
    if toplam == 0:
        sonuc.notu("yer tutucu kalmamış")


def iddialari_denetle(sonuc: Sonuc) -> None:
    """Rapordaki sayisal iddialar isaretli mi - ve olculuyor mu.

    Bu betik yalnizca *isaretin varligini* soyleyebilir; sayinin dogru
    olup olmadigini `dokuman_denetimi.py` olcuyor ve `docs/RAPOR/`
    altini o da tariyor. Burada iki kez sayi olcmek, iki farkli dogru
    uretme riski demekti.
    """
    isaretli = 0
    for dosya in sorted(KAYNAK_DIZIN.glob("*.md")):
        if dosya.name.startswith("_"):
            continue
        satirlar = dosya.read_text(encoding="utf-8").splitlines()
        for indis, satir in enumerate(satirlar):
            iddialar = IDDIA.findall(satir)
            if not iddialar:
                continue
            isaretler = isaret_listesi(satir)
            if not isaretler and indis + 1 < len(satirlar):
                sonraki = satirlar[indis + 1]
                if not IDDIA.search(sonraki):
                    isaretler = isaret_listesi(sonraki)
            adet = len(isaretler)
            if adet < len(iddialar):
                sonuc.hata(
                    f"{dosya.name}:{indis + 1}: işaretsiz sayı iddiası — "
                    "satır sonuna `<!-- sayim: ... -->` ekleyin\n    " + satir.strip()
                )
            else:
                isaretli += adet
    if isaretli:
        sonuc.notu(
            f"{isaretli} sayı iddiası işaretli — değerleri `dokuman_denetimi.py` ölçüyor"
        )


# ---------------------------------------------------------------------------
def main() -> int:
    ayristirici = argparse.ArgumentParser(description=__doc__)
    ayristirici.add_argument(
        "--taslak",
        action="store_true",
        help="Yazım sürerken: boş bölüm ve yer tutucu uyarı sayılır",
    )
    ayristirici.add_argument("--belge", type=Path, default=BELGE)
    args = ayristirici.parse_args()

    if not args.belge.exists():
        print(f"belge yok: {args.belge}")
        print("  önce: .venv/Scripts/python.exe scripts/rapor_docx.py")
        return 2

    sonuc = Sonuc()
    paragraflar = paragraflari_oku(args.belge)
    sonuc.notu(f"belge: {len(paragraflar)} paragraf")

    basliklari_denetle(paragraflar, sonuc)
    kendi_sayfasi_denetle(args.belge, sonuc)
    bos_bolumleri_denetle(paragraflar, sonuc, args.taslak)
    yonergeleri_denetle(paragraflar, sonuc, args.taslak)
    kaynakcayi_denetle(sonuc, args.taslak)
    bicimi_denetle(args.belge, sonuc)
    yer_tutuculari_denetle(sonuc, args.taslak)
    iddialari_denetle(sonuc)

    for mesaj in sonuc.notlar:
        print(f"·  {mesaj}")
    if sonuc.uyarilar:
        print()
        for mesaj in sonuc.uyarilar:
            print(f"uyarı: {mesaj}")
    if sonuc.hatalar:
        print()
        for mesaj in sonuc.hatalar:
            print(f"HATA : {mesaj}")
        print(f"\n{len(sonuc.hatalar)} hata — rapor teslim edilebilir durumda değil.")
        return 1

    print("\nDenetim temiz." + (" (taslak kipi)" if args.taslak else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
