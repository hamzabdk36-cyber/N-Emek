# N-Emek Rehberi

Sistemin nasıl çalıştığı ve nasıl kullanıldığı. Kurulum için
[`BASLARKEN.md`](../BASLARKEN.md), mimari diyagramlar için
[`MIMARI.md`](MIMARI.md), tasarım gerekçeleri için [`CLAUDE.md`](../CLAUDE.md).

---

## 1. Bu sistem ne yapıyor

Bir fotoğraf paylaşılır. Biri onu kırpar, üstüne yazı ekler, kendi gönderisi olarak
paylaşır. Bir başkası onun ekran görüntüsünü alır, tekrar kırpar, tekrar paylaşır.
Üçüncü paylaşımda dosyanın içinde ilk üreticiye dair **hiçbir iz kalmaz** — metadata
silinmiş, içerik kimliği yok olmuştur. Gelir varsa son paylaşana gider.

N-Emek bu zinciri kanıtlarıyla geri kurar ve geliri ölçüme dayalı paylaştırır.

> **Ayırt edici iddia:** kaynağı *bulmak* değil, kullanılan içerik oranını **ölçmek**.
> Katkı payı tahmine değil, homografi ve piksel doğrulamasıyla ölçülmüş alan oranına
> dayanır.

Sistem asla "bu içeriğin sahibi budur" demez. Kanıtlı bir zincir **önerisi** sunar;
her öneri itiraza açıktır ve çözülmezse insan incelemesine düşer.

---

## 2. Bir içerik yüklendiğinde ne oluyor

Yükleme anında beş şey birden yapılır. Hepsi birkaç yüz milisaniye sürer.

| Adım | Ne yapılır | Ne işe yarar |
|---|---|---|
| Parmak izi | SHA-256 + pHash / dHash / wHash + 3×3 blok hash | Birebir kopya ve hafif düzenleme tespiti |
| Görünmez filigran | DCT katsayı çiftlerine 40 bit kimlik + CRC-16 | Yeniden sıkıştırma ve metadata silmeye dayanır |
| Görsel gömme | CLIP ViT-B/32 vektörü | Ağır düzenleme, filtre, kolaj |
| İçerik kimliği | C2PA manifesti imzalanır, türevse kaynak `ingredient` olarak yazılır | Zincir dosyanın içinde seyahat eder |
| İndeksleme | FAISS'e eklenir (Hamming + kosinüs) | Sonraki sorgular bu içeriği bulabilir |

Yayınlanan dosya, yüklenen dosya değildir: filigran gömülmüş ve manifest imzalanmış
sürümdür. Kullanıcılar bu sürümü görür ve indirir.

---

## 3. Kaynağı nasıl buluyor — beş aşamalı hat

Yüklenen dosyada içerik kimliği yoksa köken kurtarma hattı çalışır. Aşamalar
sırayla denenir, her biri kendi kanıtını üretir.

| Aşama | Yöntem | Neye dayanıklı |
|---|---|---|
| 0 | C2PA manifest doğrulama | (manifest varsa) |
| 1 | SHA-256 tam eşleşme | Bit-birebir kopya |
| 2 | Filigran çıkarma | Yeniden sıkıştırma, hafif kırpma, metadata silme |
| 3 | Algısal hash — FAISS Hamming, eşik 12 | Ölçekleme, JPEG, renk/parlaklık |
| 4 | CLIP gömme — FAISS kosinüs, çok bölgeli sorgu | Ağır düzenleme, filtre, kolaj, meme |
| 5 | ORB/SIFT + RANSAC homografi + ZNCC piksel doğrulaması | **Kullanılan alanı ölçer** |

Aşama 4'ün "çok bölgeli sorgu" kısmı önemli: görselin tamamı yerine 11 farklı
bölgesi ayrı ayrı sorgulanır. Bir kolajın köşesindeki küçük bir alıntı, tüm görselin
gömmesinde kaybolur ama kendi bölgesinde net bulunur.

Aşama 5 sadece doğrulama değil **ölçüm** yapar — bir sonraki bölümün konusu.

### Aşamalar nasıl birleşiyor

Skorlar gürültülü-VEYA ile birleşir: `güven = 1 − Π(1 − güven_i)`. Yani bağımsız
kanıtlar birbirini güçlendirir; iki ayrı aşamanın orta güvenli bulgusu, tek
aşamanın yüksek güvenli bulgusundan daha güçlü olabilir.

İki koruma var:

- **Yalnızca benzerlik varsa güven 0,80'i geçemez.** Geometrik doğrulama olmadan
  "bu görsel şuna benziyor" ifadesi kesinlik iddia edemez.
- **Ölçülemeyen bağ cezalandırılır** (×0,40) ve payı ihtiyatlı bir varsayımla
  hesaplanır. Kaynak yeniden ölçüm isteyebilir.

---

## 4. Asıl iş: bulmak değil, ölçmek

Kaynağın bulunması yetmez. "Ayşe'nin fotoğrafı bu gönderide var" ile "Ayşe'nin
fotoğrafı bu gönderinin %86'sını kaplıyor" arasındaki fark, adil paylaşımın
tamamıdır.

Ölçüm şöyle çalışır:

1. ORB (ya da itiraz üzerine SIFT) ile iki görsel arasında yerel özellik eşleşmeleri
   bulunur, Lowe oran testinden geçirilir.
2. RANSAC ile homografi matrisi kestirilir — yani kaynağın türev içinde hangi
   dönüşümle yer aldığı.
3. Kaynağın dört köşesi bu matrisle türevin düzlemine yansıtılır; oluşan dörtgenin
   türev karesiyle kesişimi **kullanılan alanı** verir.
4. Bu alan piksel piksel doğrulanır (yerel ZNCC). Homografi geometrik olarak doğru
   olsa bile üzerine yazı bandı çizilmiş ya da boyanmış pikseller **kaynaktan
   gelmiyor** sayılır ve alandan düşülür.

Emek Kartı'ndaki maskeli karşılaştırma tam olarak bunu gösterir: kaynaktan geldiği
ölçümle doğrulanan alan parlak kalır, gelmeyen yerler griye düşer. Remixçinin
eklediği yazı bandının kararmış olması bu yüzdendir — o pikseller paya girmez.

Ayna çevrilmiş kaynaklar için model iki yönde de denenir; ORB ayna değişimine
dayanıklı değildir ve sahte bir homografi üretebildiği için seçim iç nokta oranına
bakılarak yapılır.

---

## 5. Pay nasıl hesaplanıyor

Her kaynak için ham ağırlık:

```
ağırlık = kapsama^a × güven^b × sönümleme^(derinlik − 1)
```

- **kapsama** — ölçülen alan oranı (yukarıdaki bölüm)
- **güven** — füzyondan çıkan skor
- **sönümleme** — zincirde her adım geriye gidildiğinde uygulanan katsayı

### Özel kapsama: aynı pikseli iki kez ödüllendirmemek

Zincirde Ayşe → Burak → Ceyda varsa, Ayşe'nin pikselleri Ceyda'nın içeriğine
Burak üzerinden ulaşmıştır. Ham kapsamalar iç içe geçmiştir: Burak'ın %97'si
Ayşe'nin %86'sını da içerir. İkisini toplamak aynı emeği iki kez ödüllendirir.

Bu yüzden her düğüme yalnızca **kendi kattığı** pikseller yazılır:

```
özel(A) = toplam(A) − toplam(A'nın zincirdeki doğrudan kaynakları)
```

Özel kapsamalar görselin tam bir bölütlemesidir ve doğal olarak 1,0'a toplanır.
Pay normalizasyona değil ölçüme dayanır.

Aynı sebeple, geometri aşaması Ayşe'yi Ceyda'nın içeriğinde doğrudan da bulur ve
bir Ayşe → Ceyda bağı üretir. Bu bağ **geçişli indirgemeyle** hesaptan düşülür —
gerçek türetme tarihi Ayşe → Burak → Ceyda'dır ve iki bağ aynı pikselleri temsil
eder. Bağ veritabanında kanıt olarak kalır, zincir grafiğinde çizilmez.

### Kampanya kuralları

Bunlar hesabın üstüne uygulanır: platform komisyonu, kaynak tabanı (kaynaklara
giden asgari toplam), üretici tavanı, asgari ödeme eşiği. Uygulanan her kural
Emek Kartı'nda satır satır yazılır.

---

## 6. İtiraz

Payına itiraz eden kaynak, bağın yeniden ölçülmesini ister. Bağ bu kez SIFT ile
ölçülür (daha yavaş, daha hassas). Sonuç değişirse paylar güncellenir ve dağıtım
tekrarlanır. Değişmezse itiraz moderasyon kuyruğuna düşer ve insan incelemesine
kalır.

Bu, sistemin "asla sahiplik kararı vermez" taahhüdünün pratikteki karşılığıdır.

---

## 7. Ekran ekran kullanım

### Akış

Platformdaki gönderiler. Her kart, içeriğin özgün mü türev mi olduğunu ve kaç
türev ürettiğini söyler. **İçerik yükle** ile kendi görselinizi ekleyebilirsiniz;
yükleme anında köken hattı çalışır ve bulunan kaynaklar hemen bildirilir.

Yükleme sırasında iki tercih içerik kimliğine yazılır ve içerikle birlikte seyahat
eder: remix izni ve asgari kaynak payı talebi.

### Emek Kartı (içerik detayı)

Sistemin kapak ekranı. Tek sayfada şu soruya cevap verir: *"Bu içerik kazandı.
Neden bana bu kadar geldi?"*

Yukarıdan aşağı:

1. **Köken** — kimliğin nasıl belirlendiği. Yüklenen dosyada kimlik var mıydı,
   yayınlanan sürüm imzalandı mı, filigran kimliği, kaç bağ bulundu.
2. **Pay dağılımı** — şerit ve satırlar. Her satır tıklanabilir; açıldığında
   kapsama, güven, sönümleme ve ham ağırlık değerleri ile pay formülünün o
   satır için yazılmış hâli görünür.
3. **Ölçülen bölge** — kaynak ve türev yan yana, maskeli karşılaştırma. Projenin
   temel iddiasının görsel kanıtı.
4. **Bu bağın kanıtları** — hangi aşamanın ne dediği, ham ölçüm değerleriyle.
5. **Atıf zinciri** — DAG görünümü. Ok yönü türetme yönüdür, her bağda ölçülen
   kapsama yazar. Kesikli çizgi henüz onaylanmamış bağı, kesikli çerçeveli düğüm
   ise zincirde yer alan ama payı ödeme eşiğinin altında kalan ara halkayı gösterir.

**Gelir** kutusundan tutarı değiştirip dağılımın nasıl değiştiğini
görebilirsiniz — demo için konulmuştur.

Kendi payınıza itiraz etmek için ilgili satırı açın; **İtiraz et** oradadır.
İtiraz butonu yalnızca o payın sahibi olarak görüntülerken çıkar (sağ üstteki
kullanıcı seçicisi).

### Remix Stüdyo

Bir gönderide **Remixle** deyince açılır. Kırpma, yazı ekleme, serbest çizim ve
filtre var. Yayınladığınızda zincir anında kurulur ve kendi türeviniz için Emek
Kartı açılır.

Kırpmayı fareyle ya da klavyeyle yapabilirsiniz; klavye için Sol / Üst / Genişlik /
Yükseklik alanları vardır.

### Kaynak bul

Elinizdeki herhangi bir görseli sisteme **kaydetmeden** köken hattından geçirir.
Test etmenin en hızlı yolu: akıştaki bir görselin ekran görüntüsünü alıp buraya
bırakın.

### Kampanyalar

Marka ödül havuzu tanımlar; komisyon, kaynak tabanı ve üretici tavanı buradan
belirlenir. Kampanya sonunda dağıtım simülasyonu çalıştırılabilir.

### İnceleme kuyruğu

Otomatik çözülemeyen itirazlar burada birikir ve insan kararı bekler.

---

## 8. Ölçülmüş sonuçlar

Bu projede hiçbir performans iddiası dokümandan gelmez; her biri çalıştırılabilir
bir betiğin çıktısıdır ve yeniden koşturulabilir.

| Metrik | Sonuç |
|---|---|
| Ortalama Top-1 doğruluk | %98,7 |
| Ortalama Top-5 doğruluk | %98,7 |
| Yanlış atıf oranı | %0,86 (55 / 6400) |
| Kapsama ölçüm hatası (MAE) | 0,0241 — hedef ≤ 0,05 |
| Uçtan uca gecikme | p50 386 ms · p95 703 ms |

280 indekslenmiş içerik × 20 türev senaryosu, artı indekse hiç alınmamış 40
holdout içeriğiyle **negatif kontrol**: bu sorgularda önerilen *herhangi bir* bağ
yanlış atıf sayılır. Bu projede yanlış atıf, kaçırılmış atıftan daha ağır bir
hatadır.

Ayrıntı: [`DEGERLENDIRME.md`](DEGERLENDIRME.md) · [`GECIKME.md`](GECIKME.md) ·
[`FAZ0-SONUCLARI.md`](FAZ0-SONUCLARI.md)

---

## 9. Sınırlar

Dürüstlük, jüri karşısındaki güvenilirliğin temeli; çalışmayan yerler de yazılı.

- **Filigran kırpmaya ve döndürmeye dayanmaz** — blok hizası bozulur. Bu bir
  eksiklik değil iş bölümü: hattın 3–5. aşamaları tam olarak bu durumlar için var.
- **Sistem sahiplik kararı vermez.** Kanıtlı bir zincir önerisi sunar.
- **Geometrik doğrulama yapılamayan bağlarda kapsama ölçülemez**; pay ihtiyatlı
  bir varsayımla hesaplanır ve bu durum Emek Kartı'nda açıkça yazar.
- Prototip **tek makinede, SQLite ve kaba kuvvet FAISS** ile çalışır. Ölçekleme
  yolu [`MIMARI.md`](MIMARI.md) bölüm 6'da.

---

## 10. Takılırsan

| Belirti | Sebep |
|---|---|
| Arayüz açılıyor ama veri gelmiyor | Backend çalışmıyor; uvicorn terminaline bak |
| İlk yükleme çok uzun sürdü | CLIP modeli iniyor (~600 MB), bir kereye mahsus |
| `port already in use` | 8000 veya 5173 dolu; eski terminali kapat |
| Demo verisi karıştı | `python scripts/seed_demo.py --reset` her şeyi baştan kurar |
| İtiraz butonu görünmüyor | Sağ üstten o payın sahibi kullanıcıya geç |
| Python tarafındaki değişiklik yansımıyor | uvicorn'u `--reload` ile başlat |

Sağlaması:

```bash
cd backend && ../.venv/Scripts/python.exe -m pytest tests/
```

125 test: <!-- sayim: backend --> 22 pay motorunun değişmez kuralları, 13 uçtan uca altın
senaryo, 65 API sözleşmesi, 12 indeks kalıcılığı, 7 Emek Kartı maliyeti, 6 dağıtım
idempotentliği.
