# Ekran Görüntüleri

Teknik rapor ve sunum için. **11 Ağustos 2026**, `docker compose up --build` ile ayağa
kalkan yığından, demo verisiyle (altın senaryo) çekildi. Masaüstü kareleri 1568×745,
mobil kare 390×844, hepsi JPEG.

Bu klasördeki her görüntü **çalışan sistemden** alındı; hiçbiri maket veya çizim değil.

## Yeniden üretmek

```bash
docker compose up --build -d
.venv/Scripts/python.exe scripts/ekran_goruntuleri.py            # on bir kare
.venv/Scripts/python.exe scripts/rapor_takvim.py                 # 12-takvim.png
.venv/Scripts/python.exe scripts/ekran_goruntuleri.py --sadece 03,11
```

Önkoşul: `pip install playwright` (Playwright kendi Chromium'unu indiremezse betik
sistemdeki Chrome'a düşüyor).

Kareler 10 Ağustos'ta elle çekilmişti. 11 Ağustos'ta arayüzün yazı tipi değişti — Inter
pakete gömüldü, öncesinde her ekran Segoe UI ile render ediliyordu — ve **onunun da**
eskidiği anlaşıldı. Elle çekim her tasarım değişikliğinde aynı işi tekrarlamayı
gerektiriyor; kimse tekrarlamayınca rapordaki görseller sessizce üründen ayrışıyor.
Betik o döngüyü kapatıyor ve iki şeyi kendisi doğruluyor: Inter yüklenmemişse **durur**
(kare eski yazı tipiyle çıkacaktı), mobil karede yatay kayma varsa **durur**.

## Kareler

| Dosya | Ekran | Ne gösteriyor |
|---|---|---|
| `01-akis.jpg` | Akış | Üç gönderi, kökeni tek satır düz metinle: "2 kaynaktan türedi", "özgün içerik · 2 türev üretildi" |
| `02-emek-karti-koken.jpg` | Emek Kartı — üst | Köken anlatısı ve pay dağılımının başı. "Yüklenen dosyada kimlik: yoktu / Yayınlanan sürüm: imzalandı" — kimliğin silinip yeniden kurulduğu durum |
| `03-pay-gerekcesi.jpg` | Emek Kartı — pay satırı açık | **Raporun ana görseli.** Kapsama %85,2 · güven 0,95 · sönümleme 0,85 · ham ağırlık 0,692 ve bunları birleştiren formül satırı: `pay = kapsama × güven × sönümleme`. Altında kanıt satırları |
| `04-olculen-bolge.jpg` | Ölçülen bölge | Kaynak ve türev yan yana; türevde **yeşil alan** ölçümle o kaynaktan geldiği doğrulanan bölge |
| `05-olculen-bolge-oran.jpg` | Ölçülen bölge — oran | Aynı karşılaştırma, "ölçülen kullanılan alan: %12,2" ve kanıt satırlarıyla. Geometri satırı sayıyı açıkça yazıyor: 620 noktada eşleşme, oran %97,5 |
| `06-atif-zinciri.jpg` | Atıf zinciri | Üç halkalı DAG, kenarlarda ölçülmüş kapsama rozetleri (%87, %97). Seçili düğüm altın çerçeveli |
| `07-remix-studyosu.jpg` | Remix Stüdyosu | Tuval ve dört araç (kırp, yazı, çizim, filtre); her işlem bir C2PA eylemine karşılık geliyor |
| `08-kampanya-paneli.jpg` | Kampanyalar | Marka kampanyası: ödül havuzu ₺50.000,00, kaynak tabanı %15, komisyon %10 |
| `09-inceleme-kuyrugu.jpg` | İnceleme kuyruğu | Boş durum — aşağıdaki nota bakın |
| `10-kaynak-bul.jpg` | Kaynak bul | **Gerçek bir sorgunun sonucu.** Burak'ın remixinin kırpılmış kopyası soruluyor: içerik kimliği yok, birebir eşleşme yok, filigran okunamıyor — sonra algısal parmak izi, görsel benzerlik ve geometrik doğrulama sırayla buluyor. Aşamaların süreleri ve "bulunan kaynaklar (3)" ekranda |
| `11-mobil.jpg` | Mobil — Emek Kartı | 390×844'te aynı ekran: iki satırlık üst çubuk, pay dağılımı, açık gerekçe ve formül satırı. Yatay kayma yok |
| `12-takvim.png` | — | Ekran görüntüsü değil: iş paketleri ve zaman çizelgesi. `scripts/rapor_takvim.py` üretiyor, kaynağı oradaki `PAKETLER` listesi |

## Üç not — dürüstlük için

**İnceleme kuyruğu neden boş.** Demo verisinde bir itiraz var ama otomatik çözülmüş
(`RESOLVED_REJECTED`): bağ SIFT ile yeniden ölçülmüş, sonuç değişmemiş, itiraz
reddedilmiş. Kuyruk yalnızca **insana yükseltilmiş** itirazları gösteriyor, yani boş
olması sistemin çalıştığı anlamına geliyor. Ekrandaki metin de bunu söylüyor: "Ölçüm yine
sonuç vermezse karar insana bırakılır — sistem karar veremediği yeri gizlemez." Dolu bir
kuyruk göstermek için itirazın kararsız kalması gerekirdi; demo verisine sahte bir itiraz
eklemek yerine gerçek durum çekildi.

**Maske neden Burak'ın satırında.** Maskeli karşılaştırma yalnızca **doğrudan** ölçülen
bağlarda var. Ayşe zincirde iki adım geride ve onun yaprakla doğrudan bağı geçişli
indirgemeyle düşürülmüş (aynı pikseller Burak üzerinden zaten sayılıyor), dolayısıyla o
satırda maske yok. `04` ve `05` bu yüzden Burak seçiliyken çekildi.

**Kadraj neyi kesiyor.** `03`, formül satırını merkeze alacak şekilde kadrajlandı;
"Bu paya itiraz et" düğmesi hemen altında ama kadrajın dışında kalıyor. İtiraz akışının
kendisi `docs/KULLANICI-AKISLARI.md` §2 sahne 5'te ve `DEMO-SENARYOSU.md`'de anlatılıyor.

## Mobil kare hakkında

Mobil görüntü 10 Ağustos'ta alınamamıştı: tarayıcı otomasyonu pencereyi yeniden
boyutlandıramıyordu (`window.innerWidth` sabit kalıyordu) ve CSS ile dar bir görünüm
taklit etmek yerine boş bırakılmıştı — raporda gerçek olmayan bir ekran göstermek doğru
olmazdı.

O turda ayrıca şöyle bir cümle yazılmıştı: *"Mobil yerleşim `ERISILEBILIRLIK.md`
kapsamında zaten değerlendirildi ve çalışıyor; eksik olan yalnızca görüntüsü."* **Bu
doğru değildi.** O belge mobil düzeni "Yapılmayanlar" altında tutuyordu, ve 11 Ağustos'ta
390 pikselde ilk kez ölçüldüğünde üst çubuğun ekranın beşte birini yediği görüldü
(163 piksel, yapışkan). Düzeltildi — çubuk şimdi 109 piksel — ve ölçümün tamamı
`ERISILEBILIRLIK.md` 11 numaralı bulguda.

Kare artık gerçek: Playwright'ın görüntü alanı pencereden bağımsız kurulduğu için ölçü
390×844'te tutuyor.
