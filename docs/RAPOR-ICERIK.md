# Teknik Rapor — İçerik Blokları

> **Bu dosya raporun kendisi değil.** KYS'deki resmî şablon henüz elimizde olmadığı için,
> şablondan bağımsız bölümler burada hazırlandı. Şablon geldiğinde bu bloklar kendi
> başlıklarının altına taşınacak. Şartname açık: *"şablona uygun olmayan, eksik veya hatalı
> yüklenen raporlar değerlendirmeye alınmaz ve ilgili takımlar yarışmadan elenir."*
>
> **Sayı disiplini:** buradaki her rakam `docs/DEGERLENDIRME.md`, `docs/GECIKME.md` veya
> `docs/FAZ0-SONUCLARI.md` dosyalarından gelir; onlar da çalıştırılabilir betiklerin
> çıktısıdır. Rapora aktarırken sayıyı elle değiştirme — ölçüm değiştiyse betiği koştur.

---

## 1. Özet

Bir görsel kırpıldığında, üstüne yazı eklendiğinde, ekran görüntüsü alındığında veya
remixlendiğinde ilk üreticinin emeği görünmez olur; içerik kimliği taşıyan metadata ilk
yeniden paylaşımda silinir ve gelir paylaşımı yapılamaz hâle gelir.

**N-Emek**, N'Sosyal'e takılan bir *emek katmanı*dır. İki iş yapar: içeriğin kaynak
zincirini kanıtlarıyla yeniden kurar ve bu zinciri **açıklanabilir, itiraz edilebilir** bir
gelir paylaşımına çevirir.

Ayırt edici teknik iddia şudur: sistem kaynağı yalnızca *bulmaz*, kullanılan içerik oranını
**ölçer**. Katkı payının girdisi olan "bu içeriğin yüzde kaçı şu kaynaktan geliyor" sorusu
tahminle değil, homografi kestirimi ve yerel piksel doğrulamasıyla yanıtlanır.

320 görsellik korpus üzerinde, 20 farklı türev senaryosunda, **6.400 sorguluk** bir
değerlendirme koşuldu. Ölçülen sonuçlar:

| Metrik | Sonuç |
|---|---|
| Kaynak bulma doğruluğu (Top-1) | **%98,7** |
| Yanlış atıf oranı | **%0,86** |
| Kullanılan alan oranı ölçüm hatası (MAE) | **0,0241** |
| Uçtan uca gecikme | p50 **386 ms** |

Prototip çalışır durumdadır: referans sosyal medya istemcisi, remix stüdyosu, Emek Kartı,
zincir görselleştirmesi, marka kampanya paneli, itiraz akışı ve moderasyon kuyruğu dahil.

---

## 2. Problem tanımı

### 2.1 Somut durum

Bir içerik zinciri şöyle ilerler:

1. **Ayşe** özgün bir fotoğraf paylaşır.
2. **Burak** bunu kırpar, üstüne yazı ve kendi çizimini ekleyip yeniden paylaşır.
3. **Ceyda** Burak'ın gönderisinin ekran görüntüsünü alır, yeniden sıkıştırır ve paylaşır.

Üçüncü adımda içerik kimliği tamamen kaybolur. Platform açısından Ceyda'nın gönderisi
"kaynağı olmayan yeni bir içerik"tir. Gelir bu gönderiye akar; Ayşe ve Burak hiçbir şey
almaz. Bugün yaygın olan davranış budur.

### 2.2 Sorunun üç bileşeni

**Kimlik kırılganlığı.** İçerik kimliği taşıyan metadata (EXIF, C2PA manifesti) yeniden
kodlamada, ekran görüntüsünde ve çoğu platformun kendi yeniden boyutlandırmasında silinir.
Kimliğe *tek başına* güvenen her sistem ilk yeniden paylaşımda kör kalır.

**Ölçüm yokluğu.** Kaynağın bulunduğu durumlarda bile "ne kadar kullanıldığı" bilinmez.
Sabit oranlı paylaşım (örneğin "kaynağa %20") kırpılmış bir alıntıyla neredeyse birebir
kopyayı aynı kefeye koyar; ikisi de adaletsizdir.

**Açıklanamazlık.** Kullanıcı payının neden o kadar olduğunu göremediğinde sisteme
güvenmez. İtiraz edemediği bir hesaplama, hata yaptığında düzeltilemez.

### 2.3 Neden mevcut yaklaşımlar yetmiyor

| Yaklaşım | Ne yapar | Neden tek başına yetmez |
|---|---|---|
| C2PA / içerik kimlik bilgileri | İmzalı köken beyanı taşır | Yeniden kodlamada silinir; *beyandır*, ne kadar kullanıldığını söylemez |
| Görünmez filigran | Piksellere kimlik gömer | Kırpma ve döndürmede blok hizası bozulur |
| Algısal hash (pHash) | Yeniden sıkıştırma ve ölçeklemeye dayanır | Ağır kırpma, döndürme ve aynada çöker |
| Gömme tabanlı benzerlik (CLIP) | Ağır düzenlemeye dayanır | "Aynı sahne" ile "aynı içerik"i ayırmaz; oran ölçmez |
| Telif eşleştirme sistemleri | Kopyayı bulup içeriği kaldırır | İkili karar üretir (ihlal / değil); paylaşımlı bir ekonomi kurmaz |

Her yöntemin dayandığı ve çöktüğü yer farklıdır. N-Emek'in yaklaşımı bunları yarıştırmak
değil, **iş bölümü** kurmak ve üstüne bir *ölçüm* katmanı koymaktır.

---

## 3. Yöntem: Köken Kurtarma Hattı

### 3.1 Genel yapı

Hat iki aşamalıdır: ucuz aday üretimi, ardından pahalı doğrulama.

| Aşama | Yöntem | Neye dayanıklı | Güven |
|---|---|---|---|
| 0 | C2PA manifest doğrulama | manifest korunmuşsa | 0,99 |
| 1 | SHA-256 tam eşleşme | bit-birebir kopya | 0,99 |
| 2 | Görünmez filigran (CRC-16 doğrulamalı) | yeniden sıkıştırma, ölçekleme, metadata silme | 0,90 |
| 3 | pHash + 3×3 blok hash (Hamming ≤ 12) | ölçekleme, JPEG, renk/parlaklık | 0,45–0,80 |
| 4 | CLIP ViT-B/32, çok bölgeli | ağır düzenleme, filtre, kolaj, meme | 0,30–0,75 |
| 5 | Homografi + ZNCC piksel doğrulaması | **kullanılan alanı ölçer** | 0,60–0,95 |

Aşama 5 yalnızca doğrulama yapmaz, **ölçüm** yapar. Homografi matrisinden kaynağın türev
içindeki geometrik konumu çıkarılır; kaynak türev çerçevesine warp edilip yerel normalize
edilmiş çapraz korelasyon (ZNCC) ile piksel piksel doğrulanır. Sonuç, katkı payı motorunun
girdisi olan *görsel kapsama* oranıdır.

### 3.2 Karar füzyonu

Aşama güvenleri gürültülü-VEYA ile birleşir:

```
birleşik güven = 1 − Π (1 − güvenᵢ)
```

Gerekçe: her aşama kaynağı **bağımsız bir fiziksel izden** bulur — metadata, bayt özeti,
frekans alanı, piksel istatistiği, yerel geometri. Aynı sonuca farklı yollardan varmaları
güveni artırmalıdır. Toplamsal bir model bu bağımsızlığı ifade edemezdi.

İki emniyet supabı vardır:

- **Benzerlik tavanı (0,80).** Yalnızca pHash ve CLIP'ten gelen güven bu değerle sınırlanır.
  Benzerlik "aynı sahne" ile "aynı içerik"i ayırmaz; tek başına yüksek güven vermemelidir.
- **Doğrulanamama cezası (×0,40).** Geometrik doğrulamayı geçemeyen bir benzerlik adayının
  güveni düşürülür ve genellikle eşiğin altına iner.

Her ikisinin de tek bir gerekçesi var: **yanlış atıf, kaçırılmış atıftan ağır bir hatadır.**
Eşikler bu yönde hata payı bırakacak biçimde ayarlanmıştır.

### 3.3 Sistemin asla yapmadığı şey

Sistem "bu içeriğin sahibi budur" demez. Kanıtlarıyla birlikte bir **zincir önerisi** sunar:
hangi aşamanın ne bulduğu, güven skoru, ölçülen alan oranı ve eşleşen bölgenin maskesi
kullanıcıya gösterilir. Kullanıcı onaylayabilir veya itiraz edebilir; çözülmeyen itiraz
insan incelemesine düşer.

---

## 4. Katkı payı motoru

### 4.1 Formül

Bir kaynağın ham ağırlığı üç çarpanın çarpımıdır:

```
ağırlık = kapsama^a × güven^b × sönümleme^(derinlik−1)
```

Çarpımsal seçilmesinin nedeni, her çarpanın bağımsız bir gerekçe taşıması ve kullanıcıya
tek cümleyle anlatılabilmesidir: *"içeriğin %41'i senden geldi, buna %92 eminiz, sen
zincirde iki adım geridesin."* Toplamsal bir model, kapsaması sıfır olan bir kaynağa güven
bileşeninden pay verirdi; çarpımsal model vermez.

Üstüne kampanya kuralları uygulanır: üretici tabanı (hiçbir remix "sıfır emek" değildir),
üretici tavanı (kaynak payı tamamen silinemez), kaynak tabanı ve minimum ödeme eşiği. Her
ara değer kaydedilir ve Emek Kartı'nda satır satır gösterilir.

### 4.2 İki kritik kural

Bu iki kural, ölçümde ortaya çıkan gerçek hataları düzeltir. İlk uygulamada payların toplamı
**%182** çıkıyor ve tabana çarpıyordu.

**Geçişli indirgeme.** Geometri, Ayşe'nin içeriğini Ceyda'nın gönderisinde de bulur —
pikseller oraya Burak üzerinden gelmiştir. Bu doğrudan bağ pay hesabına girerse aynı emek
iki kez ödüllendirilir. P'den C'ye uzunluğu ≥2 bir yol varsa doğrudan P→C bağı hesaptan
düşülür; veritabanında kanıt olarak kalır.

**Özel kapsama bölüntüsü.** Ölçülen kapsamalar iç içedir: Burak'ın %97'si Ayşe'nin %84'ünü
de kapsar. Her düğüme yalnızca kendi kattığı pikseller yazılır:

```
özel(A) = toplam(A) − Σ toplam(A'nın zincirdeki doğrudan kaynakları)
```

Böylece kapsamalar görselin tam bir bölüntüsü olur ve **doğal olarak 1,0'a toplanır**. Pay,
normalizasyona değil ölçüme dayanır.

Bu düzeltmenin bir yan sonucu oldu ve kayda değer: zincir sönümleme katsayısı 0,50'den
**0,85**'e çıkarıldı. Özel kapsama zaten her tarafı yalnızca kendi kattığı piksellerle
ödüllendirdiği için agresif sönümleme, tam da bu projenin düzeltmeye çalıştığı haksızlığı
üretiyordu: ilk üretici, başkaları içeriğini remixlediği için cezalandırılmış oluyordu.

### 4.3 Emek Kartı

Tek ekranda: kaynak ve türev yan yana, eşleşen bölge maskeli; kanıt satırları (hangi aşama
ne buldu, hangi eşikle); güven rozeti; pay dağılımı ve her rakamın altında gerekçesi;
"İtiraz et" düğmesi.

Maskede ayrım renkle değil **kontrastla** kurulur — eşleşen bölge parlak kalır, eşleşmeyen
griye düşer. Kapsama %90'ı aştığında yoğun bir renk katmanı görüntüyü yutuyordu.

---

## 5. Ölçümün yönlendirdiği tasarım kararları

Bu bölüm raporun en ayırt edici parçası olmalı: aşağıdaki dört karar planda yoktu, ölçüm
sonucu ortaya çıktı. Her biri önce bir sayının beklenenden kötü çıkmasıyla fark edildi.

### 5.1 Çok bölgeli sorgu (geri getirme %88,5 → %99'un üzeri)

İlk kurulum yalnızca tam görsel üzerinden pHash ve CLIP arıyordu; ortalama geri getirme
%88,5 çıktı ve üç senaryoda çöktü: meme %25, kolaj %42, kırpma+yazı %8. Ortak neden,
kaynağın türev tuvalinin yalnızca bir bölümünü kaplaması — global tanımlayıcılar tüm tuvali
görüyordu.

Çözüm: sorgu görselini sabit bir bölge kümesine (tam, merkez, dört çeyrek, dört yarım, düz
çerçevesi kırpılmış hâli) ayırıp her bölgeyi ayrı aramak. İndeks tarafı değişmedi; maliyet
yalnızca sorgu anında ve tek bir GPU yığınına sığıyor. Değişiklikten sonra ortalama %99,2
ölçüldü; aynı ölçüm temizlenmiş korpusta yinelendiğinde **%99,5** çıktı.

*(%88,5 taban değeri, korpus tekilleştirilmeden önce ölçüldü ve sonradan yinelenmedi;
raporda bu iki sayı yan yana verilirken bu not düşülmeli.)*

### 5.2 Dokuya duyarlı piksel doğrulaması (MAE 0,0215 → 0,0102)

Salt homografi, kaynağın üstüne konan yazıyı, sticker'ı veya çizimi göremez; geometrik
olarak bölge hâlâ "kaynaktan gelmiş" görünür. Bu yüzden ZNCC ile piksel doğrulaması
eklendi. İlk sürüm ağır renk filtresinde 0,878 verdi (doğru cevap 1,000); düşen bölgeler
koyu ve düz alanlardı — orada yapısal doku olmadığı için ZNCC gürültüye dönüyordu.

Üç durumlu karar kuralına geçildi:

- **İkisi de dokulu** → ZNCC karar verir (asıl ölçüm)
- **Kaynak dokulu, türev düz** → üzeri kapatılmış, sayılmaz (yazı bandı ve sticker bu dala düşer)
- **İkisi de düz** → yapısal olarak ayırt edilemez; hiçbir yöntem düz bir alanın üstüne aynı
  tonda düz bir alan konup konmadığını söyleyemez, geometrik karar korunur

### 5.3 CRC-16 doğrulamalı filigran (4 yanlış okuma → 0)

Hazır `invisible-watermark` paketi bu ortamda kullanılamadı: kayıpsız çevrimde bile 12
görselde yalnızca 6–11 doğru okuma verdi. Yerine kanonik ölçekli DCT katsayı-çifti filigranı
yazıldı.

Çoğunluk oyu tek başına yetmedi: ağır kırpılmış bir görselde bloklar rastgele oy veriyor ve
eşiği tesadüfen geçen bir "kimlik" üretebiliyordu — ölçümde 4 kez oldu. Yüke CRC eklendi:
CRC-8 ile 3 yanlış okuma kaldı, **CRC-16 ile 0**. Yük yapısı 40 bit kimlik + 16 bit CRC.
Fazlalıktan feragat edip doğrulama gücü artırıldı, çünkü yanlış atıf bu projede daha ağır
bir hatadır.

### 5.4 Ayna farkındalıklı ölçüm (Top-1 %15,7 → %99,6)

Bu, tam hat ölçülmeden görülemeyen bir hataydı. Faz 0'da ayna senaryosunda geri getirme
%100 görünüyordu, çünkü orada sorulan soru "kaynak aday listesinde var mı" idi. Üretimdeki
hat koşturulduğunda Top-1 %15,7 çıktı.

Teşhis: ORB tanımlayıcıları yansımaya dayanıklı değil. Beklenenden kötü olan taraf şuydu —
eşleşme tamamen başarısız olmuyor, birkaç tesadüfi özellik üzerinden **eşiği geçen sahte bir
homografi** kuruluyor ve yanlış bir kapsama ölçülüyordu.

Düzeltme "başarısız olursa tekrar dene" değil, **daha iyi modeli seç** biçiminde kuruldu:
doğrudan eşleşmenin inlier oranı zayıfsa kaynağın aynalanmış hâli de denenir ve daha çok
inlier veren yönelim kazanır. Eşik ölçülerek seçildi:

| | inlier oranı |
|---|---|
| Gerçek eşleşmeler (19 senaryo) | 0,79 – 1,00 |
| Ayna sahte eşleşmeleri | 0,15 – 0,22 |
| **Seçilen kapı** | **0,60** |

Ayrım keskin olduğu için kapı diğer 19 senaryoda hiç tetiklenmiyor; ek maliyet yalnızca ayna
senaryosunda ve p50 480 ms düzeyinde kalıyor.

### 5.5 Değerlendirme verisinin kendisindeki iki hata

Dürüstlük gereği bunlar da yazılmalı, çünkü ikisi de rapora yanlış sayı sokabilirdi.

**Korpusta yinelenen görseller.** Test korpusu 320 dosyaydı ama yalnızca 276'sı benzersizdi;
görsel sağlayıcı farklı tohumları aynı fotoğrafa eşlemişti. Negatif kontrolde, indekste
birebir ikizi olan bir görsel için bağ bulmak *doğru* davranıştır ama sayaç bunu yanlış atıf
yazıyordu: ölçüm %32,5 yanlış atıf bildirdi, gerçek değer bunun kırkta biriydi. Korpus
indiricisi tekilliği garanti edecek şekilde düzeltildi.

**Döndürme senaryolarının doğru cevabı yanlıştı.** Beklenen kapsama 1,00 yazılmıştı; oysa
döndürme kenar tekrarı kullandığı için boşalan köşeler gerçek kaynak içeriği değil. Doğru
değerler hesaplandı: 5° için 0,96, 15° için 0,89. Ölçüm 0,876 veriyordu — sözde hata 0,124,
gerçek hata 0,017. Tüm beklenen değerler artık dönüşümün geometrisinden hesaplanıyor ve
türetimleri kodda yazılı.

---

## 6. Deneysel değerlendirme

### 6.1 Kurgu

320 benzersiz görselden oluşan korpus önce platformun yayın adımlarından geçirildi (filigran
gömüldü, C2PA manifesti imzalandı). Türevler bu **yayınlanmış** hâlden üretildi.

- **280 görsel** indekslendi, **40 görsel** indekse hiç alınmadı (negatif kontrol)
- Her görsel **20 türev senaryosundan** geçirildi → **6.400 sorgu**
- Her sorgu, üretimdeki `recovery.recover()` fonksiyonunun kendisinden geçti

İki nokta bu kurguyu güçlü kılıyor:

**En zor durum ölçüldü.** Türev üretimi piksel dizisi üzerinde çalıştığı için manifest ve tüm
metadata siliniyor; hattın 0. aşaması hiçbir sorguda tetiklenmiyor. Ölçülen şey saf
*kurtarma* başarısıdır.

**Negatif kontrol var.** Holdout görsellerinin türevlerinde önerilen *herhangi bir* bağ
yanlış atıftır. Bu, "sistem olmayan bir kaynağı uyduruyor mu" sorusunun doğrudan ölçümüdür.

### 6.2 Sonuçlar

| Metrik | Sonuç | Hedef |
|---|---|---|
| Ortalama Top-1 doğruluk | **%98,7** | ≥ %90 |
| Ortalama Top-5 doğruluk | **%98,7** | — |
| Yanlış atıf oranı | **%0,86** (55 / 6.400) | mümkün olan en düşük |
| Kapsama ölçüm hatası (MAE) | **0,0241** (5.519 ölçüm) | ≤ 0,05 |
| Uçtan uca gecikme | p50 **386 ms** · p95 703 ms | — |

Senaryo bazlı tam tablo: `docs/DEGERLENDIRME.md`.

### 6.3 Aşamaların iş bölümü

Doğru bulunan bağlarda belirleyici olan aşama:

| Aşama | Pay |
|---|---|
| CLIP (çok bölgeli) | %44,2 |
| Filigran | %39,7 |
| pHash / blok hash | %16,1 |

Bu dağılım tasarımı doğruluyor: piksel düzeni korunmuşsa filigran kesin kanıt veriyor,
geometrik dönüşümlerde devreyi CLIP alıyor. Tek bir yönteme dayanan bir sistem senaryoların
yaklaşık yarısını kaçırırdı.

### 6.4 Uçtan uca gecikme

Altın senaryo 5 kez, 200 içerikli indeks üzerinde koşuldu:

| Adım | Ortalama |
|---|---|
| Özgün içerik yükleme | 666 ms |
| Remix yükleme | 569 ms |
| Kimliksiz içerik yükleme (tam kurtarma) | 476 ms |
| Emek Kartı üretimi | 6 ms |
| Kampanya dağıtımı | 31 ms |
| İtiraz çözümü (SIFT ile yeniden ölçüm) | 79 ms |

İki gözlem:

**En ağır adım kimliksiz yükleme değil, özgün yükleme.** Sebebi anlamlı: özgün bir içerikte
doğrulanacak adayların hepsi yanlış çıkar ve her biri elenene kadar tam maliyetini ödetir.
Gerçek kaynak varsa eşleşme erken ve güçlüdür. Sistem, yükleyenin sözüne değil ölçüme bakar
— kaynak *olmadığını* doğrulamak da kaynak bulmak kadar iştir.

**Pay hesabı tarafı ihmal edilebilir** (Emek Kartı + dağıtım toplam 37 ms). Maliyet tamamen
köken kurtarmadadır; ölçeklendirmenin nereden yapılacağı bu ölçümle belirlenmiştir.

Kullanıcı deneyimi açısından anlamlı sonuç, yükleme adımlarının yarım saniye civarında
olmasıdır: zincir önerisi yüklemeden hemen sonra, beklemeden gösterilebilir.

---

## 7. Uygulanabilirlik ve ölçeklenebilirlik

Prototip tek makinede, SQLite ve kaba kuvvet FAISS indeksleriyle çalışır. On binler
mertebesinde bu kurulum fazlasıyla hızlı ve %100 geri getirme garantilidir. Gecikme ölçümü,
büyümede hangi düğmelerin çevrileceğini açıkça gösteriyor:

| Darboğaz | Bugün | Ölçekte |
|---|---|---|
| Aday arama | `IndexBinaryFlat` + `IndexFlatIP` | IVF-PQ / HNSW — indeks arayüzü aynı kalır |
| Geometrik doğrulama | aday başına ~90 ms, en fazla 8 aday | aday sayısı ayarlanabilir; kuyruk üzerinden asenkron |
| CLIP gömme | tek GPU, yığın 32 | gömme çevrimdışı; yatay ölçeklenir |
| Veritabanı | SQLite | PostgreSQL — veri modeli değişmez |

Mimarinin bu geçişi kolaylaştıran yanı, `provenance/` ve `attribution/` katmanlarının
veritabanını tanımamasıdır: köken kurtarma bir protokol arayüzü alır, pay hesabı saf bir
fonksiyondur.

---

## 8. Dürüst sınırlar

Bu bölüm raporda mutlaka bulunmalı. Jüri karşısındaki güvenilirlik, çalışmayan yerleri de
yazmakla kurulur.

- **Filigran kırpmaya ve döndürmeye dayanmaz.** Blok hizası bozulur. Bu bir eksiklik değil iş
  bölümüdür: hattın 3–5. aşamaları tam olarak bu durumlar için vardır ve ölçümlere göre
  orada %91–100 başarılıdır (en düşük: kırpma+yazı %91,1).
- **Ağır küçültmede kapsama ölçümü eksik kalıyor.** Görsel 200×150 piksele indiğinde yerel
  özellikler seyrekleşiyor; beklenen 1,00'e karşı 0,875 ölçülüyor. Sapmanın yönü önemli:
  hata kaynağa *eksik* pay verme yönünde ve kaynak itiraz edip yeniden ölçüm isteyebiliyor.
- **En zor iki senaryo** kırpma %30 (Top-1 %92,5) ve kırpma+yazı (%91,1). Bu senaryolarda
  kaynak genellikle aday listesinde var ama en üstte değil; sistem tek bir kaynağı
  dayatmadığı için pratikteki etki Top-1 farkından küçüktür.
- **Yanlış atıf sıfır değil, %0,86.** Sıfıra indirmek eşikleri sıkmakla mümkün ama bu
  kaçırılan atıfı artırır. Bu denge bilinçli kuruldu ve itiraz mekanizması bu yüzden
  ürünün ayrılmaz parçasıdır.
- **Değerlendirme tek bir görsel dağılımı üzerinde yapıldı.** Fotoğraf ağırlıklı bir korpus
  kullanıldı; illüstrasyon, ekran görüntüsü metinleri ve grafik içerikte davranış ayrıca
  ölçülmelidir.

---

## 9. Etik, mahremiyet ve veri

**Sistem karar vermez, öneri sunar.** Otomatik atıf hiçbir zaman nihai değildir; her bağ
itiraza açıktır ve çözülmeyen itiraz insan incelemesine düşer.

**Yanlış atıf asimetrisi bilinçli bir etik tercihtir.** Birine ait olmayan bir içerikten pay
vermek, hak edeni atlamaktan daha ağır bir hatadır: ilki üçüncü bir tarafa haksızlık eder ve
sistemin meşruiyetini yok eder, ikincisi itirazla düzeltilebilir. Tüm eşikler bu yönde
ayarlanmıştır.

**Veri asgariliği.** Sistem içerik parmak izlerini ve gömmelerini saklar; kişi tanıma, yüz
eşleştirme veya kullanıcı profilleme yapmaz. CLIP gömmeleri görsel benzerlik için kullanılır,
kimlik çıkarımı için değil.

**Açıklanabilirlik bir özellik değil, zorunluluk.** Gelir dağıtan bir sistemin her kararı
gerekçesiyle birlikte gösterilmelidir; bu yüzden pay formülü deterministik ve denetlenebilir
tutuldu, öğrenilmiş bir skorlayıcı tercih edilmedi.

**Üretici denetimi.** Her içerik, C2PA manifestine gömülü bir remix politikası taşır: remixe
izin verilip verilmediği, ticari remixe izin verilip verilmediği ve üreticinin talep ettiği
asgari kaynak payı.

---

## 10. İş modeli ve sürdürülebilirlik

**Değer önermesi.** Markalar için: remix kampanyası düzenlerken ödül havuzunun kime neden
gittiğini kanıtlarıyla görmek. İçerik üreticileri için: içerikleri yeniden dolaşıma
girdiğinde gelirden pay almak. Platform için: içerik üreticisini elde tutan ve marka
bütçesini çeken bir mekanizma.

**Gelir modeli.** Marka kampanyalarının ödül havuzundan alınan platform komisyonu
(prototipte %10). Kampanya paneli havuzu, remix kurallarını ve süreyi tanımlar; kampanya
sonunda dağıtım kanıtlarıyla birlikte raporlanır.

**Neden sürdürülebilir.** Model, platformun zaten var olan bir gelir akışının (marka
işbirlikleri) üzerine kurulur; yeni bir ödeme davranışı icat etmeyi gerektirmez. Üretici
tarafında ise doğrudan teşvik yaratır: içeriğin remixlenmesi artık kayıp değil kazanç
kaynağıdır.

**Ölçek ekonomisi.** Maliyetin tamamı köken kurtarmada ve içerik başına bir kezliktir;
sonraki her dağıtım hesabı milisaniyeler mertebesindedir.

---

## 11. Yaygın etki

- **İçerik üreticileri için:** emeğin zincirin sonunda kaybolmaması, remixin kayıp değil
  kazanç olması.
- **Platform için:** üretici bağlılığı ve marka bütçelerini çeken kanıtlanabilir bir
  paylaşım altyapısı.
- **Ekosistem için:** içerik kimliğinin (C2PA) yalnızca doğrulama için değil, **ekonomik
  paylaşım** için kullanıldığı bir örnek. Kimlik silindiğinde de çalışan bir kurtarma
  katmanı, standardın pratikteki en büyük zaafını kapatıyor.
- **Yöntemsel katkı:** "kullanılan içerik oranının ölçülmesi" fikri, gelir paylaşımının
  ötesinde telif müzakeresi, atıf zorunluluğu ve içerik denetimi gibi alanlara taşınabilir.

---

## 12. Rapora eklenecekler (kontrol listesi)

Şablon geldiğinde tamamlanacaklar:

- [ ] Takım tanıtımı ve görev dağılımı — **takımdan bilgi gerekiyor**
- [ ] Şablonun istediği kapak, özet ve biçim öğeleri
- [ ] Mimari diyagramların rapora uygun görsele dönüştürülmesi (`docs/MIMARI.md` kaynak)
- [ ] Arayüz ekran görüntüleri (Emek Kartı, zincir, remix stüdyosu, kampanya paneli)
- [ ] Kullanıcı senaryoları ve akış şemaları
- [ ] Daha önce başka yarışmaya katılım beyanı — şartname gereği (**katılmadıysak "yoktur"**)
- [ ] Kaynakça: C2PA belirtimi, CLIP, ORB, RANSAC, pHash için resmî kaynaklar
