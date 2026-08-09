# Başlarken

N-Emek'i kendi bilgisayarında çalıştırmak için kısa yol. Ayrıntı gerekirse
[`README.md`](README.md), tasarım kararları için [`CLAUDE.md`](CLAUDE.md).

**Bu ne?** Sosyal medyada bir görsel kırpılıp, üstüne yazı eklenip, ekran görüntüsü
alınarak paylaşıldığında ilk üreticinin emeği kayboluyor. N-Emek içeriğin kaynak
zincirini kanıtlarıyla geri kuruyor ve geliri ölçüme dayalı olarak paylaştırıyor.

---

## Gerekenler

- **Python 3.13** ve **Node 24**
- ~5 GB boş disk (çoğu PyTorch ve yapay zekâ modeli)
- Ekran kartı şart değil; yoksa kod işlemciye düşer, sadece yavaşlar

## Kurulum — dört adım

Komutları projenin ana klasöründe çalıştır.

**1. Python ortamı**

```bash
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r backend/requirements.txt
```

Sonra PyTorch. NVIDIA ekran kartın varsa:

```bash
.venv/Scripts/python.exe -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cu126
```

Yoksa sadece:

```bash
.venv/Scripts/python.exe -m pip install torch torchvision
```

**2. Arayüz paketleri**

```bash
cd frontend
npm install
cd ..
```

**3. Sertifika, görsel, demo verisi**

```bash
.venv/Scripts/python.exe scripts/gen_dev_certs.py
.venv/Scripts/python.exe scripts/fetch_eval_images.py 20
.venv/Scripts/python.exe scripts/seed_demo.py --reset
```

Ortadaki komut test görselleri indirir. Sadece bakmak için **20** yeterli; ölçüm
betiklerini de koşacaksan sayıyı yazma, 320 iner (~100 MB).

Son komut demo senaryosunu kurar ve terminale adım adım anlatır — Ayşe fotoğrafını
yükler, Burak remixler, Ceyda ekran görüntüsü alır, sistem kaynağı bulur, gelir
paylaştırılır, Ayşe itiraz eder. Bu çıktıyı okumaya değer.

> İlk çalıştırmada yapay zekâ modeli internetten iniyor (~600 MB), bir kez.

**4. Çalıştır** — iki ayrı terminal gerekiyor.

```bash
.venv/Scripts/python.exe -m uvicorn app.main:app --reload --app-dir backend
```

```bash
cd frontend
npm run dev
```

Tarayıcıda **http://localhost:5173**

Windows kullanmıyorsan `.venv/Scripts/python.exe` yerine `.venv/bin/python`.

---

## Neye bakmalı

Sırayla gez, hikâye böyle kuruluyor:

**1. Akış.** Üç gönderi var: Ayşe'nin özgün fotoğrafı, Burak'ın remixi, Ceyda'nın
ekran görüntüsü. Kartlardaki "2 kaynak" gibi rozetler sistemin bulduğu bağlar.

**2. Ceyda'nın gönderisinde "Emek Kartı".** Asıl ekran burası. Ceyda dosyayı ekran
görüntüsü olarak yüklediği için içerik kimliği tamamen silinmişti; sistem yine de
Burak'ı **ve** onun üzerinden Ayşe'yi buldu. Sayfanın başındaki "Köken" kutusu bunu
söylüyor.

**3. Aynı sayfada eşleşen bölge maskesi.** Kaynak ve türev yan yana. Türevin
üzerinde, ölçümle o kaynaktan geldiği doğrulanan alan parlak kalır; gelmeyen yerler
griye düşer. Burak'ın eklediği yazı bandının ve çizdiği dairenin kararmış olduğuna
dikkat et — o pikseller Ayşe'den gelmiyor ve paya da girmiyor. Projenin temel iddiası
bu: kaynağı bulmak değil, **ne kadar kullanıldığını ölçmek**.

**4. Pay dağılımı.** Her rakamın altında gerekçesi yazıyor: ölçülen alan oranı, güven,
zincirde kaçıncı adım, kampanya kuralları. Kanıt satırlarına tıklarsan ham ölçümler
açılır.

**5. Atıf zinciri.** Ayşe → Burak → Ceyda, her bağda ölçülen oran.

**6. Remix Stüdyo.** Bir gönderide "Remixle" de: kırp, yazı ekle, çiz, filtre uygula,
yayınla. Zincir anında kurulur, kendi türevin için Emek Kartı açılır.

**7. Kaynak bul.** Elindeki herhangi bir görseli sisteme kaydetmeden hattan geçirir.
Yukarıdaki görsellerden birinin ekran görüntüsünü alıp burada dene.

---

## Takılırsan

| Belirti | Sebep |
|---|---|
| Arayüz açılıyor ama veri gelmiyor | Backend çalışmıyor; birinci terminale bak |
| İlk yükleme çok uzun sürdü | Yapay zekâ modeli iniyor, bir kereye mahsus |
| `port already in use` | 8000 veya 5173 dolu; eski terminali kapat |
| Demo verisi karıştı | `scripts/seed_demo.py --reset` her şeyi baştan kurar |
| Python tarafında değişiklik yansımıyor | uvicorn'u `--reload` ile başlattığından emin ol |

## Sağlamasını yapmak istersen

```bash
cd backend
../.venv/Scripts/python.exe -m pytest tests/
```

71 test. Ayrıca `docs/` altında ölçüm sonuçları var: `DEGERLENDIRME.md` (6.400
sorguluk değerlendirme), `GECIKME.md` (süreler), `MIMARI.md` (diyagramlar).
Bu dosyalardaki hiçbir sayı elle yazılmadı; hepsi `backend/eval/` ve `backend/poc/`
altındaki betiklerin çıktısı ve yeniden koşturulabilir.
