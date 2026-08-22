"""Gorusme kayitlarindan kullanici arastirmasi bulgularini uretir.

Neden var
---------
Kullanilabilirlik testiyle ayni gerekce: bu projede hicbir sayi elle
yazilmaz. Nitel bir arastirmada da sayi var - "uc ve daha fazla kiside
gorulen oruntu", "dort katilimcinin dordu dogruladi" gibi. Bunlar elle
sayilirsa yanlis sayilabilir ve kimse fark etmez.

Is bolumu net: **yargi** insanin, **sayim** betigin. Gorusmeci her
kayda etiket ve varsayim sonucu yazar (dogruladi / curuttu /
sinanamadi); kac kiside gorundugunu betik sayar.

Betik yalnizca `## Bulgular` bolumunden sonrasini yazar; ustundeki
duzenek metni (varsayimlar, profiller, gorusme rehberi) elle yazilmis
ve oyle kaliyor.

Kullanim
--------
    .venv/Scripts/python.exe scripts/kullanici_arastirmasi.py

Girdi : data/kullanici-arastirmasi/gorusmeler.json
Cikti : docs/KULLANICI-ARASTIRMASI.md  (yalnizca "## Bulgular" sonrasi)
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

KOK = Path(__file__).resolve().parent.parent
VARSAYILAN_VERI = KOK / "data" / "kullanici-arastirmasi" / "gorusmeler.json"
VARSAYILAN_BELGE = KOK / "docs" / "KULLANICI-ARASTIRMASI.md"

# "Uc ve daha fazla kisi" - duzenek metninde yazili esik.
ORUNTU_ESIGI = 3

VARSAYIMLAR = {
    "V1": "Üreticiler içeriklerinin izinin kaybolmasından rahatsız",
    "V2": "Remix üretenler kaynağı anmak istiyor ama nasıl yapacağını bilmiyor",
    "V3": "Paylaşan kişi mağduriyet yaratmak istemiyor, yalnızca kaynağı bilmiyor",
}

BASLANGIC = "## Bulgular"


class Hata(Exception):
    """Veri kabul edilemez - betik durur, yarim belge uretmez."""


def veriyi_oku(yol: Path) -> dict:
    if not yol.exists():
        raise Hata(f"{yol} yok.")
    veri = json.loads(yol.read_text(encoding="utf-8"))
    gorusmeler = veri.get("gorusmeler") or []
    if not gorusmeler:
        raise Hata("Görüşme yok.")
    gecerli = {"doğruladı", "çürüttü", "sınanamadı", "kapsam dışı"}
    bilinen = set(veri.get("oruntuler") or {})
    for g in gorusmeler:
        kod = g.get("kod", "?")
        if g.get("sonuc") not in gecerli:
            raise Hata(f"{kod}: sonuç {sorted(gecerli)} arasından olmalı.")
        for etiket in g.get("etiketler") or []:
            if etiket not in bilinen:
                raise Hata(f"{kod}: tanımsız örüntü etiketi `{etiket}`.")
    return veri


def belge_uret(veri: dict) -> str:
    gorusmeler = veri["gorusmeler"]
    kosum = veri.get("kosum") or {}
    n = len(gorusmeler)

    s: list[str] = []
    y = s.append

    y(BASLANGIC)
    y("")
    y("> Bu bölüm elle düzenlenmez. Ham görüşme kayıtları")
    y("> `data/kullanici-arastirmasi/gorusmeler.json` içindedir; buradaki her sayı")
    y("> `scripts/kullanici_arastirmasi.py` tarafından sayılır. Yargı görüşmecinin")
    y("> (etiket ve varsayım sonucu), sayım betiğin.")
    y("")
    y("| | |")
    y("|---|---|")
    y(f"| Tarih | {kosum.get('tarih_araligi', '—')} |")
    y(f"| Görüşmeyi yapan | {kosum.get('yoneten', '—')} |")
    y(f"| Yöntem | {kosum.get('yontem', '—')} |")
    y(f"| Görüşme sayısı | **{n}** |")
    y("")

    # --- Profil dagilimi
    profiller = Counter(g["profil"] for g in gorusmeler)
    y("### Kimlerle konuşuldu")
    y("")
    y("| Profil | Kaç kişi |")
    y("|---|--:|")
    for profil, adet in profiller.most_common():
        y(f"| {profil} | {adet} |")
    y(f"| **Toplam** | **{n}** |")
    y("")
    if kosum.get("not"):
        y(kosum["not"])
        y("")

    # --- Gorusme basina bir satir
    y("### Görüşme başına")
    y("")
    y("Alıntılar birebir; özetlenmiş alıntı bulgu sayılmaz.")
    y("")
    y("| Kod | Profil | Varsayım | Sonuç | Birebir alıntı |")
    y("|---|---|---|---|---|")
    for g in gorusmeler:
        y(
            f"| {g['kod']} | {g['profil']} | {g['varsayim']} | {g['sonuc']} "
            f"| \"{g['alinti']}\" |"
        )
    y("")
    notlu = [g for g in gorusmeler if g.get("sonuc_notu")]
    for g in notlu:
        y(f"- **{g['kod']}:** {g['sonuc_notu']}")
    if notlu:
        y("")

    # --- Varsayimlarin durumu
    y("### Varsayımların durumu")
    y("")
    y("| # | Varsayım | Doğruladı | Çürüttü | Sınanamadı |")
    y("|---|---|--:|--:|--:|")
    for kod, metin in VARSAYIMLAR.items():
        ilgili = [g for g in gorusmeler if g["varsayim"] == kod]
        sayac = Counter(g["sonuc"] for g in ilgili)
        y(
            f"| {kod} | {metin} | {sayac['doğruladı']} | {sayac['çürüttü']} "
            f"| {sayac['sınanamadı']} |"
        )
    y("")
    curuten = [g for g in gorusmeler if g["sonuc"] == "çürüttü"]
    if curuten:
        y("**Çürüyen varsayım var.** İlgili görüşmeler: "
          + ", ".join(g["kod"] for g in curuten)
          + ". Ürüne yansıması aşağıda yazılır.")
    else:
        y("Hiçbir görüşme bir varsayımı çürütmedi. Bu, varsayımların *kanıtlandığı*")
        y("anlamına gelmez: örneklem küçük ve seçilmiş, üstelik iki görüşmede")
        y("koşullar varsayımı sınamaya elverişli olmadı (yukarıdaki notlar).")
    y("")

    # --- Tekrar eden oruntuler
    tanimlar = veri.get("oruntuler") or {}
    sayac: Counter = Counter()
    kimde: dict[str, list[str]] = {}
    for g in gorusmeler:
        for etiket in g.get("etiketler") or []:
            sayac[etiket] += 1
            kimde.setdefault(etiket, []).append(g["kod"])

    y("### Tekrar eden örüntüler")
    y("")
    y(f"Düzenek metnindeki eşik: **{ORUNTU_ESIGI} ve daha fazla** kişide görülen davranış.")
    y("")
    y("| Örüntü | Kaç kişi | Kimde |")
    y("|---|--:|---|")
    for etiket, adet in sayac.most_common():
        if adet < ORUNTU_ESIGI:
            continue
        y(f"| {tanimlar[etiket]} | **{adet}** / {n} | {', '.join(kimde[etiket])} |")
    y("")
    esik_alti = [(e, a) for e, a in sayac.most_common() if a < ORUNTU_ESIGI]
    if esik_alti:
        y("Eşiğin altında kalanlar (örüntü sayılmaz, kayıt için): "
          + " · ".join(f"{tanimlar[e]} ({a})" for e, a in esik_alti))
        y("")

    # --- Terimler
    terim_sayaci: Counter = Counter()
    for g in gorusmeler:
        for terim in g.get("terimler") or []:
            terim_sayaci[terim] += 1

    y("### Kullanıcının kelimeleri, arayüzün kelimeleri")
    y("")
    y("Katılımcıların **kendiliğinden** kullandığı terimler ve arayüzdeki karşılıkları.")
    y("Fark varsa arayüz terimi tartışmaya açılır.")
    y("")
    y("| Katılımcı ne diyor | Kaç kişide | Arayüzde ne yazıyor |")
    y("|---|--:|---|")
    for esleme in veri.get("terim_esleme") or []:
        adet = terim_sayaci.get(esleme["kullanici"], 0)
        y(f"| {esleme['kullanici']} | {adet} / {n} | {esleme['arayuz']} |")
    y("")

    # --- Ozet: rapora giren bolum
    ozet = veri.get("ozet") or {}
    y("## Özet")
    y("")
    dogrulayan = sum(1 for g in gorusmeler if g["sonuc"] == "doğruladı")
    curuten_s = sum(1 for g in gorusmeler if g["sonuc"] == "çürüttü")
    sinanamayan = sum(1 for g in gorusmeler if g["sonuc"] == "sınanamadı")
    kapsam_disi = sum(1 for g in gorusmeler if g["sonuc"] == "kapsam dışı")
    y(
        f"**{n} görüşme yapıldı.** {dogrulayan} görüşme ilgili varsayımı doğruladı, "
        f"{curuten_s} tanesi çürüttü, {sinanamayan} tanesinde koşullar varsayımı "
        f"sınamaya elverişli olmadı, {kapsam_disi} görüşme V1-V3'ün dışında bir "
        f"soruyu sınadı."
    )
    y("")
    y("**Ürüne yansıyanlar.** Görüşmelerden çıkan ve ürün kararına dönüşen maddeler;")
    y("her biri yukarıdaki sayılara dayanıyor.")
    y("")
    for madde in ozet.get("urune_yansiyanlar") or []:
        y(f"- {madde}")
    y("")
    if curuten_s == 0:
        y("**Çürüyen varsayım çıkmadı.** Bu iyi bir sonuç değil, *nötr* bir sonuçtur:")
        y("örneklem küçük ve kartopu yöntemiyle seçildi, dolayısıyla varsayımı")
        y("doğrulayan kişilere ulaşma eğilimi taşıyor. Asıl bilgi doğrulamanın")
        y("kendisinde değil, katılımcıların **ne istediğini söylediğinde**: talep")
        y("edilen şey ağırlıkla gelir değil görünürlük çıktı ve bu, ürünün vurgusunu")
        y("doğrudan etkiliyor.")
        y("")

    # --- Sinirlar
    y("## Sınırlar")
    y("")
    y("- Örneklem seçilmiş (kartopu) — temsili değil, keşif amaçlı.")
    y("- Geçmişe dair sorular hatıra yanlılığı taşır; kişi olayı olduğundan çarpıcı")
    y("  anlatabilir.")
    for profil, adet in profiller.items():
        if adet == 1:
            y(f"- **{profil}** profilinde tek kişi var; o profilden gelen bulgular tek")
            y("  görüşmeye dayanıyor ve örüntü sayılamaz.")
    for madde in ozet.get("sinirlar_ek") or []:
        y(f"- {madde}")
    y("")
    # --- Ham kayitlar
    y("### Ham görüşme kayıtları")
    y("")
    y("Her cevap birebir; soru numaraları düzenek metnindeki görüşme rehberinden.")
    y("")
    for g in gorusmeler:
        y(f"#### {g['kod']} — {g['profil']}")
        y("")
        for no, cevap in sorted(g["cevaplar"].items(), key=lambda x: int(x[0])):
            y(f"**{no}.** {cevap}")
            y("")

    return "\n".join(s) + "\n"


def main() -> int:
    ayristirici = argparse.ArgumentParser(description="Kullanici arastirmasi bulgulari")
    ayristirici.add_argument("--veri", type=Path, default=VARSAYILAN_VERI)
    ayristirici.add_argument("--belge", type=Path, default=VARSAYILAN_BELGE)
    arg = ayristirici.parse_args()

    try:
        veri = veriyi_oku(arg.veri)
    except Hata as exc:
        print(f"HATA: {exc}")
        return 1

    mevcut = arg.belge.read_text(encoding="utf-8")
    if BASLANGIC not in mevcut:
        print(f"HATA: {arg.belge} içinde `{BASLANGIC}` başlığı yok.")
        return 1

    ust = mevcut[: mevcut.index(BASLANGIC)]
    arg.belge.write_text(ust + belge_uret(veri), encoding="utf-8")
    print(f"✓ {arg.belge}  ({len(veri['gorusmeler'])} görüşme)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
