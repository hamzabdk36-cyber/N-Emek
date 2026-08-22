"""Kullanilabilirlik oturumlarinin ham kayitlarindan sonuc belgesi uretir.

Neden var
---------
Projenin degismez kurali: hicbir sayi elle yazilmaz. Kullanilabilirlik
testi bu kuralin en kirilgan yeri, cunku verisi bir olcum betiginden
degil bir insandan geliyor - yani "elle yazmak" fiziksel olarak mumkun.

Bu betik araya girer: moderator yalnizca **ham** degerleri girer
(basari harfi, saniye, yanlis tiklama, 1-5 SUS cevaplari); turetilmis
her sayiyi - SUS puani, basari orani, ortalama sure - betik hesaplar.
Boylece SONUCLARI.md de digerleri gibi bir betik ciktisi olur.

Ikinci gorevi bir emniyet supabi: ornek dosya gercek veri sanilamaz,
pilot kosum da dis kosum gibi raporlanamaz.

Kullanim
--------
    .venv/Scripts/python.exe scripts/kullanilabilirlik_sonuclari.py
    .venv/Scripts/python.exe scripts/kullanilabilirlik_sonuclari.py --veri baska.json

Girdi : data/kullanilabilirlik/oturumlar.json  (sema: oturumlar.ornek.json)
Cikti : docs/KULLANILABILIRLIK-SONUCLARI.md
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

KOK = Path(__file__).resolve().parent.parent
VARSAYILAN_VERI = KOK / "data" / "kullanilabilirlik" / "oturumlar.json"
VARSAYILAN_CIKTI = KOK / "docs" / "KULLANILABILIRLIK-SONUCLARI.md"

# Gorev adi ve hedef sure (sn) - protokolden, tek kaynak burasi.
GOREVLER = [
    ("1", "Akıştan türetilmiş içerik bul", 45),
    ("2", "Payın gerekçesini kendi cümlesiyle söyle", 90),
    ("3", "Ölçülen bölgeyi göster", 60),
    ("4", "Remix üretip yayınla", 180),
    ("5", "Elindeki görselin kaynağını bul", 90),
    ("6", "Bir paya itiraz et", 90),
]

SUS_MADDELERI = [
    "Sık kullanmak isterim",
    "Gereksiz karmaşık",
    "Kullanımı kolaydı",
    "Teknik destek gerekir",
    "İşlevler bütünleşik",
    "Tutarsızlık fazla",
    "Çabuk öğrenilir",
    "Hantal",
    "Kendime güvendim",
    "Önce çok şey öğrenmem gerekti",
]

BASARI_ADI = {"T": "tam", "Y": "yardımla", "B": "başarısız"}


class Hata(Exception):
    """Veri kabul edilemez - betik durur, yarim belge uretmez."""


def sayi(deger: float, basamak: int = 1) -> str:
    """Turkce ondalik ayraci: 68.4 -> '68,4'."""
    return f"{deger:.{basamak}f}".replace(".", ",")


def yuzde(pay: int, toplam: int) -> str:
    if toplam == 0:
        return "—"
    return "%" + sayi(100.0 * pay / toplam)


def veriyi_oku(yol: Path) -> dict:
    if not yol.exists():
        ornek = VARSAYILAN_VERI.parent / "oturumlar.ornek.json"
        raise Hata(
            f"{yol} yok.\n"
            f"  Şema: {ornek}\n"
            f"  Kopyalayıp gerçek oturum verileriyle doldurun."
        )
    veri = json.loads(yol.read_text(encoding="utf-8"))

    if veri.get("_ornek"):
        raise Hata(
            "Bu dosya şema örneği (`_ornek: true`). Gerçek veri değil.\n"
            "  oturumlar.json olarak kopyalayın, `_ornek` alanını silin ve doldurun."
        )

    katilimcilar = veri.get("katilimcilar") or []
    if not katilimcilar:
        raise Hata("Katılımcı yok. En az bir oturum girilmeli.")

    for k in katilimcilar:
        kod = k.get("kod", "?")
        sus = k.get("sus") or []
        if len(sus) != 10:
            raise Hata(f"{kod}: SUS 10 cevap olmalı, {len(sus)} verilmiş.")
        if any(not isinstance(c, int) or not 1 <= c <= 5 for c in sus):
            raise Hata(f"{kod}: SUS cevapları 1-5 arası tam sayı olmalı.")
        for no, _, _ in GOREVLER:
            g = (k.get("gorevler") or {}).get(no)
            if not g:
                raise Hata(f"{kod}: görev {no} kaydı eksik.")
            if g.get("basari") not in BASARI_ADI:
                raise Hata(f"{kod}: görev {no} başarısı T/Y/B olmalı.")
            if not isinstance(g.get("sure"), int) or g["sure"] <= 0:
                raise Hata(
                    f"{kod}: görev {no} süresi girilmemiş. "
                    "Başarısız görevde 3 dakikalık sınır yazılır (180)."
                )
    return veri


def sus_puani(cevaplar: list[int]) -> float:
    """Tek numarali madde: cevap-1. Cift numarali: 5-cevap. Toplam x 2,5."""
    toplam = 0
    for i, cevap in enumerate(cevaplar, start=1):
        toplam += (cevap - 1) if i % 2 else (5 - cevap)
    return toplam * 2.5


def belge_uret(veri: dict) -> str:
    kosum = veri.get("kosum") or {}
    katilimcilar = veri["katilimcilar"]
    n = len(katilimcilar)
    pilot = kosum.get("tur") == "pilot"

    s: list[str] = []
    y = s.append

    y("# Kullanılabilirlik Testi Sonuçları")
    y("")
    y("> Bu belge elle düzenlenmez. Ham kayıtlar")
    y("> `data/kullanilabilirlik/oturumlar.json` içindedir; buradaki her türetilmiş sayı")
    y("> `scripts/kullanilabilirlik_sonuclari.py` tarafından hesaplanır.")
    y("")

    if pilot:
        y("> ## ⚠️ PİLOT KOŞUM — KULLANILABİLİRLİK SONUCU DEĞİLDİR")
        y(">")
        y("> Bu oturumlar **takım içinde** koşuldu. Amaç görev metinlerinin")
        y("> anlaşılırlığını, süre sınırlarının gerçekçiliğini ve demo verisinin")
        y("> görevlere uygunluğunu denemekti. Katılımcılar ürünü önceden bildiği için")
        y("> **buradaki hiçbir sayı** kullanılabilirlik ölçümü olarak sunulamaz ve teknik")
        y("> raporun 3.3 bölümüne sonuç olarak girmez. Rapora yalnızca *protokol pilot")
        y("> oturumla denendi* ifadesiyle girer.")
        y("")

    y("## Koşum bilgileri")
    y("")
    y("| | |")
    y("|---|---|")
    y(f"| Koşum türü | {'Pilot (takım içi)' if pilot else 'Dış katılımcı'} |")
    y(f"| Tarih aralığı | {kosum.get('tarih_araligi', '—')} |")
    y(f"| Oturumu yöneten | {kosum.get('yoneten', '—')} |")
    y(f"| Prototip sürümü (commit) | {kosum.get('commit', '—')} |")
    y(f"| Ortam | {kosum.get('ortam', '—')} |")
    y(f"| Katılımcı sayısı | **{n}** |")
    y("")

    y("## Katılımcılar")
    y("")
    y('İsim yazılmaz. Tarama soruları protokol §"Tarama soruları"nda.')
    y("")
    y(
        "| Kod | Profil | Haftalık paylaşım | Düzenleyip paylaştı "
        "| Atıf aracı deneyimi | Cihaz |"
    )
    y("|---|---|---|---|---|---|")
    for k in katilimcilar:
        y(
            f"| {k['kod']} | {k.get('profil', '—')} | {k.get('haftalik_paylasim', '—')} "
            f"| {k.get('duzenleyip_paylasti', '—')} "
            f"| {k.get('atif_araci_deneyimi', '—')} | {k.get('cihaz', '—')} |"
        )
    dokunmatik = sum(1 for k in katilimcilar if k.get("dokunmatik"))
    y("")
    y(f"Dokunmatik cihazda koşulan oturum: **{dokunmatik}** / {n}")
    y("")

    y("## Görev sonuçları")
    y("")
    y("Başarı: **T** tam · **Y** yardımla · **B** başarısız (3 dk doldu).")
    y("Başarısız görevlerde süre 3 dakikalık sınıra (180 sn) sabitlenir; ortalamalar bu")
    y("değerle hesaplanır, yani gerçek süreyi değil **en iyi ihtimali** gösterir.")
    y("")

    kodlar = [k["kod"] for k in katilimcilar]
    ozet: list[tuple] = []

    for no, ad, hedef in GOREVLER:
        kayitlar = [k["gorevler"][no] for k in katilimcilar]
        tam = sum(1 for g in kayitlar if g["basari"] == "T")
        yard = sum(1 for g in kayitlar if g["basari"] == "Y")
        bas = sum(1 for g in kayitlar if g["basari"] == "B")
        ort_sure = sum(g["sure"] for g in kayitlar) / n
        ort_tik = sum(g.get("yanlis_tiklama", 0) for g in kayitlar) / n
        ozet.append((no, ad, hedef, tam, yard, bas, ort_sure))

        y(f"### Görev {no} — {ad} · hedef {hedef} sn")
        y("")
        if no == "2":
            y("> Oturumun en önemli görevi: açıklanabilirlik iddiası burada sınanıyor.")
            y("")
        y("| | " + " | ".join(kodlar) + " | Ortalama |")
        y("|---|" + "---|" * (n + 1))
        y(
            "| Başarı | "
            + " | ".join(g["basari"] for g in kayitlar)
            + f" | {tam}/{n} tam |"
        )
        y(
            "| Süre (sn) | "
            + " | ".join(str(g["sure"]) for g in kayitlar)
            + f" | {sayi(ort_sure)} |"
        )
        y(
            "| Yanlış tıklama | "
            + " | ".join(str(g.get("yanlis_tiklama", 0)) for g in kayitlar)
            + f" | {sayi(ort_tik)} |"
        )
        y("")
        notlar = [(k["kod"], k["gorevler"][no].get("not", "")) for k in katilimcilar]
        notlar = [(kod, m) for kod, m in notlar if m.strip()]
        if notlar:
            for kod, m in notlar:
                y(f"- **{kod}:** {m}")
            y("")

    y("### Toplu görev tablosu")
    y("")
    y("| Görev | Tam | Yardımla | Başarısız | Ortalama süre | Hedef |")
    y("|---|--:|--:|--:|--:|--:|")
    for no, ad, hedef, tam, yard, bas, ort_sure in ozet:
        isaret = "" if ort_sure <= hedef else " ⚠"
        y(
            f"| {no} · {ad} | {tam} | {yard} | {bas} "
            f"| {sayi(ort_sure)} sn{isaret} | {hedef} sn |"
        )
    toplam_deneme = n * len(GOREVLER)
    toplam_tam = sum(o[3] for o in ozet)
    toplam_yard = sum(o[4] for o in ozet)
    y("")
    y(
        f"**Görev başarı oranı:** {toplam_tam}/{toplam_deneme} tam = "
        f"**{yuzde(toplam_tam, toplam_deneme)}** "
        f"(yardımla tamamlananlar dahil edilirse "
        f"{yuzde(toplam_tam + toplam_yard, toplam_deneme)})."
    )
    y("Rapora giren sayı, yardımsız tamamlanan orandır — daha katı olan budur.")
    y("")

    y("## SUS")
    y("")
    y("Ham cevaplar (1 = kesinlikle katılmıyorum … 5 = kesinlikle katılıyorum):")
    y("")
    y("| Madde | " + " | ".join(kodlar) + " |")
    y("|---|" + "---|" * n)
    for i, madde in enumerate(SUS_MADDELERI):
        y(
            f"| {i + 1} · {madde} | "
            + " | ".join(str(k["sus"][i]) for k in katilimcilar)
            + " |"
        )
    y("")
    puanlar = [sus_puani(k["sus"]) for k in katilimcilar]
    ortalama = sum(puanlar) / n
    y("| | " + " | ".join(kodlar) + " | **Ortalama** |")
    y("|---|" + "---|" * (n + 1))
    y(
        "| SUS puanı | "
        + " | ".join(sayi(p) for p in puanlar)
        + f" | **{sayi(ortalama)}** |"
    )
    y("")
    y("Puanlama: tek numaralı maddelerde `cevap − 1`, çift numaralı maddelerde")
    y("`5 − cevap`; on değer toplanıp 2,5 ile çarpılır. Bu bir yüzde değildir.")
    y("")
    karar = "hedefin üzerinde" if ortalama >= 68 else "hedefin altında"
    y(f"Hedef ≥ 68 (sektör ortalaması). Sonuç: **{sayi(ortalama)}** — {karar}.")
    y("")

    y("## Açık sorular")
    y("")
    sorular = [
        ("ne_yapiyor", '**"Bu uygulama ne yapıyor?"** — her katılımcının cevabı birebir:'),
        ("kafa_karistiran", '**"En kafa karıştırıcı şey neydi?"**'),
        ("yukler_miydiniz", '**"Kendi içeriğinizi yükler miydiniz? Neden?"**'),
    ]
    for anahtar, baslik in sorular:
        y(baslik)
        y("")
        for k in katilimcilar:
            cevap = (k.get("acik") or {}).get(anahtar, "").strip() or "—"
            y(f"- {k['kod']}: {cevap}")
        y("")

    y("## Bulgular")
    y("")
    y("Ağırlık sırasına göre. Düzeltilenler `ERISILEBILIRLIK.md`'deki")
    y("*bulgu → değişiklik → doğrulama* deseniyle kaydedilir.")
    y("")
    bulgular = [b for b in (veri.get("bulgular") or []) if (b.get("bulgu") or "").strip()]
    if bulgular:
        y("| # | Bulgu | Kaç katılımcı | Ağırlık | Durum |")
        y("|--:|---|--:|---|---|")
        for i, b in enumerate(bulgular, start=1):
            y(
                f"| {i} | {b['bulgu']} | {b.get('kac_katilimci', '—')} "
                f"| {b.get('agirlik', '—')} | {b.get('durum', '—')} |"
            )
    else:
        y("*(Oturumlardan bulgu kaydedilmedi.)*")
    y("")

    y("## Bu sonuçların sınırları")
    y("")
    if pilot:
        y("- **Katılımcılar ürünü biliyordu.** Pilot koşumun amacı düzeneği denemekti;")
        y("  öğrenilebilirlik ve keşfedilebilirlik ölçülemez.")
    else:
        y(f"- **{n} katılımcı istatistik vermez.** SUS puanı bir eğilim göstergesidir;")
        y("  güven aralığı hesaplanacak kadar örneklem yok.")
        if n < 5:
            y(f"- **Protokol beş katılımcı öngörüyordu, {n} kişiyle koşuldu.** Nielsen'in")
            y("  beş kişide yaklaşık %85 kusur yakalama bulgusu bu örneklemde geçerli")
            y("  değil; bulunmayan kusurların olduğu varsayılmalıdır.")
        y("- **Katılımcılar tanıdık çevreden geliyor.** Nezaket yanlılığı SUS'u yukarı")
        y("  çeker. Görev başarısı ve süre bu yanlılıktan daha az etkilenir; asıl ağırlık")
        y("  onlarda.")
    y("")

    return "\n".join(s) + "\n"


def rapor_blogu(veri: dict) -> str:
    """Teknik raporun 3.3 bolumune yapistirilacak dort sayi."""
    katilimcilar = veri["katilimcilar"]
    n = len(katilimcilar)
    toplam_deneme = n * len(GOREVLER)
    toplam_tam = sum(
        1
        for k in katilimcilar
        for no, _, _ in GOREVLER
        if k["gorevler"][no]["basari"] == "T"
    )
    gerekce = sum(1 for k in katilimcilar if k["gorevler"]["2"]["basari"] == "T")
    ortalama = sum(sus_puani(k["sus"]) for k in katilimcilar) / n
    return "\n".join(
        [
            "| Ölçüt | Sonuç |",
            "|---|---|",
            f"| Katılımcı sayısı | {n} |",
            f"| Görev başarı oranı (altı görev ortalaması) "
            f"| {yuzde(toplam_tam, toplam_deneme)} |",
            f"| Payın gerekçesini doğru anlatan katılımcı | {gerekce} / {n} |",
            f"| SUS skoru (hedef ≥ 68) | {sayi(ortalama)} |",
        ]
    )


def main() -> int:
    ayristirici = argparse.ArgumentParser(description="Kullanilabilirlik sonuc belgesi")
    ayristirici.add_argument("--veri", type=Path, default=VARSAYILAN_VERI)
    ayristirici.add_argument("--cikti", type=Path, default=VARSAYILAN_CIKTI)
    arg = ayristirici.parse_args()

    try:
        veri = veriyi_oku(arg.veri)
    except Hata as exc:
        print(f"HATA: {exc}")
        return 1

    arg.cikti.write_text(belge_uret(veri), encoding="utf-8")
    n = len(veri["katilimcilar"])
    print(f"✓ {arg.cikti}  ({n} katılımcı)")

    if (veri.get("kosum") or {}).get("tur") == "pilot":
        print("\nPİLOT koşum — teknik raporun 3.3 bölümüne sonuç olarak GİRMEZ.")
        return 0

    print("\nTeknik rapor 3.3'e yapıştırılacak blok:\n")
    print(rapor_blogu(veri))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
