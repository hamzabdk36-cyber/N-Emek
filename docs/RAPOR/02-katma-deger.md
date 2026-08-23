# 2 · KATMA DEĞER VE YENİLİKÇİLİK

## 2.1. Problem Tanımı ve Mevcut Çözümler

**Somut durum.** Bir içerik zinciri şöyle ilerler: Ayşe özgün bir fotoğraf paylaşır;
Burak bunu kırpar, üstüne yazı ve kendi çizimini ekleyip yeniden paylaşır; Ceyda,
Burak'ın gönderisinin ekran görüntüsünü alır, yeniden sıkıştırır ve paylaşır. Üçüncü
adımda içerik kimliği tamamen kaybolur. Platform açısından Ceyda'nın gönderisi "kaynağı
olmayan yeni bir içerik"tir. Gelir bu gönderiye akar; Ayşe ve Burak hiçbir şey almaz.

Sorunun üç ayrı bileşeni var ve üçü de bugünkü sistemlerde çözümsüz:

**Kimlik kırılganlığı.** İçerik kimliği taşıyan üstveri, yeniden kodlamada ve ekran
görüntüsünde silinir. C2PA standardı [6] içerik kimlik bilgilerini kriptografik olarak
imzalayarak taşır, ancak manifest dosyanın üstverisinde durur — bir ekran görüntüsü
alındığında piksel dizisi korunur, manifest korunmaz. Kimliğe *tek başına* güvenen her
sistem ilk yeniden paylaşımda kör kalır.

**Ölçüm yokluğu.** Kaynağın bulunduğu durumlarda bile "ne kadar kullanıldığı" bilinmez.
Sabit oranlı bir paylaşım kuralı (örneğin "kaynağa %20"), kırpılmış küçük bir alıntıyla
neredeyse birebir kopyayı aynı kefeye koyar. İkisi de adaletsizdir ve ikisi de itiraz
üretir.

**Açıklanamazlık.** Kullanıcı payının neden o kadar olduğunu göremediğinde sisteme
güvenmez. İtiraz edemediği bir hesaplama, hata yaptığında düzeltilemez.

**Problemin büyüklüğü.** Türkiye'de 16-74 yaş grubundaki bireylerin internet kullanım
oranı 2025'te %90,9'a ulaştı; bireylerin %72,9'u YouTube, %68,1'i Instagram gibi içerik
paylaşım platformlarını kullanıyor [1]. Küresel ölçekte içerik üretici ekonomisinin
toplam pazar büyüklüğü 2023'te 250 milyar dolar olarak tahmin edildi ve 2027 için 480 milyar
dolar öngörülüyor; aynı çalışma 50 milyon küresel içerik üreticisinin yıllık %10-20
bileşik büyüme hızıyla artacağını tahmin ediyor [2].

Bu büyüyen pazarın gelir dağılımı ise son derece dengesiz: içerik üreticilerinin %46'sı
yılda 1.000 dolardan az kazanıyor ve tam zamanlı üreticilerin %57'si asgari geçim
düzeyinin altında kalıyor [3]. Sorun üretilen değerin azlığı değil, **değerin kime
gittiğinin ölçülememesi**. Bir içerik zincirin ilerisinde defalarca yeniden kullanıldığı
hâlde, bu kullanımların hiçbiri ilk üreticinin gelirine yansımıyor.

Hukuki çerçeve bu boşluğu tanıyor ama teknik olarak dolduramıyor. Türk hukukunda
5846 sayılı Fikir ve Sanat Eserleri Kanunu, bir eserden yararlanılarak meydana getirilen
işlenme eserleri ayrıca düzenler ve asıl eser sahibinin haklarını saklı tutar [5]. Avrupa
Birliği'nin 2019/790 sayılı Dijital Tek Pazarda Telif Hakları Direktifi'nin 17. maddesi,
kullanıcı yüklemeli içerik platformlarını hak sahipleriyle lisans müzakeresine ve
ücretlendirmeye yönlendirir [4]. Her iki düzenleme de hakkın *varlığını* kabul eder;
ancak "bu türev içeriğin ne kadarı hangi kaynaktan geliyor" sorusunu yanıtlayacak bir
ölçüm aracı sunmaz. Uygulamada bu soru elle ve iyi niyetle yanıtlanmaya çalışılır.

**Mevcut çözümler ve neden yetersiz kaldıkları.**

| Yaklaşım | Ne yapar | Neden tek başına yetmez |
|---|---|---|
| C2PA / içerik kimlik bilgileri [6] | İmzalı köken beyanı taşır | Yeniden kodlamada silinir; *beyandır*, ne kadar kullanıldığını söylemez |
| Görünmez filigran [7] | Piksellere kimlik gömer | Kırpma ve döndürmede blok hizası bozulur |
| Algısal hash (pHash) [8] | Yeniden sıkıştırma ve ölçeklemeye dayanır | Ağır kırpma, döndürme ve aynada çöker |
| Gömme tabanlı benzerlik (CLIP) [9] | Ağır düzenlemeye dayanır | "Aynı sahne" ile "aynı içerik"i ayırmaz; oran ölçmez |
| Telif eşleştirme sistemleri (Content ID vb.) | Kopyayı bulup içeriği kaldırır | İkili karar üretir (ihlal / değil); paylaşımlı bir ekonomi kurmaz |
| Elle atıf ve etiketleme | Üreticinin beyanına dayanır | İyi niyete bağlı; kırpma ve ekran görüntüsü zinciri koparır |

Ortak eksik nettir: bu yöntemlerin hiçbiri **kullanılan içerik oranını ölçmez.** Kaynağı
bulmak ile ne kadarının kullanıldığını bilmek farklı sorulardır ve gelir paylaşımı
ikincisine ihtiyaç duyar.

## 2.2. Çözüm Fikri, Özgünlük ve Yerlilik

**Çözüm fikri.** N-Emek, içeriğin kaynak zincirini kanıtlarıyla yeniden kuran ve bu
zinciri ölçülmüş katkıya göre gelire çeviren bir emek katmanıdır. Yukarıdaki yöntemleri
yarıştırmak yerine **iş bölümüne** sokar ve üstlerine bir ölçüm katmanı koyar: her aşama
kaynağı bağımsız bir fiziksel izden arar, güvenler gürültülü-VEYA ile birleşir, ve son
aşama kaynağın türev içindeki geometrik konumunu çıkarıp piksel piksel doğrular.

Ayırt edici teknik iddia şudur: **sistem kaynağı yalnızca bulmaz, kullanılan içerik
oranını ölçer.** Kaynak, homografi kestirimiyle türev çerçevesine warp edilir [11][12][13]
ve yerel normalize edilmiş çapraz korelasyonla piksel düzeyinde doğrulanır [14]. Çıkan
sayı — *görsel kapsama* — katkı payı motorunun doğrudan girdisidir.

**Yenilikçi yönler.** Dördü de ölçümle doğrulanmıştır:

- **Ölçüme dayalı pay.** Pay formülü `kapsama × güven × sönümleme` biçiminde çarpımsaldır;
  her çarpan bağımsız bir gerekçe taşır ve kullanıcıya tek cümleyle anlatılabilir.
  Toplamsal bir model, kapsaması sıfır olan bir kaynağa güven bileşeninden pay verirdi.
- **Özel kapsama bölüntüsü.** Ölçülen kapsamalar iç içedir; her düğüme yalnızca kendi
  kattığı pikseller yazılır. Böylece kapsamalar görselin tam bir bölüntüsü olur ve
  **doğal olarak 1,0'a toplanır** — pay normalizasyona değil ölçüme dayanır. İlk
  uygulamada payların toplamı %182 çıkıyordu; bu kural o hatayı düzeltti.
- **Geçişli indirgeme.** Geometri, zincirin başındaki içeriği iki adım ilerideki
  gönderide de bulur; pikseller oraya aradaki türev üzerinden gelmiştir. Bu doğrudan bağ
  pay hesabına girerse aynı emek iki kez ödüllendirilir, dolayısıyla düşülür — ama
  veritabanında kanıt olarak kalır.
- **Açıklanabilirliğin zorunlu tutulması.** Sistem hiçbir zaman "bu içeriğin sahibi
  budur" demez; kanıtlarıyla bir zincir önerisi sunar. Her payın altında hangi aşamanın
  ne bulduğu, güven skoru ve ölçülen alan oranı satır satır durur. Bu yüzden pay formülü
  bilinçli olarak deterministik ve denetlenebilir tutuldu; öğrenilmiş bir skorlayıcı
  tercih edilmedi. Gelir dağıtan bir sistemde açıklanabilirlik bir özellik değil,
  meşruiyet koşuludur.

**Somut piyasa kıyası.** Aynı ödül havuzunun bugünkü modelle ve N-Emek ile nasıl
dağıldığı, çalışan sistemden okunan rakamlarla:

| Kişi | Bugünkü model | N-Emek ile | Fark |
|---|--:|--:|--:|
| Özgün üretici (zincirin başı) | ₺6.750,00 | ₺34.548,96 | **5,1×** |
| Remixleyen | ₺14.625,00 | ₺5.726,04 | 0,39× |
| Paylaşan | ₺23.625,00 | ₺4.725,00 | 0,20× |
| Platform | ₺5.000,00 | ₺5.000,00 | aynı |

**Havuz büyümüyor, yer değiştiriyor.** Bu modelde remixleyen ve paylaşan daha az alıyor;
bunu saklamıyoruz. İddia "herkes kazanır" değil, **"ödeme ölçülmüş katkıya gider"**. İki
denge unsuru kuralda yazılı: üretici tabanı %20 (hiçbir remix "sıfır emek" değildir) ve
üretici tavanı %80 (kaynak varken kaynak payı tamamen silinemez).

Telif eşleştirme sistemleriyle kıyas da nettir: onlar ihlal tespiti ve içerik kaldırma
için tasarlandı, ikili bir karar üretirler. N-Emek kaldırmaz, **böler**. Aynı ölçüm
altyapısı bir yasak mekanizması yerine bir ekonomi mekanizması kurar.

**Pazarda uygulanabilirlik.** Model, platformun zaten var olan bir gelir akışının (marka
işbirlikleri) üzerine kurulur; yeni bir ödeme davranışı icat etmeyi gerektirmez — ne
kullanıcıdan abonelik ister, ne yeni reklam envanteri. Değiştirdiği tek şey havuzun
**bölünme kuralı**dır. N-Emek bağımsız bir sosyal ağ da kurmaz; bir katman olarak
konumlanır ve kimlik doğrulamayı ana platformun işi sayar. Maliyetin tamamı köken
kurtarmadadır ve içerik başına bir kezliktir; sonraki her dağıtım hesabı milisaniyeler
mertebesindedir.

**Yerlilik.** Dürüst olmak gerekir: sistemin kullandığı bazı temel bileşenler yabancı
menşeli açık kaynak kütüphanelerdir — CLIP görsel gömme modeli [9], FAISS benzerlik
arama kütüphanesi [10], OpenCV ve PyTorch. Bunların yerine yerli bir muadil yazmak, bu
projenin katma değer ürettiği yer değildir ve iddia edilmemektedir.

Buna karşılık **projenin özgün çekirdeği tamamen takım tarafından geliştirilmiştir** ve
bunlar sistemin ayırt edici işini yapan parçalardır:

- **Görünmez filigran.** Hazır `invisible-watermark` paketi bu ortamda kullanılabilir
  sonuç vermedi: kayıpsız çevrimde bile on iki görselde yalnızca 6-11 doğru okuma
  üretti. Yerine, DCT katsayı-çifti tabanlı [7] ve CRC-16 doğrulamalı özgün bir filigran
  yazıldı. Çoğunluk oyu tek başına yetmemişti — ağır kırpılmış bir görselde bloklar
  rastgele oy verip eşiği tesadüfen geçen sahte bir kimlik üretebiliyordu ve ölçümde bu
  dört kez oldu. CRC-8 ile üç yanlış okuma kaldı, **CRC-16 ile sıfır**.
- **Katkı payı motoru.** Geçişli indirgeme ve özel kapsama bölüntüsü dahil, formülün
  tamamı özgündür. Akademik alternatif olan Shapley değeri [15] gerekçeli biçimde tercih
  edilmedi: üretimde hesaplama maliyeti kabul edilemez ve sonucu kullanıcıya tek cümleyle
  açıklanamaz.
- **Köken kurtarma hattının kendisi.** Çok bölgeli sorgu, ayna farkındalıklı geometrik
  eşleme ve dokuya duyarlı ZNCC karar kuralı; üçü de ölçüm sonucu ortaya çıkan ve
  literatürdeki hazır bileşenlerin üstüne yazılan özgün katmanlardır.
- **Ürünün kendisi Türkçe ve yerli platform için tasarlandı.** Arayüzün tamamı, tüm
  açıklanabilirlik metinleri ve ölçüm etiketleri Türkçedir; hedef entegrasyon noktası
  yerli bir sosyal medya platformu olan N'Sosyal'dir.
