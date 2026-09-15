# 04 · Problemin Tanımı

## zincir
- **Ayşe** · özgün fotoğrafını paylaşır; içerik kimliği dosyada
- **Burak** · kırpar, yazı ve çizim ekler; kaynağı anmak ona kalmış
- **Ceyda** · ekran görüntüsüyle paylaşır; kimlik silinir, gelir buraya akar

## bilesenler
### Sorunun üç bileşeni
- **Kimlik kırılganlığı.** C2PA manifesti dosyanın üstverisinde durur; ekran görüntüsü alındığında pikseller kalır, manifest kalmaz.
- **Ölçüm yokluğu.** Kaynak bulunsa bile ne kadarının kullanıldığı bilinmez. Sabit oranlı bir kural, küçük bir alıntıyla birebir kopyayı aynı kefeye koyar.
- **Açıklanamazlık.** Gerekçesini göremediği bir paya kullanıcı güvenmez; hatalı hesaplamaya itiraz edecek yol da yoktur.

## hukuk
**Hukuki çerçeve hakkı tanıyor, ölçüm aracı sunmuyor.** FSEK (5846) işlenme eserlerde asıl eser sahibinin haklarını saklı tutar [5]; AB 2019/790 Direktifi platformları hak sahipleriyle ücretlendirmeye yönlendirir [4]. İkisi de bir türevin ne kadarının hangi kaynaktan geldiğini söyleyemez.

## istatistik
- **480 milyar $** · içerik üretici ekonomisi için 2027 öngörüsü; 2023 tahmini 250 milyar $ [2]
- **%46** · yılda 1.000 $ altında kazanan üreticiler; tam zamanlıların %57 oranı asgari geçimin altında [3]

## mevcut
| Yaklaşım | Eksik kaldığı yer |
|---|---|
| C2PA içerik kimliği [6] | Yeniden kodlamada silinir; kullanım oranı taşımaz |
| Görünmez filigran [7] | Kırpma ve döndürmede okunamaz |
| Algısal hash [8] | Ağır kırpma, döndürme ve aynada çöker |
| Görsel benzerlik, CLIP [9] | Aynı sahneyi aynı içerikten ayıramaz |
| Telif eşleştirme (Content ID vb.) | İhlal var ya da yok der; paylaşım kurmaz |
| Elle etiketleme | İyi niyete bağlı, zincirde kaybolur |

## kaynak
[2] Goldman Sachs Research, 2023 · [3] Linktree Creator Report, 2022 · [4] Directive (EU) 2019/790 · [5] 5846 sayılı Fikir ve Sanat Eserleri Kanunu · [6] C2PA Technical Specification 2.2, 2025 · [7] Cox vd., IEEE TIP, 1997 · [8] Zauner, 2010 · [9] Radford vd., ICML, 2021

## not
Somut bir zincirle başlayalım. Ayşe özgün bir fotoğraf paylaşıyor. Burak kırpıyor, üstüne yazı ve çizim ekliyor; kaynağı anmak tamamen ona kalmış. Ceyda Burak'ın gönderisinin ekran görüntüsünü alıyor ve bu anda içerik kimliği tamamen siliniyor. Platform için Ceyda'nın gönderisi artık kaynağı olmayan yeni bir içerik; gelir de oraya akıyor. Sorunun üç bileşeni var: kimlik kırılgan, çünkü C2PA gibi standartlar üstveride duruyor; kaynak bulunsa bile ne kadarının kullanıldığı ölçülmüyor; ve kullanıcı gerekçesini görmediği bir paya güvenmiyor. Pazar büyük: üretici ekonomisi 2027 için 480 milyar dolar öngörülüyor, ama üreticilerin yüzde 46'sı yılda bin doların altında kazanıyor. Hukuk hakkı tanıyor, ölçmüyor. Sağdaki tablo mevcut yaklaşımların her birinin nerede eksik kaldığını gösteriyor: hiçbiri kullanılan oranı ölçmüyor.
