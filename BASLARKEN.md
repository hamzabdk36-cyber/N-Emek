# Başlarken

N-Emek'i kendi bilgisayarında çalıştırmak için kısa yol. Sistemin nasıl işlediğini
ve her ekranın ne işe yaradığını anlatan tam rehber:
[`docs/REHBER.md`](docs/REHBER.md). Ayrıntı gerekirse [`README.md`](README.md),
tasarım kararları için [`CLAUDE.md`](CLAUDE.md).

**Bu ne?** Sosyal medyada bir görsel kırpılıp, üstüne yazı eklenip, ekran görüntüsü
alınarak paylaşıldığında ilk üreticinin emeği kayboluyor. N-Emek içeriğin kaynak
zincirini kanıtlarıyla geri kuruyor ve geliri ölçüme dayalı olarak paylaştırıyor.

---

## 0. Projeyi indir

Depo **özel**; indirmek için depoya davet edilmiş olmak gerekiyor. Erişimin yoksa
depo sahibinden iste — GitHub'da **Settings → Collaborators → Add people** ile
kullanıcı adını ekliyor, sana e‑posta ile davet geliyor.

**Git ile** (önerilen — sonradan `git pull` ile güncelleyebilirsin):

```bash
git clone https://github.com/hamzabdk36-cyber/N-Emek.git
cd N-Emek
```

İlk kez klonluyorsan GitHub kullanıcı adı ve **parola yerine bir kişisel erişim
jetonu** (Settings → Developer settings → Personal access tokens) soracak.

**Git yoksa:** GitHub'da depo sayfasında yeşil **Code** düğmesi → **Download ZIP**.
Açtığın klasörün adı `N-Emek-master` olur; aşağıdaki komutları o klasörün içinde
çalıştır. Bu yol da erişim ister; davet edilmemişsen sayfa 404 döner.

Bundan sonraki bütün komutlar projenin ana klasöründen çalıştırılıyor.

---

## En kısa yol: Docker

Bilgisayarında Docker varsa tek komut yeter:

```bash
docker compose up --build
```

Sonra **http://localhost:5173**. Aşağıdaki elle kurulum adımlarının hepsi kapsayıcı
içinde otomatik yapılır — sertifikalar, test görselleri, demo verisi.

**İlk açılış 10–15 dakika sürer.** Bu sürede sırasıyla: Python ve Node bağımlılıkları
kurulur, CLIP modeli HuggingFace'ten iner (~600 MB), 24 görsellik test korpusu iner
(~10 MB) ve demo senaryosu kurulur. Sonraki açılışlar saniyeler sürer; indirilen her şey
Docker birimlerinde (`nemek-data`, `nemek-certs`, `nemek-model-cache`) kalıcı.

Uzun süren ilk açılışı arka planda izlemek istersen:

```bash
docker compose up --build -d          # arka planda başlat
docker compose logs -f backend        # ne yaptığını izle (Ctrl+C çıkar, durdurmaz)
```

Açıldı mı, kesin cevap:

```bash
curl http://localhost:8000/api/health
# {"status":"ok","indexed_contents":3,"device":"cpu","c2pa_signing":true}
```

Durdurmak ve sıfırlamak iki ayrı şey:

| Komut | Ne yapar |
|---|---|
| `docker compose down` | Kapsayıcıları durdurur. Veri, model ve sertifikalar **kalır**; sonraki açılış hızlı. |
| `docker compose down -v` | Birimleri de siler. Her şey sıfırlanır; sonraki açılış yine 10–15 dakika. |

Birkaç ayar:

- **Ekran kartı.** İmaj bilerek CPU sürümü PyTorch kuruyor; her makinede tek komutla
  çalışması hızdan önemliydi. NVIDIA sürücüsü ve `nvidia-container-toolkit` varsa
  `docker-compose.yml` sonundaki yorum bloğu GPU'ya nasıl geçileceğini anlatıyor.
- **Korpus boyutu.** `docker-compose.yml` içindeki `NEMEK_CORPUS_COUNT` varsayılan
  **24**. Ölçüm betiklerini de koşacaksan **320** yaz (~120 MB).
- **Diğer ayarlar.** [`.env.example`](.env.example) bütün `NEMEK_` değişkenlerini
  açıklamalarıyla listeliyor.

Docker yoksa aşağıdaki elle kurulum da çalışıyor.

---

## Gerekenler

- **Python 3.13** ve **Node 24**
- ~5 GB boş disk (çoğu PyTorch ve yapay zekâ modeli)
- Ekran kartı şart değil; yoksa kod işlemciye düşer, sadece yavaşlar

## Kurulum — dört adım

Komutları projenin ana klasöründe çalıştır (yukarıdaki **0. adımda** indirdiğin klasör).
Ayarları değiştirmek istersen `cp .env.example .env` — hepsinin bir varsayılanı var,
hiçbiri zorunlu değil.

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

**8. Kim ne yapabilir.** Sağ üstteki kullanıcı seçici sadece görüntüyü değiştirmiyor,
oturum açıyor: geliri yalnızca içeriğin sahibi değiştirip dağıtabilir, bir paya yalnızca
o payın sahibi itiraz edebilir. Demo verisinde **Ceyda moderatör** (adının yanında rozeti
var) — kampanya havuzunu dağıtmak ve insan incelemesine düşen itirazı karara bağlamak
onun yetkisinde. Ayşe'yken "Havuzu dağıt" düğmesine basarsan **403** görürsün; bu bir
hata değil, kuralın işlediğinin kanıtı.

**9. Silme — "unutulma hakkı".** Kendi içeriğinde sol sütunda "İçeriği sil" var. Demo
verisindeki içeriklere ödeme yapıldığı için silme **409** ile reddedilir ve sebebi
yazılır: gerçekleşmiş bir ödemenin kaydı, gelir dağıtan bir sistemde silinemez. Sınırı
gizlemek yerine söylüyoruz.

---

## Takılırsan

| Belirti | Sebep |
|---|---|
| Arayüz açılıyor ama veri gelmiyor | Backend çalışmıyor; birinci terminale bak |
| İlk yükleme çok uzun sürdü | Yapay zekâ modeli iniyor, bir kereye mahsus |
| `port already in use` | 8000 veya 5173 dolu; eski terminali kapat |
| Demo verisi karıştı | `scripts/seed_demo.py --reset` her şeyi baştan kurar |
| Python tarafında değişiklik yansımıyor | uvicorn'u `--reload` ile başlattığından emin ol |
| "Havuzu dağıt" **403** veriyor | Moderatör değilsin; sağ üstten Ceyda'ya geç |
| Ceyda'da moderatör rozeti yok | Veritabanı eski. `python scripts/set_role.py ceyda moderator` |
| Sunucu yeniden başlayınca oturum düştü | Normal: imzalama anahtarı süreç başına üretiliyor. Arayüz sessizce yeniliyor; kalıcı istersen `NEMEK_TOKEN_SECRET` ver (bkz. [`.env.example`](.env.example)) |

Docker'da çalışıyorsan `set_role.py`'yi kapsayıcı içinde koştur — böylece
`down -v` yapıp her şeyi sıfırlamak zorunda kalmazsın:

```bash
docker compose exec backend python /app/scripts/set_role.py ceyda moderator
```

## Sağlamasını yapmak istersen

```bash
cd backend
../.venv/Scripts/python.exe -m pytest tests/
```

128 test. <!-- sayim: backend --> Ayrıca `docs/` altında ölçüm sonuçları var: `DEGERLENDIRME.md` (6.400
sorguluk değerlendirme), `GECIKME.md` (süreler), `MIMARI.md` (diyagramlar).
Bu dosyalardaki hiçbir sayı elle yazılmadı; hepsi `backend/eval/` ve `backend/poc/`
altındaki betiklerin çıktısı ve yeniden koşturulabilir.
