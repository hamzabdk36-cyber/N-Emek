"""Teknik raporu resmi sablonun kopyasina enjekte eder.

Neden var
---------
Sartname acik: "sablona uymayan, eksik veya gec yuklenen raporlar
degerlendirmeye alinmaz." Bicim bir tercih degil, eleme kriteri.

Ayni zamanda rapordaki her sayinin kaynagi olculmus bir dokuman
(`DEGERLENDIRME.md`, `GECIKME.md`, `IS-MODELI.md`). Olcum degisirse rapor
da degismeli. Word'de elle bicimlendirilmis bir dosyada bu bag ilk
duzeltmede kopar - kimse 27 sayfayi yeniden bicimlendirmek istemez.

Bu yuzden icerik `docs/RAPOR/*.md` altinda yasiyor ve `.docx`
*uretiliyor*. Sablonun kendisi hic elle acilmiyor; kopyasi uzerinde
calisiliyor.

Nasil calisiyor
---------------
Sablonun govdesi duz: 163 paragraf, ic ice yapi yok. Betik iki tur
"capa" tanir:

    Balk1 stilli baslik        ->  "PROJE OZETI", "KAYNAKCA"
    `N.N.` ile baslayan satir  ->  "1.1. Proje Konusu ve amaci"

Her capadan sonraki sablon aciklamalari (jurinin degil, yazanin okumasi
icin konmus yonergeler) silinir, yerine ilgili Markdown dosyasinin o
basligin altindaki bolumu gelir.

`docs/RAPOR/*.md` icindeki `## <baslik>` satirlari capa adlariyla
**birebir** eslesmek zorunda. Eslesmezse betik durur: sessizce yanlis
yere yazmaktansa durmasi iyi.

Sonda, "PUANLAMA VE DEGERLENDIRME ESASLARI" bolumu ve format notu
tablosu silinir - ikisi de "Bu sayfaya raporlarda yer verilmeyecektir"
diyor.

Bicim
-----
Sablonun yazili kurali: Arial 12 pt, baslik Arial Black 14 pt, satir
araligi 1,15, iki yana yasli, kenar bosluklari 2,5 cm.

Dosyanin kendi `docDefaults` degeri satir araligini 1,5 (line=360)
veriyor ve yaslamayi hic soylemiyor. Yazili kural kazaniyor: eklenen her
paragrafa `line=276` ve `jc=both` aciktan yaziliyor.

Desteklenen Markdown
--------------------
Paragraf · `###` alt alt baslik · `- ` madde · `1. ` numarali madde ·
`| a | b |` tablo · `![altyazi](yol.jpg)` gorsel · `> ` alinti ·
satir ici `**kalin**`, `*egik*`, `` `kod` `` · `<!-- yorum -->` atilir.

Kullanim
--------
    .venv/Scripts/python.exe scripts/rapor_docx.py
    .venv/Scripts/python.exe scripts/rapor_docx.py --cikti /tmp/deneme.docx

Onkosul: `pip install python-docx`.
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

try:
    import docx
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.oxml.ns import qn
    from docx.shared import Cm, Pt, RGBColor
    from PIL import Image
except ModuleNotFoundError as exc:  # pragma: no cover - kurulum yonlendirmesi
    print(f"eksik paket: {exc.name}")
    print("  .venv/Scripts/python.exe -m pip install python-docx")
    raise SystemExit(1)

ROOT = Path(__file__).resolve().parents[1]
SABLON = ROOT / "docs" / "NSosyal_Inovasyon_2026_-_Proje_Teknik_Raporu_1_u6IVb.docx"

# Kapak, sablonun kendi metin kutusu. Bu betik her kosumda sablonu bastan
# kopyaladigi icin (shutil.copy2), Word'de elle doldurulan bir kapak bir
# sonraki uretimde sessizce silinirdi - govdedeki yer tutucularla ayni
# tuzak. Bu yuzden kapak da tek kaynaktan, buradan doluyor.
KAPAK = {
    "Proje Adı:": "N-Emek — Açıklanabilir İçerik Atıf ve Adil Gelir Paylaşım Sistemi",
    "Takım Adı:": "ZENITH N",
    "Takım ID:": "1003461",
    "Başvuru ID:": "5382505",
    # Sablon uc temayi da yan yana yaziyor; yalnizca basvurulan tema kalir.
    "Tematik Alan:": "İçerik Ekonomisi",
}
KAYNAK_DIZIN = ROOT / "docs" / "RAPOR"
CIKTI = KAYNAK_DIZIN / "N-Emek-Teknik-Rapor.docx"

# Silinecek bolumun basladigi yer. Sablon bunu kendisi soyluyor:
# "(Bu sayfaya raporlarda yer verilmeyecektir.)"
KESME_BASLIGI = "PUANLAMA VE DEĞERLENDİRME ESASLARI"

# Sablonda "İÇİNDEKİLER" basliginin *icinde* bir yonerge duruyor:
# "(Raporun tüm ana başlıkları ve sayfa numaraları eksiksiz olarak
# listelenecektir.)". Bu juriye degil yazana soylenmis; baslikta kalirsa
# rapor kendi kullanim kilavuzunu basmis olur. Tek istisna bu, o yuzden
# genel bir "parantezi kirp" kurali yerine acik bir liste.
YONERGE_KIRP = ("İÇİNDEKİLER",)

# Sablonun format notu: "Kapak, Icindekiler ve Kaynakca icin 3 ayri
# sayfa ayrilmalidir." Kapak ve icindekiler zaten kendi sayfalarinda
# (sablonun sayfa sonlari), ama kaynakca gövdenin devami olarak
# akiyordu ve takim bolumuyle ayni sayfayi paylasiyordu. Baslik "onunde
# sayfa sonu" ile isaretleniyor - sabit bir sayfa sonu karakteri
# eklemek, metin kisalinca bos sayfa birakirdi.
KENDI_SAYFASINDA = ("KAYNAKÇA",)

GOVDE_PUNTO = Pt(12)
GOVDE_YAZI_TIPI = "Arial"
# Word satir araligini 240'ta bir olcuyor: 1,15 x 240 = 276.
SATIR_ARALIGI = 276
# 21 cm sayfa - 2 x 2,5 cm kenar = 16 cm kullanilabilir genislik.
# Gorseller bilerek tam genislikte degil: Word bir gorseli bolemiyor,
# sigmadiginda tumunu sonraki sayfaya atiyor ve geride yarim sayfalik
# bosluk birakiyor. Tam genislikteyken (15,5 cm) rapor 29 sayfaydi ve
# icerigin ~7 sayfasi bu bosluklardan olusuyordu; daraltmak icerikten
# hicbir sey goturmeden o sayfalari geri kazandi.
ICERIK_GENISLIGI = Cm(13.0)
# Bir gorsel ne kadar yuksek olursa olsun bunu asmaz. Dikey bir mobil
# ekran goruntusu (390x844) tam genislikte 33 cm oluyordu, yani tek
# basina bir sayfadan uzun.
EN_FAZLA_YUKSEKLIK = Cm(8.0)


# ---------------------------------------------------------------------------
# Sablon capalari
# ---------------------------------------------------------------------------
ALT_BASLIK = re.compile(r"^\d+\.\d+\.\s")


def paragraf_metni(p) -> str:
    return "".join(dugum.text or "" for dugum in p.iter(qn("w:t"))).strip()


def icindekiler_duzelt(belge) -> bool:
    """Icindekiler alanini dile bagimli olmaktan cikarir.

    Sablonun alan kodu `TOC \\h \\u \\z \\t "Heading 1,1,..."`. `\\t`
    switch'i stilleri **gorunen adiyla** toplar; belgedeki stilin adi
    ise yerellesmis: Turkce Word'de "Başlık 1". Sonuc, sablonun kendi
    icindekileri: "Hiçbir içindekiler tablosu ögesine rastlanmadi."

    `\\o "1-3"` anahat duzeyine bakar ve dilden bagimsizdir.
    """
    degisti = False
    for alan in belge.element.body.iter(qn("w:instrText")):
        if alan.text and "TOC" in alan.text and "\\t" in alan.text:
            alan.text = ' TOC \\h \\u \\z \\o "1-3" '
            degisti = True
    return degisti


def anahat_duzeyi(paragraf, duzey: int) -> None:
    """Paragrafi icindekilerde gorunur kilar.

    Numarali alt basliklar (`1.1.`) sablonda duz paragraf; anahat
    duzeyleri yok, dolayisiyla icindekilere hic girmiyorlar. Sablon
    "raporun tum ana basliklari ... eksiksiz" istiyor.
    """
    ppr = paragraf._p.get_or_add_pPr()
    mevcut = ppr.find(qn("w:outlineLvl"))
    if mevcut is None:
        mevcut = ppr.makeelement(qn("w:outlineLvl"), {})
        ppr.append(mevcut)
    mevcut.set(qn("w:val"), str(duzey))


def capa_mi(p) -> bool:
    """Bir paragraf, altina icerik yazilacak bir baslik mi?

    Iki tur: `Balk1` stilli ana basliklar ve `1.1.` ile baslayan alt
    basliklar. Bosluk paragraflarinin stili de `Balk1` olabiliyor
    (sablonun 80. ve 82. paragraflari boyle), o yuzden metin sarti var.
    """
    metin = paragraf_metni(p._p)
    if not metin:
        return False
    if ALT_BASLIK.match(metin):
        return True
    stil = p.style.name if p.style is not None else ""
    return stil in ("heading 1", "Heading 1", "Balk1")


# ---------------------------------------------------------------------------
# Markdown ayristirma
# ---------------------------------------------------------------------------
YORUM = re.compile(r"<!--.*?-->", re.DOTALL)


def bolumleri_oku(dizin: Path) -> dict[str, list[str]]:
    """`docs/RAPOR/*.md` -> {baslik: satirlar}.

    Ayni baslik iki dosyada gecerse durur: hangisinin kazandigi belli
    olmayan bir birlestirme, sessizce yarim rapor uretirdi.
    """
    bolumler: dict[str, list[str]] = {}
    nereden: dict[str, str] = {}

    for dosya in sorted(dizin.glob("*.md")):
        if dosya.name.startswith("_"):
            continue  # `_` ile baslayanlar not dosyasi, rapora girmez
        metin = YORUM.sub("", dosya.read_text(encoding="utf-8"))
        baslik: str | None = None
        for satir in metin.splitlines():
            if satir.startswith("## "):
                baslik = satir[3:].strip()
                if baslik in bolumler:
                    raise SystemExit(
                        f"'{baslik}' iki dosyada birden tanımlı: "
                        f"{nereden[baslik]} ve {dosya.name}"
                    )
                bolumler[baslik] = []
                nereden[baslik] = dosya.name
            elif baslik is not None:
                bolumler[baslik].append(satir)
    return bolumler


def bloklara_ayir(satirlar: list[str]) -> list[tuple[str, list[str]]]:
    """Satirlari ("paragraf"|"madde"|"tablo"|... , icerik) bloklarina boler."""
    bloklar: list[tuple[str, list[str]]] = []
    tampon: list[str] = []
    tur = "paragraf"

    def bosalt() -> None:
        nonlocal tampon, tur
        if tampon:
            bloklar.append((tur, tampon))
        tampon = []
        tur = "paragraf"

    for ham in satirlar:
        satir = ham.rstrip()
        if not satir.strip():
            bosalt()
            continue

        if satir.startswith("### "):
            bosalt()
            bloklar.append(("altbaslik", [satir[4:].strip()]))
            continue
        if satir.startswith("!["):
            bosalt()
            bloklar.append(("gorsel", [satir]))
            continue
        if satir.startswith("---"):
            bosalt()
            continue

        yeni = (
            "tablo" if satir.lstrip().startswith("|")
            else "alinti" if satir.startswith("> ")
            else "madde" if re.match(r"^\s*[-*]\s", satir)
            else "numarali" if re.match(r"^\s*\d+\.\s", satir)
            else "paragraf"
        )
        # Bir maddenin devami girintili yazilabiliyor; onu yeni blok
        # saymak listeyi ortasindan bolerdi.
        if tampon and tur in ("madde", "numarali") and yeni == "paragraf" and ham.startswith("  "):
            tampon[-1] += " " + satir.strip()
            continue
        if tampon and yeni != tur:
            bosalt()
        tur = yeni
        tampon.append(satir)

    bosalt()
    return bloklar


# ---------------------------------------------------------------------------
# Word'e yazma
# ---------------------------------------------------------------------------
BICIM = re.compile(r"(\*\*.+?\*\*|\*[^*]+?\*|`[^`]+?`)")


def metni_yaz(paragraf, metin: str) -> None:
    """Satir ici `**kalin**`, `*egik*` ve `` `kod` `` isaretlerini uygular."""
    for parca in BICIM.split(metin):
        if not parca:
            continue
        if parca.startswith("**") and parca.endswith("**"):
            paragraf.add_run(parca[2:-2]).bold = True
        elif parca.startswith("*") and parca.endswith("*"):
            paragraf.add_run(parca[1:-1]).italic = True
        elif parca.startswith("`") and parca.endswith("`"):
            calisma = paragraf.add_run(parca[1:-1])
            calisma.font.name = "Consolas"
            calisma.font.size = Pt(10.5)
        else:
            paragraf.add_run(parca)


def govde_bicimi(paragraf, *, yasla: bool = True) -> None:
    bicim = paragraf.paragraph_format
    bicim.space_after = Pt(6)
    bicim.space_before = Pt(0)
    if yasla:
        paragraf.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    # python-docx satir araligini punto olarak yaziyor; 1,15 "coklu"
    # deger olarak lazim, o yuzden dogrudan XML'e yaziliyor.
    ppr = paragraf._p.get_or_add_pPr()
    aralik = ppr.find(qn("w:spacing"))
    if aralik is None:
        aralik = ppr.makeelement(qn("w:spacing"), {})
        ppr.append(aralik)
    aralik.set(qn("w:line"), str(SATIR_ARALIGI))
    aralik.set(qn("w:lineRule"), "auto")
    for calisma in paragraf.runs:
        if calisma.font.name is None:
            calisma.font.name = GOVDE_YAZI_TIPI
        if calisma.font.size is None:
            calisma.font.size = GOVDE_PUNTO


# Metin alani: A4 genisligi 21 cm, sablonun kenar bosluklari 2,5 cm.
TABLO_GENISLIGI = Cm(16.0)
EN_DAR_SUTUN = 1.3      # cm - "Kod", "#" gibi sutunlar bunun altina inmez
EN_UZUN_SAYILAN = 60    # karakter - bunun ustu ayni agirlikta sayilir
# Arial 10 pt'de ortalama karakter genisligi ~0,19 cm; hucre yan bosluklari
# 2 x 80 twip. Kelimenin bolunmemesi icin gereken en dar genislik bundan cikiyor.
KARAKTER_CM = 0.20
HUCRE_BOSLUGU_CM = 0.30


def kenarlik_ver(tablo) -> None:
    """Disi koyu, ici acik gri cerceve + dar hucre bosluklari.

    Sablonda tablo stili tanimli degil; cizgiyi kendimiz koyuyoruz. Ic
    cizgiler dista kalanlardan acik: tablo bir izgara gibi degil, bir
    blok gibi okunuyor.
    """
    ozellik = tablo._tbl.tblPr
    kenarliklar = ozellik.makeelement(qn("w:tblBorders"), {})
    for yon, kalinlik, renk in (
        ("top", "6", "7E8894"),
        ("left", "6", "7E8894"),
        ("bottom", "6", "7E8894"),
        ("right", "6", "7E8894"),
        ("insideH", "4", "C6CDD5"),
        ("insideV", "4", "C6CDD5"),
    ):
        e = kenarliklar.makeelement(qn(f"w:{yon}"), {})
        e.set(qn("w:val"), "single")
        e.set(qn("w:sz"), kalinlik)
        e.set(qn("w:color"), renk)
        kenarliklar.append(e)
    ozellik.append(kenarliklar)

    # Varsayilan yan bosluk 0,19 cm; dar sutunlarda metnin yerini yiyor.
    bosluk = ozellik.makeelement(qn("w:tblCellMar"), {})
    for yon, deger in (("top", "40"), ("bottom", "40"), ("left", "80"), ("right", "80")):
        e = bosluk.makeelement(qn(f"w:{yon}"), {})
        e.set(qn("w:w"), deger)
        e.set(qn("w:type"), "dxa")
        bosluk.append(e)
    ozellik.append(bosluk)


def sutun_genislikleri(hucreler: list[list[str]], sutun: int) -> list[float]:
    """Sutun genisliklerini icerige gore dagitir (cm doner).

    Word'un varsayilani butun sutunlari esit genislikte yapiyor. Sonucu
    olculdu: "Kod" sutunu ("IP-1") ile "Alt faaliyetler" sutunu (150
    karakterlik metin) ayni genislikte kaliyor, uzun hucre sekiz satira
    sariyor ve tek satir bir sayfanin dortte birini yiyordu.

    Iki kural birlikte calisiyor:

    1. **Hicbir sutun en uzun kelimesinden dar olamaz.** Salt orantiyla
       dagitildiginda "Durum" sutunu 1,4 cm'e dusuyor ve "Tamamlandi"
       uc satira bolunuyordu ("Tama/mland/i") - bu da tasarrufu geri
       veriyor, cunku satiri o hucre uzatiyor.
    2. Artan genislik, icerik uzunluguna gore paylastirilir. Cok uzun
       hucreler bir tavanda kesiliyor; yoksa tek bir paragraf butun
       tabloyu ezerdi.
    """
    def en_uzun_kelime(j: int) -> int:
        kelimeler = [
            k for s in hucreler if j < len(s) for k in s[j].split() if k
        ]
        return max((len(k) for k in kelimeler), default=1)

    def en_uzun_hucre(j: int) -> int:
        return max((len(s[j]) for s in hucreler if j < len(s)), default=1)

    taban = [
        max(EN_DAR_SUTUN, en_uzun_kelime(j) * KARAKTER_CM + HUCRE_BOSLUGU_CM)
        for j in range(sutun)
    ]
    toplam = TABLO_GENISLIGI.cm

    # Tabanlar sigmiyorsa orantili kucult: kelime bolunecek ama tablo
    # sayfayi tasmayacak. Bu rapordaki tablolarda gerceklesmiyor.
    if sum(taban) >= toplam:
        return [toplam * t / sum(taban) for t in taban]

    agirlik = [min(max(en_uzun_hucre(j), 4), EN_UZUN_SAYILAN) for j in range(sutun)]
    artan = toplam - sum(taban)
    return [t + artan * a / sum(agirlik) for t, a in zip(taban, agirlik)]


def tablo_kur(belge, satirlar: list[str]):
    """Markdown tablosunu Word tablosuna cevirir."""
    hucreler = [
        [h.strip() for h in satir.strip().strip("|").split("|")]
        for satir in satirlar
        # `|---|---|` ayrac satiri veri degil
        if not re.fullmatch(r"\|[\s:|-]+\|", satir.strip())
    ]
    if not hucreler:
        raise ValueError("tablo boş")
    sutun = max(len(s) for s in hucreler)

    tablo = belge.add_table(rows=len(hucreler), cols=sutun)
    kenarlik_ver(tablo)

    # Sabit duzen sart: "autofit" acikken Word hesapladigimiz genislikleri
    # yok sayip yine kendi dagitimini uyguluyor.
    tablo.autofit = False
    duzen = tablo._tbl.tblPr.makeelement(qn("w:tblLayout"), {})
    duzen.set(qn("w:type"), "fixed")
    tablo._tbl.tblPr.append(duzen)

    genislikler = [Cm(g) for g in sutun_genislikleri(hucreler, sutun)]
    for izgara, genislik in zip(tablo._tbl.findall(qn("w:tblGrid"))[0], genislikler):
        izgara.set(qn("w:w"), str(int(genislik.twips)))

    for i, satir in enumerate(hucreler):
        # Satir sayfa ortasindan bolunmesin: onceki surumde bir is paketi
        # satiri iki sayfaya bolunuyor ve ust sayfada basliksiz birkac
        # kelime kaliyordu.
        ozellik = tablo.rows[i]._tr.get_or_add_trPr()
        ozellik.append(ozellik.makeelement(qn("w:cantSplit"), {}))
        if i == 0:
            # Baslik satiri her yeni sayfada tekrarlansin.
            ozellik.append(ozellik.makeelement(qn("w:tblHeader"), {}))

        for j in range(sutun):
            hucre = tablo.cell(i, j)
            hucre.width = genislikler[j]
            if i == 0:
                golge = hucre._tc.get_or_add_tcPr().makeelement(qn("w:shd"), {})
                golge.set(qn("w:val"), "clear")
                golge.set(qn("w:color"), "auto")
                golge.set(qn("w:fill"), "EEF2F6")
                hucre._tc.get_or_add_tcPr().append(golge)
            paragraf = hucre.paragraphs[0]
            metni_yaz(paragraf, satir[j] if j < len(satir) else "")
            for calisma in paragraf.runs:
                calisma.font.name = GOVDE_YAZI_TIPI
                calisma.font.size = Pt(10)
                if i == 0:
                    calisma.bold = True
            govde_bicimi(paragraf, yasla=False)
            paragraf.paragraph_format.space_after = Pt(2)
    return tablo


def gorsel_kur(belge, satir: str) -> list:
    """`![altyazi](yol)` -> gorsel paragrafi + altyazi paragrafi."""
    eslesme = re.match(r"^!\[(.*?)\]\((.+?)\)\s*$", satir)
    if not eslesme:
        raise ValueError(f"görsel satırı okunamadı: {satir}")
    altyazi, yol = eslesme.group(1), (ROOT / eslesme.group(2)).resolve()
    if not yol.exists():
        raise SystemExit(f"görsel yok: {yol}")

    with Image.open(yol) as gorsel:
        genislik_px, yukseklik_px = gorsel.size
    genislik = ICERIK_GENISLIGI
    if yukseklik_px * ICERIK_GENISLIGI.cm / genislik_px > EN_FAZLA_YUKSEKLIK.cm:
        genislik = Cm(EN_FAZLA_YUKSEKLIK.cm * genislik_px / yukseklik_px)

    uretilen = []
    p = belge.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run().add_picture(str(yol), width=genislik)
    p.paragraph_format.space_after = Pt(2)
    uretilen.append(p._p)

    if altyazi:
        a = belge.add_paragraph()
        a.alignment = WD_ALIGN_PARAGRAPH.CENTER
        metni_yaz(a, altyazi)
        for calisma in a.runs:
            calisma.font.name = GOVDE_YAZI_TIPI
            calisma.font.size = Pt(10)
            calisma.font.color.rgb = RGBColor(0x44, 0x4A, 0x51)
        a.paragraph_format.space_after = Pt(10)
        uretilen.append(a._p)
    return uretilen


def bloklari_uret(belge, bloklar: list[tuple[str, list[str]]]) -> list:
    """Bloklari belgenin sonuna yazar, uretilen XML dugumlerini doner.

    Dugumler sonra dogru capanin altina tasiniyor; python-docx'in
    "araya ekle" arayuzu tablo ve gorsel icin yok, o yuzden once sona
    yazilip tasiniyorlar.
    """
    uretilen = []
    for tur, icerik in bloklar:
        if tur == "gorsel":
            uretilen += gorsel_kur(belge, icerik[0])
            continue
        if tur == "tablo":
            tablo = tablo_kur(belge, icerik)
            uretilen.append(tablo._tbl)
            bosluk = belge.add_paragraph()
            bosluk.paragraph_format.space_after = Pt(6)
            uretilen.append(bosluk._p)
            continue
        if tur == "altbaslik":
            p = belge.add_paragraph()
            metni_yaz(p, icerik[0])
            for calisma in p.runs:
                calisma.bold = True
            govde_bicimi(p, yasla=False)
            p.paragraph_format.space_before = Pt(10)
            uretilen.append(p._p)
            continue
        if tur in ("madde", "numarali"):
            # Sablonda "List Bullet"/"List Number" stilleri tanimli
            # degil. Word'un numaralandirma altyapisini disaridan kurmak
            # yerine isaret metne yaziliyor ve asili girinti veriliyor:
            # sonuc ayni gorunuyor, yazi tipi ve punto denetim altinda
            # kaliyor.
            for sira, satir in enumerate(icerik, 1):
                govde = re.sub(r"^\s*(?:[-*]|\d+\.)\s+", "", satir)
                girinti = len(satir) - len(satir.lstrip())
                p = belge.add_paragraph()
                isaret = "•  " if tur == "madde" else f"{sira}.  "
                metni_yaz(p, isaret + govde)
                govde_bicimi(p, yasla=False)
                p.paragraph_format.space_after = Pt(3)
                p.paragraph_format.left_indent = Cm(1.4 if girinti >= 2 else 0.7)
                p.paragraph_format.first_line_indent = Cm(-0.7)
                uretilen.append(p._p)
            continue

        metin = " ".join(s.strip() for s in icerik)
        if tur == "alinti":
            metin = re.sub(r"^>\s?", "", metin).replace("> ", "")
        p = belge.add_paragraph()
        metni_yaz(p, metin)
        govde_bicimi(p)
        if tur == "alinti":
            p.paragraph_format.left_indent = Cm(0.8)
            for calisma in p.runs:
                calisma.italic = True
        uretilen.append(p._p)
    return uretilen


# ---------------------------------------------------------------------------
def kapagi_doldur(belge) -> list[str]:
    """Kapak metin kutusundaki alanlari doldurur.

    Sablonda her alan tek bir run ("Proje Adı:" gibi); etiketi koruyup
    degeri arkasina yaziyoruz. Kutu belgede iki kez geciyor - Word eski
    surumler icin alternatif bir kopya birakiyor - ve ikisi de doluyor,
    yoksa belgeyi acan surume gore kapak bos gorunebilirdi.
    """
    dolan: list[str] = []
    for kutu in belge.element.body.iter(qn("w:txbxContent")):
        for paragraf in kutu.iter(qn("w:p")):
            metin = paragraf_metni(paragraf)
            for etiket, deger in KAPAK.items():
                if not metin.startswith(etiket):
                    continue
                calismalar = paragraf.findall(qn("w:r"))
                if not calismalar:
                    continue
                ilk = calismalar[0].find(qn("w:t"))
                if ilk is None:
                    continue
                ilk.text = f"{etiket} {deger}"
                ilk.set(qn("xml:space"), "preserve")
                for fazla in calismalar[1:]:
                    metin_dugumu = fazla.find(qn("w:t"))
                    if metin_dugumu is not None:
                        metin_dugumu.text = ""
                if etiket not in dolan:
                    dolan.append(etiket)
                break
    return dolan


# ---------------------------------------------------------------------------
def uret(sablon: Path, cikti: Path, bolumler: dict[str, list[str]]) -> dict:
    cikti.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(sablon, cikti)
    belge = docx.Document(str(cikti))
    kapak = kapagi_doldur(belge)
    govde = belge.element.body

    cocuklar = list(govde)
    capalar: list[tuple[int, str]] = []
    kesme = None
    for indis, cocuk in enumerate(cocuklar):
        if cocuk.tag != qn("w:p"):
            continue
        paragraf = next(p for p in belge.paragraphs if p._p is cocuk)
        metin = paragraf_metni(cocuk)
        if metin.startswith(KESME_BASLIGI):
            kesme = indis
            break
        if capa_mi(paragraf):
            if metin in KENDI_SAYFASINDA:
                ppr = paragraf._p.get_or_add_pPr()
                if ppr.find(qn("w:pageBreakBefore")) is None:
                    ppr.insert(0, ppr.makeelement(qn("w:pageBreakBefore"), {}))
            if ALT_BASLIK.match(metin):
                anahat_duzeyi(paragraf, 1)
                for calisma in paragraf.runs:
                    calisma.bold = True
            for on_ek in YONERGE_KIRP:
                if metin.startswith(on_ek) and metin != on_ek:
                    metin = on_ek
                    ilk = True
                    for calisma in paragraf.runs:
                        calisma.text = on_ek if ilk else ""
                        ilk = False
                    break
            capalar.append((indis, metin))

    if kesme is None:
        raise SystemExit(f"şablonda '{KESME_BASLIGI}' bulunamadı — şablon değişmiş olabilir")

    icindekiler_duzelt(belge)

    capa_adlari = {ad for _, ad in capalar}
    bilinmeyen = set(bolumler) - capa_adlari
    if bilinmeyen:
        raise SystemExit(
            "şablonda karşılığı olmayan başlık(lar):\n  "
            + "\n  ".join(sorted(bilinmeyen))
            + "\n\nşablondaki başlıklar:\n  "
            + "\n  ".join(ad for _, ad in capalar)
        )

    # 1) Puanlama bolumu: kesme noktasindan sona kadar her sey. Son
    #    `sectPr` govdenin dogrudan cocugu ve kalmak zorunda - sayfa
    #    boyutu, kenar bosluklari ve ustbilgi orada.
    for cocuk in cocuklar[kesme:]:
        if cocuk.tag != qn("w:sectPr"):
            govde.remove(cocuk)
    # Kesmeden hemen onceki bos `Balk1` paragraflari da gitsin.
    while True:
        kalan = [c for c in govde if c.tag == qn("w:p")]
        if kalan and not paragraf_metni(kalan[-1]):
            govde.remove(kalan[-1])
        else:
            break

    # 2) Her capanin altini bosalt ve icerigi koy. Sondan basa gidiliyor;
    #    boylece silme islemi onceki capalarin sirasini bozmuyor.
    yazilan = 0
    for sira, (indis, ad) in enumerate(capalar):
        if ad not in bolumler:
            continue
        sonraki = capalar[sira + 1][0] if sira + 1 < len(capalar) else kesme
        for cocuk in cocuklar[indis + 1 : sonraki]:
            if cocuk.getparent() is not None:
                govde.remove(cocuk)
        yazilan += 1

    for sira in range(len(capalar) - 1, -1, -1):
        indis, ad = capalar[sira]
        if ad not in bolumler:
            continue
        capa = cocuklar[indis]
        dugumler = bloklari_uret(belge, bloklara_ayir(bolumler[ad]))
        onceki = capa
        for dugum in dugumler:
            onceki.addnext(dugum)
            onceki = dugum

    belge.save(str(cikti))
    return {
        "capa": len(capalar),
        "yazilan": yazilan,
        "bos": [ad for _, ad in capalar if ad not in bolumler],
        "kapak": kapak,
    }


def main() -> int:
    ayristirici = argparse.ArgumentParser(description=__doc__)
    ayristirici.add_argument("--cikti", type=Path, default=CIKTI)
    ayristirici.add_argument("--kaynak", type=Path, default=KAYNAK_DIZIN)
    args = ayristirici.parse_args()

    if not SABLON.exists():
        raise SystemExit(f"şablon bulunamadı: {SABLON}")
    if not args.kaynak.exists():
        raise SystemExit(f"içerik dizini yok: {args.kaynak}")

    bolumler = bolumleri_oku(args.kaynak)
    if not bolumler:
        raise SystemExit(f"{args.kaynak} altında `## başlık` bulunamadı")

    ozet = uret(SABLON, args.cikti, bolumler)
    boyut = args.cikti.stat().st_size / 1024
    print(f"✓ {args.cikti}  ({boyut:.0f} kB)")
    print(f"  {ozet['yazilan']}/{ozet['capa']} başlık dolduruldu")
    eksik_kapak = [ad for ad in KAPAK if ad not in ozet["kapak"]]
    if eksik_kapak:
        print("  KAPAK EKSİK: " + ", ".join(eksik_kapak))
    else:
        print(f"  kapak: {len(ozet['kapak'])} alan dolduruldu")
    if ozet["bos"]:
        print("  henüz boş:")
        for ad in ozet["bos"]:
            print(f"    · {ad}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
