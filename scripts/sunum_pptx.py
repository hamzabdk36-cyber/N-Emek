"""Jüri sunumunu resmi sablonun kopyasi uzerine uretir.

Neden var
---------
Sunum sablonu zorunlu ve kurallari puan kesiyor: bolum basina sayfa
siniri (her fazla sayfa 3 ceza puani), toplam en fazla 19 sayfa,
sayfalar arasinda tekrarlayan ifade yasagi, her sayfada ayni konumda
takim bilgisi. Bunlarin hicbiri PowerPoint'te elle duzenlenmis bir
dosyada kendiliginden korunmaz; ilk duzeltmede biri sessizce bozulur.

Teknik raporla ayni ilke (`rapor_docx.py`): icerik `docs/SUNUM/*.md`
altinda yasiyor, `.pptx` *uretiliyor*, sablonun kendisi hic elle
acilmiyor. Sayfa plani ve gerekceleri: `docs/SUNUM/_PLAN.md`.

Nasil calisiyor
---------------
Sablon 12 slayt: kapak, takim tanitimi, dokuz bolum sayfasi (her
bolumden bir tane) ve en sonda "Sunum Hazirlama Kurallari". Betik:

1. kurallar sayfasini siler ("SUNUMDA BU SAYFAYA YER VERILMEYECEKTIR"),
2. `SAYFALAR` listesindeki sirayla bolum sayfalarini cogaltir - sagdaki
   bolum seridi sayfanin kendi seklinde, kopya o yuzden dogru vurguyu
   tasir,
3. kirmizi yonerge kutularini rengine bakarak siler,
4. kapagi, takim sayfasini ve alt banttaki takim bilgisini doldurur,
5. icerigi yerlestirir, denetler, kaydeder.

Sablonun sabit unsurlarina (baslik, serit, logolar, alt bilgi) dokunmaz.
Alt banttaki "TAKIM ADI / TAKIM ID / BASVURU ID" etiketleri arka plan
gorselinin icinde; betik yalnizca degerleri yanlarina yazar.

Kullanim
--------
    .venv/Scripts/python.exe scripts/sunum_pptx.py
    .venv/Scripts/python.exe scripts/sunum_pptx.py --iskelet   # icerik yokken
    powershell -ExecutionPolicy Bypass -File scripts/sunum_powerpoint.ps1 -Pdf

`--iskelet`, icerik dosyasi olmayan sayfalara icerik alaninin sinirini
gosteren bir cerceve cizer ve eksik icerigi hata saymaz. Teslim
dosyasi bu bayrakla uretilmez.

Onkosul: `pip install python-pptx`.
"""

from __future__ import annotations

import argparse
import copy
import re
import sys
from dataclasses import dataclass
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

try:
    from lxml import etree
    from pptx import Presentation
    from pptx.dml.color import RGBColor
    from pptx.enum.dml import MSO_LINE_DASH_STYLE
    from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
    from pptx.opc.constants import RELATIONSHIP_TYPE as RT
    from pptx.oxml.ns import qn
    from pptx.util import Cm, Pt
except ModuleNotFoundError as exc:  # pragma: no cover - kurulum yonlendirmesi
    print(f"eksik paket: {exc.name}")
    print("  .venv/Scripts/python.exe -m pip install python-pptx")
    raise SystemExit(1)

sys.path.insert(0, str(Path(__file__).resolve().parent))
import rapor_takvim  # noqa: E402  - takvim tarihlerinin tek kaynagi
import sunum_sayfalar as sayfalar  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SABLON = ROOT / "docs" / "NSosyal_Inovasyon_Yarısması_Sunum_Sablonu_1_2_2_TTN8G.pptx"
KAYNAK_DIZIN = ROOT / "docs" / "SUNUM"
CIKTI = KAYNAK_DIZIN / "N-Emek-Sunum.pptx"

KAPAK = {
    "proje": "N-Emek",
    "proje_alt": "Açıklanabilir İçerik Atıf ve Adil Gelir Paylaşım Sistemi",
    "tema": "İçerik Ekonomisi",
    "takim": "ZENITH N",
    "takim_id": "1003461",
    "basvuru_id": "5382505",
}

# Kaptan ayri alanda; sablon "tekrar uye olarak yer vermemelisiniz" diyor.
# Fotograf yok (takim karari, 15 Eyl) - bos fotograf cerceveleri de kalkiyor.
KAPTAN = ("Hamza Budak", "Yazılım mimarisi ve testler",
          "Bursa Teknik Üniversitesi", "Fizik Lisans, 3. sınıf")
UYELER = [
    ("Berra Özer", "Kullanıcı deneyimi ve geliştirme",
     "Bursa Teknik Üniversitesi", "Fizik Lisans, 3. sınıf"),
]

# Sablondaki slayt sirasi (0 tabanli).
S_KAPAK, S_TAKIM, S_OZET, S_PROBLEM, S_COZUM, S_YONTEM, S_PROTOTIP, \
    S_UYGULANABILIRLIK, S_OZGUNLUK, S_HEDEF, S_TAKVIM, S_KURALLAR = range(12)


@dataclass(frozen=True)
class Bolum:
    ad: str
    sablon: int
    sinir: int


BOLUMLER = {
    "kapak": Bolum("Kapak", S_KAPAK, 1),
    "takim": Bolum("Takım Tanıtımı", S_TAKIM, 1),
    "ozet": Bolum("Proje Özeti ve Kapsamı", S_OZET, 1),
    "problem": Bolum("Problemin Tanımı", S_PROBLEM, 2),
    "cozum": Bolum("Çözüm Önerisi", S_COZUM, 3),
    "yontem": Bolum("Yöntem", S_YONTEM, 2),
    "prototip": Bolum("Prototip / Uygulama Geliştirme Durumu", S_PROTOTIP, 1),
    "uygulanabilirlik": Bolum("Uygulanabilirlik ve Sürdürülebilirlik", S_UYGULANABILIRLIK, 2),
    "ozgunluk": Bolum("Özgünlük ve Yerlilik Yönü", S_OZGUNLUK, 2),
    "hedef": Bolum("Hedef Kitle ve Yaygın Etki", S_HEDEF, 1),
    "takvim": Bolum("Proje Takvimi", S_TAKVIM, 1),
}

# Sunumun sayfa sirasi: (bolum, icerik dosyasi). Plan: docs/SUNUM/_PLAN.md
SAYFALAR = [
    ("kapak", None),
    ("takim", None),
    ("ozet", "03-ozet.md"),
    ("problem", "04-problem.md"),
    ("cozum", "05-cozum-1.md"),
    ("cozum", "06-cozum-2.md"),
    ("yontem", "07-yontem-1.md"),
    ("yontem", "08-yontem-2.md"),
    ("prototip", "09-prototip.md"),
    ("uygulanabilirlik", "10-uygulanabilirlik-1.md"),
    ("uygulanabilirlik", "11-uygulanabilirlik-2.md"),
    ("ozgunluk", "12-ozgunluk.md"),
    ("hedef", "13-hedef-kitle.md"),
    ("takvim", "14-takvim.md"),
]
TOPLAM_SINIR = 19

# Baslik altinda, sag seridin solunda, alt bant cizgisinin ustunde kalan
# alan. PowerPoint'te cizdirilen sablon uzerinden olculdu. Basligi iki
# satira tasan iki bolumde alan asagidan baslar.
ICERIK_SOL, ICERIK_SAG = 3.4, 41.0
ICERIK_UST, ICERIK_UST_IKI_SATIR, ICERIK_ALT = 4.3, 6.4, 25.2
IKI_SATIR_BASLIK = {S_PROTOTIP, S_UYGULANABILIRLIK}

# Sablonun paleti (slayt XML'inden ve arka plan gorsellerinden).
LACIVERT = RGBColor(0x1A, 0x42, 0x6A)
MAVI_ACIK = RGBColor(0xB7, 0xCC, 0xE4)

# Yonerge metinlerinin renkleri. Sablonda kirmiziyi baska hicbir sekil
# kullanmiyor; renk bu yuzden guvenilir bir isaret.
YONERGE_RENKLERI = {"FF0000", "DE2223", "EE0000"}

# Betigin ekledigi her sekil bu onekle adlanir: `sunum_powerpoint.ps1`
# tasma denetimini yalnizca bunlarda yapar (sablonun kendi kutulari
# otomatik boyutlu, orada tasma olculemez).
ONEK = "NEMEK"

# Yonergelerden geriye bir iz kalirsa denetim yakalasin diye.
YER_TUTUCULAR = ("ÜYE 2", "ÜYE 3", "ÜYE 4", "ÜYE 5", "VARSA", "silinmelidir",
                 "TAKIMDAKİ GÖREVİ", "EĞİTİM BİLGİSİ", "sayfada açıklanmalıdır",
                 "yararlanabilirsiniz")

R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"


# --------------------------------------------------------------------------
# Sablon islemleri
# --------------------------------------------------------------------------

def slayt_sil(prs, indeks: int) -> None:
    liste = prs.slides._sldIdLst
    sld_id = liste[indeks]
    prs.part.drop_rel(sld_id.rId)
    liste.remove(sld_id)


def slayt_kopyala(prs, kaynak):
    """Slaydi arka plani, sekilleri ve gorsel iliskileriyle kopyalar.

    python-pptx'te kopyalama yok. Yeni slayt ayni yerlesimden acilir,
    `cSld` icerigi (arka plan + sekil agaci) tasinir, gorsel iliskileri
    yeni parcaya baglanir ve `r:` nitelikleri yeni kimliklere cevrilir.
    Notlar kopyalanmaz.
    """
    yeni = prs.slides.add_slide(kaynak.slide_layout)
    esle = {}
    for rid, rel in kaynak.part.rels.items():
        if rel.reltype in (RT.SLIDE_LAYOUT, RT.NOTES_SLIDE):
            continue
        if rel.is_external:
            esle[rid] = yeni.part.relate_to(rel.target_ref, rel.reltype, is_external=True)
        else:
            esle[rid] = yeni.part.relate_to(rel.target_part, rel.reltype)

    # `slide.shapes` sekil agacinin *elemanina* baglanip onbellege aliniyor;
    # agac elemaninin kendisi degistirilirse sonraki her islem bosta kalan
    # eski agaca yazar ve kopya sayfa islenmemis cikar (bir kez oldu). Bu
    # yuzden agac yerinde kalir, yalnizca cocuklari tasinir.
    hedef_csld = yeni._element.cSld
    hedef_agac = hedef_csld.spTree
    for cocuk in list(hedef_agac):
        hedef_agac.remove(cocuk)
    for cocuk in kaynak._element.cSld.spTree:
        hedef_agac.append(copy.deepcopy(cocuk))
    arka_plan = kaynak._element.cSld.find(qn("p:bg"))
    if arka_plan is not None:
        hedef_csld.insert(0, copy.deepcopy(arka_plan))
    for el in hedef_csld.iter():
        for anahtar, deger in list(el.attrib.items()):
            if anahtar.startswith("{%s}" % R_NS) and deger in esle:
                el.set(anahtar, esle[deger])
    return yeni


def slaytlari_diz(prs) -> list:
    """Sablonu `SAYFALAR` sirasina getirir; slayt listesini dondurur."""
    sablon = list(prs.slides)
    liste = prs.slides._sldIdLst
    kimlikler = list(liste)
    kullanildi: set[int] = set()
    sira = []
    for bolum_adi, _ in SAYFALAR:
        indeks = BOLUMLER[bolum_adi].sablon
        if indeks not in kullanildi:
            kullanildi.add(indeks)
            sira.append(kimlikler[indeks])
        else:
            slayt_kopyala(prs, sablon[indeks])
            sira.append(list(liste)[-1])

    # Kullanilmayan sablon slaytlari (yalnizca kurallar sayfasi) silinir.
    for indeks in sorted(set(range(len(sablon))) - kullanildi, reverse=True):
        slayt_sil(prs, indeks)
    for sld_id in list(liste):
        liste.remove(sld_id)
    for sld_id in sira:
        liste.append(sld_id)
    return list(prs.slides)


def renkleri(sekil) -> set[str]:
    return {c.get("val").upper() for c in sekil._element.iter(qn("a:srgbClr"))}


def yonergeleri_sil(slayt) -> int:
    silinen = 0
    for sekil in list(slayt.shapes):
        if sekil.has_text_frame and renkleri(sekil) & YONERGE_RENKLERI:
            sekil._element.getparent().remove(sekil._element)
            silinen += 1
    return silinen


def sablon_sekli(slayt, kimlik: int):
    for sekil in slayt.shapes:
        if sekil.shape_id == kimlik:
            return sekil
    raise SystemExit(f"şablon değişmiş: {kimlik} numaralı şekil bulunamadı")


def sekli_sil(slayt, kimlik: int) -> None:
    el = sablon_sekli(slayt, kimlik)._element
    el.getparent().remove(el)


# --------------------------------------------------------------------------
# Metin yardimcilari
# --------------------------------------------------------------------------

def metin_kutusu(slayt, ad: str, sol: float, ust: float, gen: float, yuk: float):
    kutu = slayt.shapes.add_textbox(Cm(sol), Cm(ust), Cm(gen), Cm(yuk))
    kutu.name = f"{ONEK} {ad}"
    cer = kutu.text_frame
    cer.word_wrap = True
    cer.margin_left = cer.margin_right = cer.margin_top = cer.margin_bottom = 0
    return kutu


def paragraf_yaz(paragraf, metin: str, boyut: float, renk: RGBColor, kalin=False,
                 yazi_tipi="Arial") -> None:
    run = paragraf.add_run()
    run.text = metin
    run.font.size = Pt(boyut)
    run.font.bold = kalin
    run.font.name = yazi_tipi
    run.font.color.rgb = renk


def kosu_ekle(paragraf_el, sonra_el, metin: str, boyut: float, renk: str,
              yazi_tipi: str) -> None:
    """Sablon paragrafinda bir kosunun hemen arkasina yeni kosu ekler.

    Kapaktaki etiket paragraflari `a:br` ile bitiyor; `add_run` kosuyu en
    sona, yani satir sonunun arkasina koyardi.
    """
    r = etree.SubElement(paragraf_el, qn("a:r"))
    rpr = etree.SubElement(r, qn("a:rPr"), lang="tr-TR", sz=str(int(boyut * 100)), b="0")
    dolgu = etree.SubElement(rpr, qn("a:solidFill"))
    etree.SubElement(dolgu, qn("a:srgbClr"), val=renk)
    for etiket in ("a:latin", "a:ea", "a:cs"):
        etree.SubElement(rpr, qn(etiket), typeface=yazi_tipi)
    t = etree.SubElement(r, qn("a:t"))
    t.text = metin
    paragraf_el.remove(r)
    sonra_el.addnext(r)


# --------------------------------------------------------------------------
# Sabit sayfalar
# --------------------------------------------------------------------------

def kapagi_doldur(slayt) -> None:
    kutu = sablon_sekli(slayt, 90)
    paragraflar = kutu.text_frame.paragraphs

    def etiketin_arkasina(p_indeks: int, metin: str, boyut: float = 32,
                          yazi_tipi: str = "Arial Black") -> None:
        p = paragraflar[p_indeks]._p
        kosular = p.findall(qn("a:r"))
        kosu_ekle(p, kosular[-1], metin, boyut, "FFFFFF", yazi_tipi)

    # Etiket zaten bolunmez bosluk ile bitiyor.
    etiketin_arkasina(0, KAPAK["proje"])
    # Etiketin altindaki bos paragraf proje adinin devamina ayrildi.
    alt = paragraflar[1]
    alt.runs[0].text = KAPAK["proje_alt"]
    alt.runs[0].font.size = Pt(26)
    alt.runs[0].font.bold = True
    alt.runs[0].font.name = "Arial"
    alt.runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    etiketin_arkasina(2, " " + KAPAK["tema"])
    etiketin_arkasina(3, " " + KAPAK["takim"])
    etiketin_arkasina(5, " " + KAPAK["takim_id"])
    etiketin_arkasina(7, " " + KAPAK["basvuru_id"])


def takimi_doldur(slayt) -> None:
    if len(UYELER) != 1:
        raise SystemExit("takım sayfası yerleşimi yalnızca bir üye için yazıldı")

    # Danismani yok: cerceve, etiket ve altindaki ok. Fotograf yok: butun
    # cerceveler. Uye 2-5: kutular, metinler ve oklari.
    for kimlik in (112, 106, 103,            # danisman
                   113, 114, 115, 116, 117, 118,  # fotograf cerceveleri
                   98, 99, 100, 102,         # uye 2-5 kutulari
                   108, 109, 110, 111,       # uye 2-5 metinleri
                   119, 120, 127, 128):      # uye 2-5 oklari
        sekli_sil(slayt, kimlik)

    # Kaptan: fotograf cercevesinin yerine, kaptan etiketinin ustune.
    kaptan = slayt.shapes.add_shape(1, Cm(8.4), Cm(14.6), Cm(7.6), Cm(4.9))
    kaptan.name = f"{ONEK} kaptan"
    kaptan.fill.solid()
    kaptan.fill.fore_color.rgb = MAVI_ACIK
    kaptan.line.color.rgb = LACIVERT
    kaptan.shadow.inherit = False
    kisi_yaz(kaptan.text_frame, KAPTAN)

    # Uye 1: sablon kutusu kalir, fotograf cercevesi gittigi icin metin
    # kutunun tamamina yayilir.
    kutu = sablon_sekli(slayt, 101)
    eski = sablon_sekli(slayt, 105)
    eski._element.getparent().remove(eski._element)
    metin = metin_kutusu(slayt, "uye-1", 0, 0, 0, 0)
    metin.left, metin.top, metin.width, metin.height = kutu.left, kutu.top, kutu.width, kutu.height
    kisi_yaz(metin.text_frame, UYELER[0])


def kisi_yaz(cerceve, kisi: tuple[str, str, str, str]) -> None:
    ad, gorev, okul, bolum = kisi
    cerceve.word_wrap = True
    cerceve.vertical_anchor = MSO_ANCHOR.MIDDLE
    cerceve.margin_left = cerceve.margin_right = Cm(0.3)
    satirlar = [(ad, 17, True), (gorev, 14, False), (okul, 13, False), (bolum, 13, False)]
    for i, (metin, boyut, kalin) in enumerate(satirlar):
        p = cerceve.paragraphs[0] if i == 0 else cerceve.add_paragraph()
        p.alignment = PP_ALIGN.CENTER
        paragraf_yaz(p, metin, boyut, LACIVERT, kalin)


def alt_banda_yaz(slayt) -> None:
    """Arka plandaki TAKIM ADI / TAKIM ID / BASVURU ID etiketlerinin sagi."""
    kutu = metin_kutusu(slayt, "takim-bilgisi", 35.6, 25.95, 7.4, 2.2)
    for i, deger in enumerate((KAPAK["takim"], KAPAK["takim_id"], KAPAK["basvuru_id"])):
        p = kutu.text_frame.paragraphs[0] if i == 0 else kutu.text_frame.add_paragraph()
        p.line_spacing = Pt(20.2)
        paragraf_yaz(p, deger, 14, LACIVERT, kalin=True)


def iskelet_cercevesi(slayt, ust: float, ad: str) -> None:
    cer = slayt.shapes.add_shape(1, Cm(ICERIK_SOL), Cm(ust),
                                 Cm(ICERIK_SAG - ICERIK_SOL), Cm(ICERIK_ALT - ust))
    cer.name = f"{ONEK} iskelet"
    cer.fill.background()
    cer.line.color.rgb = MAVI_ACIK
    cer.line.dash_style = MSO_LINE_DASH_STYLE.DASH
    cer.shadow.inherit = False
    cer.text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = cer.text_frame.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    paragraf_yaz(p, f"İÇERİK YOK — {ad}", 28, MAVI_ACIK, kalin=True)


# --------------------------------------------------------------------------
# Denetim
# --------------------------------------------------------------------------

def denetle(slaytlar, iskelet: bool) -> list[str]:
    bulgular: list[str] = []

    sayac: dict[str, int] = {}
    for bolum_adi, _ in SAYFALAR:
        sayac[bolum_adi] = sayac.get(bolum_adi, 0) + 1
    for bolum_adi, adet in sayac.items():
        bolum = BOLUMLER[bolum_adi]
        if adet > bolum.sinir:
            bulgular.append(f"{bolum.ad}: {adet} sayfa, sınır {bolum.sinir}")
    if len(slaytlar) > TOPLAM_SINIR:
        bulgular.append(f"toplam {len(slaytlar)} sayfa, sınır {TOPLAM_SINIR}")
    if len(slaytlar) != len(SAYFALAR):
        bulgular.append(f"üretilen {len(slaytlar)} sayfa, planlanan {len(SAYFALAR)}")

    cumleler: dict[str, int] = {}
    for no, slayt in enumerate(slaytlar, start=1):
        metinler = [s.text_frame.text for s in slayt.shapes if s.has_text_frame]
        for sekil in slayt.shapes:
            if sekil.has_text_frame and renkleri(sekil) & YONERGE_RENKLERI:
                bulgular.append(f"sayfa {no}: kırmızı yönerge metni kaldı ({sekil.name})")
        tum = "\n".join(metinler)
        for iz in YER_TUTUCULAR:
            if iz.lower() in tum.lower():
                bulgular.append(f"sayfa {no}: yer tutucu kaldı: {iz!r}")
        if no > 1 and not any(s.name == f"{ONEK} takim-bilgisi" for s in slayt.shapes):
            bulgular.append(f"sayfa {no}: alt bantta takım bilgisi yok")
        if not iskelet and any(s.name == f"{ONEK} iskelet" for s in slayt.shapes):
            bulgular.append(f"sayfa {no}: içerik yok")

        # Tekrar yasagi: yalnizca betigin yazdigi metinlerde, bes kelimeden
        # uzun cumleler. Sablonun sabit metinleri (serit, alt bilgi) her
        # sayfada ayni ve bu kuralin konusu degil.
        for sekil in slayt.shapes:
            if not (sekil.has_text_frame and sekil.name.startswith(ONEK)):
                continue
            # Kaynak satirlari ayni yayina birden fazla sayfada atif yapabilir;
            # kural ifade tekrarini yasakliyor, kaynak gostermeyi degil.
            if sekil.name == f"{ONEK} kaynak":
                continue
            for cumle in re.split(r"(?<=[.!?])\s+|\n", sekil.text_frame.text):
                anahtar = " ".join(re.findall(r"\w+", cumle.lower()))
                if len(anahtar.split()) < 5:
                    continue
                if anahtar in cumleler and cumleler[anahtar] != no:
                    bulgular.append(
                        f"sayfa {no}: sayfa {cumleler[anahtar]} ile aynı cümle: {cumle.strip()!r}")
                cumleler.setdefault(anahtar, no)
    return bulgular


# --------------------------------------------------------------------------

def uret(cikti: Path, iskelet: bool) -> int:
    if not SABLON.exists():
        raise SystemExit(f"şablon bulunamadı: {SABLON}")
    prs = Presentation(str(SABLON))
    if len(prs.slides) != 12:
        raise SystemExit(f"şablon değişmiş: 12 slayt bekleniyordu, {len(prs.slides)} var")

    slaytlar = slaytlari_diz(prs)
    silinen = sum(yonergeleri_sil(s) for s in slaytlar)

    for no, (slayt, (bolum_adi, dosya)) in enumerate(zip(slaytlar, SAYFALAR), start=1):
        bolum = BOLUMLER[bolum_adi]
        if bolum.sablon == S_KAPAK:
            kapagi_doldur(slayt)
            continue
        alt_banda_yaz(slayt)
        if bolum.sablon == S_TAKIM:
            takimi_doldur(slayt)
            continue
        ust = ICERIK_UST_IKI_SATIR if bolum.sablon in IKI_SATIR_BASLIK else ICERIK_UST
        kaynak = KAYNAK_DIZIN / dosya
        if not kaynak.exists():
            iskelet_cercevesi(slayt, ust, f"{no:02d} {bolum.ad}")
            continue
        icerik = sayfalar.Icerik(kaynak)
        yerlesim = sayfalar.YERLESIMLER[dosya]
        if yerlesim is sayfalar.s_takvim:
            yerlesim(slayt, icerik, ust, KAYNAK_DIZIN, paketler=rapor_takvim.PAKETLER)
        else:
            yerlesim(slayt, icerik, ust, KAYNAK_DIZIN)
        icerik.artiklari_denetle()
        sayfalar.notu_yaz(slayt, icerik.bolumler.get("not"))

    cikti.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(cikti))

    print(f"şablon    : {SABLON.name}")
    print(f"çıktı     : {cikti}")
    print(f"sayfa     : {len(slaytlar)} / {TOPLAM_SINIR}")
    print(f"yönerge   : {silinen} kutu silindi")
    print()
    sayac: dict[str, int] = {}
    for bolum_adi, _ in SAYFALAR:
        sayac[bolum_adi] = sayac.get(bolum_adi, 0) + 1
    for bolum_adi, adet in sayac.items():
        bolum = BOLUMLER[bolum_adi]
        print(f"  {bolum.ad:<40} {adet} / {bolum.sinir}")

    # Denetim bellekteki nesnelerde degil, kaydedilen dosyada yapilir:
    # teslim edilen sey o. Bellekteki bir nesne yanlis agaca bagli kalirsa
    # (bkz. `slayt_kopyala`) denetim onu temiz gorur ama dosya kirli cikar.
    bulgular = denetle(list(Presentation(str(cikti)).slides), iskelet)
    print()
    if bulgular:
        print(f"DENETİM: {len(bulgular)} bulgu")
        for b in bulgular:
            print(f"  - {b}")
        return 1
    print("DENETİM: temiz" + (" (iskelet kipi)" if iskelet else ""))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--cikti", type=Path, default=CIKTI)
    ap.add_argument("--iskelet", action="store_true",
                    help="içerik dosyası olmayan sayfalara çerçeve çiz, eksik içeriği hata sayma")
    args = ap.parse_args()
    return uret(args.cikti, args.iskelet)


if __name__ == "__main__":
    raise SystemExit(main())
