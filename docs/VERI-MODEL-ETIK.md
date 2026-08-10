# Veri, Model, Etik ve Performans

Gelir dağıtan bir sistem, kararlarının **hangi veriye dayandığını, neyi saklamadığını ve
yanıldığında ne olduğunu** açıkça yazmak zorundadır. Bu belge onu yapar.

Performans rakamlarının tamamı ölçüldü ve betik çıktısıdır: `DEGERLENDIRME.md`
(6.400 sorgu), `FAZ0-SONUCLARI.md`, `GECIKME.md`, `ACILIS-SURESI.md`. Model tarafı için
`YZ-MIMARISI.md`.

---

## 1. Veri kaynakları

### Değerlendirme korpusu

| | |
|---|---|
| Kaynak | [picsum.photos](https://picsum.photos) |
| Lisans | **Unsplash Lisansı** — ticari dahil serbest kullanım, atıf zorunlu değil |
| Boyut | 320 benzersiz görsel, 800×600 |
| Depoda mı | **Hayır.** `scripts/fetch_eval_images.py` ile yeniden üretiliyor |
| Kişi içeriyor mu | Manzara/nesne ağırlıklı; insan içeren kareler bulunabilir |

> **Terim düzeltmesi:** proje planında bu korpus yer yer "CC0" diye geçiyor. Doğrusu
> **Unsplash Lisansı**; CC0'a çok yakın (atıf gerektirmez, ticari kullanıma açıktır) ama
> aynı şey değil — Unsplash Lisansı fotoğrafları bir rakip fotoğraf hizmetinde toplayıp
> yeniden dağıtmayı kısıtlar. Bu proje için fark pratik sonuç doğurmuyor, ama raporda
> doğru terim kullanılmalı.

**Tekillik neden garanti altında.** İlk korpusta picsum farklı tohumları aynı fotoğrafa
eşlemiş, 320 dosyanın yalnızca 276'sı benzersiz çıkmıştı. Yinelenen bir görsel
değerlendirmeyi *sessizce* bozuyor: indekste birebir ikizi olan bir holdout görseli için
bağ bulmak doğru davranıştır ama negatif kontrol sayacı bunu yanlış atıf yazar. Ölçüm
%32,5 yanlış atıf bildirdi — gerçek değildi. Artık indirme betiği SHA-256 ile tekilliği
garantiliyor ve `run_benchmark.dedupe()` ayrıca kontrol ediyor.

Bu, ölçüm altyapısının kendisinin de denetlenmesi gerektiğinin somut örneği.

### Demo verisi

Altın senaryo (`scripts/seed_demo.py`) aynı korpustan üretiliyor. Gerçek kullanıcı
içeriği, gerçek kişi verisi veya üçüncü taraf telifli materyal **kullanılmıyor**.

### Eğitim verisi

**Yok.** Sistemde eğitilmiş hiçbir bileşen yok; CLIP donuk kullanılıyor. Gerekçesi
`YZ-MIMARISI.md` §4'te.

---

## 2. Ne saklanıyor, ne saklanmıyor

Kullanıcı kaydında tutulan alanların **tamamı** (`models/entities.py::User`):

| Alan | İçerik |
|---|---|
| `id` | Rastgele 16 karakter |
| `handle` | Kullanıcı adı |
| `display_name` | Görünen ad |
| `accent` | Arayüz vurgu rengi |
| `created_at` | Kayıt zamanı |

**Saklanmayanlar:** e-posta, parola, telefon, konum, IP, cihaz kimliği, doğum tarihi,
biyometrik veri, çerez/izleme kimliği. Prototipte parola hiç sorulmuyor — kimlik
doğrulama ana platformun işi (`app/core/security.py`).

İçerik kaydında tutulanlar: dosya yolu, başlık, açıklama, boyutlar, parmak izleri
(SHA-256 + algısal hash'ler + blok hash'leri), filigran kimliği, C2PA manifest URN'i,
CLIP vektörü, üretici tercihleri, gelir.

**Sistemin yapmadıkları:** yüz tanıma, kişi eşleştirme, kullanıcı profilleme, davranış
takibi, reklam hedefleme, içerik moderasyonu (uygunsuz içerik sınıflandırması).

---

## 3. Gömme mahremiyeti — dürüst nüans

"Kişisel veri işlenmiyor" demek **kolay ama eksik** olurdu.

CLIP gömmesi görselden türetilir. Görselde tanınabilir bir kişi varsa, o vektör kişiye
ait görsel bilgiyi de kodlar. Vektörden görseli geri üretmek pratikte zor ama teorik
olarak bilgi oradadır.

Doğru ifade şu:

- Sistem kişisel veri **çıkarmayı amaçlamıyor** ve bu amaçla hiçbir bileşen içermiyor.
- Gömme yalnızca **görsel–görsel benzerliği** için kullanılıyor; kimlik çıkarımı,
  sınıflandırma veya etiketleme için değil.
- Ama kullanıcı içinde kişi bulunan bir fotoğraf yüklerse, o içerikten türetilen veri
  KVKK/GDPR açısından **kişisel veri sayılabilir**. Bu, N-Emek'e özgü değil; içerik
  barındıran her platformun sorumluluğu ve ana platformun aydınlatma metniyle
  yönetilmesi gereken bir konu.

**Veri asgariliği ilkesi uygulanıyor:** görselin kendisi zaten platformda; N-Emek'in
*eklediği* veri, içerik başına ~40 KB parmak izi ve vektör (`IS-MODELI.md` §6).

---

## 4. Etik omurga: yanlış atıf neden daha ağır

Bu projenin en belirleyici etik tercihi.

**Yanlış atıf**, hak etmeyen birine pay vermek demektir. Üçüncü bir tarafa doğrudan
haksızlık eder, geri alınması zordur ve fark edildiğinde sistemin tüm kararlarının
meşruiyetini yok eder.

**Kaçırılmış atıf**, hak edeni atlamaktır. Haksızlıktır ama **düzeltilebilir**: kaynak
itiraz eder, yeniden ölçüm yapılır, paylar güncellenir.

Asimetri simetrik değildir; eşikler de öyle ayarlanmadı.

### Bu tercihin koddaki karşılığı

| Önlem | Değer | Ne yapıyor |
|---|---|---|
| CLIP güven tavanı | **0,75** | Yalnızca benzerlikten gelen bir bağ asla "yüksek güven" olamaz |
| Geometri başarısızlık cezası | **× 0,40** | Doğrulanamayan bağ genelde eşiğin altına düşer |
| Bağın zincire girme eşiği | **0,35** | Zayıf kanıt bağ üretmez |
| Otomatik onay eşiği | **0,85** | Altındakiler "önerilen" kalır, kesikli çizilir |
| Ölçülemeyen kapsama tavanı | **%35** | Ölçemediğimizi yüksek varsaymayız |
| Pay eşiği | **%3** | Gürültü düzeyindeki katkı pay üretmez |

### Ölçülen sonuç

Değerlendirmenin en önemli sütunu **negatif kontrol**: 40 görsel indekse hiç alınmadı;
bu sorgularda önerilen *herhangi bir* bağ yanlış atıftır.

| Metrik | Sonuç |
|---|---|
| Yanlış atıf oranı | **%0,86** (55 / 6400) |
| — yanlış Top-1 | 3 |
| — negatif kontrol bağı | 52 |
| Top-1 doğruluk | %98,7 |

Yani sistem 6.400 sorguda 55 kez birine hak etmediği bir bağ önerdi. Bu bağların hepsi
itiraza açık ve hiçbiri "kesin" olarak sunulmuyor.

---

## 5. Sistem asla ne demez

> **"Bu içeriğin sahibi budur."**

Sistem yalnızca **kanıtlı zincir önerisi** sunar. Her bağın altında hangi aşamanın ne
bulduğu satır satır yazılıdır ve her bağ itiraz edilebilir.

Arayüz bu ayrımı görünür kılıyor:

- Onaylanmamış bağ **kesikli çizgi** ile çiziliyor
- Ölçülemeyen kapsama **"ölçülemedi"** yazıyor, sayı uydurulmuyor
- Güven bandı üç kademeli gösteriliyor (yüksek / orta / düşük) ve notu var
- Pay eşiğinin altında kalan ara halka grafikten **düşmüyor**: "ARA HALKA · PAY YOK"

---

## 6. İtiraz hakkı ve insan denetimi

İtirazı **yalnızca payın sahibi** açabilir (uç düzeyinde zorlanıyor: başkasına **403**).

```
Açık ──► SIFT ile yeniden ölçüm
           ├─ anlamlı değişim (≥ 0,05) ──► Kabul  → zincirin tüm payları güncellenir
           ├─ sonuç aynı              ──► Ret    → gerekçe kullanıcıya gösterilir
           └─ ölçüm yine yapılamadı   ──► Yükselt → insan moderatöre
```

Üç ayrıntı önemli:

1. **Eşik açık:** `MATERIAL_CHANGE = 0,05`. Neyin "anlamlı değişim" sayıldığı kodda tek
   bir sabit ve itiraz yanıtında `material_change_threshold` olarak kullanıcıya dönüyor.
2. **Yükseltme gerçek.** Ölçüm yine sonuç vermezse makine karar vermiyor; bağ insan
   incelemesine gidiyor ve kullanıcıya *"karar verilene kadar mevcut pay geçerli"*
   deniyor. Sistem karar veremediği yeri gizlemiyor.
3. **Ret de gerekçeli.** İtiraz reddedilirse kullanıcı önceki ve sonraki ölçümü,
   farkı ve eşiği görüyor.

İnsan moderatör kuyruğu ayrı bir ekran; yalnızca **açık** ve **yükseltilmiş** itirazlar
düşüyor. Demo verisinde kuyruk boş, çünkü oradaki itiraz otomatik çözüldü — boş olması
sistemin çalıştığı anlamına geliyor.

---

## 7. Üretici denetimi

Her içerik, C2PA manifestine gömülü bir remix politikası taşıyor
(`org.nemek.remix_policy`) ve bu politika **dosyayla birlikte seyahat ediyor**:

| Tercih | Etkisi |
|---|---|
| `remix_allowed` | Kapalıysa Remix Stüdyosu açılmıyor, uç **403** dönüyor |
| `commercial_remix_allowed` | Ticari remix izni |
| `min_source_share` | Üreticinin talep ettiği asgari kaynak payı (üretici tabanını aşamaz) |

---

## 8. Model etiği

Sistemde eğitim yok, ama kullanılan model birinin eğittiği bir model: CLIP ViT-B/32,
**LAION-2B** üzerinde ön eğitilmiş.

**Devralınan riskler.** LAION-2B web'den kazınmış bir veri kümesi; bilinen sorunları var
(telifli materyal, dengesiz temsil, filtrelenmemiş içerik). Bu yanlılıklar modele geçer.

**Bu sistemde etkisi neden sınırlı:**

- Model **sınıflandırma yapmıyor** — kişi, tür, duygu, uygunluk etiketi üretmiyor
- Model **karar vermiyor** — yalnızca aday sıralıyor, kararı geometrik ölçüm veriyor
- Model çıktısına **tavan** uygulanıyor (0,75)
- Yanlılığın en tehlikeli biçimi (belirli grupların sistematik olarak yanlış
  sınıflandırılması) burada karşılık bulmuyor, çünkü çıktı bir sınıf değil bir benzerlik
  skoru ve o skor tek başına hiçbir şeyi belirlemiyor

**Kalan risk:** modelin belirli görsel türlerinde daha zayıf aday üretmesi, o türlerde
kaçırılmış atıfa yol açabilir. Ölçülen senaryolarda en zayıf nokta kırpma %30 (%92,5) ve
kırpma+yazı (%91,1); ikisi de içerik türüyle değil, kaynağın kapladığı alanın küçüklüğüyle
ilgili.

---

## 9. Ölçülmüş performans — özet

| Metrik | Sonuç | Kaynak |
|---|---|---|
| Top-1 doğruluk (20 senaryo, 6.400 sorgu) | **%98,7** | `DEGERLENDIRME.md` |
| Top-5 doğruluk | %98,7 | `DEGERLENDIRME.md` |
| **Yanlış atıf oranı** | **%0,86** (55/6400) | `DEGERLENDIRME.md` |
| Kapsama ölçüm hatası (MAE) | **0,0241** (5.519 ölçüm, hedef ≤ 0,05) | `DEGERLENDIRME.md` |
| Aday bulma (birleşik, Faz 0) | %99,5 | `FAZ0-SONUCLARI.md` |
| Uçtan uca gecikme | p50 **386 ms** · p95 703 ms | `DEGERLENDIRME.md` |
| Emek Kartı üretimi | 6 ms | `GECIKME.md` |
| Açılış (280 içerik) | 16 ms | `ACILIS-SURESI.md` |

### En zayıf noktalar — saklanmıyor

| Senaryo | Top-1 | Neden |
|---|--:|---|
| kırpma + yazı | %91,1 | Kaynak tuvalin küçük bir bölümünü kaplıyor |
| kırpma %30 | %92,5 | Aynı sebep, daha uç hâli |
| ölçek %25 | %96,4 | 200×150 pikselde yerel özellikler seyrekleşiyor |

Kapsama ölçümünde 0,10 hata payını aşan tek senaryo **ölçek %25** (beklenen 1,00, ölçülen
0,875). **Sapmanın yönü önemli:** kaynağa *eksik* pay veriyor — yani itirazla
düzeltilebilir yönde. Ayrıca 8 doğru bağda geometrik doğrulama hiç yapılamadı; o bağlarda
ihtiyatlı tavan uygulanıyor ve kaynak yeniden ölçüm isteyebiliyor.

---

## 10. Silme hakkı — nasıl çalışıyor

`DELETE /api/contents/{id}` · yetki: **yalnızca içeriğin sahibi** (başkasına 403).

Silmek tek satırlık bir işlem değil; aynı içerikten türemiş izler beş yerde duruyor ve
biri kalırsa silme yarım kalır. Uç hepsini birlikte götürüyor:

| Ne | Nerede |
|---|---|
| Yayınlanan görsel | Diskte |
| Eşleşme maskeleri | Diskte (PNG) |
| Parmak izleri + CLIP vektörü | Veritabanı satırında |
| Bağlar ve o bağlara açılmış itirazlar | Veritabanında |
| Arama indeksi girdileri | Bellekte (FAISS) + diskteki anlık görüntü |

İndeks, silmeden sonra veritabanından yeniden kuruluyor. FAISS "flat" indekslerde tek tek
satır silmek, satır numarası → içerik eşlemesini de kaydırır; yeniden kurmak hem daha
basit hem daha güvenli. Vektörler veritabanında durduğu için bu artık milisaniyeler
sürüyor.

### Kalan sınır: ödemesi olan içerik silinmiyor

Ödeme yapılmış bir içerik silinmek istenirse uç **409** döner:

> *"Bu içeriğe 4 ödeme bağlı. Gerçekleşmiş ödemelerin kaydı silinemez; mali kayıtların
> bütünlüğü korunmalıdır."*

`Payout`, gerçekleşmiş bir ödemenin dondurulmuş kaydı. Gelir dağıtan bir sistemde bunu
silmek denetlenebilirliği yok eder. **Bu, silme hakkının tam karşılanmadığı bir sınır ve
saklanmıyor:** doğru çözüm ödeme kayıtlarının kişisel veriden arındırılıp (anonimleştirme)
içeriğin yine de silinebilmesi. Ürünleşme aşamasının işi.

---

## 11. Yetki haritası

Durum değiştiren **hiçbir uç** oturumsuz çalışmıyor.

| Uç | Yetki |
|---|---|
| `POST /contents` · `/remix` | Oturum (sahip jetondan) |
| `POST /contents/{id}/revenue` | İçeriğin sahibi |
| `DELETE /contents/{id}` | İçeriğin sahibi |
| `POST /contents/{id}/distribute` | İçeriğin sahibi |
| `POST /disputes` | Payın sahibi |
| `POST /disputes/{id}/resolve` | İtirazı açan |
| `GET /disputes/queue` | Oturum |
| `POST /disputes/{id}/moderate` | **Moderatör** |
| `POST /campaigns` | Oturum |
| `POST /campaigns/{id}/distribute` | **Moderatör** |

Açık kalan uçların tamamı **okuma**: akış, içerik, Emek Kartı, maske, kampanya listesi,
sağlık ve `/verify`. Bunlar bilinçli olarak herkese açık — sistemin şeffaflık iddiası
bunu gerektiriyor. `/verify` boyut sınırıyla korunuyor (32 MB, 413).

**Moderatör rolü** (`User.role = "moderator"`) yalnızca iki şeye yetiyor: insana yükselen
itirazı karara bağlamak ve kampanya havuzunu dağıtmak. İkisi de geri alınamaz sonuç
doğuruyor. Demo verisinde **atanmış moderatör yok** — bu doğru davranış; rol açıkça
verilmeli.

**İnceleme kuyruğunun oturumla görülebilir olması bilinçli:** sistemin karar veremediği
yerler gizlenmiyor. Karara bağlamak ayrı bir yetki.

---

## 12. Bilinen açıklar

Dürüstlük için ayrı bölüm. Bunlar bilinmiyor değil, **henüz yapılmadı**.

| Açık | Sonucu | Doğru çözüm |
|---|---|---|
| **Ödemesi olan içerik silinemez** | Silme hakkı bu durumda tam karşılanmıyor (§10) | Ödeme kayıtlarının anonimleştirilmesi |
| **Kullanıcı silme yok** | Yalnızca içerik silinebiliyor | `DELETE /users/{id}` + içeriklerinin toplu işlenmesi |
| **Aydınlatma metni yok** | Kullanıcıya veri işleme bildirimi gösterilmiyor | Ana platformun aydınlatma metnine eklenmesi |
| **Kişi içeren görsel** | Gömme kişisel veri türevi sayılabilir (§3) | Ana platform politikasıyla yönetilmeli |
| **Marka rolü yok** | Kampanyayı herhangi bir kullanıcı oluşturabiliyor | Marka hesabı ve bütçe doğrulaması |

Bunların hiçbiri prototipin gösterdiği iddiayı zayıflatmıyor; hepsi ürünleşme aşamasının
işi ve şimdiden yazıldı ki sonradan "gözden kaçtı" denmesin.

---

## 11. Özet

- Veri **açık lisanslı** ve depoda değil, betikle yeniden üretiliyor
- Kullanıcı kaydında **e-posta bile yok**
- Model **eğitilmiyor**, karar da vermiyor
- Yanlış atıf kaçırılmış atıftan ağır sayılıyor ve bu **altı ayrı eşikte** karşılık buluyor
- Ölçülen yanlış atıf **%0,86**
- Her karar itiraza açık, çözülemeyen itiraz **insana** gidiyor
- Sistemin bilmediği yerler ekranda **"ölçülemedi"** diye yazıyor
- İçerik **silinebiliyor**; silme, diskteki dosyayı ve indeksi de götürüyor
- Durum değiştiren **hiçbir uç** oturumsuz çalışmıyor
- Açıklar bu belgede, gizlenmiyor
