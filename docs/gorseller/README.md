# Ekran Görüntüleri

Teknik rapor ve sunum için. **10 Ağustos 2026**, `docker compose up --build` ile ayağa
kalkan yığından, demo verisiyle (altın senaryo) çekildi. Görüntü 1568×745, JPEG.

Bu klasördeki her görüntü **çalışan sistemden** alındı; hiçbiri maket veya çizim değil.
Yeniden üretmek için: `docker compose up --build` → `http://localhost:5173`.

| Dosya | Ekran | Ne gösteriyor |
|---|---|---|
| `01-akis.jpg` | Akış | Üç gönderi, kökeni tek satır düz metinle: "2 kaynaktan türedi", "özgün içerik · 2 türev üretildi" |
| `02-emek-karti-koken.jpg` | Emek Kartı — üst | Köken anlatısı ve pay dağılımının başı. "Yüklenen dosyada kimlik: yoktu / Yayınlanan sürüm: imzalandı" — kimliğin silinip yeniden kurulduğu durum |
| `03-pay-gerekcesi.jpg` | Emek Kartı — pay satırı açık | **Raporun ana görseli.** Kapsama %85,2 · güven 0,95 · sönümleme 0,85 · ham ağırlık 0,692 ve bunları birleştiren formül satırı; altında kanıtlar ve "Bu paya itiraz et" |
| `04-olculen-bolge.jpg` | Ölçülen bölge | Kaynak ve türev yan yana; türevde **yeşil alan** ölçümle o kaynaktan geldiği doğrulanan bölge |
| `05-olculen-bolge-oran.jpg` | Ölçülen bölge — oran | Aynı karşılaştırma, "ölçülen kullanılan alan: %12,2" ve kanıt satırlarıyla |
| `06-atif-zinciri.jpg` | Atıf zinciri | Üç halkalı DAG, kenarlarda ölçülmüş kapsama rozetleri (%87, %97). Seçili düğüm mavi çerçeveli |
| `07-remix-studyosu.jpg` | Remix Stüdyosu | Tuval ve dört araç (kırp, yazı, çizim, filtre); her işlem bir C2PA eylemine karşılık geliyor |
| `08-kampanya-paneli.jpg` | Kampanyalar | Marka kampanyası: ödül havuzu ₺50.000,00, kaynak tabanı %15, komisyon %10 |
| `09-inceleme-kuyrugu.jpg` | İnceleme kuyruğu | Boş durum — aşağıdaki nota bakın |
| `10-kaynak-bul.jpg` | Kaynak bul | Platforma kaydetmeden köken sorgulama |

## İki not — dürüstlük için

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

## Eksik: mobil görünüm

Mobil ekran görüntüsü bu turda alınamadı — tarayıcı otomasyonu pencereyi yeniden
boyutlandıramadı (`window.innerWidth` 1536'da sabit kaldı), dolayısıyla duyarlı yerleşim
tetiklenmedi. CSS ile dar bir görünüm taklit etmek yerine boş bırakıldı: raporda gerçek
olmayan bir ekran göstermek doğru olmazdı.

Elle almak için: Chrome'da `http://localhost:5173` → **F12** → **Ctrl+Shift+M** (cihaz
kipi) → iPhone/Pixel seç → ekran görüntüsü. Mobil yerleşim `docs/ERISILEBILIRLIK.md`
kapsamında zaten değerlendirildi ve çalışıyor; eksik olan yalnızca görüntüsü.
