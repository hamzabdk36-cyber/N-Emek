# Faz 0 — Risk Kapatma Sonuçları

**Tarih:** 8 Ağustos 2026
**Ortam:** Windows 11, Python 3.13.12, RTX 3050 Laptop (4 GB VRAM), 12 çekirdek CPU
**Amaç:** Prototipin dayandığı dört teknik varsayımın gerçekten çalıştığını, kod yazmaya devam etmeden önce ölçerek doğrulamak.

Bu belgedeki tüm sayılar `backend/poc/` altındaki çalıştırılabilir betiklerden üretilmiştir; teknik rapora buradan aktarılacaktır.

---

## Özet

| # | Risk | Durum | Ölçüm |
|---|---|---|---|
| 1 | C2PA imzalama ve türev zinciri | **Kapandı** | İmzalama, doğrulama, `parentOf` zinciri ve manifest kaybı tespiti çalışıyor |
| 2 | Kaynak adayı bulma | **Kapandı** | 20 senaryoda ortalama **%99.2** geri getirme (320 görsellik korpus) |
| 3 | Kullanılan alan oranı ölçümü | **Kapandı** | **MAE 0.0102** (hedef ≤0.05), yanlış atıf 0, kaçırma 0 |
| 4 | Görünmez filigran | **Kapandı** | 8/20 senaryoda okunuyor, PSNR 41.6 dB, **yanlış kimlik okuması 0** |

---

## Risk 1 — C2PA içerik kimliği

`backend/poc/poc_c2pa.py`

`c2pa-python 0.37.5` (Rust `c2pa-rs` 0.90.5 bağlantısı) Windows/Python 3.13'te sorunsuz kuruldu. Alternatif plana (c2patool binary / kendi imzalı JSON manifest) gerek kalmadı.

Doğrulanan üç davranış:

1. ES256 kendinden imzalı sertifika zinciriyle JPEG'e manifest gömülüyor ve geri okunuyor.
2. Remix içeriği `ingredient` (`relationship: parentOf`) ve `c2pa.actions.v2` (`opened` → `cropped` → `edited`) ile kaynağına bağlanıyor; okuyucu kaynak manifest URN'ini döndürüyor.
3. Görsel yeniden kaydedildiğinde manifest gidiyor ve okuyucu bunu `ManifestNotFound` olarak raporluyor — köken kurtarma hattının tetikleneceği durum tam olarak bu.

Projeye özel `org.nemek.remix_policy` assertion'ı ile üreticinin remix izinleri ve minimum kaynak payı tercihi manifeste yazılabiliyor.

**Kurulum tuzağı:** `C2paSignerInfo(ta_url=...)` alanına boş bytes (`b""`) verilirse imzalama `Signature: empty string` hatasıyla düşüyor. Zaman damgası sunucusu kullanılmayacaksa `None` verilmeli.

---

## Risk 2 — Kaynak adayı bulma

`backend/poc/poc_similarity.py`

320 görsellik korpus (picsum.photos, Unsplash lisansı) indekslendi; 40 görselin 20 farklı türevi sorgu olarak çalıştırıldı. Top-5 geri getirme:

| Senaryo | pHash | Blok hash | CLIP | **Birleşik** |
|---|---|---|---|---|
| orijinal | %100 | %100 | %100 | **%100** |
| jpeg_q50 / q30 | %100 | %100 | %100 | **%100** |
| ölçek %50 / %25 | %100 | %100 | %100 | **%100** |
| kırpma %90 | %100 | %90 | %100 | **%100** |
| kırpma %70 | %45 | %5 | %100 | **%100** |
| kırpma %50 | %5 | %5 | %100 | **%100** |
| kırpma %30 | %0 | %0 | %95 | **%95** |
| yazı bandı | %85 | %100 | %98 | **%100** |
| sticker | %60 | %100 | %100 | **%100** |
| meme | %55 | %5 | %100 | **%100** |
| ağır renk | %98 | %100 | %98 | **%100** |
| gri ton | %100 | %100 | %98 | **%100** |
| döndürme 5° | %82 | %32 | %100 | **%100** |
| döndürme 15° | %5 | %0 | %100 | **%100** |
| ayna | %0 | %0 | %100 | **%100** |
| ekran görüntüsü | %98 | %82 | %100 | **%100** |
| kolaj | %100 | %0 | %100 | **%100** |
| kırpma + yazı | %0 | %2 | %90 | **%90** |
| **Ortalama** | | | | **%99.2** |

### Ölçümün yönlendirdiği tasarım kararı: çok bölgeli sorgu

İlk kurulum (yalnızca tam görsel üzerinden pHash + CLIP) **%88.5** verdi ve üç senaryoda çöktü: meme %25, kolaj %42, kırpma+yazı %8. Ortak neden, kaynağın türev tuvalinin yalnızca bir bölümünü kaplaması — global tanımlayıcılar tüm tuvali görüyor.

Çözüm, sorgu görselini sabit bir bölge kümesine (tam, merkez, dört çeyrek, dört yarım, düz çerçevesi kırpılmış hâli) ayırıp her bölgeyi ayrı aramak. İndeks tarafı değişmedi, maliyet yalnızca sorgu anında ve tek bir GPU yığınına sığıyor. Ortalama **%88.5 → %99.2**.

`backend/app/provenance/regions.py`

### Performans

| İşlem | Süre |
|---|---|
| Parmak izi (pHash + dHash + wHash + 3×3 blok) | 39 ms/görsel |
| CLIP ViT-B/32 gömme (CUDA, yığın 32) | 28 ms/görsel |
| Sorgu (çok bölgeli, 320 kayıtlık indeks) | 12–205 ms |

---

## Risk 3 — Kullanılan alan oranı ölçümü

`backend/poc/poc_geometry.py` · `backend/app/provenance/geometry.py`

**Projenin temel teknik iddiası:** türev içerikte kaynağın ne kadar kullanıldığını tahmin etmiyoruz, ölçüyoruz. Katkı payı motorunun girdisi bu sayı.

Bilinen doğru cevaplarla üretilmiş senaryolarda ORB + RANSAC homografi + piksel doğrulaması:

| Senaryo | Doğru cevap | Ölçülen | Hata |
|---|---|---|---|
| Kırpma %50 + 1.4× büyütme | 1.000 | 0.990 | 0.010 |
| Kırpma %30 + JPEG q40 | 1.000 | 1.000 | 0.000 |
| Alt %18 opak yazı bandı | 0.820 | 0.859 | 0.038 |
| Yan yana kolaj (sol yarı) | 0.500 | 0.495 | 0.005 |
| 12° döndürülmüş %25'lik yama | 0.229 | 0.224 | 0.004 |
| Yoğun renk derecelendirme | 1.000 | 0.987 | 0.013 |
| Kenar kırpma + %80 ölçek + JPEG 55 | 1.000 | 1.000 | 0.000 |
| İlgisiz görsel | — | **reddedildi** | — |

**MAE 0.0102** · yanlış atıf 0 · kaçırma 0 · tipik süre ~90 ms

### Ölçümün yönlendirdiği tasarım kararı: dokuya duyarlı piksel doğrulaması

Salt homografi, kaynağın üstüne konan yazı/sticker/çizimi göremez — geometrik olarak bölge hâlâ "kaynaktan gelmiş" görünür. Bu yüzden warp edilmiş kaynak ile türev arasında yerel ZNCC hesaplanıyor. İlk sürüm ağır renk filtresinde 0.878 (doğru cevap 1.000) verdi; düşen bölgeler koyu ve düz alanlardı — orada yapısal doku olmadığı için ZNCC gürültüye dönüyordu.

Üç durumlu karar kuralına geçildi:

- **İkisi de dokulu** → ZNCC karar verir (asıl ölçüm)
- **Kaynak dokulu, türev düz** → üzeri kapatılmış, sayılmaz (yazı bandı, sticker bu dala düşer)
- **İkisi de düz** → yapısal olarak ayırt edilemez; hiçbir yöntem düz bir alanın üstüne aynı tonda düz bir alan konup konmadığını söyleyemez, geometrik karar korunur

MAE **0.0215 → 0.0102**; ağır filtre senaryosu 0.878 → 0.987.

Bilinçli ödünç: yazı bandı senaryosunda 0.038 fazla sayıyoruz, çünkü bandın koyu ve düz zemine denk gelen kısmı üçüncü dala düşüyor. Bu yönde hata yapmak (kaynağa biraz fazla pay) yanlış atıftan daha kabul edilebilir.

---

## Risk 4 — Görünmez filigran

`backend/poc/poc_watermark.py` · `backend/app/provenance/watermark.py`

Hazır `invisible-watermark` paketi (0.2.0) bu ortamda kullanılamadı: `dwtDct` ve `dwtDctSvd` yöntemleri **kayıpsız çevrimde bile** 12 görselde yalnızca 6–11 doğru okuma verdi, JPEG q50'de tamamen çöktü. Güç katsayısı 36→120 aralığında denendi, sonuç değişmedi (PSNR 41→32 dB'ye düşerken doğruluk artmadı).

Yerine kanonik ölçekli katsayı-çifti filigranı yazıldı:

- Y kanalı sabit 512×512 kanonik boyuta ölçeklenir — bu, filigranı **ölçek değişimine bağışık** yapar (herhangi bir boyuttaki sorgu görseli çözmeden önce aynı kanonik boyuta getirilir, 8×8 blok hizası geri kazanılır)
- 4096 blok, anahtar türetimli permütasyonla 56 bitlik yüke dağıtılır (blok başına ~73 kat fazlalık)
- Her blokta aynı frekans bandındaki iki DCT katsayısının işaret ilişkisi bite göre zorlanır; JPEG bu iki katsayıyı benzer ölçüde etkilediği için ilişki korunur
- Çözümde bloklar arası çoğunluk oyu

| Senaryo | Geri okuma |
|---|---|
| orijinal | %100 |
| jpeg_q50 | %97 |
| jpeg_q30 | %87 |
| ölçek %50 | %100 |
| yazı bandı | %100 |
| sticker | %100 |
| ağır renk | %100 |
| gri ton | %100 |
| kırpma / döndürme / ayna / kolaj | %0 |

**PSNR 41.6 dB** (40 dB üzeri gözle ayırt edilemez) · **yanlış kimlik okuması 0**

### Ölçümün yönlendirdiği tasarım kararı: CRC-16

Çoğunluk oyu tek başına yetmiyor. Ağır kırpılmış bir görselde bloklar rastgele oy veriyor ve eşiği tesadüfen geçen bir "kimlik" üretebiliyor — ölçümde 4 kez oldu. Yüke CRC eklendi: CRC-8 ile 3 yanlış okuma kaldı, **CRC-16 ile 0**. Yük yapısı 40 bit kimlik + 16 bit CRC.

Yanlış atıf, bu projede kaçırılmış atıftan çok daha ağır bir hata; bu yüzden fazlalıktan feragat edip doğrulama gücü artırıldı.

### Dürüst sınır

Filigran kırpma ve döndürmeye dayanmıyor; blok hizası bozuluyor. Bu bir eksiklik değil, iş bölümü: hattın 3–5. aşamaları (pHash, CLIP, geometri) tam olarak bu durumlar için var ve ölçümlere göre orada %95–100 başarılılar. Filigranın görevi, metadatası silinmiş ama piksel düzeni korunmuş içerikte *kesin* kanıt sağlamak — benzerlik "buna benziyor" derken filigran "bu, şu kimlikli içerikten türemiştir" diyor.

---

## Sonraki adım

Faz 1: yükleme + remix stüdyosu, beş aşamalı köken kurtarma hattının birleştirilmesi, katkı payı motoru, Emek Kartı veri katmanı, zincir görünümü.
