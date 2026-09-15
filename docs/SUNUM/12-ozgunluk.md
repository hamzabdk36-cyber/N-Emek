# 12 · Özgünlük ve Yerlilik Yönü

## ana
Temel bileşenler açık kaynak; sistemin ayırt edici işini yapan katmanları takım kendisi yazdı.

## ozgun
- **Köken kurtarma hattının kurgusu** ve karar füzyonu
- **Görünmez filigran:** DCT katsayı çifti + CRC-16
- **Çok bölgeli sorgu** ve ayna farkındalıklı geometri
- **Pay motoru:** geçişli indirgeme, özel kapsama
- **Emek Kartı**, itiraz ve moderasyon akışı
- **Ölçüm düzeneği:** 20 türev senaryosu

## hazir
- CLIP
- FAISS
- OpenCV
- PyTorch
- C2PA kütüphanesi
- FastAPI
- React

## filigran
### Kendi filigranımız
Hazır görünmez filigran paketi kayıpsız çevrimde bile on iki görselde yalnızca 6–11 doğru okuma verdi. Yerine yazdığımız filigranda CRC-8 ile üç yanlış kimlik okuması kaldı; **CRC-16 ile sıfır.**

## sorgu
### Model büyütmeden daha iyi sorgu
Tam görsel üzerinden tek vektörle arama, geri getirmede %88,5 düzeyinde kaldı; kolajda ve kırpılıp yazı eklenmiş görselde çöktü. Görseli 11 bölgeye ayırıp her bölgeyi ayrı aramak bu oranı **%99,2** düzeyine çıkardı.

## literatur
### Literatürden ayrışan yön
C2PA [6] kökeni doğrulamak için tasarlandı. N-Emek onu kimlik silindiğinde de çalışan bir kurtarma hattıyla tamamlayıp **gelir paylaşımına** bağlıyor. Pay için Shapley değeri [15] yerine tek cümleyle açıklanabilen, hesaplaması hafif bir kural seçildi.

## yerlilik
### Yerlilik
Arayüz, pay gerekçeleri ve ölçüm etiketleri baştan Türkçe yazıldı. Hedef entegrasyon noktası yerli sosyal medya platformu **N'Sosyal**. Kaynak kod, eşik kalibrasyonu ve değerlendirme düzeneği takımın; dış hizmet alınmadı.

## kaynak
[6] C2PA Technical Specification 2.2, 2025 · [7] Cox vd., IEEE TIP, 1997 · [15] Shapley, Contributions to the Theory of Games, 1953 · filigran ve sorgu ölçümleri: docs/FAZ0-SONUCLARI.md, docs/YZ-MIMARISI.md

## not
Özgünlük konusunda dürüst olmak istiyoruz. CLIP, FAISS, OpenCV ve PyTorch gibi temel bileşenler açık kaynak; bunların yerli muadilini yazmak projenin katma değer ürettiği yer değil. Ayırt edici işi yapan katmanları ise kendimiz yazdık: köken kurtarma hattının kurgusu, filigran, çok bölgeli sorgu, pay motoru ve Emek Kartı. İki örnek vereyim. Hazır filigran paketi bizim ortamımızda kayıpsız çevrimde bile güvenilir okuyamadı; kendi filigranımızı yazdık ve CRC-16 ile yanlış okumayı sıfıra indirdik. İkincisi, benzerlik aramasında daha büyük model yerine daha iyi sorgu kurduk: görseli 11 bölgeye ayırmak geri getirmeyi yüzde 88,5'ten 99,2'ye çıkardı. Literatürden farkımız C2PA'yı ekonomik paylaşıma bağlamamız. Yerlilik tarafında arayüz ve tüm gerekçeler Türkçe, hedefimiz N'Sosyal.
