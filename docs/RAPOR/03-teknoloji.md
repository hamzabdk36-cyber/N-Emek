# 3 · TEKNOLOJİ KULLANIMI

## 3.1. İzlenecek Yöntem, altyapı ve Sürüm Kontrolü

**Kod reposu.** Kaynak kodun tamamı GitHub üzerinde, tek bir monorepo olarak
saklanmaktadır:

> **https://github.com/hamzabdk36-cyber/N-Emek**

Geliştirme adımları commit geçmişinden takip edilebilir. Depo 8 Ağustos 2026'da açıldı;
raporun yazıldığı tarih itibarıyla 58 commit <!-- sayim: commit --> içeriyor. Commit mesajları Türkçe ve her
biri *neyin neden değiştiğini* söyler — ölçüm sonucu ortaya çıkan tasarım kararları
mesajlarda kayıtlıdır. Sürekli tümleştirme (GitHub Actions) her itmede backend ve arayüz
testlerini, tip denetimini, üretim derlemesini ve doküman tutarlılık denetimini koşar.

**Kullanılan diller ve teknolojiler.**

| Katman | Teknoloji |
|---|---|
| Backend | Python 3.13 · FastAPI 0.141 · SQLAlchemy 2.0 · SQLite |
| Görüntü işleme | OpenCV (contrib) 5.0 · Pillow 12.3 · NumPy 2.5 · SciPy 1.18 · PyWavelets |
| Köken ve benzerlik | `c2pa-python` 0.37.5 (Rust `c2pa-rs` bağlantısı) · ImageHash 4.3 · FAISS 1.15 · `open_clip_torch` 3.3 |
| Yapay zekâ | CLIP ViT-B/32, `laion2b_s34b_b79k` kontrol noktası, PyTorch CUDA |
| Arayüz | React 19 · TypeScript 5.9 · Vite 7 · Tailwind CSS 4 · React Router 7 |
| Test | pytest (backend) · Vitest + Testing Library (arayüz) |
| Dağıtım | Docker Compose — arayüz nginx üzerinden `:5173`, backend `:8000` |

Bağımlılık listesi bilinçli olarak dardır. Planlama aşamasında düşünülen React Flow,
Zustand ve Framer Motion kütüphanelerinin hiçbiri kullanılmadı: atıf zinciri grafiği
yaklaşık iki yüz satırlık kendi SVG yerleşim kodumuzla çiziliyor, durum yönetimi React'in
kendi ilkelleriyle yapılıyor. Gerekçe, üç yüz kilobaytlık bir grafik kütüphanesinin bu
ekran için gereğinden ağır olması ve yerleşimin test edilebilir saf bir fonksiyona
çıkarılabilmesiydi.

**Teknik altyapı.** Sistem iki servisten oluşur. Backend, FastAPI üzerinde 22 uç nokta
<!-- sayim: uc --> sunar: içerik yükleme, remix, atıf, Emek Kartı, kampanya, ödeme,
itiraz, moderasyon ve doğrulama. Veri modeli SQLAlchemy ile tanımlıdır (`Content`,
`Edge`, `Manifest`, `Claim`, `Payout`, `Dispute`, `Campaign`). Mimarinin kritik özelliği,
`provenance/` ve `attribution/` katmanlarının veritabanını **tanımamasıdır**: köken
kurtarma bir protokol arayüzü alır, katkı payı hesabı saf bir fonksiyondur. Bu ayrım,
SQLite'tan PostgreSQL'e geçişi veri modelini değiştirmeden mümkün kılar.

Prototip `docker compose up --build` ile tek komutta ayağa kalkar; jürinin kendi
makinesinde çalıştırabilmesi için README'de üç adımlık kurulum bulunur.

**Veri setleri.** Üç ayrı veri kümesi kullanılmaktadır:

- **Değerlendirme korpusu** — 320 CC0 lisanslı görsel. Tekilleştirildikten sonra
  indekse 280, negatif kontrole 40 görsel ayrıldı. Türevler, korpusun **yayınlanmış**
  hâlinden (filigran gömülü, C2PA imzalı) üretildi.
- **Demo verisi** — jüri sunumu için üç kullanıcı, üç gönderi ve bir marka kampanyasından
  oluşan altın senaryo; `scripts/seed_demo.py` ile yeniden üretilebilir.
- **Eğitim verisi** — **yoktur.** Gerekçesi 3.2'de.

**Analizler ve doğrulama disiplini.** Projenin değişmez kuralı şudur: *hiçbir performans
sayısı elle yazılmaz, hepsi çalıştırılabilir bir betiğin çıktısıdır.* Ölçüm betikleri
`backend/eval/` altında, doküman üretenler `scripts/` altındadır. Bu kural bir denetim
betiğiyle zorlanır: `scripts/dokuman_denetimi.py` testlerin ve uç noktaların gerçek
sayısını ölçer, dokümanlardaki işaretli iddialarla karşılaştırır ve uyuşmazlıkta
dosya:satır vererek sıfırdan farklı çıkar. Bu raporun kaynak metni de aynı denetimden
geçmektedir.

Testler: backend 128 test, arayüz 114 test. <!-- sayim: backend, arayuz -->
Sürekli tümleştirme, uzun süren işaretlenmiş testler hariç
125 test <!-- sayim: backend-hizli --> koşar.

## 3.2. Model ve Veri Doğrulama

Bu bölümün baştan söylenmesi gereken bir özelliği var: **projede eğitilen bir model
yoktur.** Yapay zekâ bileşeni (CLIP) yalnızca çıkarım için, dondurulmuş ağırlıklarla
kullanılır. Bu bir eksiklik değil, bilinçli bir tasarım kararıdır ve üç gerekçesi vardır.

**Birincisi, asıl iddia öğrenilebilir bir şey değil.** Sistemin ürettiği kritik sayı,
türevde kaynağın kapladığı alan oranıdır. Bu bir *ölçümdür*: homografi kestirilip
pikseller doğrulanır. Bir model eğitmek bu sayıyı tahmine çevirirdi — yani projenin tam
olarak karşı çıktığı şeye.

**İkincisi, etiketli veri yok.** "Bu türevde kaynağın %41'i var" diye etiketlenmiş bir
veri kümesi mevcut değildir; üretmek için zaten geometrik ölçüme ihtiyaç vardır. Kendi
ölçümümüzle etiketleyip onu bir modele öğretmek, ölçümün hatasını modele kopyalamaktan
başka bir şey yapmazdı.

**Üçüncüsü, denetlenebilirlik.** Eğitilmiş bir bileşen veri kümesi yanlılığı ve model
kayması riski getirir. İtiraz eden bir kullanıcıya "modelimiz böyle öğrendi" demek, gelir
dağıtan bir sistemin meşruiyetini yok eder. Bugün her sayının arkasında ya bir imza, ya
bir özet, ya da yeniden üretilebilir bir geometrik ölçüm vardır.

Bu karar, doğrulama yükünü ortadan kaldırmaz — yerini değiştirir. Aşağıdaki tablo
şablonun sorduğu her maddenin bu mimarideki karşılığını gösterir:

| Beklenen | Bu projedeki karşılığı |
|---|---|
| Veri ön işleme | Korpus tekilleştirme, kanonik ölçekleme, yayın adımları, çok bölgeli sorgu ayrıştırması |
| Model eğitimi | Eğitim yok; yerine **eşik kalibrasyonu** — her eşik ölçümle seçildi |
| Aşırı öğrenme önlemi | Holdout negatif kontrol · veri sızıntısının bulunup temizlenmesi · beklenen değerlerin geometriden türetilmesi |
| Performans metrikleri | Top-1/Top-5 doğruluk, kesinlik, duyarlılık, F1, yanlış atıf oranı, kapsama MAE, gecikme |

**Veri ön işleme.** Korpustaki her görsel önce platformun yayın adımlarından geçirilir:
kanonik ölçeğe getirilir, görünmez filigran gömülür, C2PA manifesti imzalanır. Sorgu
tarafında görsel sabit bir bölge kümesine ayrılır — tam görüntü, merkez, dört çeyrek,
dört yarım ve düz çerçevesi kırpılmış hâli. Bu ayrıştırma, kaynağın türev tuvalinin
yalnızca bir bölümünü kapladığı durumlarda global gömmenin kaynağı seyreltmesini önler.

**Eğitim yerine kalibrasyon.** Sistemdeki her eşik, tahminle değil ölçümle seçildi. En
öğretici örnek ayna senaryosudur. İlk değerlendirmede ayna senaryosunda geri getirme
%100 görünüyordu, çünkü sorulan soru "kaynak aday listesinde var mı" idi. Üretimdeki hat
koşturulduğunda Top-1 doğruluğu **%15,7** çıktı. Teşhis: ORB tanımlayıcıları [11]
yansımaya dayanıklı değil — ve beklenenden kötü olan taraf, eşleşmenin tamamen
başarısız olmaması, birkaç tesadüfi özellik üzerinden eşiği geçen **sahte bir homografi**
kurulup yanlış bir kapsama ölçülmesiydi.

Düzeltme "başarısız olursa tekrar dene" değil, "daha iyi modeli seç" biçiminde kuruldu:
doğrudan eşleşmenin aykırı-değer oranı zayıfsa kaynağın aynalanmış hâli de denenir ve
daha çok içeriden nokta veren yönelim kazanır. Kapı değeri ölçülerek belirlendi:

| Durum | İçeriden nokta oranı |
|---|---|
| Gerçek eşleşmeler (diğer 19 senaryo) | 0,79 – 1,00 |
| Ayna sahte eşleşmeleri | 0,15 – 0,22 |
| **Seçilen kapı** | **0,60** |

Ayrım keskin olduğu için kapı diğer senaryolarda hiç tetiklenmiyor; ek maliyet yalnızca
ayna senaryosunda oluşuyor. Top-1 doğruluğu %15,7'den **%99,6**'ya çıktı. Aynı disiplinle
seçilen diğer eşikler: algısal hash için Hamming mesafesi ≤ 12, yalnızca benzerlikten
gelen güven için tavan 0,80, doğrulanamayan adaylar için çarpan 0,40.

**Aşırı öğrenme önlemleri.** Eğitim olmadığı için klasik anlamda aşırı öğrenme riski
yoktur; ancak eşik kalibrasyonunun kendisi bir uydurma riski taşır ve buna karşı üç önlem
alınmıştır.

*Holdout negatif kontrol.* 40 görsel indekse **hiç alınmadı**. Bu görsellerin
türevlerinde önerilen *herhangi bir* bağ yanlış atıftır. Bu, "sistem olmayan bir kaynağı
uyduruyor mu" sorusunun doğrudan ölçümüdür ve eşikleri gevşetme yönündeki her ayarı
anında cezalandırır.

*Veri sızıntısının bulunup temizlenmesi.* Test korpusu başlangıçta 320 dosyaydı ama
yalnızca 276'sı benzersizdi; görsel sağlayıcı farklı tohumları aynı fotoğrafa
eşlemişti. Negatif kontrolde, indekste birebir ikizi bulunan bir görsel için bağ bulmak
*doğru* davranıştır — ama sayaç bunu yanlış atıf yazıyordu. Ölçüm %32,5 yanlış atıf
bildirdi; gerçek değer bunun kırkta biriydi. Korpus indiricisi tekilliği garanti edecek
şekilde düzeltildi. Bu, değerlendirme kurgusunun kendi sızıntısını bulup kapattığı bir
örnektir.

*Beklenen değerlerin geometriden türetilmesi.* Kapsama ölçümünün "doğru cevabı" elle
etiketlenmez, türevi üreten dönüşümün geometrisinden hesaplanır. Bir hata bu yolla da
yakalandı: döndürme senaryolarında beklenen kapsama 1,00 yazılmıştı, oysa döndürme kenar
tekrarı kullandığı için boşalan köşeler gerçek kaynak içeriği değildir. Doğru değerler
hesaplandığında (5° için 0,96, 15° için 0,89) sözde 0,124'lük hata gerçek 0,017'ye indi.

**Performans metrikleri.** Değerlendirme, 280 indekslenmiş ve 40 holdout görselin her
birinin 20 türev senaryosundan geçirilmesiyle, toplam 6.400 sorgu üzerinde yapıldı. Her
sorgu üretimdeki `recovery.recover()` fonksiyonunun kendisinden geçti.

| Metrik | Sonuç | Hedef |
|---|---|---|
| Ortalama Top-1 doğruluk | **%98,7** | ≥ %90 |
| Ortalama Top-5 doğruluk | **%98,7** | — |
| Kesinlik (bağ düzeyi) | **%96,39** | — |
| Duyarlılık (bağ düzeyi) | **%98,70** | — |
| **F1 (bağ düzeyi)** | **0,9753** | — |
| Yanlış atıf oranı | **%0,86** (55 / 6.400) | mümkün olan en düşük |
| Kapsama ölçüm hatası (MAE) | **0,0241** (5.519 ölçüm) | ≤ 0,05 |
| Uçtan uca gecikme | p50 **386 ms** · p95 703 ms | — |

Kesinlik, duyarlılık ve F1 bağ düzeyinde sayılır: doğru pozitif, gerçek kaynağa önerilen
bağdır; yanlış pozitif, gerçek kaynağın yanında önerilen her fazladan bağ ile negatif
kontrolde önerilen her bağdır. Bu ölçü, yanlış atıf oranından **bilinçli olarak daha
katıdır** — doğru kaynak bulunmuş olsa bile fazladan bir bağ hata sayılır. Hatanın
ağırlıklı tarafı yanlış pozitiftir (207'ye karşı 73 kaçırılan bağ); en zayıf senaryo
ağır küçültmedir (F1 0,9106).

Aşamaların iş bölümü de ölçüldü: doğru bulunan bağlarda belirleyici aşama %44,2 CLIP,
%39,7 filigran, %16,1 algısal hash. Bu dağılım tasarımı doğrular — piksel düzeni
korunmuşsa filigran kesin kanıt verir, geometrik dönüşümlerde devreyi CLIP alır. Tek bir
yönteme dayanan bir sistem senaryoların yaklaşık yarısını kaçırırdı. Aşama 0 ve 1 bu
dağılımda görünmez, çünkü değerlendirme türevleri üstverisi silinerek üretilir; Aşama 5
ise aday bulmaz, bulunanın kapsamasını ölçer.

**Dürüst sınırlar.** Ağır küçültmede (görsel 200×150 piksele indiğinde) yerel özellikler
seyrekleşiyor ve kapsama eksik ölçülüyor: beklenen 1,00'e karşı 0,875. Sapmanın yönü
önemlidir — hata kaynağa *eksik* pay verme yönündedir ve kaynak itiraz edip yeniden ölçüm
isteyebilir. Yanlış atıf oranı sıfır değildir; sıfıra indirmek eşikleri sıkmakla mümkün
ama bu kaçırılan atıfı artırır. Denge bilinçli kuruldu; itiraz mekanizması bu yüzden
ürünün ayrılmaz parçasıdır. Değerlendirme fotoğraf ağırlıklı tek bir korpus üzerinde
yapılmıştır; illüstrasyon ve grafik içerikte davranış ayrıca ölçülmelidir.

## 3.3. Kullanıcı Deneyimi (UI/UX) Tasarımı

**Kullanıcı akışları.** Ürün beş sahnelik bir altın senaryo etrafında tasarlandı ve
akışların tamamı `docs/KULLANICI-AKISLARI.md` içinde durum makineleriyle belgelendi.
Kritik akış üçüncü sahnedir: kimliği silinmiş bir içerik yüklendiğinde sistem köken
kurtarma hattını çalıştırır, bulduğu zinciri kanıtlarıyla önerir ve kullanıcı bunu
onaylayabilir ya da itiraz edebilir.

| Kullanıcının sorusu | Cevaplandığı ekran |
|---|---|
| Bu içerik nereden geldi? | Emek Kartı — köken anlatısı |
| Payım neden bu kadar? | Emek Kartı — pay satırı ve formül |
| Sistem bunu nereden biliyor? | Kanıt satırları — hangi aşama ne buldu |
| Kaynağın ne kadarı kullanılmış? | Ölçülen bölge — maskeli karşılaştırma |
| Katılmıyorum, ne yapabilirim? | İtiraz akışı |
| Elimdeki görselin kaynağı ne? | Kaynak Bul |

**Arayüz tasarım kararları — ve neden öyle.** Kararların her biri bir gerekçeye bağlıdır:

- **Her rakamın altında gerekçesi.** Pay dağılımında her satır açılabilir ve kapsama,
  güven, sönümleme değerleriyle birlikte bunları birleştiren formülü gösterir. Gelir
  dağıtan bir arayüzde sayının kendisi yeterli değildir.
- **Maskede ayrım renkle değil kontrastla.** Eşleşen bölge parlak kalır, eşleşmeyen
  griye düşer. İlk tasarımda renkli bir katman kullanılıyordu; kapsama %90'ı aştığında
  yoğun renk görüntüyü yutuyor ve kullanıcı neyin ölçüldüğünü göremiyordu.
- **Ham ölçüm adları kullanıcıya gösterilmez.** Kanıt satırlarında `phash_blok` gibi iç
  anahtarlar değil, insan diliyle yazılmış etiketler ve birimli değerler görünür.
  Etiketler tek bir kaynaktan gelir, böylece backend ile arayüz ayrışamaz.
- **Boş durumlar açıklar.** Moderasyon kuyruğu boşken "kayıt yok" demez; kuyruğun
  yalnızca insana yükseltilmiş itirazları gösterdiğini, dolayısıyla boş olmasının
  sistemin çalıştığı anlamına geldiğini anlatır.

![Şekil 1 — Emek Kartı'nda bir payın gerekçesi: ölçülen kapsama, güven, sönümleme ve bunları birleştiren formül satırı, altında kanıt satırları.](docs/gorseller/03-pay-gerekcesi.jpg)

![Şekil 2 — Ölçülen bölge: kaynak ve türev yan yana, türevde yeşil alan ölçümle o kaynaktan geldiği doğrulanan bölge. Geometri satırı sayıyı açıkça yazıyor.](docs/gorseller/05-olculen-bolge-oran.jpg)

![Şekil 3 — Kimliği silinmiş bir görselin kaynağının bulunması: aşamalar sırayla deneniyor, her birinin süresi ve sonucu ekranda.](docs/gorseller/10-kaynak-bul.jpg)

**Erişilebilirlik yaklaşımı.** WCAG 2.1 AA hedef alındı ve değerlendirme
`docs/ERISILEBILIRLIK.md` içinde belgelendi. Denetim gözle değil betikle yapıldı: altı
rotada erişilebilir ad, `alt` metni ve form etiketi kontrol edildi; kontrast oranları
WCAG göreli parlaklık formülünün doğrudan uygulanmasıyla hesaplandı. On bir kusur
bulundu; onu düzeltildi, biri gerekçesiyle kabul edildi.

En ağır bulgu, klavyeyle görsel yüklenememesiydi: dosya seçici gizlenmiş bir `input`
üzerine kurulmuştu ve sekme sırasına hiç girmiyordu — klavye kullanan biri ürünün ilk
adımını tamamlayamıyordu. İkinci önemli bulgu mobil düzendi. Arayüz masaüstünde
çalışıyordu ama dar ekranda hiç ölçülmemişti; kodda "başlık üç satır yerine iki satır oluyor" diyen bir
yorum vardı ve ölçüm bunun doğru olmadığını gösterdi: yapışkan üst çubuk **163 piksel**,
yani 844 piksellik ekranın beşte biri kadardı. Üç değişiklikle çubuk **109 piksele**
indirildi ve altı ekranın hiçbirinde yatay kayma kalmadı (WCAG 1.4.10).

Bilinçli olarak kabul edilen bir sınır da kayıtlıdır: Remix Stüdyosu'ndaki serbest el
çizim aracı klavyeyle kullanılamaz. Bunun yerine aracın çıktısı — kaç katman eklendiği,
hangi filtrenin uygulandığı, kırpma durumu — ekran okuyucuya bildirilir ve tüm yayın
akışı çizim yapmadan tamamlanabilir.

Henüz yapılmayanlar da açıkça yazılıdır: gerçek ekran okuyucu (NVDA/VoiceOver) ile test,
uçtan uca elle klavye gezintisi, Lighthouse skoru ve metin büyütme (WCAG 1.4.4) ölçümü.

![Şekil 4 — Aynı Emek Kartı 390×844 piksellik mobil görünümde: iki satırlık üst çubuk, pay dağılımı ve formül satırı; yatay kayma yok.](docs/gorseller/11-mobil.jpg)

**Kullanılabilirlik testi.** Test, üç profilden (içerik üreticisi, sıradan paylaşan, marka
yöneticisi) beş katılımcıyla, altı görevlik bir protokolle koşuldu. Protokolün merkezindeki
görev ikincidir: *"Emek Kartı'ndaki payın gerekçesini kendi cümlenle söyle."* Bu görev,
projenin açıklanabilirlik iddiasını doğrudan sınar — kullanıcı formülü değil, **nedeni**
anlatabiliyor mu. Ölçütler görev başına başarı, süre, hata sayısı ve sesli düşünme
notlarıdır; oturum sonunda Türkçeleştirilmiş SUS ölçeği uygulanır.

| Ölçüt | Sonuç |
|---|---|
| Katılımcı sayısı | 5 — 2 üretici · 2 paylaşan · 1 marka yöneticisi |
| Görev başarı oranı (altı görev ortalaması) | **%60,0** yardımsız · %80,0 yardımla |
| Payın gerekçesini doğru anlatan katılımcı | **3 / 5** |
| SUS skoru (hedef ≥ 68) | **60,0 — hedefin altında** |

**Sonuç hedefin altında kaldı ve bu saklanmıyor.** Ölçümün amacı arayüzü doğrulamak
değil kusurlarını bulmaktı; dördü doğrudan açıklanabilirlik iddiasına dokunan yedi bulgu
çıktı. Kaynak arama ekranını beş katılımcıdan yalnızca biri yardımsız buldu; itiraz iki
katılımcıda şikâyet kutusu sanıldı, yeniden ölçüm başlattığı anlaşılmadı; ölçülen bölge
maskesi iki katılımcıda ters okundu — parlak alan, kaynaktan gelen bölge değil
*değiştirilen* bölge sanıldı; pay oranlarının hangi ölçüme göre değiştiği üç katılımcıda
anlaşılmadı. Hiçbiri teslim itibarıyla kapatılmadı, düzeltmeler mentörlük dönemine
planlandı. Sınırlar da kayıtlı: beş katılımcı istatistik üretmez, oturumları tek
moderatör yürüttü ve başarısız görevlerde gerçek süre kaydedilmediği için ortalamalar
protokolün üç dakikalık sınırıyla hesaplandı.

Protokolün tamamı ve oturum kayıt formu `docs/KULLANILABILIRLIK-PROTOKOL.md` ile
`docs/KULLANILABILIRLIK-FORMU.md`, ham kayıtlar ve hesaplanmış sonuçlar
`docs/KULLANILABILIRLIK-SONUCLARI.md` belgelerindedir.

**Kullanıcı araştırması.** Ayrı bir soruyu sınamak için — *ürün kullanılabiliyor mu*
değil, *problem gerçek mi* — dört profilden on kişiyle, kullanılabilirlik testine
katılmamış katılımcılarla görüşüldü (`docs/KULLANICI-ARASTIRMASI.md`). Sorular
bilerek geçmişe dairdi; hipotetik soru sorulmadı. Üreticilerin dördü de içeriğinin
izinsiz kullanıldığı somut bir olay anlattı; on kişiden beşi kaynağı bulmak için
tersine görsel arama denedi, dördü takibi sonuçsuz bıraktı — problem tanımının
doğrudan karşılığı. Marka tarafı da aynı
boşluğu doğruladı: ödül beğeniye göre dağıtılmış, bir katılımcı *"benim fotoğrafım
daha iyiydi ama çevrem olmadığı için kaybettim"* demiş ve marka bunu haklı bulmuş.

En değerli bulgu beklenenin dışındaydı: **kendiliğinden talep edilen şey gelir değil
görünürlüktü** (on kişinin yedisi isim, etiket veya bildirim istedi; gelir konusunu
yalnızca iki kişi ve ancak "sormadığınız soru" olarak açtı). Bu, gelir paylaşımını
geçersiz kılmıyor ama ürünün vurgusunu etkiliyor: atıf ve bildirim katmanı en az
dağıtım kadar görünür olmalı. İkinci bulgu terim düzeyinde: "emek" kelimesini altı
katılımcı kendiliğinden kullandı, "atıf" ve "köken" hiçbir görüşmede geçmedi.

**Hedef kitleye uygunluk.** Arayüz, teknik olmayan bir içerik üreticisinin ürünü
anlayabilmesi üzerine kuruldu. Akıştaki bir gönderinin kökeni tek satır düz metinle
özetlenir ("2 kaynaktan türedi", "özgün içerik · 2 türev üretildi"); ayrıntı isteyen
kullanıcı Emek Kartı'na iner. Ölçüm dili her yerde aynıdır ve hiçbir ekran kullanıcıdan
bir eşik değeri veya model adı bilmesini beklemez.
