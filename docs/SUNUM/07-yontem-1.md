# 07 · Yöntem (1/2)

## mimari
- **Referans istemci** · React 19 + TypeScript · Akış, Emek Kartı, Remix Stüdyo, Kaynak Bul, Kampanya, İnceleme
- **REST API** · FastAPI · imzalı oturum jetonu, sahiplik ve moderatör yetkisi
- **Servis katmanı** · yükleme ve remix · dağıtım · itiraz · indeks yaşam döngüsü
- **Depolama** · SQLite · FAISS indeksleri · yayınlanmış görseller ve maskeler

## motor
- **Köken kurtarma** · kanıt üretir, veritabanını tanımaz
- **Atıf ve pay** · zincir ve saf pay fonksiyonu

## asamalar
| # | Aşama | Yöntem | Güven |
|---|---|---|---|
| 0 | İçerik kimliği | C2PA manifesti [6] | 0,99 |
| 1 | Tam eşleşme | SHA-256 | 0,99 |
| 2 | Filigran | DCT katsayı çifti + CRC-16 | 0,90 |
| 3 | Parmak izi | pHash ve blok hash [8] | 0,45–0,80 |
| 4 | Görsel benzerlik | CLIP ViT-B/32 [9] + FAISS [10] | 0,30–0,75 |
| 5 | **Alan ölçümü** | **Homografi + RANSAC + ZNCC** [11–14] | **0,60–0,95** |

## hat_not
Ucuz aşamalar aday üretir, pahalı aşama doğrular. Her aşama bağımsız bir izden baktığı için güvenler gürültülü-VEYA ile birleşir.

## yz
### Yapay zekânın rolü
- Sistemde öğrenen tek bileşen **CLIP**; o da karar vermez, yalnızca aday üretir.
- Paya giren sayıyı klasik bilgisayarlı görü ölçer: deterministik ve tekrar üretilebilir.
- **Model eğitimi yok.** "Bu türevde kaynağın %41 oranı var" diye etiketlenmiş veri mevcut değil; ölçülebilen bir değeri tahmine çevirmek istemedik.
- Ağırlıklar donuk ve adlandırılmış bir kontrol noktasından geliyor (laion2b_s34b_b79k); GPU olmadan da çalışıyor.

## kaynak
[6] C2PA 2.2, 2025 · [8] Zauner, 2010 · [9] Radford vd., ICML, 2021 · [10] Johnson vd., IEEE TBD, 2021 · [11] Rublee vd., ICCV, 2011 · [12] Lowe, IJCV, 2004 · [13] Fischler ve Bolles, CACM, 1981 · [14] Lewis, 1995

## not
Soldaki şema sistemin katmanlarını gösteriyor. Üstte referans istemci: gerçek platform API'si olmadığı için N'Sosyal'i temsil eden bir istemci yazdık. Altında FastAPI ile REST katmanı ve imzalı oturum; sonra servisler. Kalbi motor: köken kurtarma ve pay hesabı. İkisi de veritabanını tanımıyor, bu yüzden bağımsız test edilip ölçülebiliyor. Sağda altı aşamalı hat. Sıfırıncı aşamada C2PA manifesti varsa okunuyor; sonra SHA-256, kendi filigranımız, algısal parmak izi ve CLIP ile görsel benzerlik. Bunlar ucuz ve aday üretiyor. Beşinci aşama pahalı olan: homografi, RANSAC ve ZNCC ile kaynağın türevde kapladığı alanı ölçüyor. Yapay zekânın rolü bilinçli olarak sınırlı: öğrenen tek bileşen CLIP ve karar vermiyor. Model eğitmedik, çünkü ölçülebilen bir şeyi tahmine çevirmek istemedik.
