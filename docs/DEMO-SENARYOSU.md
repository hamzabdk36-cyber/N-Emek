# Demo Videosu — Çekim Senaryosu

**Hedef:** 4 dakika 30 saniye, Türkçe anlatım, ekran kaydı.
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

Bu yüzden burada iki çıktı üretilir: tam **4:30** sürüm (madde 2 ve 3 için) ve aşağıdaki
"Süre daraltma" bölümünden türetilen **≤60 sn'lik kısa kesit** (madde 1 için).

## Durum notu (15 Eylül)

**Sıra.** Transkripte göre jüri günü akışı *15 dk sunum → kısa soru-cevap → jüri
"prototipi gösterebilirsiniz" deyince 2–3 dk canlı gösterim*, kendi bilgisayarımızdan.
Gösterim sunumun sonunda; süre "15 artı 2 gibi" ve değişebilir. Sunum PDF olarak teslim
edildiği için ≤60 sn'lik klibin sunuma gömülmesi pratikte mümkün değil (PDF video
oynatmaz); video yalnızca yedek ve teslimat kalemi olarak kalıyor.

**Görev.** Sunumu Berra Özer, sistemi ve canlı demoyu Hamza Budak üstleniyor. Canlı
demonun biçimi seçildi: **"canlı kanıt"** — bir sonraki bölüm. Ondan sonraki sahneler
4:30'luk video içindir.

**Bu belgedeki sayılar eski.** Ekrandakiyle karşılaştırma (yerel `data/nemek.db`,
15 Eylül okuması):

| Sahne | Bu belgede | Yerel demo veritabanı | Sunum sayfası |
|---|---|---|---|
| 4 · Ayşe kapsama | %85,2 | %87,1 | %87,2 (5. sayfa) |
| 4 · Ayşe payı | %68,1 | %68,1 · ₺2.574,63 | %68,2 · ₺2.576,30 |
| 5 · Burak ölçülen alan | %12,2 | %12,5 | %12,5 |
| 6 · Burak → Ceyda bağı | %97 | 0,9965 | — |
| 6 · Ayşe → Burak bağı | %87 | 0,8743 | — |
| 8 · Ayşe kampanya toplamı | "34.500" | ₺34.541,45 | ₺34.548,96 (10. sayfa) |

Güven 0,98 her üçünde aynı. Farkın sebebi, demo verisinin her `seed_demo.py --reset`
koşusunda yeniden ölçülmesi; ekran görüntüleri büyük olasılıkla Docker birimindeki
veritabanından çekildi (15 Eylül'de Docker kapalıydı, doğrulanmadı). Replikler, jüri
günü kullanılacak veritabanı seçilip dondurulduktan sonra ondan okunarak güncellenecek.
O veritabanı seçildikten sonra salonda `--reset` ya da `docker compose down -v`
çalıştırılmaz: ikisi de demo verisini yeniden ölçer ve sayılar yine kayar.

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

```bash
.venv/Scripts/python.exe -m uvicorn app.main:app --app-dir backend   # :8000, --reload YOK
cd frontend && npm run dev                                           # :5173
.venv/Scripts/python.exe scripts/demo_hazirla.py                     # "Hazır" yazmalı
```

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
| 0:00–0:10 | **Akış** | "Üç gönderi, tek zincir: Ayşe'nin fotoğrafı, Burak'ın remixi, Ceyda'nın ekran görüntüsü." |
| 0:10–0:35 | "Bulduğum kare" → **Emek Kartı**, Köken paneli | "Ceyda'nın dosyasında içerik kimliği yoktu. Sistem kaynağı yine de buldu; güveni ekranda." |
| 0:35–1:00 | Pay dağılımında **Ayşe** satırını aç | "Ayşe iki adım geride ama en büyük pay onun. Satırda kapsama, güven ve sönümleme; altındaki satır üçünün çarpımı." Sayıları **ekrandan okuyun**. |
| 1:00–1:20 | **Burak** satırı → ölçülen bölge, "Kaynaktan gelen bölgeyi vurgula" kutusunu kapat/aç | "Parlak kalan pikseller ölçümle Burak'tan geldiği doğrulanan bölge. Burak'a yalnızca kendi kattığı alan yazılıyor." |
| 1:20–1:45 | **Kaynak bul** → `kaynak-bul-turev.jpg` → Kökeni çöz | "Bu dosyayı sistem hiç görmedi: Ayşe'nin fotoğrafından kırpılıp üstüne yazı eklendi. Şimdi hattı çalıştırıyorum." Sonuç gelince: "Kaynak bulundu, kullanılan alan ölçüldü." |
| 1:45–1:55 | Aynı ekranda `kaynak-bul-ilgisiz.jpg` → Kökeni çöz | "Bu fotoğrafın sistemde hiçbir kaynağı yok." Sonuç: **"Kaynak bulunamadı."** "Bulamadığında uydurmuyor." |
| 1:55–2:00 | — | "Emek görünür olsun diye: tahminle değil, ölçümle." |

15 Eylül yerel ölçümünde türev dosyası iki kaynak verdi: Sabah ışığı %93,0 ve
Bulduğum kare %67,9 kullanılan alan. Bulduğum kare de Ayşe'nin piksellerini taşıdığı için
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
| "Kendi görselimizle deneyelim" | Kaynak bul'a jürinin görselini yükle; kayıt yapmaz. Sistemde olmayan bir görselse beklenen sonuç "kaynak bulunamadı". |
| "Yükleme / remix de gösterin" | Remix Stüdyo çalışır ama demo verisini değiştirir. Yapılırsa demo sonrasında `data/` yedeği geri yüklenir. |

### Bir şey ters giderse

| Belirti | Hamle |
|---|---|
| "Hat çalışıyor…" 5 sn'den uzun sürüyor | Beklemeyi bırak, Emek Kartı sekmesine dön: "Bu adımı az önce denetledik; asıl ölçüm burada görünüyor." |
| Bir ekran hata veriyor | Başka bir ekrana geç. Hata sınırı başlığı ve gezinmeyi ayakta tutuyor. |
| Sayfalar hiç yüklenmiyor | Yedek terminalde backend'i yeniden başlat. 30 sn içinde gelmezse `docs/gorseller/` kareleri (02 → 03 → 04 → 06) üzerinden anlat ve durumu açıkça söyle. |
| Projeksiyon düşük çözünürlükte, mobil düzen açıldı | Devam et; düzen bilerek duyarlı. Gerekirse tarayıcı yakınlaştırmasını düşür. |

### Sahnede yapılmayacaklar

- Akışa içerik yüklemek, itiraz göndermek, kampanya dağıtmak, içerik silmek
- `seed_demo.py --reset`, `docker compose down -v`, backend'i `--reload` ile çalıştırmak
- API'yi `localhost` ile çağırmak: Windows'ta istek başına ~2 sn ekliyor, `127.0.0.1` kullanılır

### Henüz açık

- Jüri günü veritabanı seçilip dondurulmadı (yukarıdaki durum notu).
- Wi-Fi kapalı prova yapılmadı. CLIP ağırlıkları önbellekte olsa da model yüklenirken
  ağa çıkma denemesi olabilir; `HF_HUB_OFFLINE=1` ile sınanmalı.
- Yedek terminaldeki yeniden başlatmanın süresi ölçülmedi.

### Kalan iş: demo verisini zenginleştirme (onaylandı, uygulanmadı — 15 Eylül)

**Neden.** İndekste yalnızca altın senaryonun 3 içeriği var. Canlı Kaynak Bul sorgusu bu
yüzden zayıf bir kanıt ("üç görselin içinden bulmak kolay"); akış da üç gönderiyle
geliştirici demosu gibi duruyor. **Ön koşul:** önce jüri günü veritabanı (yerel ya da
Docker) seçilir; betik o veritabanında çalıştırılır.

**Değişmemesi gerekenler:**
- altın senaryonun Emek Kartı sayıları
- kampanya dağıtımı (sunumun 10. sayfası ₺34.548,96)
- `demo_hazirla.py`'nin "ilgisiz görselde bağ yok" sonucu

Uygulama koduna, `seed_demo.py`'ye ve testlere dokunulmaz.

**Plan: yeni betik `scripts/demo_zenginlestir.py`.** `seed_demo.py` kalıbında, süreç içinde
çalışır; `--reset` ve `drop_all` yok.

1. **Ön koşullar.** Biri tutmazsa betik durur.
   - Backend kapalı olmalı: `127.0.0.1:8000/api/health` yanıt veriyorsa betik çalışmaz.
   - Altın senaryonun üç başlığı veritabanında bulunmalı.
   - Eklenecek kullanıcı kimlikleri zaten varsa "zaten eklenmiş" deyip çıkar; iki kez çalıştırmak bir şey değiştirmez.
   - Korpusta yeterli görsel olmalı.
2. **Yedek.** `data/nemek.db`, `data/uploads/` ve `data/index/` klasörleri
   `data/yedek/<zaman>/` altına kopyalanır; `.gitignore`'a `data/yedek/` eklenir.
3. **Karşılaştırma için önceden kaydedilenler.**
   - bağ sayısı
   - her bağın kapsama ve güven değeri
   - `Payout` sayısı ve toplam tutar
   - Ceyda'nın Emek Kartı'ndaki pay satırları (`build_labour_card`)
4. **Kullanıcılar.** 2–3 kurgusal kullanıcı, rolleri `user`; moderatör yalnızca Ceyda kalır.
   Kimlik renkleri temanın anlam renklerinden ve mevcut mor/turkuaz/pembeden ayrık seçilir.
5. **Aday görseller.** `sorted(data/raw/*.jpg)` sırasından alınır; iki sıra hariç tutulur:
   - sıra 3: altın senaryonun kaynağı
   - sıra 10: `demo_hazirla.ILGISIZ_SIRA`, sahnedeki ilgisiz görsel

   Her aday yüklemeden önce `recovery.recover` ile sorgulanır. Bağ çıkan aday atlanır;
   böylece yeni içerik ne altın zincire ne de birbirine bağlanır. Varsayılan hedef 20 içerik
   (`--adet`).
6. **Yükleme.** `ingest(..., campaign_id=None)` ile yapılır. Gelir 0 kalır, dağıtım
   çağrılmaz. Başlıklar nötr ve tam imlalı Türkçe ("Günün karesi", "Arşivden" gibi).
7. **Akış sırası.** Akış `created_at` alanına göre en yeniden eskiye sıralı. Yeni içeriklerin
   tarihi Ayşe'nin gönderisinden `i+1` saat önceye çekilir, böylece altın üçlü en üstte kalır.
8. **Sonra doğrulama.** Biri tutmazsa betik yedeği geri yükleyip durur.
   - 3. adımdaki değerler birebir aynı olmalı.
   - Yeni içeriklerde hiç bağ olmamalı.
   - İndeks anlık görüntüsü güncellenir.
   - Özet basılır.

**Doğrulama sırası:**
1. Önce veritabanı kopyasında, sonra gerçek veritabanında çalıştırılır.
2. Backend başlatılır, `demo_hazirla.py` yeniden çalıştırılır; "Hazır" yazmalı.
3. `/api/feed` sonucunun ilk üçü altın senaryo olmalı; `indexed_contents` = 3 + eklenen.
4. Betik ikinci kez çalıştırılır; "zaten eklenmiş" deyip çıkmalı.
5. `pytest -m "not slow"` ve `dokuman_denetimi.py` çalıştırılır.
6. Arayüzde gözle bakılır: akış, kullanıcı seçici, Emek Kartı ve Kampanyalar.

**Sonrasında güncellenecek belgeler:**
- `CLAUDE.md`: betik listesi.
- Bu belge: tek seferlik hazırlık adımı, "indekste N içerik" repliği, jüri sorusu "bu
  içerikler ne?" ve video kontrol listesindeki `indexed_contents: 3`.
- `docs/SUNUM/_PLAN.md`: 9. sayfadaki akış görüntüsü üç gönderi gösteriyor; yenilenip
  yenilenmeyeceği Berra'nın kararı.

**Docker notu.** Docker 24 görsel indiriyor; 20 ilgisiz içerik için yetmez.
`NEMEK_CORPUS_COUNT` artırılır ya da hedef adet düşürülür.

---

## Çekim öncesi kontrol listesi

Demonun canlı çökmesi, videonun kendisinden daha pahalıya mal olur.

```bash
docker compose up --build -d          # iki kapsayıcı da "healthy" olana kadar bekleyin
curl -s http://localhost:8000/api/health
```

- [ ] `indexed_contents: 3` ve `c2pa_signing: true` dönüyor mu
- [ ] `http://localhost:5173` açılıyor, akışta **üç** gönderi var
- [ ] Üstteki kullanıcı seçici **Ayşe Yılmaz**'da (itiraz sahnesi buna bağlı)
- [ ] "Bulduğum kare" gönderisinin geliri **₺4.200** — değiştiyse Gelir kutusundan geri alın
- [ ] Tarayıcı tam ekran, yer imleri çubuğu kapalı, bildirimler susturulmuş
- [ ] Ekran çözünürlüğü 1920×1080, tarayıcı yakınlaştırması **%100**
- [ ] Kayıt öncesi bir prova turu atın: fare hareketleri yavaş ve kararlı olmalı

> **Kritik:** Kayıt sırasında yeni içerik yüklemeyin. Yükleme zinciri değiştirir ve
> aşağıdaki bütün sayılar kayar. Yükleme göstermek isterseniz en sona bırakın.

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

**Ekran:** Akış sayfasındaki üç kart sırayla vurgulanır (fareyle üzerlerinde durun).

> "N-Emek, bu zinciri geri kuran bir emek katmanı. Ayırt edici yanı şu: kaynağı
> **bulmakla** yetinmiyor, o kaynağın türev içerikte **ne kadar** kullanıldığını
> ölçüyor.
>
> Ekranda gördüğünüz üç gönderi aslında tek bir zincir: Ayşe'nin fotoğrafı, Burak'ın
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
> Nasıl? Sırayla denedi: içerik kimliği yok, dosya özeti tutmuyor. Sonra piksellere
> gömülü görünmez filigranı okudu, görüntü parmak izi ve görsel benzerlikle adayları
> daraltı, ve son adımda geometrik olarak doğruladı.
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
> Satırı açalım. **Kapsama yüzde seksen beş virgül iki** — bu tahmin değil, ölçüm.
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
> Solda Burak'ın içeriği, sağda Ceyda'nın gönderisi. Yeşil alan, ölçümle o kaynaktan
> geldiği **doğrulanmış** piksel bölgesi. Kararan yerler Burak'tan gelmiyor.
>
> Sağ altta yazıyor: ölçülen kullanılan alan **yüzde on iki virgül iki.** Burak'ın
> gönderide toplam görünen oranı yüzde doksan yedi — ama bunun büyük kısmı zaten
> Ayşe'den geliyor. Her tarafa yalnızca **kendi kattığı** pikseller yazılıyor, yoksa
> aynı emek iki kez ödüllendirilirdi."

**Yönerge:** Maskeli görsele yakınlaşın. "Kaynaktan gelen bölgeyi vurgula" onay kutusunu bir kez
kapatıp açın — farkı izleyici görsün.

---

## Sahne 6 — Zincir · 3:20–3:40 (20 sn)

**Ekran:** Aşağı kaydırın, Atıf zinciri paneli.

> "Zincirin tamamı burada. Ayşe'den Burak'a yüzde seksen yedi, Burak'tan Ceyda'ya
> yüzde doksan yedi. Ok yönü türetme yönü. Kesikli bir çizgi görürseniz, o bağ henüz
> onaylanmamış demektir — sistem 'sahibi budur' demiyor, kanıtıyla birlikte **öneri**
> sunuyor."

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

## Sahne 8 — Marka tarafı · 4:05–4:25 (20 sn)

**Ekran:** Kampanyalar sayfası.

> "Marka tarafında da aynı mantık. Elli bin liralık ödül havuzu, son paylaşana değil,
> ölçülmüş katkıya göre zincirin tamamına bölünüyor.
>
> Bu kampanyada Ayşe otuz dört bin beş yüz lira aldı — **bir** içerik yükleyip hiç remix
> yapmadan. Çünkü içeriği zincirde yaşıyor ve bu ölçüldü."

---

## Sahne 9 — Kapanış · 4:25–4:30 (5 sn)

**Ekran:** Akış sayfasına dönün.

> "N-Emek. Emek görünür olsun diye — tahminle değil, ölçümle."

---

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
2. Sahne 8 (marka) → 20 sn yerine 12 sn
3. Sahne 1 (problem) → 25 sn yerine 15 sn

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
- [ ] Süre 3–5 dakika aralığında
