# N-Emek

Açıklanabilir içerik atıf ve adil gelir paylaşım sistemi. TEKNOFEST 2026 NSosyal İnovasyon Yarışması, **İçerik Ekonomisi** kategorisi.

> Bu proje, aynı takımın elektronik harp çalışmasından (`Desktop/Zenith`) **tamamen bağımsızdır**. İki proje karıştırılmaz; buradaki kararlar, dokümanlar ve kod o projeye referans vermez.

## Neyi çözüyoruz

Bir içerik kırpıldığında, üstüne yazı eklendiğinde veya remixlendiğinde ilk üreticinin emeği görünmez oluyor ve gelir adil paylaşılamıyor. N-Emek, içerik zincirini görünür kılan, **açıklanabilir ve itiraz edilebilir** bir atıf ve gelir paylaşım katmanı.

Ayırt edici iddia: kaynağı *bulmak* değil, kullanılan içerik oranını **ölçmek**. Katkı payı tahmine değil, homografi + piksel doğrulamasıyla ölçülmüş alan oranına dayanıyor.

## Takvim (sert tarihler)

| Tarih | Aşama |
|---|---|
| **24 Ağu 2026, 17:00 TSİ** | Teknik Rapor teslimi (KYS) — şablona uymayan veya geç rapor doğrudan eleme |
| 2 Eyl 2026 | Teknik rapor sonuçları |
| 2–7 Eyl 2026 | Mentörlük |
| **14 Eyl 2026, 17:00 TSİ** | Final sunumu + çalışan prototip teslimi |
| 30 Eyl – 4 Eki 2026 | TEKNOFEST Şanlıurfa |

Puan ağırlıkları: Yenilikçilik %20 · Teknik Yeterlilik %20 · Problem Çözme %20 · **UI/UX %20** · Sunum ve Prototip Kalitesi %10 · İş Modeli %10. Arayüz, AI motoruyla eşit ağırlıkta — "geliştirici demosu" görünümü puanın beşte birini götürür.

Plan: `docs/PLAN.md` · Mimari ve diyagramlar: `docs/MIMARI.md` · Rapor içeriği: `docs/RAPOR-ICERIK.md`
Ölçümler: `docs/FAZ0-SONUCLARI.md` (risk kapatma) · `docs/DEGERLENDIRME.md` (tam korpus) · `docs/GECIKME.md` (uçtan uca)

## Kurulum

```bash
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r backend/requirements.txt
.venv/Scripts/python.exe -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cu126
.venv/Scripts/python.exe scripts/gen_dev_certs.py      # C2PA imzalama sertifikaları
.venv/Scripts/python.exe scripts/fetch_eval_images.py  # 320 görsellik test korpusu
```

Sertifikalar ve korpus depoda değil; her ikisi de yukarıdaki komutlarla yeniden üretilir.

## Doğrulama

```bash
cd backend && ../.venv/Scripts/python.exe -m pytest tests/   # 71 test: pay motoru + uçtan uca + API
.venv/Scripts/python.exe scripts/seed_demo.py --reset        # altın senaryoyu kur ve anlat

# Uygulamayı çalıştır (iki terminal)
.venv/Scripts/python.exe -m uvicorn app.main:app --reload --app-dir backend  # :8000
cd frontend && npm run dev                                                   # :5173
```

Vite `/api` isteklerini 8000'e vekilliyor; arayüz kodunda mutlak URL yok. **Backend'i `--reload` olmadan başlattıysanız, Python tarafında yaptığınız değişiklik sunucuya yansımaz** — tarayıcıda eski metinleri görürseniz önce bunu kontrol edin.

Faz 0 ölçüm betikleri (her biri sonunda `RISK n KAPANDI/ACIK` basar):

```bash
.venv/Scripts/python.exe backend/poc/poc_c2pa.py        # imzalama + türev zinciri
.venv/Scripts/python.exe backend/poc/poc_similarity.py  # aday bulma, 20 senaryo
.venv/Scripts/python.exe backend/poc/poc_geometry.py    # alan oranı ölçüm hatası
.venv/Scripts/python.exe backend/poc/poc_watermark.py   # filigran dayanıklılığı
```

Faz 2 kapsamlı ölçümler (`backend/` dizininden, çıktıyı doğrudan `docs/` altına yazarlar):

```bash
../.venv/Scripts/python.exe -m eval.run_benchmark              # ~2 sa; docs/DEGERLENDIRME.md
../.venv/Scripts/python.exe -m eval.run_benchmark --corpus 20  # hızlı deneme
../.venv/Scripts/python.exe -m eval.run_latency                # docs/GECIKME.md
```

PoC'lerden farkı: `run_benchmark` aşamaları tek tek değil **üretimdeki `recovery.recover()`
fonksiyonunun kendisini** çağırır ve korpusun bir kısmını indekse hiç almaz (negatif
kontrol) — o görsellerde önerilen *herhangi bir* bağ yanlış atıftır. Koşu uzun; her
senaryo bitiminde ara sonuç `data/eval/sonuclar.json`'a yazılır, ilerleme oradan izlenir.
`run_latency` kendi geçici veritabanını kullanır, demo verisine dokunmaz.

Testler kendi geçici veritabanını kullanır (`tests/conftest.py`), demo verisini bozmaz.

Üç katman ayrı ayrı ölçülüyor ve biri diğerinin yerine geçmez: `test_contribution.py`
pay formülünün değişmez kurallarını, `test_e2e_altin_senaryo.py` servis katmanını,
`test_api_ucnoktalari.py` ise HTTP sözleşmesini sınar. Sonuncusu olmadan `schemas.py`'de
bir alan adı değişse diğer 35 test yeşil kalıyor ama arayüz sessizce kırılıyordu — bu
mutasyonla doğrulandı. Ağır iki test `slow` işaretli: `-m "not slow"` ile atlanabilir.

## Mimari

```
backend/app/provenance/   köken kurtarma hattı — projenin kalbi
  fingerprint.py          SHA-256 + pHash/dHash/wHash + 3x3 blok hash
  watermark.py            kanonik ölçekli DCT katsayı-çifti filigranı (kendi uygulamamız)
  embedding.py            CLIP ViT-B/32, CUDA
  index.py                FAISS: IndexBinaryFlat (Hamming) + IndexFlatIP (kosinüs)
  geometry.py             ORB/SIFT + RANSAC + ZNCC piksel doğrulaması → kullanılan alan
  regions.py              çok bölgeli sorgu (kolaj/meme/kırpma+yazı için şart)
  recovery.py             5 aşamanın orkestrasyonu + noisy-OR karar füzyonu
  c2pa_service.py         manifest imzalama/okuma, org.nemek.remix_policy
backend/app/attribution/
  chain.py                zincir yürüyüşü, geçişli indirgeme, özel kapsama bölüntüsü
  contribution.py         pay formülü (saf fonksiyon, DB'den bağımsız)
  explain.py              Emek Kartı verisi
backend/app/services/     ingest (yükleme/remix), payout, dispute, registry (indeks)
backend/app/api/          FastAPI uçları ve şemalar
backend/eval/attacks.py   20 türev senaryosu — tüm ölçümlerin tek kaynağı
backend/eval/run_benchmark.py  kapsamlı değerlendirme (üretim hattı + negatif kontrol)
backend/eval/run_latency.py    altın senaryonun adım adım gecikmesi
backend/poc/              Faz 0 doğrulama betikleri
scripts/seed_demo.py      altın senaryoyu kurup anlatır (demo provası)

frontend/src/
  theme.css               koyu tema belirteçleri; renk disiplini burada tanımlı
  api.ts                  tipli istemci — backend/app/api/schemas.py ile birebir
  components/ui.tsx       Panel, Badge, ConfidenceBadge, ShareBar, Stat, Button
  components/Pipeline.tsx StageTimeline (5 aşama) + EvidenceList (kanıt satırları)
  components/ImageCompare.tsx  kaynak/türev + maskeli vurgu (canvas ile birleştirme)
  components/ChainGraph.tsx    SVG DAG, katmanlı yerleşim
  pages/                  Feed, ContentDetail (Emek Kartı), RemixStudio,
                          Verify, Campaigns, Moderation
```

### Arayüz renk disiplini

Altın = para ve pay · yeşil = doğrulanmış / yüksek güven · turuncu = orta güven · kırmızı = düşük güven ve itiraz · mavi = zincir ve bağlantı. Bu eşleme her ekranda aynı; kullanıcı bir rengi bir kez öğrenince her yerde okuyabiliyor. Yeni bir renk eklemeden önce mevcut beşinden biri işe yarar mı diye bak.

`ImageCompare` maskeyi CSS `mask-image` ile değil canvas üzerinde birleştirir: `mask-mode: luminance` tarayıcı desteği tutarsız ve bu ekran demonun en kritik görüntüsü. Ayrım renkle değil **kontrastla** kurulur — eşleşen bölge parlak kalır, eşleşmeyen griye düşer; kapsama %90'ı aştığında yoğun bir yeşil katman görüntüyü yutuyordu.

### Pay hesabının iki kritik kuralı

Bunlar sonradan "sadeleştirme" diye kaldırılmamalı; ikisi de ölçümdeki gerçek bir hatayı düzeltiyor.

**Geçişli indirgeme** (`chain._redundant_edges`): geometri, Ayşe'nin içeriğini Ceyda'nın gönderisinde de bulur — pikselleri oraya Burak üzerinden gelmiştir. Bu doğrudan bağ pay hesabına girerse aynı emek iki kez ödüllendirilir. P'den C'ye uzunluğu ≥2 bir yol varsa doğrudan P→C bağı hesaptan düşülür (veritabanında kanıt olarak kalır).

**Özel (exclusive) kapsama** (`chain.build_chain`): ölçülen kapsamalar iç içedir — Burak'ın %97'si Ayşe'nin %84'ünü de kapsar. Her düğüme yalnızca kendi kattığı pikseller yazılır: `özel(A) = toplam(A) − Σ toplam(A'nın zincirdeki doğrudan kaynakları)`. Böylece kapsamalar görselin tam bir bölüntüsü olur ve doğal olarak 1.0'a toplanır; pay normalizasyona değil ölçüme dayanır.

Bu düzeltmeden önce kaynakların toplamı %182 çıkıyor ve tabana çarpıyordu.

### Köken kurtarma hattı

Sıralı aşamalar, her biri kanıt üretir:

| Aşama | Yöntem | Güven |
|---|---|---|
| 0 | C2PA manifest doğrulama | 0.99 |
| 1 | SHA-256 tam eşleşme | 0.99 |
| 2 | Filigran çıkarma (CRC-16 doğrulamalı) | 0.90 |
| 3 | pHash / blok hash (Hamming ≤ 12) | 0.45–0.80 |
| 4 | CLIP kosinüs, çok bölgeli | 0.30–0.75 |
| 5 | Homografi + ZNCC → **kullanılan alan ölçümü** | 0.60–0.95 |

Sistem asla "sahibi budur" demez; kanıtlı **zincir önerisi** sunar. Kullanıcı itiraz edebilir.

## Çalışma kuralları

- **Ölçmeden iddia etme.** Her performans iddiası `backend/poc/` veya `backend/eval/` altında çalıştırılabilir bir betikten gelmeli. `docs/FAZ0-SONUCLARI.md`, `docs/DEGERLENDIRME.md` ve `docs/GECIKME.md` bu betiklerin çıktısıdır; sayıları elle düzenleme, betiği çalıştır.
- **Yanlış atıf, kaçırılmış atıftan ağırdır.** Eşik ayarlarında bu yönde hata payı bırak. Yanlış pozitifi sıfırlamak için geri getirmeden feragat etmek doğru karar.
- **Dürüst sınırlar yaz.** Bir yöntemin çalışmadığı senaryolar dokümanda açıkça yazılır (örn. filigran kırpmaya dayanmaz). Jüri karşısında güvenilirliği bu sağlar.
- **Türkçe imla, kullanıcıya görünen her yerde tam.** Arayüz metinleri, API'nin döndürdüğü `aciklama` / kural günlüğü / itiraz özeti gibi tüm kullanıcıya görünen dizgeler diakritikli ve doğru imlayla yazılır — jüri bunları okuyacak. Sayı biçimi Türkçe: ondalık ayracı virgül (`%82,0`), yüzde işareti sayıdan önce ve bitişik. Apostrofla ek almaktan kaçın (`%99,9'unun` yerine "oranı %99,9 olarak ölçüldü").
  Kod içi **yorumlar** ASCII kalır (mevcut dosyalarla tutarlılık için). `print()` kullanan betikler `sys.stdout.reconfigure(encoding="utf-8")` çağırır; Windows konsolu varsayılan cp1254 ile Türkçe çıktıyı bozuyor.
- Yeni bir türev senaryosu gerekiyorsa `backend/eval/attacks.py` içine ekle — hem PoC hem kapsamlı değerlendirme oradan okuyor.

## Arayüz revizyonu — yapıldı (10 Ağu 2026)

Takımın iki geri bildirimi de karşılandı; `a8fe341` ve `3b774a3`.

**1. Zincir grafiğinde rakamların çizgi altında kalması.** Sebep kenarların
*içinde* değil arasındaydı: grafik ham kenar tablosunu çiziyordu, yani pay
hesabının geçişli indirgemeyle düştüğü Ayşe→Ceyda bağı da çiziliyordu. Üç düğüm de
tek sütunda olduğu için o kenar da aynı x'te dikey bir çizgiydi ve en son
çizildiğinden diğer rozetlerin tam ortasından geçiyordu. Grafik artık
`chain.reduced_subgraph`'ten besleniyor ve çizim üç katmana ayrıldı (bağlar →
düğümler → rozetler), böylece hiçbir çizgi bir rozetin üstüne düşemiyor. Rozet
metne göre genişliyor ve pay eşiğinin altında kalan ara halkalar artık grafikten
düşmüyor (`contributes: false`).

**2. "AI belli ediyor".** Şablon kalıpları ayıklandı: kartlarda tekrar eden CTA
butonu, rozet yığını, sayfaların kendini anlatan alt başlıkları, mükerrer brüt
gelir, BÜYÜK HARF panel başlıkları, üst çubuktaki `cuda`, ve kullanıcı vurgu
renklerinin tema anlam renkleriyle (altın=para, yeşil=doğrulanmış, mavi=zincir)
çakışması.

**Yedek:** `arayuz-v1` etiketi ve masaüstünde `N-Emek-arayuz-yedek-20260810.zip`.
Geri dönmek için: `git checkout arayuz-v1 -- frontend/src`

**Açık kalan:** Akışta `image.jpeg` başlıklı bir artık test yüklemesi duruyor
(başlığı dosya adı, geliri sıfır, remix kapalı). Jüri demosundan önce silinmeli.

## Bilinen tuzaklar

- **Korpusta yinelenen görsel, değerlendirmeyi sessizce bozar.** picsum farklı tohumları aynı fotoğrafa eşleyebiliyor; ilk korpusta 320 dosyanın yalnızca 276'sı benzersizdi. İndekste birebir ikizi olan bir holdout görseli için bağ bulmak *doğru* davranıştır ama negatif kontrol sayacı bunu yanlış atıf yazar — ölçüm %32,5 yanlış atıf bildirdi, gerçek değil. `fetch_eval_images.py` artık tekilliği garanti ediyor, `run_benchmark.dedupe()` da ayrıca kontrol ediyor. Korpusu elle genişletirsen bu iki kapıyı atlama.
- `c2pa.C2paSignerInfo(ta_url=b"")` → `Signature: empty string`. Zaman damgası sunucusu yoksa `None` ver.
- `invisible-watermark` paketi bu ortamda çalışmıyor (kayıpsız çevrimde bile başarısız). Kendi `watermark.py` modülümüz kullanılıyor; pakete geri dönme.
- CLIP modeli ilk çağrıda HuggingFace'ten iniyor (~600 MB), sonrası önbellekten.
