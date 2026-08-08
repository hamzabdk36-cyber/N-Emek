# Kapsamlı Değerlendirme — Köken Kurtarma Hattı

**Tarih:** 08.08.2026 21:49  
**Ortam:** cuda, korpus 320 görsel  
**Üreten:** `backend/eval/run_benchmark.py` — bu dosya elle düzenlenmez.

İndekste **280** yayınlanmış içerik var. **280** içeriğin ve indekste bulunmayan **40** içeriğin her biri **20** türev senaryosundan geçirildi: toplam **6400** sorgu.

Her sorgu, üretimdeki `recovery.recover()` fonksiyonunun kendisinden geçer; ölçülen davranış, bir kullanıcı görsel yüklediğinde çalışan davranışın aynısıdır.

### Ölçüm kurgusu

Korpustaki her görsel önce platformun yayın adımlarından geçirildi (görünmez filigran gömüldü, C2PA manifesti imzalandı) ve türevler bu **yayınlanmış** hâlden üretildi. Türev üretimi piksel dizisi üzerinde çalıştığı için manifest ve tüm metadata siliniyor — yani hattın 0. aşaması hiçbir sorguda tetiklenmiyor. Ölçülen şey saf **kurtarma** başarısıdır: içerik kimliği silinmiş bir dosyada kaynağı bulabiliyor muyuz.

**Negatif kontrol:** holdout görselleri indekse hiç alınmadı. Bu sorgularda önerilen *herhangi bir* bağ yanlış atıftır. Bu projede yanlış atıf, kaçırılmış atıftan daha ağır bir hatadır; tabloların en önemli sütunu budur.

---

## Özet

| Metrik | Sonuç |
|---|---|
| Ortalama Top-1 doğruluk | **%98,7** |
| Ortalama Top-5 doğruluk | **%98,7** |
| Yanlış atıf oranı (yanlış Top-1 + negatif kontrol bağları) | **%0,86** (55 / 6400) |
| Kapsama ölçüm hatası (MAE) | **0,0241** (5519 ölçüm, hedef ≤ 0,05) |
| Uçtan uca gecikme | p50 **386 ms** · p95 703 ms |

---

## Senaryo başına doğruluk

| Senaryo | Top-1 | Top-5 | Bulundu | Yanlış Top-1 | Negatif kontrol bağı |
|---|---|---|---|---|---|
| orijinal | %100,0 | %100,0 | %100,0 | 0 | 3 |
| jpeg_q50 | %100,0 | %100,0 | %100,0 | 0 | 4 |
| jpeg_q30 | %100,0 | %100,0 | %100,0 | 0 | 2 |
| olcek_%50 | %99,6 | %100,0 | %100,0 | 1 | 0 |
| olcek_%25 | %96,4 | %96,4 | %96,4 | 1 | 5 |
| kirpma_%90 | %100,0 | %100,0 | %100,0 | 0 | 2 |
| kirpma_%70 | %99,3 | %99,3 | %99,3 | 0 | 2 |
| kirpma_%50 | %97,9 | %97,9 | %97,9 | 0 | 2 |
| kirpma_%30 | %92,5 | %92,5 | %92,5 | 1 | 4 |
| yazi_bandi | %100,0 | %100,0 | %100,0 | 0 | 2 |
| sticker | %100,0 | %100,0 | %100,0 | 0 | 3 |
| meme | %100,0 | %100,0 | %100,0 | 0 | 2 |
| agir_renk | %100,0 | %100,0 | %100,0 | 0 | 4 |
| gri_ton | %100,0 | %100,0 | %100,0 | 0 | 3 |
| dondurme_5d | %99,6 | %99,6 | %99,6 | 0 | 4 |
| dondurme_15d | %99,3 | %99,3 | %99,3 | 0 | 4 |
| ayna | %99,6 | %99,6 | %99,6 | 0 | 3 |
| ekran_goruntusu | %98,6 | %98,6 | %98,6 | 0 | 1 |
| kolaj | %99,6 | %99,6 | %99,6 | 0 | 1 |
| kirpma+yazi | %91,1 | %91,1 | %91,1 | 0 | 1 |
| **Ortalama** | **%98,7** | **%98,7** | | **3** | **52** |

---

## Kullanılan alan oranı ölçümü

Katkı payı motorunun girdisi bu sayıdır. Beklenen değer, türevi üreten dönüşümün geometrisinden hesaplanır (`eval/attacks.py: EXPECTED_COVERAGE`).

| Senaryo | Beklenen | Ölçülen (ort.) | MAE | Ölçülen / ölçülemeyen |
|---|---|---|---|---|
| orijinal | 1,00 | 1,000 | **0,0000** | 280 / 0 |
| jpeg_q50 | 1,00 | 0,995 | **0,0049** | 279 / 1 |
| jpeg_q30 | 1,00 | 0,990 | **0,0101** | 279 / 1 |
| olcek_%50 | 1,00 | 0,956 | **0,0437** | 277 / 3 |
| olcek_%25 | 1,00 | 0,875 | **0,1245** ⚠ | 270 / 0 |
| kirpma_%90 | 1,00 | 0,992 | **0,0081** | 280 / 0 |
| kirpma_%70 | 1,00 | 0,989 | **0,0107** | 278 / 0 |
| kirpma_%50 | 1,00 | 0,978 | **0,0224** | 274 / 0 |
| kirpma_%30 | 1,00 | 0,977 | **0,0235** | 259 / 0 |
| yazi_bandi | 0,84 | 0,881 | **0,0422** | 279 / 1 |
| sticker | 0,94 | 0,956 | **0,0186** | 280 / 0 |
| meme | 0,78 | 0,768 | **0,0123** | 280 / 0 |
| agir_renk | 1,00 | 0,965 | **0,0351** | 278 / 2 |
| gri_ton | 1,00 | 1,000 | **0,0000** | 280 / 0 |
| dondurme_5d | 0,96 | 0,937 | **0,0230** | 279 / 0 |
| dondurme_15d | 0,89 | 0,874 | **0,0163** | 278 / 0 |
| ayna | 1,00 | 0,997 | **0,0032** | 279 / 0 |
| ekran_goruntusu | 1,00 | 0,973 | **0,0275** | 276 / 0 |
| kolaj | 0,50 | 0,484 | **0,0156** | 279 / 0 |
| kirpma+yazi | 0,84 | 0,855 | **0,0450** | 255 / 0 |

Genel MAE: **0,0241** (hedef ≤ 0,05)

---

## Kararın hangi aşamadan geldiği

Doğru bulunan bağlarda, en güçlü kanıtı hangi aşamanın ürettiği. Aşamaların iş bölümünü gösterir: filigran piksel düzeni korunmuşsa kesin kanıt verir, geometrik dönüşümlerde devreyi CLIP ve homografi devralır.

| Aşama | Kaç kararda belirleyici oldu | Oran |
|---|---|---|
| clip | 2440 | %44,2 |
| watermark | 2194 | %39,7 |
| phash | 892 | %16,1 |

---

## Gecikme

| Senaryo | p50 (ms) | p95 (ms) |
|---|---|---|
| orijinal | 455 | 777 |
| jpeg_q50 | 422 | 763 |
| jpeg_q30 | 419 | 716 |
| olcek_%50 | 251 | 484 |
| olcek_%25 | 150 | 283 |
| kirpma_%90 | 417 | 803 |
| kirpma_%70 | 320 | 619 |
| kirpma_%50 | 272 | 467 |
| kirpma_%30 | 222 | 376 |
| yazi_bandi | 437 | 696 |
| sticker | 392 | 635 |
| meme | 493 | 789 |
| agir_renk | 387 | 664 |
| gri_ton | 422 | 709 |
| dondurme_5d | 424 | 795 |
| dondurme_15d | 405 | 727 |
| ayna | 480 | 810 |
| ekran_goruntusu | 254 | 451 |
| kolaj | 514 | 737 |
| kirpma+yazi | 271 | 491 |

### Aşama başına ortalama süre

| Aşama | Ortalama (ms) | Toplamdaki payı |
|---|---|---|
| phash_search | 129,1 | %32,3 |
| geometry | 120,8 | %30,3 |
| embed | 115,3 | %28,9 |
| fingerprint | 19,9 | %5,0 |
| watermark | 12,7 | %3,2 |
| clip_search | 0,7 | %0,2 |
| c2pa | 0,6 | %0,1 |

---

## Dürüst sınırlar

Tüm senaryolarda Top-1 doğruluğu %90'ın üzerinde.

Kapsama ölçümünde 0,10 hata payını aşan senaryolar:

- **olcek_%25** — beklenen 1,00, ölçülen 0,875 (MAE 0,1245); kaynağa eksik pay yönünde.

Sapmanın yönü önemli: kaynağa **eksik** pay veren bir hata, kaynağın itiraz edip yeniden ölçüm isteyebildiği bir sistemde düzeltilebilir. Ağır küçültmede (görsel 200×150 piksele indiğinde) yerel özellikler seyrekleşiyor ve homografi kaynağın kenarlarını tam oturtamıyor; kaybedilen alan çerçevenin dışına değil, ölçülemeyen kenar bandına gidiyor.

8 doğru bağda geometrik doğrulama yapılamadı; bu bağlarda pay hesabı ihtiyatlı kapsama varsayımıyla (`unverified_coverage`) çalışır ve kaynak itiraz ederek yeniden ölçüm isteyebilir.

