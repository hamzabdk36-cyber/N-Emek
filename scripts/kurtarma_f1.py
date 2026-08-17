"""Koken kurtarmanin siniflama metriklerini (kesinlik/duyarlilik/F1) hesaplar.

Neden ayri bir betik
--------------------
`DEGERLENDIRME.md` Top-1, Top-5, yanlis atif orani ve kapsama MAE'sini
veriyor. Sartnamenin rapor sablonu 3.2'de bunlara ek olarak acikca
"F1 vb." istiyor.

Bu sayilar `backend/eval/run_benchmark.py`'nin urettigi
`data/eval/sonuclar.json` icindeki **tam sayilardan** cikiyor:
`onerilen_bag`, `yanlis_bag`, `negatif_bag`, `bulundu`, `pozitif_sorgu`.
Yani 6.400 sorgunun yeniden kosulmasi gerekmiyor - o kosu 43,5 dakika
surmustu ve GPU istiyor.

Neden `write_report`'a eklenmedi: o fonksiyon gecikme yuzdeliklerini ham
listelerden hesapliyor, listeler JSON'da yok. Sadece raporu yeniden
uretmek icin listeleri "yeniden uydurmak" gerekirdi ve p50 yanlis
cikardi. Bu projede yanlis bir sayi, eksik bir sayidan kotudur.

Tanimlar
--------
Sayim **bag duzeyinde**. Her pozitif sorgunun tek bir dogru cevabi var
(turevin uretildigi kaynak); negatif kontrol sorgularinin dogru cevabi
"hicbir bag".

    DP (dogru pozitif)  = onerilen_bag - yanlis_bag
    YP (yanlis pozitif) = yanlis_bag + negatif_bag
    YN (yanlis negatif) = pozitif_sorgu - DP

`negatif_bag` `onerilen_bag`'in **icinde degil**: `evaluate()` pozitif ve
holdout sorgularini ayri sayiyor (`run_benchmark.py:331` ve `:360`).
Ikisini toplamak gerekiyor, yoksa holdout'ta uretilen sahte baglar
kesinligin disinda kalirdi.

Kullanim
--------
    .venv/Scripts/python.exe scripts/kurtarma_f1.py
    .venv/Scripts/python.exe scripts/kurtarma_f1.py --yaz
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[1]
SONUCLAR = ROOT / "data" / "eval" / "sonuclar.json"
CIKTI = ROOT / "docs" / "SINIFLAMA-METRIKLERI.md"


def _tr(deger: float, basamak: int = 1) -> str:
    return f"{deger:.{basamak}f}".replace(".", ",")


def olc(senaryo: dict) -> tuple[int, int, int]:
    """Bir senaryo icin (DP, YP, YN)."""
    onerilen = senaryo["onerilen_bag"]
    yanlis = senaryo["yanlis_bag"]
    negatif = senaryo["negatif_bag"]
    pozitif = senaryo["pozitif_sorgu"]

    dogru_pozitif = onerilen - yanlis
    yanlis_pozitif = yanlis + negatif
    yanlis_negatif = pozitif - dogru_pozitif
    return dogru_pozitif, yanlis_pozitif, yanlis_negatif


def oranlar(dp: int, yp: int, yn: int) -> tuple[float, float, float]:
    kesinlik = dp / (dp + yp) if (dp + yp) else 0.0
    duyarlilik = dp / (dp + yn) if (dp + yn) else 0.0
    f1 = 2 * kesinlik * duyarlilik / (kesinlik + duyarlilik) if (kesinlik + duyarlilik) else 0.0
    return kesinlik, duyarlilik, f1


def rapor(veri: dict) -> list[str]:
    meta = veri["meta"]
    senaryolar = veri["senaryolar"]

    satirlar: list[str] = []
    ekle = satirlar.append

    ekle("# Sınıflama Metrikleri — Kesinlik, Duyarlılık, F1")
    ekle("")
    ekle(f"**Kaynak koşum:** {meta['tarih']} · {meta['ortam']}  ")
    ekle("**Üreten:** `scripts/kurtarma_f1.py` — bu dosya elle düzenlenmez.")
    ekle("")
    ekle(
        "Sayılar `data/eval/sonuclar.json` içindeki tam sayı sayaçlardan çıkıyor; "
        "`DEGERLENDIRME.md` ile **aynı koşumu** anlatıyor, farklı bir ölçüm değil."
    )
    ekle("")
    ekle("## Sayım nasıl yapılıyor")
    ekle("")
    ekle(
        "Sayım bağ düzeyinde. Her pozitif sorgunun tek bir doğru cevabı var: türevin "
        "üretildiği kaynak. Negatif kontrol sorgularının doğru cevabı **hiçbir bağ** — "
        "orada önerilen her bağ yanlış pozitiftir."
    )
    ekle("")
    ekle("```")
    ekle("doğru pozitif  = önerilen bağ − yanlış bağ")
    ekle("yanlış pozitif = yanlış bağ + negatif kontrolde önerilen bağ")
    ekle("yanlış negatif = pozitif sorgu − doğru pozitif")
    ekle("```")
    ekle("")
    ekle(
        "Bu projede yanlış pozitif, yanlış negatiften **ağır** bir hatadır: birine ait "
        "olmayan bir içerikten pay vermek üçüncü bir tarafa haksızlık eder; kaçırılan "
        "bir atıf ise itirazla düzeltilebilir. Eşikler bu yönde ayarlandı."
    )
    ekle("")
    ekle(
        "**Bu tablo, `DEGERLENDIRME.md`'deki yanlış atıf oranından daha katı bir "
        "ölçüdür ve öyle olması amaçlandı.** Orada payda tüm sorgular, pay ise yanlış "
        "Top-1 ile negatif kontrol bağlarıdır. Burada payda önerilen tüm bağlar, ve "
        "gerçek kaynağın *yanında* önerilen her fazladan bağ da yanlış pozitif sayılır "
        "— doğru kaynak bulunmuş olsa bile. İki sayı çelişmiyor; farklı soruları "
        "yanıtlıyorlar: \"sistem yanlış birine pay verdi mi\" ile \"önerdiği her bağ "
        "doğru muydu\"."
    )
    ekle("")
    ekle("---")
    ekle("")
    ekle("## Senaryo başına")
    ekle("")
    ekle("| Senaryo | Kesinlik | Duyarlılık | F1 | DP | YP | YN |")
    ekle("|---|---|---|---|--:|--:|--:|")

    toplam_dp = toplam_yp = toplam_yn = 0
    for ad, senaryo in senaryolar.items():
        dp, yp, yn = olc(senaryo)
        toplam_dp += dp
        toplam_yp += yp
        toplam_yn += yn
        kesinlik, duyarlilik, f1 = oranlar(dp, yp, yn)
        ekle(
            f"| {ad} | %{_tr(kesinlik * 100)} | %{_tr(duyarlilik * 100)} | "
            f"{_tr(f1, 4)} | {dp} | {yp} | {yn} |"
        )

    kesinlik, duyarlilik, f1 = oranlar(toplam_dp, toplam_yp, toplam_yn)
    ekle(
        f"| **Tümü** | **%{_tr(kesinlik * 100, 2)}** | **%{_tr(duyarlilik * 100, 2)}** | "
        f"**{_tr(f1, 4)}** | **{toplam_dp}** | **{toplam_yp}** | **{toplam_yn}** |"
    )
    ekle("")
    ekle("---")
    ekle("")
    ekle("## Okuma")
    ekle("")
    ekle(
        f"Genel F1 **{_tr(f1, 4)}**; kesinlik %{_tr(kesinlik * 100, 2)}, duyarlılık "
        f"%{_tr(duyarlilik * 100, 2)}. Toplam {toplam_dp + toplam_yn} doğru bağın "
        f"{toplam_yn} tanesi kaçırıldı, {toplam_yp} yanlış bağ önerildi."
    )
    ekle("")

    # Hangi tarafin baskin oldugu sayidan okunuyor. Sabit bir yorum
    # yazmak, siralama degistiginde sessizce yanlisa donusurdu.
    baskin = (
        "yanlış pozitif (fazladan önerilen bağ)"
        if toplam_yp > toplam_yn
        else "yanlış negatif (kaçırılan bağ)"
    )
    ekle(
        f"Hatanın ağırlıklı tarafı **{baskin}**: {toplam_yp} yanlış pozitife karşı "
        f"{toplam_yn} yanlış negatif."
    )
    ekle("")

    en_zayif = min(senaryolar.items(), key=lambda kv: oranlar(*olc(kv[1]))[2])
    zdp, zyp, zyn = olc(en_zayif[1])
    zk, zd, zf = oranlar(zdp, zyp, zyn)
    zayif_yon = (
        "kesinlik" if zk < zd else "duyarlılık" if zd < zk else "her iki taraf da eşit"
    )
    ekle(
        f"En zayıf senaryo **{en_zayif[0]}** — F1 {_tr(zf, 4)} (kesinlik "
        f"%{_tr(zk * 100)}, duyarlılık %{_tr(zd * 100)}). Zayıf taraf **{zayif_yon}**: "
        f"{zdp} doğru bağa karşı {zyp} yanlış pozitif ve {zyn} kaçırılan bağ."
    )
    ekle("")
    return satirlar


def main() -> int:
    ayristirici = argparse.ArgumentParser(description=__doc__)
    ayristirici.add_argument("--yaz", action="store_true", help=f"{CIKTI.name} dosyasını üret")
    args = ayristirici.parse_args()

    if not SONUCLAR.exists():
        print(f"bulunamadı: {SONUCLAR}")
        print("  önce: python -m eval.run_benchmark  (backend/ içinden)")
        return 2

    veri = json.loads(SONUCLAR.read_text(encoding="utf-8"))
    satirlar = rapor(veri)

    if args.yaz:
        CIKTI.write_text("\n".join(satirlar), encoding="utf-8")
        print(f"✓ {CIKTI.relative_to(ROOT).as_posix()}")
    else:
        print("\n".join(satirlar))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
