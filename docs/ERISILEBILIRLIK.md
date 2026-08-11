# Erişilebilirlik Değerlendirmesi

**Tarih:** 9 Ağustos 2026
**Kapsam:** N-Emek referans istemcisinin altı ekranı — Akış, İçerik Detay (Emek Kartı),
Remix Stüdyo, Kaynak Bul, Kampanyalar, İnceleme Kuyruğu
**Ölçüt:** WCAG 2.1 AA

Şartnamenin istediği teslimatlardan biri. Değerlendirme, arayüz tamamlandıktan sonra
"puan için" yapılan bir kontrol listesi değil; bulunan altı kusurun beşi aynı gün
düzeltildi ve düzeltmeler kodda gerekçeleriyle birlikte duruyor.

---

## Yöntem

Üç ayrı ölçüm yapıldı, hiçbiri göz kararı değil:

1. **Kontrast hesabı.** Tema belirteçlerindeki her metin rengi, üç zemin rengine karşı
   WCAG göreli parlaklık formülüyle hesaplandı.
2. **Betikle denetim.** Altı rotanın her birinde, tarayıcıda çalışan bir betik tüm
   etkileşimli öğeleri gezip erişilebilir ad üretip üretmediklerini, görsellerin `alt`
   taşıyıp taşımadığını ve form alanlarının etiketli olup olmadığını denetledi.
3. **Sekme sırası çıkarımı.** Odaklanabilir öğeler DOM sırasıyla listelenip her birinin
   erişilebilir adı okundu; klavyeyle ulaşılamayan işlev arandı.

---

## Bulunan kusurlar ve durumları

| # | Kusur | WCAG | Durum |
|---|---|---|---|
| 1 | Klavyeyle görsel yüklenemiyordu | 2.1.1 Klavye | **Düzeltildi** |
| 2 | Üçüncül metin rengi kontrast eşiğinin altındaydı | 1.4.3 Kontrast | **Düzeltildi** |
| 3 | Form alanlarında odak halkası eziliyordu | 2.4.7 Odak Görünürlüğü | **Düzeltildi** |
| 4 | Hata mesajları ekran okuyucuya bildirilmiyordu | 4.1.3 Durum Mesajları | **Düzeltildi** |
| 5 | Pay dağılımı yalnızca renkle aktarılıyordu | 1.1.1 / 1.4.1 | **Düzeltildi** |
| 6 | Kırpma yalnızca fareyle yapılabiliyordu | 2.1.1 Klavye | **Düzeltildi** |
| 7 | Her sayfada gezinme baştan sekmeleniyordu | 2.4.1 Blokları Atlama | **Düzeltildi** |
| 8 | Serbest el çizim fareye bağlı | 2.1.1 (istisna) | **Kabul edildi**, aşağıda |
| 9 | Atıf zinciri ekran okuyucuya tek cümle söylüyordu | 1.1.1 Metin Olmayan İçerik | **Düzeltildi** |
| 10 | Ölçüm adları İngilizce değişken adlarıyla yazılıydı | 3.1.2 Parçaların Dili | **Düzeltildi** |

### 1. Klavyeyle görsel yüklenemiyordu — en ağır bulgu

Akış ve Kaynak Bul ekranlarındaki yükleme alanı `<div onClick>` idi; gerçek dosya alanı
`display:none` ile gizlenmiş ve tıklamayla tetikleniyordu. Sonuç: gizli alan sekme
sırasında yok, tıklanabilir div klavyeyle etkinleştirilemiyor. **Klavyeyle gezen bir
kullanıcı hiç görsel yükleyemiyordu** — sistemin en temel işlevi.

Alanlar `<button type="button">` yapıldı; sürükle-bırak davranışı korundu, üstüne
durumu bildiren bir erişilebilir ad eklendi ("Seçilen dosya: … Değiştir").

### 2. Üçüncül metin rengi

`--color-ink-3` (#6b7482) arayüzdeki küçük metinlerin çoğunda kullanılıyor: ölçüm
etiketleri, ipuçları, kanıt satırlarının alt yazıları. Ölçülen kontrast:

| Zemin | Önce | Sonra |
|---|---|---|
| `bg` #0a0c0f | 4,15 | **5,18** |
| `surface` #12151a | 3,87 | **4,84** |
| `surface-2` #181c23 | 3,62 | **4,52** |

Üçü de AA eşiği olan 4,5'in altındaydı — yani kural uygulama genelinde ihlal ediliyordu.
Aynı mavi-gri ton korunarak #7a8494'e taşındı; üç zeminde de geçiyor.

Diğer tüm renkler zaten geçiyordu ve değiştirilmedi:

| Renk | bg | surface | surface-2 |
|---|---|---|---|
| ink | 16,53 | 15,44 | 14,42 |
| ink-2 | 9,06 | 8,46 | 7,90 |
| gold (para) | 10,36 | 9,68 | 9,04 |
| verify (doğrulanmış) | 8,36 | 7,81 | 7,30 |
| caution (orta güven) | 7,99 | 7,46 | 6,97 |
| alert (itiraz) | 6,06 | 5,66 | 5,28 |
| link (zincir) | 6,06 | 5,66 | 5,29 |

### 3. Odak halkası

Temada `:focus-visible` için 2 piksellik bir halka tanımlıydı, ama ortak `inputClass` ve
kullanıcı seçim kutusu `focus:outline-none` taşıyordu ve daha yüksek özgüllükle bu
halkayı eziyordu. Geriye yalnızca 1 piksellik bir kenar rengi değişimi kalıyordu.
İki geçersiz kılma da kaldırıldı.

### 4. Hata mesajları

`ErrorNote` bileşeni kırmızı bir kutu çiziyordu ama canlı bölge değildi: görsel kullanıcı
hatayı görüyor, ekran okuyucu kullanan hiçbir şey duymuyordu. `role="alert"` eklendi.

Aynı sınıftan bir kusur `Spinner`'da vardı: `role="status"` dönen halkanın kendisindeydi,
yanındaki "Yükleniyor" metni canlı bölgenin dışında kalıyordu. Rol sarmalayıcıya taşındı.

### 5. Pay dağılımı çubuğu

`ShareBar`, dağılımı yalnızca renk ve genişlikle aktarıyordu; `title` bir `div` üzerinde
ekran okuyuculara güvenilir biçimde ulaşmıyor. Çubuk tek bir `role="img"` olarak sunuldu
ve tam dağılım metne çevrildi: *"Pay dağılımı: Ceyda Aksoy %20,0 · Ayşe Yılmaz %68,0 ·
Burak Demir %12,0 · N'Sosyal %10,0"*.

Bu, projenin iddiasıyla doğrudan ilgili: gelir paylaşımını **açıklanabilir** kılmayı
hedefleyen bir sistemin, dağılımı göremeyen kullanıcıya sessiz kalması tutarsız olurdu.

### 6. Kırpma

Remix Stüdyo'da kırpma tuval üzerinde sürükleyerek yapılıyordu. Kırpma araç olarak
seçildiğinde artık dört sayısal alan (Sol, Üst, Genişlik, Yükseklik) açılıyor; değerler
kaynak alanının dışına taşamayacak şekilde sınırlanıyor ve aynı "Kırpmayı uygula"
düğmesine bağlanıyor.

### 7. Blokları atlama

Her sayfada başlık ve dört gezinme bağlantısı, içerikten önce sekmeleniyordu. Sayfanın en
başına, yalnızca odaklandığında görünen bir "İçeriğe atla" bağlantısı eklendi; hedefi
`<main>`.

### 8. Serbest el çizim — bilinçli olarak kabul edilen sınır

Remix Stüdyo'daki fırça aracı fareye (veya dokunmaya) bağlı. WCAG 2.1.1, kullanıcının
**hareket yoluna bağlı** girdileri bu kuraldan açıkça muaf tutuyor ve serbest el çizim
bunun tipik örneği. Kırpma için durum farklıydı — bir dikdörtgen dört sayıyla ifade
edilebilir — ve o yüzden klavye karşılığı eklendi.

Çizim yapamayan kullanıcı sistemin geri kalanını kullanabiliyor: yükleme, kırpma, yazı
ekleme, filtre, yayınlama, Emek Kartı, itiraz ve moderasyon akışlarının hepsi klavyeyle
tamamlanabiliyor.

*(11 Ağustos eki: fırça artık işaretçi olaylarıyla çalışıyor, yani dokunmatik ekranda da
çiziliyor — önceden yalnızca fare olaylarını dinliyordu ve dokunmatik cihazda hiçbir şey
çizilmiyordu. Bu bir WCAG maddesi değil, düpedüz çalışmayan bir işlevdi. İşaretçi
yakalama da eklendi: imleç ya da parmak tuvalden çıkınca çizgi artık ortasından
kopmuyor.)*

**Hata kurtarma (11 Ağustos).** Yanlış bir fırça darbesinin tek çaresi "Tümünü sıfırla"
idi — kırpma, yazı ve filtre dahil her şey giderdi. Bu, titremesi olan ya da işaretçiyi
hassas kullanamayan kullanıcıyı orantısız cezalandırıyordu: bir hata, bütün emeği
siliyordu. **"Son işlemi geri al"** eklendi; çizim ve yazı katmanlarını kapsıyor, kırpma
ve filtreye dokunmuyor (ikisinin kendi geri dönüşü var). Yığın mantığı
`pages/duzenlemeGecmisi.ts` içinde saf fonksiyon olarak duruyor ve orada sınanıyor —
stüdyonun kendisi jsdom'da canvas bağlamı olmadığı için test edilemiyor.

### 9. Atıf zinciri grafiği — 11 Ağustos'ta bulundu

`ChainGraph` SVG'si `role="img"` idi ve erişilebilir adı tek bir sabit dizgeydi:
*"İçerik atıf zinciri"*. Görsel olmayan kullanıcı için grafiğin **tamamı** bu altı
harften ibaretti — kimin kimden türediği, hangi oranda katkı verdiği, hangi halkanın pay
almadığı; hiçbiri ulaşmıyordu.

Bu, 5 numaralı bulgunun aynısı. `ShareBar` düzeltilirken zincir grafiği gözden kaçmış.
Aynı desen uygulandı: yerleşim değil **anlam** metne çevrildi, yapraktan kökene doğru
okuma sırasıyla:

> Atıf zinciri, 3 halka. Bulduğum kare — Ceyda Aksoy, yayınlanan. Kaynağı: Şehrin
> Renkleri — Burak Demir, 1 adım geride, kullanılan alan %97,5. Onun kaynağı: Sabah ışığı
> — Ayşe Yılmaz, 2 adım geride, kullanılan alan %87,5.

Ölçülemeyen alan gizlenmiyor (*"kullanılan alan ölçülemedi"*), pay eşiğinin altında kalan
ara halka da atlanmıyor (*"ara halka, payı yok"*) — ekranda ne yazıyorsa metinde de o var.

**Düğümlerin tıklanabilirliği bilinçli olarak klavyeye açılmadı.** Bir düğüme tıklamak,
o kaynağın maskesini seçiyor; **aynı seçim** Emek Kartı'ndaki pay satırlarından da
yapılabiliyor ve onlar zaten `<button>`, yani sekmeyle ulaşılabilir. Grafik, işlevi başka
yerde tam karşılanan bir görsel kısayol. `role="img"` içine `role="button"` gömmek
(erişilebilirlik ağacında görünmez) ya da grafiği `application` yapmak, kazanç olmadan
karmaşıklık eklerdi.

Metin karşılığı `ChainGraph.test.tsx` içinde dört testle sabitlendi; etiket sabit bir
dizgeye indirildiğinde beşi birden kırmızıya dönüyor (mutasyonla doğrulandı).

### 10. Ölçüm adları — 11 Ağustos'ta bulundu

Kanıt satırlarındaki "ölçümler" panelinde backend'in sözlük anahtarları olduğu gibi
yazıyordu: `INLIER_COUNT`, `VISUAL_COVERAGE`, `SOURCE_USAGE`, `ROTATION_DEG`. Sayfa dili
`tr` olduğu için ekran okuyucu bunları **Türkçe okuma kurallarıyla seslendiriyordu**;
görsel kullanıcı için de anlamsızdı. Karışım ayrıca tutarsızdı: `esik` ve `tam` Türkçe,
`hamming` ve `cosine` İngilizce.

Her ölçüm artık Türkçe adı, doğru biçimi (oranlar yüzde, ondalık ayracı virgül) ve
birimiyle yazılıyor; `title` özniteliğinde ölçümün ne olduğunu anlatan bir cümle var.
Haritada karşılığı olmayan bir anahtar **gizlenmiyor**, ham hâliyle kalıyor — bu sayede
atlanan bir alan (`remeasured`) ekranda görülüp eklendi.

---

## Denetim sonucu

Düzeltmelerden sonra altı rotada betikle yapılan denetim:

| Ekran | Adsız etkileşimli öğe | `alt` eksiği | Etiketsiz form alanı |
|---|---|---|---|
| Akış | 0 | 0 | 0 |
| İçerik Detay | 0 | 0 | 0 |
| Remix Stüdyo | 0 | 0 | 0 |
| Kaynak Bul | 0 | 0 | 0 |
| Kampanyalar | 0 | 0 | 0 |
| İnceleme Kuyruğu | 0 | 0 | 0 |

Denetim sırasında iki alan yakalanıp düzeltildi: Emek Kartı'ndaki gelir alanı ve Kaynak
Bul'daki dosya seçici.

Yapısal olarak ayrıca doğrulanan noktalar: sayfa dili `lang="tr"`, tek `<h1>` ve altında
tutarlı `<h2>` düzeyi, gezinme `<nav>` içinde ve etiketli, ana bölge `<main>`, atıf zinciri
SVG'si `role="img"` ve açıklamalı, remix tuvali `role="img"` ve durumunu bildiren bir adla
(katman sayısı, uygulanan filtre, kırpma durumu).

---

## Yapılmayanlar

Dürüstlük gereği: aşağıdakiler henüz yapılmadı ve sonuçları bu belgede yok.

- **Gerçek ekran okuyucu ile test** (NVDA/VoiceOver). Yapılan denetim erişilebilirlik
  ağacını programatik olarak okudu; bir ekran okuyucunun gerçek okuma sırası ve
  anlaşılırlığı ayrıca denenmeli.
- **Elle klavye gezintisi.** Sekme sırası ve odak halkası yapısal olarak doğrulandı,
  ancak uçtan uca elle gezinti (özellikle Remix Stüdyo'nun araç değişimleri) yapılmadı.
- **Lighthouse erişilebilirlik skoru.** Hedef ≥90; henüz ölçülmedi.
- **Küçültme ve yeniden akış** (WCAG 1.4.4 / 1.4.10). Arayüz şu an masaüstü ağırlıklı;
  mobil düzen ayrı bir iş kalemi olarak duruyor.
*(Bu listede önce `prefers-reduced-motion` de vardı; kontrol edince temada zaten
karşılandığı görüldü — `theme.css` hem animasyon yardımcılarını kapatıyor hem tüm
geçiş sürelerini sıfırlıyor. Madde yanlış yazılmıştı, kaldırıldı.)*

---

## Bu değerlendirmenin yeniden üretilmesi

Kontrast tablosu ve denetim betiği elle yazılmış sayılar değil. Kontrast hesabı WCAG
göreli parlaklık formülünün doğrudan uygulaması; denetim betiği tarayıcı konsolunda
çalıştırılabilir ve her rotada aynı üç kontrolü yapar (erişilebilir ad, `alt`, form
etiketi). Arayüz değiştiğinde ikisi de yeniden koşturulmalı.
