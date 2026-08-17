# Sınıflama Metrikleri — Kesinlik, Duyarlılık, F1

**Kaynak koşum:** 08.08.2026 21:49 · cuda, korpus 320 görsel  
**Üreten:** `scripts/kurtarma_f1.py` — bu dosya elle düzenlenmez.

Sayılar `data/eval/sonuclar.json` içindeki tam sayı sayaçlardan çıkıyor; `DEGERLENDIRME.md` ile **aynı koşumu** anlatıyor, farklı bir ölçüm değil.

## Sayım nasıl yapılıyor

Sayım bağ düzeyinde. Her pozitif sorgunun tek bir doğru cevabı var: türevin üretildiği kaynak. Negatif kontrol sorgularının doğru cevabı **hiçbir bağ** — orada önerilen her bağ yanlış pozitiftir.

```
doğru pozitif  = önerilen bağ − yanlış bağ
yanlış pozitif = yanlış bağ + negatif kontrolde önerilen bağ
yanlış negatif = pozitif sorgu − doğru pozitif
```

Bu projede yanlış pozitif, yanlış negatiften **ağır** bir hatadır: birine ait olmayan bir içerikten pay vermek üçüncü bir tarafa haksızlık eder; kaçırılan bir atıf ise itirazla düzeltilebilir. Eşikler bu yönde ayarlandı.

**Bu tablo, `DEGERLENDIRME.md`'deki yanlış atıf oranından daha katı bir ölçüdür ve öyle olması amaçlandı.** Orada payda tüm sorgular, pay ise yanlış Top-1 ile negatif kontrol bağlarıdır. Burada payda önerilen tüm bağlar, ve gerçek kaynağın *yanında* önerilen her fazladan bağ da yanlış pozitif sayılır — doğru kaynak bulunmuş olsa bile. İki sayı çelişmiyor; farklı soruları yanıtlıyorlar: "sistem yanlış birine pay verdi mi" ile "önerdiği her bağ doğru muydu".

---

## Senaryo başına

| Senaryo | Kesinlik | Duyarlılık | F1 | DP | YP | YN |
|---|---|---|---|--:|--:|--:|
| orijinal | %96,9 | %100,0 | 0,9842 | 280 | 9 | 0 |
| jpeg_q50 | %97,2 | %100,0 | 0,9859 | 280 | 8 | 0 |
| jpeg_q30 | %97,9 | %100,0 | 0,9894 | 280 | 6 | 0 |
| olcek_%50 | %94,3 | %100,0 | 0,9705 | 280 | 17 | 0 |
| olcek_%25 | %86,3 | %96,4 | 0,9106 | 270 | 43 | 10 |
| kirpma_%90 | %96,9 | %100,0 | 0,9842 | 280 | 9 | 0 |
| kirpma_%70 | %97,5 | %99,3 | 0,9841 | 278 | 7 | 2 |
| kirpma_%50 | %97,9 | %97,9 | 0,9786 | 274 | 6 | 6 |
| kirpma_%30 | %94,9 | %92,5 | 0,9367 | 259 | 14 | 21 |
| yazi_bandi | %97,9 | %100,0 | 0,9894 | 280 | 6 | 0 |
| sticker | %97,6 | %100,0 | 0,9877 | 280 | 7 | 0 |
| meme | %98,2 | %100,0 | 0,9912 | 280 | 5 | 0 |
| agir_renk | %97,2 | %100,0 | 0,9859 | 280 | 8 | 0 |
| gri_ton | %97,2 | %100,0 | 0,9859 | 280 | 8 | 0 |
| dondurme_5d | %95,9 | %99,6 | 0,9772 | 279 | 12 | 1 |
| dondurme_15d | %95,5 | %99,3 | 0,9737 | 278 | 13 | 2 |
| ayna | %97,6 | %99,6 | 0,9859 | 279 | 7 | 1 |
| ekran_goruntusu | %97,5 | %98,6 | 0,9805 | 276 | 7 | 4 |
| kolaj | %96,9 | %99,6 | 0,9824 | 279 | 9 | 1 |
| kirpma+yazi | %97,7 | %91,1 | 0,9427 | 255 | 6 | 25 |
| **Tümü** | **%96,39** | **%98,70** | **0,9753** | **5527** | **207** | **73** |

---

## Okuma

Genel F1 **0,9753**; kesinlik %96,39, duyarlılık %98,70. Toplam 5600 doğru bağın 73 tanesi kaçırıldı, 207 yanlış bağ önerildi.

Hatanın ağırlıklı tarafı **yanlış pozitif (fazladan önerilen bağ)**: 207 yanlış pozitife karşı 73 yanlış negatif.

En zayıf senaryo **olcek_%25** — F1 0,9106 (kesinlik %86,3, duyarlılık %96,4). Zayıf taraf **kesinlik**: 270 doğru bağa karşı 43 yanlış pozitif ve 10 kaçırılan bağ.
