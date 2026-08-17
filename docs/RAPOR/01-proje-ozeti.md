# 1 · PROJE ÖZETİ

## 1.1. Proje Konusu ve amacı

**Proje konusu.** Sosyal medyada bir görsel kırpıldığında, üstüne yazı eklendiğinde,
ekran görüntüsü alınıp yeniden paylaşıldığında ilk üreticinin emeği görünmez olur.
İçerik kimliği taşıyan üstveri (EXIF, C2PA manifesti) yeniden kodlamada silinir; platform
açısından yeni gönderi "kaynağı olmayan özgün bir içerik" hâline gelir. Gelir bu son
gönderiye akar, zincirin başındaki üretici hiçbir şey almaz. Proje bu somut soruna —
**içerik zincirinde emeğin izinin kaybolması ve gelirin ölçülmemiş bir varsayıma göre
dağıtılması** — odaklanmaktadır.

**Amaç.** N-Emek, N'Sosyal'e takılan bir *emek katmanı*dır ve iki iş yapar: bir içeriğin
kaynak zincirini kanıtlarıyla yeniden kurar, ardından bu zinciri **açıklanabilir ve
itiraz edilebilir** bir gelir paylaşımına çevirir. Nihai amaç, içerik üreticisinin
gelirini iyi niyete veya elle etiketlemeye değil, **ölçüme** dayandıran çalışır bir
altyapı ortaya koymaktır.

Projenin ayırt edici teknik iddiası tek cümlede şudur: sistem kaynağı yalnızca *bulmaz*,
kullanılan içerik oranını **ölçer**. "Bu içeriğin yüzde kaçı şu kaynaktan geliyor"
sorusu, katkı payının doğrudan girdisidir ve tahminle değil homografi kestirimi ile
yerel piksel doğrulaması kullanılarak yanıtlanır.

**Tematik alan.** Proje birincil olarak **İçerik Ekonomisi** temasına hitap etmektedir.
Şartnamenin örnek çözüm alanları arasında saydığı *gelir paylaşım sistemleri* ile
*marka–içerik üretici eşleştirme platformları* kalemlerinin ikisini birden karşılar.
İki temayla da doğrudan kesişir: köken kurtarma hattı görsel yapay zekâ (CLIP gömmeleri,
yerel özellik eşleme) üzerine kurulduğu için **Sosyal Yapay Zekâ**, gelirin gerekçesini
kullanıcıya satır satır gösteren Emek Kartı arayüzü nedeniyle **Kullanıcı Katılımı ve
Arayüz (UI/UX)** temalarına da değer üretir.

**Yarışma hedefleriyle ilişkisi.** Şartnamenin 1. bölümünde sıralanan hedeflerden
üçüyle doğrudan örtüşmektedir: *içerik üreticilerine sürdürülebilir gelir modelleri
sunan yenilikçi sistemlerin geliştirilmesi*, *güvenli, etik, şeffaf ve kullanıcı
mahremiyetini ön planda tutan çözümler* ve *yapay zekâ destekli yeni nesil sosyal medya
platformlarına katkı*. Sistem hiçbir zaman "bu içeriğin sahibi budur" demez; kanıtlarıyla
birlikte bir zincir **önerisi** sunar, kullanıcı itiraz edebilir, çözülmeyen itiraz insan
incelemesine düşer. Şeffaflık bir sunum tercihi değil, mimarinin kendisidir.

## 1.2. Proje Kapsamı ve Yöntemi

**Kapsam.** Prototip iki parçadan oluşur. Birincisi, gerçek platform API'si olmadığı
için geliştirilen **referans sosyal medya istemcisi**: akış, içerik yükleme, remix
stüdyosu, kampanya paneli ve moderasyon kuyruğu. Bu, N'Sosyal'i taklit eden bir kopya
değil, N-Emek'in entegre edileceği ana platformu temsil eden bir kaptır. İkincisi
**N-Emek motoru**: köken kurtarma, katkı payı hesabı, açıklanabilirlik, itiraz ve gelir
dağıtımı.

**Sınırlar — kapsam dışında bırakılanlar.** Proje bağımsız bir sosyal ağ kurmaz; bir
katman olarak konumlanır ve kimlik doğrulamayı bile ana platformun işi sayar. Telif
ihlali tespiti ve içerik kaldırma yapmaz — ikili bir ihlal kararı değil, paylaşımlı bir
ekonomi üretir. Görsel içerikle sınırlıdır; video ve ses aynı yöntemsel çerçeveye
oturmakla birlikte bu prototipte ölçülmemiştir. Ödeme altyapısı (gerçek para transferi)
kapsam dışıdır: sistem dağıtımı hesaplar ve kaydeder, parayı taşımaz.

**Teknik yöntem.** Köken kurtarma, ucuz aday üretimi ve pahalı doğrulama olmak üzere iki
katmanlı, altı aşamalı bir hat olarak kuruldu:

| Aşama | Yöntem | Neye dayanıklı |
|---|---|---|
| 0 | C2PA manifest doğrulama | manifest korunmuşsa |
| 1 | SHA-256 tam eşleşme | bit-birebir kopya |
| 2 | Görünmez filigran (CRC-16 doğrulamalı) | yeniden sıkıştırma, ölçekleme, üstveri silme |
| 3 | Algısal hash + blok hash | ölçekleme, JPEG, renk ve parlaklık değişimi |
| 4 | CLIP gömmesi, çok bölgeli sorgu | ağır düzenleme, filtre, kolaj, meme |
| 5 | Homografi + ZNCC piksel doğrulaması | **kullanılan alanı ölçer** |

Aşamalar birbirinin yedeği değil, **iş bölümü** içindedir: her biri kaynağı bağımsız bir
fiziksel izden bulur (üstveri, bayt özeti, frekans alanı, piksel istatistiği, yerel
geometri). Güvenler bu bağımsızlık nedeniyle gürültülü-VEYA ile birleştirilir.

**Akademik yöntem.** Proje boyunca izlenen kural şudur: *hiçbir performans sayısı elle
yazılmaz, hepsi çalıştırılabilir bir betiğin çıktısıdır.* Değerlendirme, 280 görselin
indekslendiği ve 40 görselin indekse hiç alınmadığı (negatif kontrol) bir korpus
üzerinde, 20 türev senaryosuyla toplam 6.400 sorgu koşularak yapıldı; her sorgu
üretimdeki kurtarma fonksiyonunun kendisinden geçti. Kullanılan alan oranı ölçümünün
doğru cevabı elle etiketlenmez, türevi üreten dönüşümün geometrisinden hesaplanır.

**Tema ile doğrudan ilişki.** İçerik Ekonomisi teması, içerik üreticilerinin
sürdürülebilir gelir elde edebilmesini sağlayacak modellerin geliştirilmesini istiyor.
N-Emek tam olarak bunun eksik halkasını hedefler: gelir paylaşımının *kime ne kadar*
sorusuna cevap veren ölçüm katmanı. Marka kampanyası havuzunu son paylaşana değil,
zincirin tamamına ölçülmüş katkıya göre böler; her ödemenin altında gerekçesi durur.

**Çalışan prototip.** Proje fikir düzeyinde bırakılmamıştır. Prototip
`docker compose up --build` ile tek komutta ayağa kalkar; referans istemci, remix
stüdyosu, Emek Kartı, atıf zinciri görselleştirmesi, marka kampanya paneli, itiraz akışı
ve moderasyon kuyruğu çalışır durumdadır. Kaynak kod sürüm kontrolü altındadır ve
geliştirme adımları commit geçmişinden takip edilebilir (bkz. 3.1).

**Yeni çalışmalara zemin.** "Kullanılan içerik oranının ölçülmesi" fikri gelir
paylaşımına özgü değildir. Aynı ölçüm; telif müzakeresi, atıf zorunluluğu, veri kümesi
kökeni denetimi ve üretken yapay zekâ çıktılarının kaynak izlenebilirliği gibi alanlara
doğrudan taşınabilir. Değerlendirme düzeneği, saldırı senaryosu üreticisi ve ölçüm
betikleri bu çalışmaların üzerine kurulabileceği yeniden üretilebilir bir taban
oluşturur.
