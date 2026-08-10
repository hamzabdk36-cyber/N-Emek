# Yapay Zekâ Mimarisi

Bu belge sistemdeki öğrenilmiş bileşenin **ne olduğunu, nerede durduğunu ve neden orada
durduğunu** anlatır. Genel sistem mimarisi `MIMARI.md`'de.

Buradaki bütün rakamlar ölçüldü: `FAZ0-SONUCLARI.md` (aşama bazlı geri getirme),
`DEGERLENDIRME.md` (6.400 sorgulu tam korpus), `GECIKME.md` (uçtan uca), ve bu belge için
koşulan GPU/CPU karşılaştırması (§9).

---

## 1. Özet — model nerede, nerede değil

Sistemde **öğrenen tek bileşen CLIP ViT-B/32'dir ve o bile karar vermez.**

CLIP'in görevi *aday üretmek*: "şu görsel şuna benziyor". Nihai karar — yani pay
hesabına giren **kullanılan alan oranı** — klasik bilgisayarlı görüden gelir: homografi
kestirimi + RANSAC + ZNCC piksel doğrulaması. Bunlar deterministik, açıklanabilir ve
denetlenebilir.

| Katman | Yöntem | Öğrenilmiş mi | Kararı verir mi |
|---|---|---|---|
| 0 · İçerik kimliği | C2PA manifest doğrulama | Hayır | Evet (kanıt) |
| 1 · Tam eşleşme | SHA-256 | Hayır | Evet (kanıt) |
| 2 · Filigran | DCT katsayı çifti + CRC-16 | Hayır | Evet (kanıt) |
| 3 · Algısal parmak izi | pHash / dHash / wHash / blok | Hayır | Hayır — aday |
| 4 · Görsel benzerlik | **CLIP ViT-B/32** | **Evet** | **Hayır — yalnızca aday** |
| 5 · Alan ölçümü | Homografi + RANSAC + ZNCC | Hayır | **Evet — pay bu sayıdan çıkar** |

> Bu ayrım, projenin jüri karşısındaki en savunulabilir yanı: "yapay zekâ öyle dedi"
> diyen bir sistem değil. Model yanılsa bile geometri aşaması onu eler; geometrinin
> ürettiği sayı ise her kullanıcıya maskesiyle birlikte gösterilir.

---

## 2. Neden CLIP gerekli — ölçümle

Algısal hash'ler ucuz ve kesin, ama **geometrik dönüşümlerde çöküyorlar.** Faz 0'da
320 görsellik korpusta ölçülen Top-5 geri getirme (`poc_similarity.py`):

| Senaryo | pHash | Blok hash | **CLIP** |
|---|--:|--:|--:|
| döndürme 15° | %0 | %0 | **%100** |
| ayna | %0 | %0 | **%100** |
| kırpma %50 | %5 | %5 | **%100** |
| kırpma %30 | %2 | %0 | **%98** |
| kırpma + yazı | %0 | %0 | **%92** |
| meme | %40 | %12 | **%100** |
| döndürme 5° | %78 | %25 | **%100** |

Tersi de doğru: **gri ton** senaryosunda pHash %100, CLIP %92. İki aile birbirini
tamamlıyor; hiçbiri tek başına yeterli değil. Birleşik geri getirme **%99,5**.

CLIP olmasaydı kırpma, döndürme ve ayna senaryolarında zincir hiç kurulamazdı — ve bunlar
sosyal medyada istisna değil, kural.

---

## 3. Model seçimi: neden ViT-B/32

**`ViT-B/32`, `laion2b_s34b_b79k` ön eğitimi, 512 boyut.**

Seçimin mantığı, modelin sistemdeki rolünden çıkıyor: CLIP **aday üretiyor**, karar
vermiyor. Aday listesinin ilk 8'ine girmek yeterli; sıralamayı bir tık iyileştirmek pay
hesabını değiştirmiyor çünkü kararı geometri veriyor.

| Aday model | Boyut | Bellek | Hız | Bu sistemde kazancı |
|---|--:|--:|--:|---|
| **ViT-B/32** (seçilen) | 512 | ~4 GB VRAM'e rahat sığar | 21–27 ms/görsel (CUDA) | Geri getirme zaten %92–100 |
| ViT-L/14 | 768 | ~3× daha ağır | ~4–5× yavaş | Aday sıralaması iyileşir, **karar değişmez** |
| ViT-H/14 | 1024 | GPU zorunlu | çok daha yavaş | Aynı — üstelik CPU'da demo imkânsızlaşır |
| DINOv2 | 768+ | ağır | yavaş | Kendi kendine denetimli; benzer davranış, aynı kısıt |
| Klasik tanımlayıcılar (SIFT/ORB) | — | hafif | hızlı | Zaten **5. aşamada** kullanılıyor |

Belirleyici kısıt: **jüri makinesinde GPU olmayabilir.** Docker imajı bilerek CPU
PyTorch ile kuruluyor ve tek komutla çalışması hızdan önemli. ViT-B/32, CPU'da da
kabul edilebilir bir bütçede kalan en büyük model (§9).

Model adı ve ön eğitim `NEMEK_CLIP_MODEL` / `NEMEK_CLIP_PRETRAINED` ile değiştirilebilir;
kod hiçbir yerde 512 boyutu varsaymaz (`EMBEDDING_DIM` tek kaynak).

---

## 4. Neden eğitim yok, yalnızca çıkarım var

Bu bilinçli bir karar ve üç gerekçesi var.

**1. Asıl iddia öğrenilebilir bir şey değil.** Sistemin ürettiği kritik sayı "türevde
kaynağın kapladığı alan oranı". Bu bir *ölçüm*: homografi kestirip pikselleri
doğruluyoruz. Bir model eğitmek bu sayıyı tahmine çevirirdi — yani projenin tam olarak
karşı çıktığı şeye.

**2. Etiketli veri yok.** "Bu türevde kaynağın %41'i var" diye etiketlenmiş bir veri
kümesi mevcut değil; üretmek için zaten geometrik ölçüme ihtiyaç var. Kendi ölçümümüzle
etiketleyip onu öğretmek, ölçümün hatasını modele kopyalamaktan başka bir şey yapmazdı.

**3. Denetlenebilirlik.** Eğitilmiş bir bileşen, veri kümesi yanlılığı ve model kayması
riski getirir. İtiraz eden bir kullanıcıya "modelimiz böyle öğrendi" demek, bu projenin
vaadiyle çelişir. Bugün her sayının arkasında ya bir imza, ya bir hash, ya da tekrar
üretilebilir bir geometrik ölçüm var.

**Sonuç:** ön eğitimli CLIP donuk (`model.eval()`, `torch.no_grad()`) kullanılıyor.
İnce ayar yok, kalibrasyon katmanı yok. Ağırlıklar adlandırılmış bir kontrol noktasından
(`laion2b_s34b_b79k`) geliyor, yani ölçümler yeniden üretilebilir.

---

## 5. Ölçümün yönlendirdiği tasarım: çok bölgeli sorgu

İlk kurulum (yalnızca tam görsel üzerinden pHash + CLIP) **%88,5** geri getirme verdi ve
üç senaryoda çöktü: meme %25, kolaj %42, kırpma+yazı %8.

Ortak sebep modelin zayıflığı değil, **sorunun kurulumu**: kaynak, türev tuvalinin
yalnızca bir bölümünü kaplıyor; global bir gömme tüm tuvali görüyor ve kaynağı
seyreltiyor.

Çözüm sorgu tarafında: görsel sabit bir bölge kümesine ayrılıp her bölge ayrı aranıyor —
tam, merkez, dört çeyrek, dört yarım, düz çerçevesi kırpılmış hâli (**11 bölge**).

- Ortalama geri getirme **%88,5 → %99,2**
- İndeks tarafı **değişmedi** — depolanan hâlâ içerik başına tek vektör
- Maliyet yalnızca sorgu anında ve **tek bir GPU yığınına** sığıyor

Bu, "daha büyük model" yerine "daha iyi sorgu" tercihinin ölçülmüş karşılığı.

---

## 6. Benzerlikten güvene: tavan neden 0,75

CLIP kosinüs benzerliği doğrudan güven olarak kullanılmıyor:

```
benzerlik < 0,75          -> güven 0,00  (aday bile sayılmaz)
0,75 ≤ benzerlik ≤ 1,00   -> güven 0,30 + (benzerlik − 0,75) × 1,8, tavan 0,75
```

**Tavan bilinçli.** CLIP "aynı sahne" ile "aynı içerik" ayrımını yapamaz: aynı kafede
çekilmiş iki farklı fotoğraf da yüksek benzerlik verir. Yalnızca benzerlikten gelen bir
bağ hiçbir zaman "yüksek güven" bandına çıkamaz; oraya çıkmanın tek yolu geometrik
doğrulamadan geçmektir.

İkinci emniyet supabı: geometrik doğrulama **başarısız olursa** güven **× 0,40** ile
cezalandırılır ve genelde eşiğin altına düşer.

Bu iki kural, "yanlış atıf kaçırılmış atıftan ağırdır" ilkesinin koddaki karşılığı.

---

## 7. Karar füzyonu: gürültülü-VEYA

Birden fazla aşama aynı kaynağı bulduğunda güvenler şöyle birleşir:

```
güven = 1 − Π (1 − güvenᵢ)
```

Gerekçe: her aşama kaynağı **bağımsız bir fiziksel izden** buluyor — metadata, bayt
özeti, frekans alanı, piksel istatistiği, yerel geometri. Aynı sonuca farklı yollardan
varmaları güveni artırmalı. Toplamsal bir model bunu ifade edemez, üstelik 1,0'ı aşabilir.

---

## 8. Gecikme bütçesi

Ölçülen (`GECIKME.md`, yerel CUDA), kimliksiz içerik yükleme — yani **tam kurtarma hattı**:

| Aşama | Süre | Payı |
|---|--:|---|
| c2pa | 0,7 ms | ihmal edilebilir |
| fingerprint | 10,5 ms | ucuz |
| watermark | 17,5 ms | ucuz |
| **embed (CLIP, çok bölgeli)** | **62,7 ms** | model burada |
| phash_search | 72,7 ms | FAISS Hamming |
| clip_search | 0,6 ms | FAISS kosinüs — neredeyse bedava |
| **geometry** | **116,5 ms** | **en pahalı adım** |

Uçtan uca: özgün yükleme 666 ms · remix 569 ms · kimliksiz 476 ms. Tam korpus
değerlendirmesinde p50 **386 ms**, p95 703 ms.

İki gözlem:

1. **Model, maliyetin en büyük parçası değil.** Geometri daha pahalı — ve o bir model
   değil, klasik CV.
2. **Arama neredeyse bedava.** `clip_search` 0,6 ms: FAISS kosinüs araması indeks
   büyüdükçe ölçeklenecek yer, ama bugün darboğaz değil.

Emek Kartı üretimi **6 ms** — yani açıklanabilirlik katmanı pratikte bedava.

---

## 9. GPU/CPU davranışı — ölçüldü

Bu belge için koşuldu: aynı 16 görsel, aynı model, iki ortam.

| Ortam | Tekil görsel | 16'lık yığın | Yığında görsel başına |
|---|--:|--:|--:|
| Yerel, **CUDA** | 27,0 ms | 341 ms | **21,3 ms** |
| Docker, **CPU** | 182,9 ms | 1.408 ms | **88,0 ms** |

**CPU, GPU'dan 4,1× (yığın) – 6,8× (tekil) yavaş.** Sistem çalışmaya devam ediyor; tek
yükleme CPU'da da saniyenin altında kalıyor.

Tasarım kararları buradan çıktı:

- **Docker imajı CPU PyTorch ile kuruluyor.** Jüri makinesinde NVIDIA sürücüsü ve
  `nvidia-container-toolkit` olmayabilir; tek komutla kurulumun çalışması hızdan önemli.
  GPU isteyenler için gerekli blok `docker-compose.yml` içinde yorum olarak duruyor.
- **Yığınlama önemli.** CPU'da yığın, görsel başına maliyeti 183 ms'den 88 ms'ye
  indiriyor. Sistemde iki yerde 32'lik yığın kullanılıyor: çok bölgeli sorgunun 11
  bölgesi (`recovery`) ve açılışta indeksin kurulması (`registry`).
- **CUDA'da `float16` autocast** açık; CPU'da kapalı (kazancı yok, risk var).
- **Cihaz seçimi tek yerde:** `embedding.pick_device()`. `NEMEK_FORCE_CPU=1` ile
  zorlanabiliyor — CI bunu kullanıyor ki test ortamı sessizce değişmesin.

---

## 10. Model yaşam döngüsü

| Konu | Karar |
|---|---|
| Sürüm sabitleme | `open_clip_torch==3.3.0`, kontrol noktası `laion2b_s34b_b79k` — adlandırılmış ve sabit |
| İndirme | İlk çağrıda HuggingFace'ten (~600 MB), sonrası önbellekten |
| Önbellek | Docker'da ayrı birim (`nemek-model-cache`); CI'da `actions/cache` |
| Yükleme | `lru_cache(maxsize=1)` — süreç başına bir kez |
| Model değişirse | Saklanan vektörler **geçersiz olur.** `clip_vector` sütunu ve FAISS anlık görüntüsü yeniden üretilmeli |

> **Bilinen açık:** vektörlerin hangi modelle üretildiği veritabanında **yazmıyor**.
> Bugün tek model var ve sabit, ama model değiştirilirse eski vektörler sessizce yanlış
> sonuç üretir. Doğru çözüm `contents` tablosuna bir model sürümü sütunu eklemek ve
> açılışta uyuşmayanları yeniden hesaplamak. Kayıt altına alındı, henüz yapılmadı.

---

## 11. Sınırlar — dürüst hâli

| Sınır | Sonucu | Neden kabul edilebilir |
|---|---|---|
| CLIP "aynı sahne"yi "aynı içerik" sanabilir | Yanlış aday | Tavan 0,75 + geometri elemesi; ölçülen yanlış atıf **%0,86** |
| Kırpma %30'un altında geri getirme düşüyor | %92,5 Top-1 | Kaynağın kalanı zaten çok az; pay da küçük olurdu |
| Filigran döndürme ve kırpmaya dayanmıyor | O senaryolarda kesin kanıt yok | 3–5. aşamalar tam bu durum için var, %92–100 başarılı |
| Sentetik olarak yeniden çizilmiş içerik | Ölçülemez | Piksel düzeyinde ortak bölge kalmıyor — dürüstçe "ölçülemedi" denir |
| CPU'da 4–7× yavaş | Demo yavaşlar | Tek yükleme yine saniyenin altında |
| Model sürümü kayıtlı değil | Model değişirse sessiz hata | §10'da açıkça yazıldı |

Ölçülemeyen durumda sistem tahmin üretmiyor: kapsama `None` kalıyor, ihtiyatlı tavan
(%35) uygulanıyor ve ekranda **"ölçülemedi"** yazıyor.

---

## 12. Neden bu mimari denetlenebilir

- Öğrenen tek bileşen donuk ve adlandırılmış bir kontrol noktasından geliyor
- O bileşen karar vermiyor, aday üretiyor
- Kararı veren ölçüm deterministik ve tekrar üretilebilir
- Her bağın altında hangi aşamanın ne bulduğu kanıt satırı olarak duruyor
- Kullanıcı itiraz edebiliyor; itiraz daha hassas bir dedektörle **yeniden ölçüm**
  tetikliyor, modele yeniden sormuyor
- Ölçüm betikleri depoda: `poc_*.py` ve `eval/run_*.py`; dokümanlardaki sayılar elle
  yazılmıyor, betik çıktısı
