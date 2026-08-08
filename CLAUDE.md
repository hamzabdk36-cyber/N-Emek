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

Plan: `docs/PLAN.md` · Faz 0 ölçümleri: `docs/FAZ0-SONUCLARI.md`

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
cd backend && ../.venv/Scripts/python.exe -m pytest tests/   # 35 test: pay motoru + uçtan uca
.venv/Scripts/python.exe scripts/seed_demo.py --reset        # altın senaryoyu kur ve anlat
.venv/Scripts/python.exe -m uvicorn app.main:app --reload --app-dir backend
```

Faz 0 ölçüm betikleri (her biri sonunda `RISK n KAPANDI/ACIK` basar):

```bash
.venv/Scripts/python.exe backend/poc/poc_c2pa.py        # imzalama + türev zinciri
.venv/Scripts/python.exe backend/poc/poc_similarity.py  # aday bulma, 20 senaryo
.venv/Scripts/python.exe backend/poc/poc_geometry.py    # alan oranı ölçüm hatası
.venv/Scripts/python.exe backend/poc/poc_watermark.py   # filigran dayanıklılığı
```

Testler kendi geçici veritabanını kullanır (`tests/conftest.py`), demo verisini bozmaz.

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
backend/poc/              Faz 0 doğrulama betikleri
scripts/seed_demo.py      altın senaryoyu kurup anlatır (demo provası)
```

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

- **Ölçmeden iddia etme.** Her performans iddiası `backend/poc/` veya `backend/eval/` altında çalıştırılabilir bir betikten gelmeli. `docs/FAZ0-SONUCLARI.md` bu betiklerin çıktısıdır; sayıları elle düzenleme, betiği çalıştır.
- **Yanlış atıf, kaçırılmış atıftan ağırdır.** Eşik ayarlarında bu yönde hata payı bırak. Yanlış pozitifi sıfırlamak için geri getirmeden feragat etmek doğru karar.
- **Dürüst sınırlar yaz.** Bir yöntemin çalışmadığı senaryolar dokümanda açıkça yazılır (örn. filigran kırpmaya dayanmaz). Jüri karşısında güvenilirliği bu sağlar.
- **Türkçe.** Kod içi yorumlar, dokümanlar ve arayüz metinleri Türkçe. Kaynak kodda ASCII kullan (Windows konsol kodlama sorunları için); Markdown dosyalarında tam Türkçe imla.
- Yeni bir türev senaryosu gerekiyorsa `backend/eval/attacks.py` içine ekle — hem PoC hem kapsamlı değerlendirme oradan okuyor.

## Bilinen tuzaklar

- `c2pa.C2paSignerInfo(ta_url=b"")` → `Signature: empty string`. Zaman damgası sunucusu yoksa `None` ver.
- `invisible-watermark` paketi bu ortamda çalışmıyor (kayıpsız çevrimde bile başarısız). Kendi `watermark.py` modülümüz kullanılıyor; pakete geri dönme.
- CLIP modeli ilk çağrıda HuggingFace'ten iniyor (~600 MB), sonrası önbellekten.
