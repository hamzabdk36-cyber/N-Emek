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
Kullanıcı gözünden: `docs/KULLANICI-AKISLARI.md` (yolculuk + akış diyagramları) · `docs/REHBER.md` (ekran ekran) · `docs/gorseller/` (ekran görüntüleri)
İş modeli: `docs/IS-MODELI.md` — dağıtım rakamları kayıtlı `Payout` satırlarından okundu, uydurulmadı
YZ mimarisi: `docs/YZ-MIMARISI.md` — model seçimi, eğitim yok–çıkarım var gerekçesi, GPU/CPU ölçümü
Veri, model, etik: `docs/VERI-MODEL-ETIK.md` — ne saklanıyor, yanlış atıf asimetrisi, itiraz hakkı, bilinen açıklar
Kullanıcı tarafı ölçüm: `docs/ERISILEBILIRLIK.md` (denetim + bulgular) · `docs/KULLANICI-ARASTIRMASI.md` ve `docs/KULLANILABILIRLIK-PROTOKOL.md` (düzenek) → `docs/KULLANILABILIRLIK-SONUCLARI.md`. **Son ikisi gerçek katılımcı bekliyor; şablonlardaki `___` alanları tahminle doldurulmaz.**
Demo ve sunum: `docs/DEMO-SENARYOSU.md` (replikli çekim senaryosu) · `docs/SUNUM.md` (slayt içeriği, Marp uyumlu)
Ölçümler: `docs/FAZ0-SONUCLARI.md` (risk kapatma) · `docs/DEGERLENDIRME.md` (tam korpus) · `docs/GECIKME.md` (uçtan uca) · `docs/ACILIS-SURESI.md` (indeks kalıcılığı)

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
cd backend && ../.venv/Scripts/python.exe -m pytest tests/   # pay motoru + uçtan uca + API + yetki + silme + indeks + maliyet + dağıtım
cd frontend && npm test                                      # yerleşim + bileşenler + ekranlar + oturum
.venv/Scripts/python.exe scripts/seed_demo.py --reset        # altın senaryoyu kur ve anlat

# Uygulamayı çalıştır (iki terminal)
.venv/Scripts/python.exe -m uvicorn app.main:app --reload --app-dir backend  # :8000
cd frontend && npm run dev                                                   # :5173
```

Backend 125 test, arayüz 106 test. <!-- sayim: backend, arayuz --> Bu sayılar elle
tutulmuyor: `python scripts/dokuman_denetimi.py` dokümanlardaki her sayısal iddiayı
ölçümle karşılaştırır ve CI'da koşar.

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
../.venv/Scripts/python.exe -m eval.run_startup                # docs/ACILIS-SURESI.md
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
bir alan adı değişse diğer 35 test yeşil kalıyor ama arayüz sessizce kırılıyordu <!-- sayim: tarihsel --> — bu
mutasyonla doğrulandı. Ağır iki test `slow` işaretli: `-m "not slow"` ile atlanabilir.

### Arayüz testleri (Vitest + Testing Library, jsdom)

10 Ağustos'taki rozet–çizgi çakışması ekranda duran, kod okunarak bulunamayan ve
ancak takım şikâyet edince görülen bir hataydı. Arayüzde hiç test yoktu; bu boşluk
kapatıldı.

Ağırlık merkezi `components/chainLayout.ts`: zincir yerleşimi bileşenden ayrılmış
**saf bir fonksiyon** ve DOM'a hiç dokunmuyor. Böylece asıl iddia tek satırda
sınanabiliyor — *hiçbir kapsama rozeti hiçbir düğüm kutusuyla ve hiçbir başka
rozetle kesişmez*. Dört sentetik DAG üzerinde koşuyor: düz zincir, elmas, tek
atlama, iki atlama. Değişmezlerin boş olmadığı mutasyonla doğrulandı: koridora
çıkarma mantığı kapatıldığında altı test kırmızıya döndü.

`api.oturum.test.ts` ve `session.test.tsx` oturum katmanını koruyor: `fetch` sahtelenip
gönderilen `Authorization` başlığına doğrudan bakılıyor, 401 sonrası tek seferlik sessiz
yenileme ve sonsuz döngüye girmemesi sınanıyor. Bu katman sessizce bozulabilir — jeton
eklenmezse ekranda yalnızca "bir şey çalışmıyor" görünür, sebebi görünmez.

Diğer dosyalar davranışı koruyor: `ChainGraph.test.tsx` katkısız ara halkanın
grafikten düşmediğini ve kesikli çizildiğini, `ui.test.tsx` `ShareBar`'ın dağılımın
tamamını `aria-label`'a çevirdiğini (bu, görsel olmayan kullanıcının payları
öğrenebildiği tek yer), `ContentDetail.test.tsx` pay satırı açıldığında
kapsama/güven/sönümleme ve formül satırının göründüğünü ve itiraz kutusunun yalnızca
payın sahibinde çıktığını, `Feed.test.tsx` kartın tek bir Emek Kartı hedefi
gösterdiğini sınıyor.

Fikstürler `src/test/veri.ts` içinde ve demo verisinden bağımsız: bir yerleşim kuralı
kırıldığında "demo verisi değişmiş" mazereti olmasın. Sayfa testleri `src/test/kur.tsx`
üzerinden yönlendirici + oturum bağlamıyla sarmalanıyor; uçlar `vi.spyOn(api, …)` ile
sahteleniyor, yani `api.ts` sözleşmesi gerçek kalıyor.

`api.test.ts` sayı biçimini sabitliyor. Kullanıcıya görünen her ondalıklı sayı üç
yardımcıdan birinden geçiyor ve ayraç yalnızca `api.ts` içinde tanımlı: `pct` (oran →
yüzde), `pctRaw` (hazır yüzde), `sayi` (güven/sönümleme/ham ağırlık gibi yüzde olmayan
ölçümler). Önceden `pctRaw` nokta üretiyordu ("%84.0") ve bunu yalnızca `ShareBar` kendi
içinde düzeltiyordu; skorlar da altı ayrı yerde doğrudan `toFixed` ile yazılıyordu.
Kodda kalan `toFixed` çağrıları ya bu üç yardımcının içinde ya da `toFixed(0)`, yani
ondalık ayracı hiç çıkmıyor.

### Hata sınırı

`components/HataSiniri.tsx`, `App.tsx` içinde `Routes`'u sarıyor. Bir bileşen render
sırasında hata fırlatırsa React tüm ağacı söküyor ve ekranda **bembeyaz bir sayfa**
kalıyor — jüri demosunda geri dönüşü olmayan bir durum, çünkü gezinme çubuğu da gidiyor.
Sınır bilerek uygulamanın en dışında değil `Sayfalar` içinde: başlık, gezinme ve kullanıcı
seçici ayakta kalıyor, kullanıcı başka bir ekrana geçerek demoya devam edebiliyor. Rota
değişince `key` ile sıfırlanıyor. Yığın izi ekrana dökülmüyor (kapalı bir `details`
içinde) ama konsola bırakılıyor.

React 19'da da hata sınırı yazmanın tek yolu sınıf bileşeni;
`getDerivedStateFromError` / `componentDidCatch` kancalarla karşılığı olmayan iki API.

### Sürekli tümleştirme

`.github/workflows/ci.yml` — her gönderim ve her PR'da iki bağımsız iş:

| İş | Ne koşar |
|---|---|
| backend | torch **önce** ve CPU indeksinden → `requirements.txt` → C2PA sertifikaları → 8 görsellik test korpusu → `pytest -m "not slow" -rs` (122 test) <!-- sayim: backend-hizli --> → doküman denetimi |
| arayüz | `npm ci` → `tsc --noEmit` → `vitest run` → `npm run build` → doküman denetimi |

**Yeşil rozet gerçekten bir şey söylemeli.** İlk CI koşusu korpussuz çalıştı ve yeşil
yandı: `test_api_ucnoktalari` ile `test_e2e_altin_senaryo` modül fikstürlerinden atlandı,
geriye yalnızca 22 saf pay testi kaldı. 47 test sessizce atlanmıştı <!-- sayim: tarihsel, tarihsel --> ama iş başarılı
görünüyordu — yani rozet, API sözleşmesini ve altın senaryoyu hiç doğrulamadığı halde
doğruluyormuş gibi duruyordu. İki karşı önlem kondu:

1. Korpus CI'da indiriliyor. Testler yalnızca `photos[0]` ve `photos[3]`'ü kullanıyor,
   dolayısıyla 8 görsel yetiyor; tam korpus (320) değerlendirme betikleri için ve yerelde
   kalıyor. **`fetch_eval_images.py 8` yerelde çalıştırılmamalı** — hedefi aşan dosyaları
   siler, yani mevcut 320'lik korpusu 8'e düşürür.
2. `tests/conftest.py` içindeki `gorsel_korpusu()`, korpus eksikken yerelde atlıyor ama
   `CI` ortam değişkeni varsa **duruyor**. Yerelde atlama doğru davranış (korpus depoda
   değil, yeni klonlayan biri önce onu indirmek zorunda kalmasın); CI'da eksiklik kurulum
   hatasıdır.

CLIP ağırlıkları (~600 MB) `actions/cache` ile önbelleğe alınıyor — altın senaryo testi
köken kurtarma hattının tamamını çalıştırdığı için modele ihtiyaç var. `slow` işaretli iki
test yine koşmuyor; onlar hattı tam korpusla ölçüyor.

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
  components/ChainGraph.tsx    SVG DAG çizimi (yalnızca çizim)
  components/chainLayout.ts    zincir yerleşimi — saf fonksiyon, testin asıl hedefi
  components/HataSiniri.tsx    hata sınırı — beyaz ekran yerine çıkış yolu
  test/                        fikstürler (veri.ts) + sayfa sarmalayıcısı (kur.tsx)
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

### Emek Kartı'nın maliyeti

İki düzeltme; ikisi de çıktıyı değiştirmiyor, yalnızca aynı kartı daha ucuza üretiyor.
Bu yüzden gerilemeleri gözle görülmez — `test_emek_karti_maliyeti.py` sayıları değil
**kaç kez hesaplandığını ve kaç sorgu atıldığını** sınıyor.

**Alt grafik bir kez toplanıyor.** `build_chain` pay hesabı için alt grafiği toplayıp
geçişli indirgemeyi koşuyor, `_chain_graph` de zincir görünümü için baştan aynı ikisini
koşuyordu — aynı istekte iki BFS, iki indirgeme. `chain.collect()` bir `Subgraph` üretiyor
ve `build_labour_card` onu iki tarafa da veriyor.

**İçerik ve sahipler toplu çekiliyor.** `build_chain` ve `_chain_graph` düğüm başına
`session.get(Content)` + `session.get(User)` yapıyordu. `chain.fetch_contents` /
`fetch_owners` tek `IN` sorgusuna indiriyor.

Değişmezlerin boş olmadığı mutasyonla doğrulandı: iki düzeltme geri alındığında üç test
kırmızıya döndü. `_collect_subgraph` hâlâ BFS'te düğüm başına bir kenar sorgusu atıyor —
bu kapsam dışında bırakıldı, testler de yalnızca `contents`/`users` tablolarını sayarak
düzeltilen şeyi izole ediyor.

### Yükleme boyutu sınırı

`await file.read()` dosyanın tamamını belleğe alıyordu ve sınırın uygulandığı tek yer
Docker'daki nginx'ti — yani yerel çalıştırmada hiçbir sınır yoktu ve tek bir istek
sunucunun belleğini tüketebiliyordu. `routes._read_upload` dosyayı 1 MB'lık parçalar
hâlinde okuyup `max_upload_mb` aşılınca **413** döndürüyor; belleğe alınan miktar hiçbir
zaman sınırdan fazla olmuyor.

`frontend/nginx.conf` içindeki `client_max_body_size` ile ayarlardaki `max_upload_mb` aynı
değerde (32 MB) tutulmalı — ayrılırlarsa aynı istek ortama göre farklı yerde reddedilir.

### Silme ve yetki haritası

`DELETE /api/contents/{id}` — yalnızca sahibi. Silme beş yerdeki izi birlikte götürüyor:
görsel dosyası, eşleşme maskeleri, parmak izi + vektör (satırla), bağlar ve o bağlara
açılmış itirazlar, arama indeksi. İndeks silmeden sonra veritabanından yeniden kuruluyor —
FAISS "flat" indekste tek satır silmek satır → içerik eşlemesini kaydırıyor; yeniden
kurmak hem basit hem güvenli ve indeks kalıcılığı sayesinde milisaniyeler sürüyor.

**Ödemesi olan içerik silinmiyor (409).** `Payout` gerçekleşmiş bir ödemenin dondurulmuş
kaydı; gelir dağıtan bir sistemde silinemez. Bu, silme hakkının tam karşılanmadığı bir
sınır ve `VERI-MODEL-ETIK.md` §10'da açıkça yazılı.

**Durum değiştiren hiçbir uç oturumsuz çalışmıyor.** Sahiplik gerektirenler: `revenue`,
`delete`, `distribute` (içerik), `disputes` (payın sahibi), `resolve` (itirazı açan).
**Moderatör** (`User.role = "moderator"`) yalnızca ikisine yetiyor:
`disputes/{id}/moderate` ve `campaigns/{id}/distribute` — ikisi de geri alınamaz sonuç
doğuruyor. Rol açıkça veriliyor: demo verisinde **Ceyda** moderatör (`seed_demo.py`), var
olan bir veritabanında `scripts/set_role.py ceyda moderator`. Rol vermek bilerek bir uç
değil betik — "kim rol verebilir" sorusu bu prototipin kapsamı dışında. Tam harita:
`VERI-MODEL-ETIK.md` §11.

**Dağıtım idempotent.** `distribute_content` yeni ödemeleri yazmadan önce o gönderinin
eski ödemelerini siliyor; `distribute_campaign` kampanyanın tümünü. Kural: *bir gönderi,
bir ödeme kümesi.* Önceden değildi ve düğmeye iki kez basmak kazançları ikiye
katlıyordu — para ile ilgili sessiz bir doğruluk hatası. Üç mutasyonla doğrulandı
(`tests/test_dagitim_idempotent.py`).

### İndeks kalıcılığı ve açılış süresi

İndeks eskiden her açılışta **veritabanındaki her içeriğin görselini okuyup CLIP'i
yeniden çalıştırarak** kuruluyordu. Üç içerikle fark yoktu; maliyet içerik başına bir
model çıkarımı olduğu için açılış içerik sayısıyla doğrusal büyüyordu.

Üç kademeli açılış (`services/registry.py::load_or_rebuild`):

| Kademe | Ne yapıyor |
|---|---|
| **anlık görüntü** | `data/index/snapshot/` altındaki FAISS dosyaları okunur; kimlik kümesi veritabanıyla aynıysa kullanılır |
| **veritabanı** | parmak izi `phash/dhash/whash` + `tile_hashes`'ten, vektör `clip_vector`'dan kurulur; görsele ve modele dokunulmaz |
| **görseller** | yalnızca vektörü eksik **ya da başka bir modelden gelen** içerikler için; hesaplananlar veritabanına geri yazılır |

Hazır olma ölçütü iki şey: vektör var mı, ve `embedding_model` bugünkü modelle aynı mı.
İkincisi olmadan model değiştirildiğinde eski vektörler geçerli sayılıyor ve sorgular
başka bir gömme uzayında aranıyordu — **hiçbir hata vermeden** yanlış sonuç. Anlık görüntü
de aynı kontrolden geçiyor.

Ölçüldü (`docs/ACILIS-SURESI.md`, 280 içerik): görsellerden **11,5 sn** · veritabanından
**32 ms** · anlık görüntüden **16 ms**. Docker'da gerçek demo verisiyle 4.899 ms → 27 ms.

Anlık görüntü bir **önbellek**, kaynak doğru değil: bayatsa ya da bozuksa sessizce atılıp
veritabanı kademesine düşülüyor. Bu yüzden her yüklemede güncellenmiyor — kapanışta bir
kez yazmak yetiyor. Hazır olma ölçütü yalnızca `clip_vector`: boş bir blok hash listesi
"hesaplanmadı" demek değil, geçerli bir değer.

**Şema göçü.** `create_all` var olan tabloya sütun eklemiyor, Alembic de bu ölçekte fazla.
`core/database.py::_eksik_sutunlari_ekle` eksik sütunları `ALTER TABLE` ile ekliyor —
yoksa demo veritabanı Docker biriminde yaşadığı için yeni bir sütun jüri makinesindeki
mevcut veritabanını `no such column` ile kırardı. Yalnızca *eklemeli* değişiklikler için;
tip değişimi veya silme gerekirse `docker compose down -v`.

### Oturum ve yetki

`POST /api/oturum` bir **demo kimlik sağlayıcısı**: kullanıcı kimliğini alır, imzalı ve
kısa ömürlü bir jeton döner. **Parola sorulmaz ve bu bilinçli** — N-Emek bağımsız bir
sosyal ağ değil, N'Sosyal'in içine giren bir emek katmanı; kimlik doğrulama ana platformun
işi. Gerçek dağıtımda bu ucun yerini N'Sosyal'in kimlik sağlayıcısı alır ve geri kalan
uçlar aynen çalışır, çünkü onlar jetonun *nereden geldiğini* değil geçerli olup olmadığını
soruyor. Gerekçenin tamamı `app/core/security.py` başında.

Çözdüğü somut sorun: önce `owner_id` form alanından geliyordu, yani **herkes herkes adına
içerik yükleyebiliyor, başkasının payına itiraz edebiliyor ve başkasının içeriği üzerinde
gelir değiştirebiliyordu.** Yetki kurallarının tutunabileceği bir kimlik yoktu.

Kullanıcı adına iş yapan dört uç artık `Authorization: Bearer` okuyor: `POST /contents`,
`/contents/{id}/remix`, `/disputes`, `/contents/{id}/revenue`.

| Kural | Sonuç |
|---|---|
| Jeton yok / bozuk / süresi dolmuş | **401** |
| İtirazı yalnızca payın sahibi (bağın *kaynak* tarafındaki içeriğin sahibi) açabilir | başkasına **403** |
| Geliri yalnızca içeriğin sahibi değiştirebilir | başkasına **403** |

Jeton HMAC-SHA256 ile imzalanıyor; harici bağımlılık eklenmedi (PyJWT/itsdangerous yok),
tamamı standart kütüphane — bağımlılık eklemek Docker imajını ve CI kurulumunu da
değiştirirdi.

İmzalama anahtarı ayarlarda yoksa **süreç başına rastgele** üretilir: depoya, yanlışlıkla
üretimde kullanılabilecek sahte bir varsayılan anahtar konmadı. Bedeli, sunucu yeniden
başlayınca eski jetonların geçersiz olması; arayüz bunu kaldırıyor — 401 alınca oturumu bir
kez sessizce yeniliyor ve isteği tekrarlıyor (`frontend/src/api.ts`). Üretimde
`NEMEK_TOKEN_SECRET` verilir.

Arayüzde görünür değişiklik yok: üstteki kullanıcı seçici artık arka planda oturum açıyor.

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
