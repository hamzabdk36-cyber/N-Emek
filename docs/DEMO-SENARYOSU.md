# Demo Videosu — Çekim Senaryosu

**Hedef:** yaklaşık 5 dakika, Türkçe anlatım, ekran kaydı.
**Anlatının omurgası:** kaynağı *bulmak* değil, kullanılan oranı **ölçmek**.

Replikler olduğu gibi okunabilir. Ekranda görülecek her sayı gerçek demo verisinden;
hiçbiri montajla değiştirilmemeli.

## Bu video jüri gününde ne için kullanılıyor (12 Eylül güncellemesi)

12 Eylül toplantısında organizasyon açıkça belirtti: **jüri günü ana gösterim canlı
prototiptir** (kendi bilgisayarımızdan, 2–3 dk) — video arkada oynatılarak sunum
yapılamaz, bu talep reddedildi. Dolayısıyla bu senaryo videosu üç farklı işe yarıyor,
ana gösterimin yerine geçmiyor:

1. **Sunum dosyasına gömülü kısa klip** (≤60 sn) — toplam 15 dakikalık süreyi aşmadan,
   şablon içine yerleştirilir.
2. **Yedek**: canlı demo salon içinde (ağ, GPU, donanım) arızalanırsa gösterilecek.
3. **Şartnamenin teslimat listesindeki "demo videosu" kalemi.**

Bu yüzden burada iki çıktı üretilir: tam **~5:00** sürüm (madde 2 ve 3 için) ve aşağıdaki
"Süre daraltma" bölümünden türetilen **≤60 sn'lik kısa kesit** (madde 1 için).

## Durum notu (15 Eylül)

**Sıra.** Transkripte göre jüri günü akışı *15 dk sunum → kısa soru-cevap → jüri
"prototipi gösterebilirsiniz" deyince 2–3 dk canlı gösterim*, kendi bilgisayarımızdan.
Gösterim sunumun sonunda; süre "15 artı 2 gibi" ve değişebilir. Sunum PDF olarak teslim
edildiği için ≤60 sn'lik klibin sunuma gömülmesi pratikte mümkün değil (PDF video
oynatmaz); video yalnızca yedek ve teslimat kalemi olarak kalıyor.

**Görev.** Sunumu Berra Özer, sistemi ve canlı demoyu Hamza Budak üstleniyor. Canlı
demonun biçimi seçildi: **"canlı kanıt"** — bir sonraki bölüm. Ondan sonraki sahneler
5 dakikalık video içindir.

## Sayılar düzeltildi (17 Eylül)

Aşağıdaki sahne replikleri **çalışan sistemden okunan değerlerle** güncellendi. Kaynak:
yerel `data/nemek.db`, backend ayakta (`/api/contents/.../labour-card`, `/api/verify`,
`/api/users/.../earnings`). Kural, `CLAUDE.md`: ekrandaki her sayı anlatılanla birebir aynı.

| Sahne | Eski replik | **Ekranda yazan** | Nereden okundu |
|---|---|---|---|
| 4 · Ayşe kapsama | %85,2 | **%87,1** | Emek Kartı, Ayşe satırı `factors.kapsama` = 0,8712 |
| 4 · Ayşe payı | %68,1 | **%68,1 · ₺2.574,63** | aynı satır |
| 4 · Ayşe güven / sönümleme | 0,95 / 0,85 | **0,95 / 0,85** | değişmedi |
| 5 · Burak ölçülen alan | %12,2 | **%12,5** | "Ölçülen bölge" paneli, `pct(0,1253)` |
| 5 · Burak toplam görünen | %97 | **%99,7** | Burak satırı `toplam_kapsama` = 0,9965 |
| 6 · Ayşe → Burak rozeti | %87 | **%87** | zincir rozeti tam sayıya yuvarlıyor (0,8743) |
| 6 · Burak → Ceyda rozeti | %97 | **%100** | aynı yuvarlama (0,9965 → %100) |
| 8 · Ayşe kampanya toplamı | "34.500" | **₺34.541,45** | `/api/users/.../earnings` |

Sunum dosyasındaki 5. ve 10. sayfa hâlâ %87,2 · ₺2.576,30 · ₺34.548,96 diyor (başka bir
koşumun ölçümü). Videoda **ekrandaki** değerler okunur; slayt farkı jüri sorarsa
"her kurulumda yeniden ölçülüyor" diye açıklanır (aşağıdaki soru tablosu).

### Filigran ve parmak izi iddiası kaldırıldı (17 Eylül ölçümü)

Sahne 3'ün eski metni "piksellere gömülü görünmez filigranı okudu" diyordu. Hattın
aşama günlüğü bunu doğrulamıyor. Canlı `POST /api/verify` çıktısı (türev dosya):

```
c2pa       bulunamadı   İçerik kimliği silinmiş veya hiç oluşturulmamış.
exact      bulunamadı   SHA-256
watermark  bulunamadı   filigran okunamadı
phash      bulunamadı   0 isabet
clip       bulundu      5 isabet
geometry   bulundu      2 aday doğrulandı, 2 bağ kaldı
```

Ceyda'nın kayıtlı içeriğinde de filigran kanıtı yok: Emek Kartı'ndaki kanıt satırları
Burak için `phash` + `clip` + `geometry`, Ayşe için `clip` + `geometry`. Kırpma ve
yeniden ölçekleme filigranı götürüyor — bu zaten belgelenmiş, dürüst bir sınır
(`VERI-MODEL-ETIK.md`). Replikler ekranda **duran** kanıtları anlatacak şekilde
yeniden yazıldı; bu, beş aşamalı hattın niye gerekli olduğunu anlatan daha güçlü bir
hikâye: biri düştü, diğeri taşıdı.

**Jüri günü veritabanı: yerel `data/nemek.db` (15 Eylül kararı).** Sebep: bütün demo
ölçümleri ve `demo_hazirla.py` bu kurulumda yapıldı; Docker bu hazırlıkta hiç denenmedi,
konteynerde GPU kapalı ve korpusu 24 görsel. Aynı gün ilgisiz içerikle zenginleştirildi
(aşağıda). Replikler ve slayt sayıları bu veritabanından okunur. Bundan sonra
`seed_demo.py --reset` çalıştırılmaz: demo verisini yeniden ölçer, sayılar yine kayar ve
eklenen içerikler gider.

---

## Canlı demo — "canlı kanıt" (jüri günü, 2:00 / 3:00)

**Neden bu biçim.** Slaytlar Emek Kartı ekranlarını zaten gösteriyor; demonun katacağı
şey jürinin gözü önünde **hattın gerçekten çalışması**. Kısa bir Emek Kartı turu, ardından
Kaynak Bul'da iki canlı sorgu: sisteme hiç girmemiş bir türevde kaynak bulunur, ilgisiz
bir fotoğrafta bağ önerilmez. Kaynak Bul kayıt yapmaz (`POST /api/verify`), yani demo
verisi değişmez ve sonraki sorularda ekran aynı kalır.

**Yürüten:** Hamza Budak (bilgisayar ve anlatım). Sunumu yapan Berra Özer, jüri
"prototipi gösterebilirsiniz" deyince sözü devreder.

### Sahneye çıkmadan (salon sırası gelmeden ~15 dk önce)

Tek seferlik hazırlık **yapıldı (15 Eyl):** `scripts/demo_zenginlestir.py` yerel veritabanına
kampanya dışı 20 içerik ekledi. **18 Eyl:** `scripts/demo_zincirler.py` bu içeriklerden 8 türevle
7 zincir kurdu (aşağıda). **18 Eyl gecesi** stok kareler ekibin 23 telefon fotoğrafıyla değiştirildi,
zincirler onlardan yeniden kuruldu ("Günlük fotoğraflar" bölümü). Tekrar gerekmez.

**Tek adım: depo kökündeki `demo_baslat.bat` dosyasına çift tıkla.**
Betik aşağıdaki dört komutu sırayla yürütür. Çevrimdışı değişkenleri koyar, backend'i `--reload` olmadan başlatır, arayüzü açar ve `demo_hazirla.py` ile modeli ısıtır. Sonunda büyük harfle **HAZIR** ya da **HAZIR DEĞİL** yazar ve üç sekmeyi açar.
Zaten çalışan bir sunucu varsa onu yeniden kullanır; bu yüzden arıza anında yeniden başlatma için de kullanılabilir.
Veritabanına dokunmaz. Durdurmak için açılan iki pencereyi kapatmak yeterli.
Aşağıdaki elle komutlar yedek olarak duruyor.

```powershell
$env:HF_HUB_OFFLINE = "1"          # salonda internet yoksa da model yerel onbellekten
.venv/Scripts/python.exe -m uvicorn app.main:app --app-dir backend   # :8000, --reload YOK
cd frontend; npm run dev                                             # :5173
.venv/Scripts/python.exe scripts/demo_hazirla.py                     # "Hazır" yazmalı
```

`HF_HUB_OFFLINE=1` **jüri gününde de verilir** — 17 Eylül'de ölçüldü, sistem bu
değişkenle sorunsuz çalışıyor (aşağıda "Çevrimdışı prova"). Değişkeni vermek, ağın açık
olduğu durumda bile modelin ağa çıkmayı denemesini engelliyor.

- [ ] `demo_hazirla.py` **"Hazır"** yazdı. Betik iki dosyayı `data/demo/` altına üretir,
      ikisini sunucuya gönderip modeli ısıtır ve sonucu denetler. "HAZIR DEĞİL" yazarsa
      canlı sorgu adımı atlanır, akışın geri kalanı yapılır.
- [ ] Neden şart: süreçteki **ilk** sorgu model yüklendiği için ölçümde ~9,5 sn sürdü,
      ısındıktan sonra 0,3–0,4 sn. Isıtılmamış bir sistemde jüri önünde 10 sn boş ekran olur.
- [ ] Tarayıcıda üç sekme hazır: Akış · "Bulduğum kare" Emek Kartı · Kaynak bul.
      Kullanıcı seçici **Ayşe Yılmaz**'da. F11 tam ekran, yakınlaştırma %100.
- [ ] Dosya seçme penceresi bir kez `data/demo/` klasöründe açılıp kapatıldı; sahnede
      o klasörden açılır.
- [ ] Windows: ekran **Çoğalt** (Win+P), uyku kapalı, bildirimler susturulmuş, şarj
      kablosu takılı.
- [ ] Wi-Fi kapalıyken en az bir tam prova yapıldı (salonda internet garantisi yok).

### Akış (2:00)

| Süre | Ekran ve hareket | Söylenecek |
|---|---|---|
| 0:00–0:10 | **Akış** | "En üstteki üç gönderi tek zincir: Ayşe'nin fotoğrafı, Burak'ın remixi, Ceyda'nın ekran görüntüsü." |
| 0:10–0:35 | "Bulduğum kare" → **Emek Kartı**, Köken paneli | "Ceyda'nın dosyasında içerik kimliği yoktu. Sistem kaynağı yine de buldu; güveni ekranda." |
| 0:35–1:00 | Pay dağılımında **Ayşe** satırını aç | "Ayşe iki adım geride ama en büyük pay onun. Satırda kapsama, güven ve sönümleme; altındaki satır üçünün çarpımı." Sayıları **ekrandan okuyun**. |
| 1:00–1:20 | **Burak** satırı → ölçülen bölge, "Kaynaktan gelen bölgeyi vurgula" kutusunu kapat/aç | "Parlak kalan pikseller ölçümle Burak'tan geldiği doğrulanan bölge. Burak'a yalnızca kendi kattığı alan yazılıyor." |
| 1:20–1:45 | **Kaynak bul** → `kaynak-bul-turev.jpg` → Kökeni çöz | "Bu dosyayı sistem hiç görmedi: Ayşe'nin fotoğrafından kırpılıp üstüne yazı eklendi. Şimdi hattı çalıştırıyorum." Sonuç gelince: "Kaynak bulundu, kullanılan alan ölçüldü." |
| 1:45–1:55 | Aynı ekranda `kaynak-bul-ilgisiz.jpg` → Kökeni çöz | "Bu fotoğrafın sistemde hiçbir kaynağı yok." Sonuç: **"Kaynak bulunamadı."** "Bulamadığında uydurmuyor." |
| 1:55–2:00 | — | "Emek görünür olsun diye: tahminle değil, ölçümle." |

15 Eylül yerel ölçümünde türev dosyası iki kaynak verdi: Sabah ışığı %93,0 ve
Bulduğum kare %67,9 kullanılan alan. Zenginleştirmeden ve zincirlerden sonra, indekste 31 içerikle, sonuç aynı. Bulduğum kare de Ayşe'nin piksellerini taşıdığı için
çıkıyor. Sayılar veritabanına göre değişir; sahneden önce `demo_hazirla.py` çıktısından
okunur.

### 3 dakika verilirse (+1:00)

- **1:55'ten sonra, +20 sn — itiraz.** Emek Kartı'na dönülür, Ayşe satırındaki "Yeniden
  ölçüm iste" düğmesi **gösterilir, tıklanmaz**. "İtirazı yalnızca payın sahibi açabilir;
  bağ daha hassas bir dedektörle yeniden ölçülür, çözülmezse insana gider."
- **+20 sn — zincir.** Atıf zinciri grafiği: "Ok yönü türetme yönü; onaylanmamış bağ
  kesikli çizilir."
- **+20 sn — pay.** Tampon süre; jüri bir şey sorarsa buraya harcanır.

### Jüri sorarsa

| Soru | Cevap |
|---|---|
| "Türevde neden iki kaynak çıktı?" | Kaynak bul bir sorgu, pay hesabı değil. Pikseller iki gönderide de var; hangi bağın paya gireceğine yayında geçişli indirgeme karar veriyor. |
| "Slayttaki sayıyla ekrandaki biraz farklı" | Demo verisi her kurulumda yeniden ölçülüyor ve koşumlar arasında binde birkaç fark çıkıyor. Sayılar elle yazılmıyor, o koşumun ölçümü. |
| "Akıştaki diğer gönderiler ne?" | Demo verisi: lisanslı test korpusundan, kampanya dışı. Bir kısmı birbirinin remixi, ekran görüntüsü ya da kolajı; onların da Emek Kartı ve küçük gelirleri var. Kaynak bul türevin kaynağını bunların da bulunduğu indekste arıyor; ilgisiz fotoğraf hiçbiriyle eşleşmiyor. |
| "Kendi görselimizle deneyelim" | Kaynak bul'a jürinin görselini yükle; kayıt yapmaz. Sistemde olmayan bir görselse beklenen sonuç "kaynak bulunamadı". |
| "Filigran ve parmak izi neden bulamadı?" | Kırpma ve yeniden ölçekleme ikisini de götürüyor; bu bilinen ve belgelenmiş bir sınır. Hattın beş aşaması tam bunun için var: biri düştüğünde diğeri taşıyor. Burada kaynağı görsel benzerlik buldu, kararı geometrik ölçüm verdi. |
| "Yükleme / remix de gösterin" | Remix Stüdyo çalışır ama demo verisini değiştirir. Yapılırsa demo sonrasında `data/` yedeği geri yüklenir. |

### Bir şey ters giderse

| Belirti | Hamle |
|---|---|
| "Hat çalışıyor…" 5 sn'den uzun sürüyor | Beklemeyi bırak, Emek Kartı sekmesine dön: "Bu adımı az önce denetledik; asıl ölçüm burada görünüyor." |
| Bir ekran hata veriyor | Başka bir ekrana geç. Hata sınırı başlığı ve gezinmeyi ayakta tutuyor. |
| Sayfalar hiç yüklenmiyor | Yedek terminalde backend'i yeniden başlat: **ölçüldü, ~4,6 sn'de ayağa kalkıyor** (indeks anlık görüntüden, 16 ms). Ardından `demo_hazirla.py` ~7 sn'de modeli ısıtır — toplam **~12 sn**. 30 sn içinde gelmezse `docs/gorseller/` kareleri (02 → 03 → 04 → 06) üzerinden anlat ve durumu açıkça söyle. |
| Projeksiyon düşük çözünürlükte, mobil düzen açıldı | Devam et; düzen bilerek duyarlı. Gerekirse tarayıcı yakınlaştırmasını düşür. |

### Sahnede yapılmayacaklar

- Akışa içerik yüklemek, itiraz göndermek, kampanya dağıtmak, içerik silmek
- `seed_demo.py --reset`, `docker compose down -v`, backend'i `--reload` ile çalıştırmak
- API'yi `localhost` ile çağırmak: Windows'ta istek başına ~2 sn ekliyor, `127.0.0.1` kullanılır

### Çevrimdışı prova ve yeniden başlatma süresi (17 Eylül, ölçüldü)

16 Eylül'deki ikinci toplantı **yapılmadı**, yani "salonda internet var mı" sorusu
cevapsız kaldı. Varsayım artık **internet yok**. Ölçüm buna göre yapıldı.

Backend `HF_HUB_OFFLINE=1` ve `TRANSFORMERS_OFFLINE=1` ile sıfırdan başlatıldı:

| Ölçülen | Sonuç |
|---|---|
| Ayağa kalkma (süreç başlangıcı → `/api/health` 200) | **4,64 sn** |
| İndeks kaynağı | anlık görüntü, **16 ms** — veritabanı ve görsel okunmadı |
| İlk (soğuk) sorgu — model yükleniyor | **5,8 sn** |
| Isınmış sorgu | **205–294 ms** |
| `demo_hazirla.py` toplam (üretim + ısıtma + denetim) | **7,0 sn** → "Hazır", çıkış kodu 0 |
| Yeniden başlatma + ısıtma toplamı | **~12 sn** (arıza tablosundaki 30 sn eşiğinin altında) |

Sunucu günlüğü modelin **yerel önbellekten** yüklendiğini gösteriyor:
`~/.cache/huggingface/hub/models--laion--CLIP-ViT-B-32-laion2B-s34B-b79K`.
Türev dosyada iki kaynak (Sabah ışığı %93,0 · Bulduğum kare %67,9), ilgisiz görselde
sıfır bağ — çevrimiçi koşumla birebir aynı.

**Neyin kanıtlandığı, neyin kanıtlanmadığı.** Kanıtlanan: model ve indeks ağ olmadan
yükleniyor, hattın çıktısı değişmiyor. Kanıtlanmayan: fiziksel olarak Wi-Fi kapalıyken
işletim sistemi seviyesinde başka bir gecikme çıkıp çıkmadığı. `HF_HUB_OFFLINE=1` ağ
isteğini baştan engellediği için risk küçük ama sıfır değil — **Wi-Fi'ı kapatıp bir tam
tur daha atmak yine de listede.**

### Henüz açık

- **Wi-Fi fiziksel olarak kapalıyken** bir tam prova (yukarıdaki ölçüm `HF_HUB_OFFLINE=1`
  ile yapıldı, ağ kartı açıktı).
- USB yedeği masaüstünde hazır (`N-Emek-USB-yedek-20260915`, geri yükleme notu içinde);
  **USB belleğe aktarılmadı** — fiziksel iş.
- Slayt sayıları (5. ve 10. sayfa) yerel veritabanındaki değerlere çekilmedi; karar
  Berra'nın (`docs/SUNUM/_PLAN.md`). Video ve canlı demo ekrandaki değerleri okuyor,
  fark jüri sorarsa soru tablosundaki cevapla karşılanıyor.
- Demo videosu çekilmedi; replik metni ve kontrol listesi hazır (aşağıda "Okuma metni").

### Demo verisi zenginleştirildi (15 Eylül)

**Neden.** İndekste yalnızca altın senaryonun 3 içeriği vardı. Canlı Kaynak Bul sorgusu bu
yüzden zayıf bir kanıttı ("üç görselin içinden bulmak kolay"), akış da üç gönderiyle
geliştirici demosu gibi duruyordu.

**Ne yapıldı.** `scripts/demo_zenginlestir.py` yerel veritabanına üç kullanıcı (Deniz Kaya,
Emre Şahin, Selin Arslan) ve kampanya dışı, gelirsiz 20 içerik ekledi. İndekste artık
23 içerik var. Betik sıfırlama yapmıyor:
- Her aday yüklemeden önce kurtarma hattından geçiriliyor, bağ çıkan atlanıyor.
- Sahnedeki ilgisiz görsel (korpus sırası 10) ve altın senaryonun kaynağı (sıra 3) hariç.
- Yeni içerikler Ayşe'nin gönderisinden eskiye tarihleniyor; altın üçlü akışın üstünde kalıyor.

**Nasıl doğrulandı.**
- Betik altın senaryonun izini önce ve sonra karşılaştırıyor: bağlar, ödemeler, kazançlar,
  üç Emek Kartı'nın dağılımı ve zinciri, kampanyadaki içerik sayısı. Ayrıca `demo_hazirla`
  beklentisini süreç içinde sınıyor. Biri tutmazsa yedeği geri yüklüyor.
- Önce veritabanı kopyasında denendi: ikinci çalıştırma "zaten eklenmiş" dedi. Sahte bir
  fark verilince yedeği geri yükledi.
- Gerçek veritabanında `demo_hazirla.py` "Hazır" verdi: türev Sabah ışığı %93,0 ·
  Bulduğum kare %67,9, ilgisiz 0 kaynak, ısınmış sorgu 281–432 ms.
- Akışın ilk üçü altın senaryo, kampanyada 3 içerik, Ceyda'nın Emek Kartı'nda Ayşe %68,1 ·
  ₺2.574,63.
- `pytest -m "not slow"` 127 geçti.

**Geri dönmek gerekirse** (backend kapalıyken): `data/yedek/20260915-115019/` altındaki
`nemek.db`, `uploads/` ve `index/` `data/` altına geri kopyalanır.

### Türev zincirleri (18 Eylül)

**Neden.** Eklenen 20 içerik bağsızdı; Emek Kartları tek taraflı ve boş duruyordu. Akışta
altın üçlünün dışında da dolu Emek Kartı olan gönderiler olsun diye `scripts/demo_zincirler.py`
bu içeriklerden 8 türev yükledi, 7 zincir kuruldu. İndekste artık 31 içerik var.

| Türev | Kaynak | Biçim | Emek Kartı (kaynak payları) |
|---|---|---|---|
| Günün karesi, benim yorumum | Günün karesi | beyanlı remix: kırpma + yazı | Deniz %80,0 |
| Akıştan kaydettim | Arşivden | beyansız ekran görüntüsü | Emre %80,0 |
| Yolda ama komik → Güldüren kare | Yolda | üç halka: beyanlı meme, sonra beyansız ekran görüntüsü | Selin %56,9 · Deniz %23,1 |
| Hafta sonu kolajı | Hafta sonu + Pencereden | beyansız iki kaynaklı kolaj | Deniz %40,8 · Emre %39,2 |
| Akşamüstü, çıkartmalı | Akşamüstü | beyanlı remix: çıkartma | Selin %80,0 |
| Eski bir kareden kesit | Eski bir kare | beyansız kırpma + yazı | Deniz %79,2 |
| Renkler ama şaka | Renkler | beyanlı meme | Selin %76,7 |

Türevlere ₺190–870 arası gelir yazıldı; Emek Kartı tutarları bundan anlık hesaplıyor. Ödeme
satırı yazılmadı, kampanyaya dokunulmadı. Her türev kaynağından 20 dk sonraya tarihlendi:
akışta kaynağının hemen üstünde duruyor, altın üçlü yine en üstte.

**Nasıl doğrulandı.** Betik her yüklemeden sonra bağların yalnızca beklenen kaynaklara (ve üç
halkada onların atasına) gittiğini, her beklenen kaynağın Emek Kartı'nda pay aldığını sınadı.
Altın senaryonun izi (bağlar, ödemeler, kazançlar, üç kart, kampanya) önce ve sonra birebir
aynı; demo türevi yalnızca altın içerikleri buluyor. `demo_baslat.bat` "HAZIR" verdi: Sabah
ışığı %93,0 · Bulduğum kare %67,9, ilgisiz 0 kaynak; Ceyda'nın kartında Ayşe %68,1.

**Geri dönmek gerekirse** (backend kapalıyken): yedek `data/yedek/20260918-174555/`.

### Günlük fotoğraflar (18 Eylül, yapıldı)

**Neden.** Berra'nın geri bildirimi: akış katalog ya da dergi gibi duruyor. Zenginleştirme
içerikleri picsum/Unsplash korpusundan geliyor ve bunlar profesyonel stok kareler. Bunların
yerine ekibin kendi telefon fotoğrafları konacak.

**Değişmeyen.** Altın üçlü kahve fotoğrafıyla kalıyor. `seed_demo.py --reset` ölçümü yeniden
yapıyor ve sayılar kayıyor: 18 Eylül'de bir kopyada denendi, Ceyda'nın kartında Ayşe %68,1
yerine %67,9 (₺2.567,22) çıktı. Bu yüzden sıfırlama yok. Yalnızca deniz, emre ve selin'in
içerikleri değişiyor.

**Hazırlık.**
1. Fotoğraflar `data/demo_fotolar/` klasörüne konur. Bu klasör depoya girmez.
2. Aynı klasöre bir `liste.csv` yazılır. Sütunlar `dosya,baslik,aciklama,sahip,anahtar`.
   Biçim `scripts/demo_fotolar.py` başında anlatılıyor.
3. Sekiz fotoğrafa zincir yuvası atanır: `gunun`, `arsiv`, `yolda`, `hafta_sonu`, `pencereden`,
   `aksam`, `eski`, `renkler`.
4. Bir fotoğrafa `ilgisiz` yazılır. O kare akışa girmez ve Kaynak Bul'daki "bağ yok" sorgusu olur.
5. İstenirse `zincirler.csv` (`adim,baslik,aciklama`) ile türev başlıkları fotoğraflara uyarlanır.

**Kurulum** (backend kapalıyken):

```bash
.venv/Scripts/python.exe scripts/demo_zenginlestir.py --foto-klasoru data/demo_fotolar --degistir
.venv/Scripts/python.exe scripts/demo_zincirler.py --foto-klasoru data/demo_fotolar
demo_baslat.bat
```

`--degistir` eski 28 içeriği silme servisiyle kaldırıyor, yani görsel, bağ ve indeks birlikte
gidiyor. Ardından fotoğrafları ekliyor. Altın içeriklere değen bağlar, ödemeler ve üç kart
önce ve sonra karşılaştırılıyor. Biri tutmazsa betik yedeği geri yüklüyor. Fotoğraflar EXIF
yönüne göre döndürülüyor ve uzun kenar 1080 px'e indiriliyor. Yeniden kodlandıkları için konum
bilgisi yüklenen dosyaya geçmiyor.

**Kopyada doğrulandı.** Geçici bir veritabanında önce eski durum kuruldu (20 içerik ve 8 türev).
Ardından iki komut, Türkçe adlı ve EXIF'le döndürülmüş dosyalar içeren bir listeyle çalıştırıldı.
Sonuç: 28 içerik silindi, 22 kare ve 8 türev eklendi. Altın senaryo izi aynı kaldı. Döndürülmüş
kare doğru yönde yüklendi ve dosyada EXIF kalmadı.

**Gerçek veritabanında yapıldı (18 Eylül gecesi).** Masaüstündeki `günlük` klasöründen gelen
27 fotoğrafın 24'ü kullanıldı. Üçü dışarıda bırakıldı:
- Vakko logosu ve uçak tescili görünen kare,
- yüzün bir kısmı görünen kare,
- akıştaki başka bir kareyle aynı bina (biri diğerinin kaynağı sanılırdı).

Atatürk tabelası ve Anıtkabir akışta sade gönderi olarak duruyor; bunlardan türev üretilmiyor.
Kiraz fotoğrafı sahnedeki ilgisiz sorgu oldu. Dağılım şöyle:
- 23 kare akışta ve 8 türev bunlardan kuruldu; indekste 34 içerik var.
- İlk denemede kolajın ikinci kaynağı kumsal karesiydi ve bulunamadı. Karanlık gök ile denizde
  eşleşecek kadar doku yok. Betik bu adımı geri aldı; kaynak "Taş sokaklar" ile değiştirildi.
- Altın senaryo izi aynı kaldı.
- `demo_hazirla.py` "Hazır" verdi: Sabah ışığı %93,0 · Bulduğum kare %67,9, ilgisiz 0 kaynak,
  ısınmış sorgu 226–405 ms.

Geri dönmek gerekirse (backend kapalıyken): stok fotoğraflı son durum `data/yedek/20260918-223140/`.

---

## Çekim öncesi kontrol listesi

Demonun canlı çökmesi, videonun kendisinden daha pahalıya mal olur.

Kurulum **yerel**, Docker değil (15 Eylül kararı: jüri günü veritabanı `data/nemek.db`).
Videoyu da aynı kurulumda çekiyoruz ki ekrandaki sayılar canlı demoyla aynı olsun.

```bash
.venv/Scripts/python.exe -m uvicorn app.main:app --app-dir backend   # :8000, --reload YOK
cd frontend && npm run dev                                           # :5173
.venv/Scripts/python.exe scripts/demo_hazirla.py                     # "Hazır" yazmalı
curl -s http://127.0.0.1:8000/api/health
```

- [ ] `indexed_contents: 23`, `device: cuda` ve `c2pa_signing: true` dönüyor
- [ ] `demo_hazirla.py` **"Hazır"** yazdı (çıkış kodu 0) — model ısındı, ilk sorgunun
      ~9 saniyesi kayda düşmeyecek
- [ ] `http://localhost:5173` açılıyor; akışta **23** gönderi var ve **en üstteki üçü**
      Ceyda → Burak → Ayşe sırasıyla altın senaryo
- [ ] Üstteki kullanıcı seçici **Ayşe Yılmaz**'da (itiraz sahnesi buna bağlı)
- [ ] "Bulduğum kare" gönderisinin geliri **₺4.200** — değiştiyse Gelir kutusundan geri alın
- [ ] Emek Kartı'nda Ayşe satırı **%87,1 · 0,95 · 0,85 → %68,1 · ₺2.574,63**,
      Burak satırı **%12,5 · 0,98 · 1,00 → %11,9 · ₺449,37** (replikler bunları okuyor)
- [ ] `demo_hazirla.py` iki sahne dosyasını `data/demo/` altına üretti; Kaynak bul'daki dosya
      seçme penceresi bir kez o klasörde açılıp kapatıldı (Sahne 8'de klasör aramak yok)
- [ ] Tarayıcı tam ekran, yer imleri çubuğu kapalı, bildirimler susturulmuş
- [ ] Ekran çözünürlüğü 1920×1080, tarayıcı yakınlaştırması **%100**
- [ ] Kayıt öncesi bir prova turu atın: fare hareketleri yavaş ve kararlı olmalı

> **Kritik:** Kayıt sırasında demo verisini değiştiren hiçbir şey yapılmaz — yeni içerik
> yükleme, itiraz **gönderme**, kampanya dağıtma, içerik silme, `seed_demo.py --reset`.
> Hepsi zinciri yeniden ölçtürür ve aşağıdaki bütün sayılar kayar. Yükleme göstermek
> isterseniz en sona bırakın ve sonrasında `data/yedek/20260915-115019/` geri yükleyin.

---

## Sahne 1 — Problem · 0:00–0:25 (25 sn)

**Ekran:** Akış sayfası, sakin bir kaydırma.

> "Bir fotoğraf çekiyorsunuz. Biri onu kırpıp üstüne yazı ekliyor. Bir başkası o hâlinin
> ekran görüntüsünü alıp paylaşıyor. Üçüncü paylaşımda içerik binlerce kez görülüyor,
> marka sponsorluğu geliyor — ve sizin adınız hiçbir yerde yok.
>
> Sorun kötü niyet değil: zincir **teknik olarak kopuyor.** Ekran görüntüsü, içeriğin
> kimliğini tek tıkla siliyor."

**Yönerge:** Bu 25 saniyede ekran hareketi az olsun; izleyici sesi dinlesin.

---

## Sahne 2 — Çözüm, tek cümle · 0:25–0:50 (25 sn)

**Ekran:** Akışın **en üstündeki** üç kart sırayla vurgulanır (fareyle üzerlerinde durun).

> "N-Emek, bu zinciri geri kuran bir emek katmanı. Ayırt edici yanı şu: kaynağı
> **bulmakla** yetinmiyor, o kaynağın türev içerikte **ne kadar** kullanıldığını
> ölçüyor.
>
> Akışın en üstündeki üç gönderi aslında tek bir zincir: Ayşe'nin fotoğrafı, Burak'ın
> remixi, Ceyda'nın paylaşımı."

---

## Sahne 3 — Kritik an: kimliği silinmiş içerik · 0:50–1:45 (55 sn)

**Ekran:** "Bulduğum kare" → **Emek Kartı** → Köken paneli.

**Aksiyon:** Kartın "Emek Kartı →" bağlantısına tıklayın, Köken panelinde durun.

> "Ceyda'nın paylaştığı bu içerik sisteme 'kaynağı yokmuş' gibi girdi. Ekran görüntüsü
> alındığı için içerik kimliği silinmişti.
>
> Panelde yazan tam olarak bu: **yüklenen dosyada kimlik yoktu.** Ama sistem kaynağı yine
> de buldu — üstelik iki tanesini.
>
> Nasıl? Sırayla denedi: içerik kimliği yok, dosya özeti tutmuyor, filigran okunamıyor —
> ekran görüntüsü onu da götürmüş. Sonra görüntü parmak izi Burak'ın gönderisini
> yakaladı, görsel benzerlik modeli Ayşe'ye kadar indi, ve son adımda geometrik
> doğrulama ikisini de piksel piksel ölçtü.
>
> Hattın beş aşaması tam bunun için var: biri düşünce diğeri taşıyor.
>
> Güven: **sıfır virgül doksan sekiz.**"

**Yönerge:** "Yüklenen dosyada kimlik / yoktu" ve "Yayınlanan sürüm / imzalandı"
alanlarını fareyle işaret edin. Güven rozetinde bir saniye durun.

---

## Sahne 4 — Payın gerekçesi · 1:45–2:45 (60 sn)

**Ekran:** Emek Kartı, pay dağılımı. **Ayşe Yılmaz** satırına tıklayıp açın.

> "Gönderi dört bin iki yüz lira kazandı. Kart bunu kime, neden verdiğini gösteriyor.
>
> Ayşe zincirde iki adım geride ama en büyük payı o alıyor: yüzde altmış sekiz virgül
> bir. Sebebi ekranda yazıyor.
>
> Satırı açalım. **Kapsama yüzde seksen yedi virgül bir** — bu tahmin değil, ölçüm.
> **Güven sıfır virgül doksan beş. Sönümleme sıfır virgül seksen beş**, çünkü zincirde
> iki adım geride.
>
> Ve altındaki satır, bu üç sayıyı nasıl birleştirdiğimizi gösteriyor:
> pay eşittir kapsama çarpı güven çarpı sönümleme.
>
> Hiçbir rakam gerekçesiz gelmiyor."

**Yönerge:** Formül satırının üzerinde iki saniye durun. Bu, videonun en önemli karesi.

---

## Sahne 5 — Ölçüm görünür · 2:45–3:20 (35 sn)

**Ekran:** Aşağı kaydırın, **Burak Demir** satırına tıklayın → "Ölçülen bölge" paneli.

> "Peki 'ölçtük' derken ne demek istiyoruz? Bakın.
>
> Solda Burak'ın içeriği, sağda Ceyda'nın gönderisi. **Parlak kalan** bölge, ölçümle o
> kaynaktan geldiği **doğrulanmış** piksel alanı. Griye düşen yerler Burak'tan gelmiyor.
>
> Sağ altta yazıyor: ölçülen kullanılan alan **yüzde on iki virgül beş.** Burak'ın
> gönderide toplam görünen oranı yüzde doksan dokuz virgül yedi — ama bunun büyük kısmı
> zaten Ayşe'den geliyor. Her tarafa yalnızca **kendi kattığı** pikseller yazılıyor, yoksa
> aynı emek iki kez ödüllendirilirdi."

**Yönerge:** Maskeli görsele yakınlaşın. "Kaynaktan gelen bölgeyi vurgula" onay kutusunu bir kez
kapatıp açın — farkı izleyici görsün.

---

## Sahne 6 — Zincir · 3:20–3:40 (20 sn)

**Ekran:** Aşağı kaydırın, Atıf zinciri paneli.

> "Zincirin tamamı burada. Ayşe'den Burak'a yüzde seksen yedi, Burak'tan Ceyda'ya
> yüzde yüz. Ok yönü türetme yönü. Kesikli bir çizgi görürseniz, o bağ henüz
> onaylanmamış demektir — sistem 'sahibi budur' demiyor, kanıtıyla birlikte **öneri**
> sunuyor."

**Yönerge:** Rozetler tam sayıya yuvarlanıyor; Burak → Ceyda bağının ölçülen değeri
%99,7, rozette **%100** görünüyor. Ekranda ne yazıyorsa o okunur. Jüri sorarsa ondalıklı
değer Emek Kartı'ndaki "toplam görünen %99,7" satırında duruyor.

---

## Sahne 7 — İtiraz · 3:40–4:05 (25 sn)

**Ekran:** Ayşe'nin satırına dönün, "Yeniden ölçüm iste" düğmesini gösterin. **Tıklamayın.**

> "Katılmıyorsanız itiraz edebilirsiniz. İtiraz, bağı daha hassas bir dedektörle yeniden
> ölçtürüyor. Sonuç değişirse zincirin **tüm payları** güncelleniyor.
>
> Dikkat edin: bu düğme yalnızca Ayşe'nin satırında var. İtirazı yalnızca payın sahibi
> açabilir; başkası denerse sunucu reddediyor.
>
> Ölçüm yine sonuç veremezse karar insana bırakılıyor. Sistem karar veremediği yeri
> gizlemiyor."

> **Yönerge:** İtirazı gerçekten göndermeyin — demo verisindeki payları değiştirir ve
> sonraki çekimlerde sayılar tutmaz. Göstermek isterseniz en sona bırakın.

---

## Sahne 8 — Kaynak Bul: hiç görülmemiş dosya · 4:05–4:35 (30 sn)

**Neden bu sahne var.** Video, salonda canlı demo arızalanırsa oynatılacak yedek. Canlı
demonun en güçlü anı da bu: sistem hiç görmediği bir türevde kaynağı buluyor, ilgisiz bir
fotoğrafta ise bağ önermiyor. Önceki sahnelerin hepsi kayıtlı içerik gösteriyordu; hattın
jürinin gözü önünde çalıştığı tek yer burası. Kaynak Bul kayıt yapmaz (`POST /api/verify`),
yani kayıt sırasında demo verisi değişmez.

**Ekran:** Üst menüden **Kaynak bul** → dosya seç → `data/demo/kaynak-bul-turev.jpg` →
**Kökeni çöz**.

> "Şimdiye kadar gördükleriniz sistemde kayıtlı içeriklerdi. Bir de sistemin hiç görmediği
> bir dosyayı deneyelim: Ayşe'nin fotoğrafından kırpılmış, üstüne yazı eklenmiş."

**Aksiyon:** Sonuç gelince (~0,4 sn) önce aşama çizelgesini, sonra Sabah ışığı satırındaki
"kullanılan alan"ı fareyle gösterin.

> "Kaynak bulundu: Ayşe'nin fotoğrafı, Sabah ışığı. Kullanılan alan **yüzde doksan üç**. Filigran ve
> parmak izi burada da düştü; görsel benzerlik ve geometri taşıdı."

**Ekran:** Aynı sayfada `data/demo/kaynak-bul-ilgisiz.jpg` → **Kökeni çöz**.

> "Şimdi de sistemde hiçbir kaynağı olmayan bir fotoğraf.
>
> **Kaynak bulunamadı.** Bulamadığında uydurmuyor: yanlış bir atıf, kaçırılmış bir
> atıftan daha ağır."

**Yönerge:** Türev dosyada listede ikinci bir satır daha çıkar: Bulduğum kare, %67,9.
Ceyda'nın gönderisi de Ayşe'nin piksellerini taşıdığı için bu doğru bir sonuç; replikte
değinilmez, jüri sorarsa cevap canlı demo bölümündeki soru tablosunda. Sayılar 18 Eylül
sabahı ölçüldü (`demo_hazirla.py`: Sabah ışığı %93,0 · Bulduğum kare %67,9, ilgisizde
0 kaynak); sahneden önce yine betiğin çıktısından okunur.

---

## Sahne 9 — Marka tarafı · 4:35–4:55 (20 sn)

**Ekran:** Kampanyalar sayfası.

> "Marka tarafında da aynı mantık. Elli bin liralık ödül havuzu, son paylaşana değil,
> ölçülmüş katkıya göre zincirin tamamına bölünüyor.
>
> Bu kampanyada Ayşe otuz dört bin beş yüz kırk bir lira aldı — **bir** içerik yükleyip
> hiç remix yapmadan. Çünkü içeriği zincirde yaşıyor ve bu ölçüldü."

---

## Sahne 10 — Kapanış · 4:55–5:00 (5 sn)

**Ekran:** Akış sayfasına dönün.

> "N-Emek. Emek görünür olsun diye — tahminle değil, ölçümle."

---

---

## Okuma metni — tek parça, zaman kodlu

Kayıt sırasında sahneler arasında gezinmemek için replikler burada tek akış hâlinde.
Sayılar 17 Eylül'de çalışan sistemden doğrulandı; **köşeli parantezler okunmaz**, ekran
hareketidir. Tempo dakikada ~140 kelime.

**[0:00 · Akış sayfası, sakin bir kaydırma. Ekran hareketi az olsun.]**

> Bir fotoğraf çekiyorsunuz. Biri onu kırpıp üstüne yazı ekliyor. Bir başkası o hâlinin
> ekran görüntüsünü alıp paylaşıyor. Üçüncü paylaşımda içerik binlerce kez görülüyor,
> marka sponsorluğu geliyor — ve sizin adınız hiçbir yerde yok.
>
> Sorun kötü niyet değil: zincir teknik olarak kopuyor. Ekran görüntüsü, içeriğin
> kimliğini tek tıkla siliyor.

**[0:25 · En üstteki üç kartın üzerinde sırayla durun.]**

> N-Emek, bu zinciri geri kuran bir emek katmanı. Ayırt edici yanı şu: kaynağı bulmakla
> yetinmiyor, o kaynağın türev içerikte ne kadar kullanıldığını ölçüyor.
>
> Akışın en üstündeki üç gönderi aslında tek bir zincir: Ayşe'nin fotoğrafı, Burak'ın
> remixi, Ceyda'nın paylaşımı.

**[0:50 · "Bulduğum kare" → Emek Kartı → Köken paneli. "Yüklenen dosyada kimlik yoktu"
alanını fareyle işaret edin.]**

> Ceyda'nın paylaştığı bu içerik sisteme "kaynağı yokmuş" gibi girdi. Ekran görüntüsü
> alındığı için içerik kimliği silinmişti.
>
> Panelde yazan tam olarak bu: yüklenen dosyada kimlik yoktu. Ama sistem kaynağı yine de
> buldu — üstelik iki tanesini.
>
> Nasıl? Sırayla denedi: içerik kimliği yok, dosya özeti tutmuyor, filigran okunamıyor —
> ekran görüntüsü onu da götürmüş. Sonra görüntü parmak izi Burak'ın gönderisini
> yakaladı, görsel benzerlik modeli Ayşe'ye kadar indi, ve son adımda geometrik doğrulama
> ikisini de piksel piksel ölçtü.
>
> Hattın beş aşaması tam bunun için var: biri düşünce diğeri taşıyor.

**[Güven rozetinde bir saniye durun.]**

> Güven: sıfır virgül doksan sekiz.

**[1:45 · Pay dağılımı. Ayşe Yılmaz satırına tıklayıp açın.]**

> Gönderi dört bin iki yüz lira kazandı. Kart bunu kime, neden verdiğini gösteriyor.
>
> Ayşe zincirde iki adım geride ama en büyük payı o alıyor: yüzde altmış sekiz virgül bir.
> Sebebi ekranda yazıyor.
>
> Satırı açalım. Kapsama yüzde seksen yedi virgül bir — bu tahmin değil, ölçüm.
> Güven sıfır virgül doksan beş. Sönümleme sıfır virgül seksen beş, çünkü zincirde iki
> adım geride.
>
> Ve altındaki satır, bu üç sayıyı nasıl birleştirdiğimizi gösteriyor: pay eşittir
> kapsama çarpı güven çarpı sönümleme.
>
> Hiçbir rakam gerekçesiz gelmiyor.

**[Formül satırının üzerinde iki saniye durun. Videonun en önemli karesi.]**

**[2:45 · Aşağı kaydırın, Burak Demir satırı → "Ölçülen bölge" paneli. Maskeli görsele
yakınlaşın, "Kaynaktan gelen bölgeyi vurgula" kutusunu bir kez kapatıp açın.]**

> Peki "ölçtük" derken ne demek istiyoruz? Bakın.
>
> Solda Burak'ın içeriği, sağda Ceyda'nın gönderisi. Parlak kalan bölge, ölçümle o
> kaynaktan geldiği doğrulanmış piksel alanı. Griye düşen yerler Burak'tan gelmiyor.
>
> Sağ altta yazıyor: ölçülen kullanılan alan yüzde on iki virgül beş. Burak'ın gönderide
> toplam görünen oranı yüzde doksan dokuz virgül yedi — ama bunun büyük kısmı zaten
> Ayşe'den geliyor. Her tarafa yalnızca kendi kattığı pikseller yazılıyor, yoksa aynı
> emek iki kez ödüllendirilirdi.

**[3:20 · Aşağı kaydırın, Atıf zinciri paneli.]**

> Zincirin tamamı burada. Ayşe'den Burak'a yüzde seksen yedi, Burak'tan Ceyda'ya yüzde
> yüz. Ok yönü türetme yönü. Kesikli bir çizgi görürseniz, o bağ henüz onaylanmamış
> demektir — sistem "sahibi budur" demiyor, kanıtıyla birlikte öneri sunuyor.

**[3:40 · Ayşe'nin satırına dönün, "Yeniden ölçüm iste" düğmesini gösterin. TIKLAMAYIN.]**

> Katılmıyorsanız itiraz edebilirsiniz. İtiraz, bağı daha hassas bir dedektörle yeniden
> ölçtürüyor. Sonuç değişirse zincirin tüm payları güncelleniyor.
>
> Dikkat edin: bu düğme yalnızca Ayşe'nin satırında var. İtirazı yalnızca payın sahibi
> açabilir; başkası denerse sunucu reddediyor.
>
> Ölçüm yine sonuç veremezse karar insana bırakılıyor. Sistem karar veremediği yeri
> gizlemiyor.

**[4:05 · Üst menüden Kaynak bul → `kaynak-bul-turev.jpg` → Kökeni çöz.]**

> Şimdiye kadar gördükleriniz sistemde kayıtlı içeriklerdi. Bir de sistemin hiç görmediği
> bir dosyayı deneyelim: Ayşe'nin fotoğrafından kırpılmış, üstüne yazı eklenmiş.

**[Sonuç gelince aşama çizelgesini, sonra "kullanılan alan"ı fareyle gösterin.]**

> Kaynak bulundu: Ayşe'nin fotoğrafı, Sabah ışığı. Kullanılan alan yüzde doksan üç. Filigran ve parmak
> izi burada da düştü; görsel benzerlik ve geometri taşıdı.

**[Aynı sayfada `kaynak-bul-ilgisiz.jpg` → Kökeni çöz.]**

> Şimdi de sistemde hiçbir kaynağı olmayan bir fotoğraf.
>
> Kaynak bulunamadı. Bulamadığında uydurmuyor: yanlış bir atıf, kaçırılmış bir atıftan
> daha ağır.

**[4:35 · Kampanyalar sayfası.]**

> Marka tarafında da aynı mantık. Elli bin liralık ödül havuzu, son paylaşana değil,
> ölçülmüş katkıya göre zincirin tamamına bölünüyor.
>
> Bu kampanyada Ayşe otuz dört bin beş yüz kırk bir lira aldı — bir içerik yükleyip hiç
> remix yapmadan. Çünkü içeriği zincirde yaşıyor ve bu ölçüldü.

**[4:55 · Akış sayfasına dönün.]**

> N-Emek. Emek görünür olsun diye — tahminle değil, ölçümle.

## Anlatım notları

- **Tempo:** dakikada ~140 kelime. Yukarıdaki metin bu tempoya göre yazıldı.
- **Sayıları okurken yavaşlayın.** "Yüzde seksen beş virgül iki" acele okunursa
  anlaşılmıyor.
- **Fare imleci anlatımı takip etsin.** Söylediğiniz şeyin üzerinde durun; rastgele
  gezinmeyin.
- **Sessizlik iyidir.** Sahne geçişlerinde yarım saniye boşluk bırakın.

## Süre daraltma (3 dakikaya inmek gerekirse)

Şu sırayla kısaltın — en az değer kaybettiren üstte:

1. Sahne 6 (zincir) → 20 sn yerine 10 sn
2. Sahne 9 (marka) → 20 sn yerine 12 sn
3. Sahne 1 (problem) → 25 sn yerine 15 sn

**Kaynak Bul (Sahne 8) kısaltılmaz:** videodaki tek canlı sorgu ve canlı demonun yedeği.

**Asla kısaltmayın:** Sahne 4 (payın gerekçesi) ve Sahne 5 (ölçüm görünür). Projenin
ayırt edici iddiası bu iki sahnede.

## Sunuma gömülecek ≤60 saniyelik kesit

Yukarıdaki 3 dakikalık daraltmadan farklı, daha sert bir kesim: sunum dosyasına
gömülecek klip yalnızca projenin ayırt edici anını göstermeli, tüm akışı değil.

Kullanılacak sahneler, olduğu gibi (toplam ~55 sn):
- **Sahne 3** (kritik an: kimliği silinmiş içerik) — kısaltılmadan, tam 55 sn.

Süre 60 sn'yi aşarsa, Sahne 3'ün yalnızca "kritik an" cümlesinden sonrasını (kaynağın
bulunduğu ve güven skorunun göründüğü an) alın; giriş kısmını (ekran görüntüsü alma
adımı) atlayabilirsiniz. Sahne 4/5 (payın gerekçesi, ölçüm görünür) bu kesite girmez —
onlar canlı prototip gösteriminde anlatılır, videoda tekrar edilmez.

## Videoda söylenmemesi gerekenler

| Söylemeyin | Neden |
|---|---|
| "Yapay zekâ kaynağı buluyor" | Model aday üretiyor, kararı geometrik ölçüm veriyor |
| "Sistem sahibini buluyor" | Sistem öneri sunuyor; bu ayrım projenin etik omurgası |
| "%100 doğru" | Ölçülen Top-1 %98,7; yanlış atıf %0,86 — rakamı olduğu gibi söyleyin |
| "Blokzincir" | Projede yok |

## Kayıt sonrası

- [ ] Ses seviyesi eşitlenmiş, nefes sesleri temizlenmiş
- [ ] Ekrandaki her sayı anlatılanla **birebir** aynı
- [ ] Altyazı eklendi (jüri sessiz izleyebilir)
- [ ] Süre ~5 dakika; 5:30'u geçerse yukarıdaki daraltma sırası uygulanır
