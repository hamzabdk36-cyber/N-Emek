# Uçtan Uca Gecikme — Altın Senaryo

**Tarih:** 08.08.2026 20:59  
**Ortam:** cuda, indeks 200 içerik  
**Üreten:** `backend/eval/run_latency.py` — bu dosya elle düzenlenmez.

Senaryo **5** kez baştan koşuldu. Ölçüm sırasında indekste **200** içerik vardı; aday arama ve geometrik doğrulama maliyeti indeks büyüklüğüne bağlı olduğu için boş bir indekste ölçüm yanıltıcı olurdu.

Süreler sunucu tarafıdır: ağ, dosya yükleme ve arayüz çizimi dahil değildir.

---

## Adım başına süre

| # | Adım | Ne yapılıyor | Ortalama | En hızlı | En yavaş |
|---|---|---|---|---|---|
| 1 | **Özgün içerik yükleme** | filigran + C2PA imzalama + indeksleme | **666 ms** | 578 ms | 719 ms |
| 2 | **Remix yükleme** | kaynak beyanlı, zincir kurulur ve alan ölçülür | **569 ms** | 417 ms | 863 ms |
| 3 | **Kimliksiz içerik yükleme** | manifest silinmiş; tam kurtarma hattı | **476 ms** | 413 ms | 587 ms |
| 4 | **Emek Kartı üretimi** | zincir yürütme + pay hesabı + açıklamalar | **6 ms** | 2 ms | 10 ms |
| 5 | **Kampanya dağıtımı** | havuzun tüm içeriğe bölüştürülmesi | **31 ms** | 17 ms | 52 ms |
| 6 | **İtiraz çözümü** | SIFT ile yeniden ölçüm | **79 ms** | 75 ms | 84 ms |

Senaryonun tamamı (altı adım): **1826 ms**

---

## Kurtarma hattının aşama dağılımı

Üç yükleme adımının içindeki köken kurtarma hattı, aşama aşama. Kimliksiz yükleme, hattın tamamının çalıştığı en ağır durumdur.

| Aşama | Özgün içerik yükleme | Remix yükleme | Kimliksiz içerik yükleme |
|---|---|---|---|
| c2pa | 8,5 ms | 0,7 ms | 0,7 ms |
| fingerprint | 29,3 ms | 11,8 ms | 10,5 ms |
| watermark | 17,4 ms | 17,0 ms | 17,5 ms |
| embed | 89,2 ms | 82,3 ms | 62,7 ms |
| phash_search | 151,4 ms | 103,8 ms | 72,7 ms |
| clip_search | 0,6 ms | 0,5 ms | 0,6 ms |
| geometry | 152,1 ms | 142,1 ms | 116,5 ms |

---

## Yorum

En ağır adım **özgün içerik yükleme**: ortalama 666 ms. Üç yükleme adımının hepsi köken kurtarma hattının tamamını koşar — özgün bir içerik yüklenirken bile, çünkü sistem yükleyenin sözüne değil ölçüme bakar: kaynak olmadığını *doğrulamak* da kaynak bulmak kadar iş.

Özgün yükleme, kimliksiz yüklemeden 190 ms daha uzun sürüyor. Aradaki farkın kaynağı yalnızca yayın adımları (filigran gömme, C2PA imzalama, indeksleme) değil; geometri aşaması da burada daha pahalı, çünkü doğrulanacak adayların hepsi yanlış çıkıyor ve her biri eleninceye kadar tam maliyetini ödetiyor. Gerçek kaynak bulunduğunda ise eşleşme erken ve güçlü oluyor.

Pay hesabı tarafı (Emek Kartı + kampanya dağıtımı) toplam 37 ms — görsel işleme içermediği için milisaniyeler mertebesinde. Sistemin maliyeti tamamen köken kurtarmada. Bu da ölçeklendirmenin nereden yapılacağını söylüyor: aday arama indeksi (bugün kaba kuvvet FAISS) ve geometrik doğrulamaya giden aday sayısı (`max_geometry_candidates`).

Kullanıcı deneyimi açısından anlamlı sayı, yükleme adımlarının yarım saniye civarında olması: bu, yüklemeden sonra zincir önerisinin **beklemeden** gösterilebileceği anlamına geliyor. Kuyruğa alıp sonra bildirim göndermek gerekmiyor.

