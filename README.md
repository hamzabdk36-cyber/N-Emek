# N-Emek

[![CI](https://github.com/hamzabdk36-cyber/N-Emek/actions/workflows/ci.yml/badge.svg)](https://github.com/hamzabdk36-cyber/N-Emek/actions/workflows/ci.yml)

**Açıklanabilir içerik atıf ve adil gelir paylaşım sistemi.**
TEKNOFEST 2026 NSosyal İnovasyon Yarışması — İçerik Ekonomisi kategorisi.

Bir içerik kırpıldığında, üstüne yazı eklendiğinde veya remixlendiğinde ilk üreticinin
emeği görünmez oluyor ve gelir adil paylaşılamıyor. N-Emek, içerik zincirini görünür kılan,
**açıklanabilir ve itiraz edilebilir** bir atıf ve gelir paylaşım katmanıdır.

> **Ayırt edici iddia:** kaynağı *bulmak* değil, kullanılan içerik oranını **ölçmek**.
> Katkı payı tahmine değil, homografi + piksel doğrulamasıyla ölçülmüş alan oranına dayanıyor.

| Ölçüm | Sonuç | Kaynak |
|---|---|---|
| Kaynak bulma (20 türev senaryosu) | Top-1 ve Top-5 doğruluk | [`docs/DEGERLENDIRME.md`](docs/DEGERLENDIRME.md) |
| Kullanılan alan oranı hatası | MAE ≤ 0,05 hedefi | [`docs/DEGERLENDIRME.md`](docs/DEGERLENDIRME.md) |
| Uçtan uca gecikme | adım adım | [`docs/GECIKME.md`](docs/GECIKME.md) |
| Açılış süresi (280 içerik) | 11,5 sn → 16 ms | [`docs/ACILIS-SURESI.md`](docs/ACILIS-SURESI.md) |
| Faz 0 risk kapatma | dört teknik varsayım | [`docs/FAZ0-SONUCLARI.md`](docs/FAZ0-SONUCLARI.md) |

Sistemin nasıl çalıştığı ve ekran ekran kullanımı: [`docs/REHBER.md`](docs/REHBER.md)
Kullanıcı gözünden yolculuk ve akış diyagramları: [`docs/KULLANICI-AKISLARI.md`](docs/KULLANICI-AKISLARI.md)
İş ve gelir modeli: [`docs/IS-MODELI.md`](docs/IS-MODELI.md)
Mimari ve diyagramlar: [`docs/MIMARI.md`](docs/MIMARI.md)
Ekran görüntüleri: [`docs/gorseller/`](docs/gorseller/)

---

## Kurulum

İki yol var. Docker daha az adım, yerel kurulum daha hızlı çalışır (GPU kullanır).

### Docker ile — tek komut

```bash
docker compose up --build
```

Tarayıcıda **http://localhost:5173**. Sertifikalar, test görselleri ve demo verisi
kapsayıcı içinde otomatik üretilir; ikinci açılışta hepsi hazır gelir.

İlk açılış ~10–15 dakika: bağımlılıklar kurulur ve yapay zekâ modeli iner (~600 MB).
Sonraki açılışlar saniyeler sürer. Sıfırlamak için `docker compose down -v`.

PyTorch bilerek CPU sürümü: jüri makinesinde NVIDIA sürücüsü olmayabilir ve tek komutla
çalışması hızdan önemli. Backend imajı 2,7 GB, arayüz 93 MB. GPU isteyenler için gerekli
blok `docker-compose.yml` içinde yorum olarak duruyor.

Doğrulandı: `docker compose up --build` ile kurulum baştan çalıştırıldı — sertifikalar
üretildi, korpus indi, altın senaryo kuruldu, arayüz nginx üzerinden backend'e bağlandı ve
Emek Kartı doğru tutarlarla göründü.

### Yerel kurulum — üç adım

Gereksinimler: **Python 3.13**, **Node 24**, ~3 GB disk. GPU zorunlu değil; yoksa kod
CPU'ya düşer (yavaşlar ama çalışır).

### 1. Bağımlılıklar

```bash
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r backend/requirements.txt
# GPU varsa (CUDA 12.6):
.venv/Scripts/python.exe -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cu126
# GPU yoksa:
.venv/Scripts/python.exe -m pip install torch torchvision

cd frontend && npm install && cd ..
```

Linux/macOS'ta `.venv/Scripts/python.exe` yerine `.venv/bin/python`.

### 2. Sertifikalar, görseller, demo verisi

```bash
.venv/Scripts/python.exe scripts/gen_dev_certs.py      # C2PA imzalama sertifikaları
.venv/Scripts/python.exe scripts/fetch_eval_images.py  # 320 görsellik test korpusu (~120 MB)
.venv/Scripts/python.exe scripts/seed_demo.py --reset  # altın senaryoyu kurar ve anlatır
```

Sertifikalar ve korpus depoda değil; ikisi de bu komutlarla yeniden üretilir. CLIP modeli
ilk çağrıda HuggingFace'ten iniyor (~600 MB), sonrası önbellekten.

### 3. Çalıştır

İki terminal:

```bash
.venv/Scripts/python.exe -m uvicorn app.main:app --reload --app-dir backend   # :8000
cd frontend && npm run dev                                                    # :5173
```

Tarayıcıda **http://localhost:5173**. Vite `/api` isteklerini 8000'e vekilliyor.

---

## Demoda ne görülüyor

`seed_demo.py` altın senaryoyu kurar; arayüzde şu sırayla gezilir:

1. **Akış** — Ayşe'nin özgün fotoğrafı, Burak'ın remixi, Ceyda'nın ekran görüntüsü.
2. **Ceyda'nın içeriği → Emek Kartı.** Dosyada içerik kimliği yoktu; sistem Burak'ı **ve**
   onun üzerinden Ayşe'yi buldu. Her aşamanın ne dediği kanıt satırlarında yazıyor.
3. **Eşleşen bölge maskesi** — kaynaktan geldiği ölçümle doğrulanan piksel alanı parlak
   kalır, geri kalanı griye düşer. Burak'ın eklediği yazı bandı ve çizim kararmış görünür:
   o pikseller Ayşe'den gelmiyor.
4. **Zincir grafiği** — Ayşe → Burak → Ceyda, her bağda güven ve ölçülen kapsama.
5. **Pay dağılımı** — her rakamın altında gerekçesi: kullanılan alan oranı, güven,
   zincir sönümlemesi, kampanya taban/tavan kuralları.
6. **İtiraz** — Ayşe payına itiraz eder, bağ SIFT ile yeniden ölçülür, paylar güncellenir.
   Çözülmezse moderasyon kuyruğuna düşer.

**Remix Stüdyo**'da (kırpma, yazı, çizim, filtre) kendi türevinizi üretip yükleyebilirsiniz;
zincir anında kurulur. **Doğrula** sayfası, elinizdeki herhangi bir görseli sisteme
kaydetmeden hattan geçirir.

---

## Doğrulama

```bash
cd backend && ../.venv/Scripts/python.exe -m pytest tests/
```

71 test, üç katman:

- **22** — pay motorunun değişmez kuralları (paylar 1,0'a toplanır, derin kaynak daha az
  alır, taban/tavan ihlal edilmez)
- **13** — uçtan uca altın senaryo (servis katmanı)
- **36** — API uç noktalarının sözleşmesi: her ucun döndürdüğü alanlar, durum kodları ve
  hatalı girdiye verdiği tepki

Üçüncüsü olmadan `schemas.py`'de bir alan adı değişse ilk 35 test yeşil kalıyor ama arayüz
sessizce kırılıyordu. Testler kendi geçici veritabanını kullanır, demo verisini bozmaz.

### Ölçüm betikleri

Bu projede hiçbir performans iddiası dokümandan gelmez; her biri çalıştırılabilir bir
betiğin çıktısıdır.

```bash
# Faz 0 — dört teknik riskin kapatılması (her biri RISK n KAPANDI/ACIK basar)
.venv/Scripts/python.exe backend/poc/poc_c2pa.py        # imzalama + türev zinciri
.venv/Scripts/python.exe backend/poc/poc_similarity.py  # aday bulma, 20 senaryo
.venv/Scripts/python.exe backend/poc/poc_geometry.py    # alan oranı ölçüm hatası
.venv/Scripts/python.exe backend/poc/poc_watermark.py   # filigran dayanıklılığı

# Faz 2 — kapsamlı değerlendirme (backend/ dizininden)
../.venv/Scripts/python.exe -m eval.run_benchmark              # ~2 saat, tam korpus
../.venv/Scripts/python.exe -m eval.run_benchmark --corpus 20  # hızlı deneme
../.venv/Scripts/python.exe -m eval.run_latency                # adım adım gecikme
```

`run_benchmark.py`, korpusun bir kısmını indekse hiç almaz (negatif kontrol): bu
görsellerin türevlerinde önerilen *herhangi bir* bağ yanlış atıf sayılır. Bu projede
yanlış atıf, kaçırılmış atıftan daha ağır bir hatadır.

---

## Yapı

```
backend/app/provenance/   köken kurtarma hattı — projenin kalbi
  fingerprint.py          SHA-256 + pHash/dHash/wHash + 3x3 blok hash
  watermark.py            kanonik ölçekli DCT katsayı-çifti filigranı (kendi uygulamamız)
  embedding.py            CLIP ViT-B/32
  index.py                FAISS: IndexBinaryFlat (Hamming) + IndexFlatIP (kosinüs)
  geometry.py             ORB/SIFT + RANSAC + ZNCC piksel doğrulaması → kullanılan alan
  regions.py              çok bölgeli sorgu (kolaj/meme/kırpma+yazı için şart)
  recovery.py             5 aşamanın orkestrasyonu + gürültülü-VEYA karar füzyonu
  c2pa_service.py         manifest imzalama/okuma, org.nemek.remix_policy
backend/app/attribution/  zincir yürüyüşü, geçişli indirgeme, pay formülü, Emek Kartı
backend/app/services/     ingest · payout · dispute · registry
backend/app/api/          FastAPI uçları ve şemalar
backend/eval/             türev senaryoları + kapsamlı değerlendirme + gecikme ölçümü
backend/poc/              Faz 0 doğrulama betikleri
frontend/src/pages/       Feed · ContentDetail · RemixStudio · Verify · Campaigns · Moderation
scripts/                  sertifika üretimi · korpus indirme · demo tohumlama
```

Ayrıntı ve tasarım gerekçeleri: [`CLAUDE.md`](CLAUDE.md) ve [`docs/MIMARI.md`](docs/MIMARI.md).

---

## Bilinen sınırlar

Dürüstlük, jüri karşısındaki güvenilirliğin temeli; bu yüzden çalışmayan yerler de yazılı.

- **Filigran kırpmaya ve döndürmeye dayanmaz** — blok hizası bozuluyor. Bu bir eksiklik
  değil iş bölümü: hattın 3–5. aşamaları tam olarak bu durumlar için var.
- **Sistem asla "sahibi budur" demez.** Kanıtlı bir zincir *önerisi* sunar; kullanıcı
  itiraz edebilir, çözülmezse insan incelemesine düşer.
- **Geometrik doğrulama yapılamayan bağlarda** kapsama ölçülemez; pay hesabı ihtiyatlı bir
  varsayımla (`unverified_coverage`) çalışır ve kaynak yeniden ölçüm isteyebilir.
- Prototip **tek makinede, SQLite ve kaba kuvvet FAISS** ile çalışır. Ölçekleme yolu
  `docs/MIMARI.md` bölüm 6'da.
