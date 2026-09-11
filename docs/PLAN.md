# N-Emek — TEKNOFEST 2026 NSosyal İnovasyon Yarışması Prototip Planı

## Context

Takım, TEKNOFEST 2026 NSosyal İnovasyon Yarışması'na **İçerik Ekonomisi** kategorisinde "N-Emek: Açıklanabilir İçerik Atıf ve Adil Gelir Paylaşım Sistemi" projesiyle ön başvuru yaptı. Şartname, fikir düzeyinde kalmayı açıkça reddediyor: "Katılımcılar, geliştirdikleri projeyi yalnızca fikir düzeyinde bırakmayıp **çalışan bir prototip** ile desteklemelidir."

Bu proje, takımın elektronik harp (Zenith EH) çalışmasından **tamamen bağımsız** yürütülecek; ayrı klasör, ayrı git deposu, ayrı doküman seti. Amaç ödül (250.000 ₺ birincilik) ve puanı maksimize etmek.

### Şartnameden çıkan sert kısıtlar

| Tarih | Aşama | Bugünden (8 Ağu 2026) |
|---|---|---|
| 20 Ağu 2026 | Son başvuru (tamamlandı) | — |
| **24 Ağu 2026, 17:00 TSİ** | **Teknik Rapor teslimi (KYS)** | **16 gün** |
| 2 Eyl 2026 | Teknik rapor sonuçları | |
| ~~2–7 Eyl 2026~~ **12 Eyl 2026, 13:00** | Mentörlük — ilk görüşme (kaydı: bkz. `docs/MENTORLUK.md`) | |
| **14 Eyl 2026, 17:00 TSİ** | **Final sunumu + prototip teslimi** | **37 gün** |
| **20 Eyl 2026** | Jüri ve katılımcılara canlı sunum | |
| 30 Eyl – 4 Eki 2026 | TEKNOFEST Şanlıurfa | |

Rapor şablona uygun değilse veya geç yüklenirse **doğrudan eleme**. Şablon KYS'de yayımlanıyor — takım kaptanı indirmeli.

### İçerik Ekonomisi puan ağırlıkları (planın önceliklerini bu belirledi)

| Kriter | Ağırlık |
|---|---|
| Yenilikçilik ve Özgünlük | %20 |
| Teknik Yeterlilik ve Uygulanabilirlik | %20 |
| Problemi Çözme Başarısı | %20 |
| **Kullanıcı Deneyimi (UI/UX)** | **%20** |
| Sunum ve Prototip Kalitesi | %10 |
| İş Modeli ve Sürdürülebilirlik | %10 |

UI/UX, AI motoruyla eşit ağırlıkta. Arayüz "geliştirici demosu" gibi görünürse puanın beşte biri gider.

### Şartnamenin istediği teslimat listesi (14 Eylül'e kadar hepsi)

Teknik rapor · sunum dosyası · kullanıcı senaryoları · çalışan prototip · kaynak kod · demo videosu · iş ve gelir modeli dokümanı · YZ mimarisi dokümanı · veri-model-etik-performans dokümanı · UI/UX tasarımları · kullanıcı akışları · kullanıcı araştırması özeti · kullanılabilirlik testi sonuçları · erişilebilirlik değerlendirmesi.

### Ortam

- Makine: RTX 3050 Laptop (4 GB VRAM), 12 çekirdek CPU, Windows 11, Python 3.13, Node 24
- Kod yazımı ağırlıklı olarak Claude'da; takım yönlendirme, test, tasarım ve içerik kararları veriyor
- Konum: `C:\Users\HAMZA\Desktop\N-Emek` (yeni git deposu)

---

## Ürün: Ne inşa ediyoruz

**N-Emek**, N'Sosyal'e takılacak bir "emek katmanı". Prototip iki parçadan oluşur:

1. **Mini N'Sosyal istemcisi** — gerçek platform API'si olmadığı için akışı, yükleme ve remix stüdyosunu içeren bir demo sosyal medya arayüzü. Bu, N'Sosyal'i taklit eden bir kopya değil; N-Emek'in entegre edileceği ana platformu temsil eden referans istemci.
2. **N-Emek motoru** — atıf, köken kurtarma, katkı payı hesabı, açıklanabilirlik, itiraz ve gelir dağıtımı.

### Jüriye gösterilecek altın senaryo (canlı demo, ~4 dakika)

1. **Ayşe** orijinal bir fotoğraf yükler → sistem C2PA manifesti imzalar, algısal parmak izi + görsel embedding çıkarır, görünmez filigran gömer.
2. **Burak** bu gönderiyi remixler: kırpar, üstüne yazı ve kendi çizimini ekler → türev içerik, C2PA'da `ingredient` + `actions` ile Ayşe'ye bağlanır. Zincir grafiğinde iki düğüm görünür.
3. **Ceyda**, Burak'ın içeriğini ekran görüntüsüyle alır, yeniden sıkıştırır, tekrar kırpar — **C2PA tamamen silinir**. Sisteme "kaynağı yok" gibi girer.
4. **Kritik an:** N-Emek köken kurtarma hattını çalıştırır. pHash + CLIP + yerel özellik eşleme ile Burak'ı **ve** Ayşe'yi bulur; ekranda eşleşen bölge maskeyle vurgulanır, güven skoru ve her aşamanın kanıtı gösterilir.
5. Marka kampanyası 50.000 ₺ ödül havuzu koymuştur. **Emek Kartı** açılır: "Bu içerik 4.200 ₺ kazandı. Ceyda 1.850 ₺, Burak 1.430 ₺, Ayşe 500 ₺, N'Sosyal 420 ₺." Her rakamın altında gerekçesi yazar — kullanılan alan oranı, eklenen özgün unsur, zincir sönümleme katsayısı, kampanya taban kuralı.
6. **Ayşe itiraz eder:** payının düşük olduğunu, orijinalin daha geniş kullanıldığını söyler ve kanıt olarak RAW dosyasını + C2PA'lı orijinali yükler. Sistem yeniden hesaplar, pay güncellenir, dağıtım tekrar yapılır. Çözülmezse insan inceleme kuyruğuna düşer.

Bu senaryo, projenin başvuru metnindeki her iddiayı tek akışta kanıtlar.

---

## Mimari

```
N-Emek/
├─ backend/                    FastAPI + SQLite
│  ├─ app/
│  │  ├─ api/                  routers: content, remix, attribution, payout, dispute, campaign
│  │  ├─ core/                 config, güvenlik, imzalama anahtarları
│  │  ├─ models/               SQLAlchemy: Content, Edge, Manifest, Claim, Payout, Dispute, Campaign
│  │  ├─ provenance/           ← projenin kalbi
│  │  │  ├─ c2pa_service.py    manifest oluştur / imzala / doğrula
│  │  │  ├─ watermark.py       görünmez filigran (DWT-DCT) göm/çıkar
│  │  │  ├─ fingerprint.py     pHash/dHash/wHash + kripto hash
│  │  │  ├─ embedding.py       CLIP ViT-B/32 (CUDA) embedding
│  │  │  ├─ index.py           FAISS indeksleri (embedding) + BK-tree (pHash)
│  │  │  ├─ geometry.py        ORB/SIFT + RANSAC homography → kullanılan alan oranı
│  │  │  └─ recovery.py        5 aşamalı hat + karar füzyonu + kanıt toplama
│  │  ├─ attribution/
│  │  │  ├─ contribution.py    katkı payı formülü (deterministik, açıklanabilir)
│  │  │  ├─ explain.py         Emek Kartı veri üretimi
│  │  │  └─ payout.py          havuz dağıtımı + N'Sosyal komisyonu
│  │  └─ main.py
│  └─ eval/                    değerlendirme seti + saldırı senaryoları + metrik üretimi
├─ frontend/                   React + TypeScript + Vite + Tailwind
│  ├─ src/pages/               Akış, GönderiDetay, RemixStüdyo, EmekKartı, Zincir,
│  │                           KampanyaPaneli, İtiraz, ModeratörKuyruğu, MetrikPaneli
│  └─ src/components/          feed kartı, kanıt satırı, güven rozeti, DAG görünümü
├─ docs/                       teknik rapor, iş modeli, YZ mimarisi, etik, UX araştırması
├─ data/                       CC0 test görselleri + üretilmiş türevler
└─ docker-compose.yml
```

### Köken Kurtarma Hattı (Provenance Recovery) — teknik farkımız

Sıralı aşamalar; her biri kanıt üretir ve erken çıkış yapabilir.

| Aşama | Yöntem | Neye dayanıklı | Güven katkısı |
|---|---|---|---|
| 0 | C2PA manifest doğrulama | — (manifest varsa) | 0.99 |
| 1 | SHA-256 tam eşleşme | bit-birebir kopya | 0.99 |
| 2 | Görünmez filigran çıkarma | yeniden sıkıştırma, hafif kırpma, metadata silme | 0.90 |
| 3 | Algısal hash (pHash 64-bit, BK-tree, Hamming ≤ 12) | ölçekleme, JPEG, renk/parlaklık | 0.55–0.80 |
| 4 | CLIP embedding + FAISS kosinüs | ağır düzenleme, filtre, kolaj, stil değişimi | 0.40–0.75 |
| 5 | ORB/SIFT + RANSAC homography | **kırpma oranını ve geometrik dönüşümü ölçer** | 0.60–0.95 |

Aşama 5 sadece doğrulama değil **ölçüm** yapar: homography matrisinden kaynak görselin hangi bölgesinin, türev içinde hangi alanı kapladığı hesaplanır. Katkı payının "kullanılan içerik oranı" bileşeni buradan gelir — tahmin değil, ölçüm. Jüriye anlatılacak temel teknik iddia bu.

Karar füzyonu: aşama skorları ağırlıklı birleşir → `Yüksek / Orta / Düşük` güven etiketi + hangi aşamanın ne dediğinin listesi. Sistem asla "sahibi budur" demez; **kanıtlı zincir önerisi** sunar (başvuru metnindeki taahhüt).

### Katkı Payı Motoru

Bir türev içerik için, her kaynak `s` başına:

```
pay(s) = normalize(
    w_alan   · A(s)          # homography ile ölçülen kullanılan alan oranı
  + w_kaynak · Kd(s)         # zincir derinliği sönümlemesi: λ^(derinlik-1), λ≈0.5
  + w_güven  · C(s)          # köken güven skoru
) · (1 - Y_özgün) · (1 - komisyon)
```

- `Y_özgün` = son üreticinin eklediği özgün unsur oranı (yeni piksel alanı + eklenen katman sayısı + algısal mesafe)
- Kampanya kuralları üstte uygulanır: kaynak tabanı (min %X), üretici tavanı (max %Y), minimum ödeme eşiği
- Her ara değer veritabanına yazılır → Emek Kartı bunları satır satır gösterir

Formül deterministik ve denetlenebilir; teknik raporda Shapley değeriyle karşılaştırmalı bir doğrulama bölümü eklenerek akademik zemin verilir (Shapley üretimde çok pahalı olduğu için gerekçeli olarak tercih edilmedi denir).

### Emek Kartı (açıklanabilirlik kartı)

Tek ekranda: kaynak ve türev yan yana, eşleşen bölge maskeli; kanıt satırları (C2PA ✓ / pHash mesafesi 6, eşik 12 / ORB 187 eşleşme, %78 inlier / kullanılan alan %41 / eklenen özgün %52 / kampanya tabanı %20); güven rozeti; "İtiraz et" ve "Onayla" butonları. Bu ekran demo videosunun kapak karesi olacak.

### Marka Kampanya Paneli ve iş modeli

Marka ödül havuzu tanımlar, remix kuralları ve süre belirler; kampanya sonunda dağıtım simülasyonu çalışır, N'Sosyal komisyon payını alır. İş modeli dokümanı bu panelden gelen gerçek rakamlarla yazılır (%10 puan kalemi).

### Değerlendirme Paneli — çoğu takımda olmayacak kalem

`eval/` altında 300–500 CC0 görselden otomatik türev üretilir: kırpma %10/%30/%50, JPEG q30/q50, yeniden boyutlandırma, yazı bindirme, filtre, ayna, ±15° döndürme, ekran görüntüsü simülasyonu, kolaj. Ölçülen metrikler: Top-1 kaynak doğruluğu, Precision/Recall, yanlış atıf oranı, aşama başına gecikme, alan oranı ölçüm hatası (MAE). Sonuç tablosu hem teknik rapora hem arayüzdeki metrik paneline girer — "biz gerçekten ölçtük" ifadesi teknik yeterlilik puanının belkemiği.

---

## Teknoloji seçimleri

**Backend:** Python 3.13, FastAPI, SQLAlchemy + SQLite, Pillow, OpenCV (`opencv-contrib-python`), `imagehash`, `faiss-cpu`, PyTorch CUDA + `open_clip_torch` (ViT-B/32; 4 GB VRAM'e rahat sığar), `c2pa-python`, `invisible-watermark`.

**Frontend:** React 19 + TypeScript + Vite, Tailwind CSS, React Flow (zincir DAG'ı), Zustand, Framer Motion (mikro animasyonlar — UI/UX puanı). Remix stüdyosu HTML Canvas üzerinde: kırpma, metin katmanı, çizim, filtre, kolaj.

**Dağıtım:** `docker-compose up` ile tek komut; jüri kendi makinesinde çalıştırabilsin diye README'de üç adımlık kurulum.

### Riskler ve hazır alternatifleri

| Risk | Alternatif |
|---|---|
| `c2pa-python` Windows'ta kurulmazsa | `c2patool` binary'sini alt süreç olarak çağır; o da olmazsa COSE benzeri kendi imzalı JSON manifestimiz (aynı veri modeli, ayrık imzalama servisi) |
| 4 GB VRAM'de PyTorch CUDA sorunu | CLIP'i CPU'da koştur (12 çekirdekte ~150 ms/görsel, demo için yeterli); indeksleme zaten çevrimdışı |
| SIFT patent/paket sorunu | ORB varsayılan, SIFT opsiyonel |
| 16 günde rapor yetişmezse | Faz 2 sonunda rapor için gereken minimum kesit sabittir: senaryo 1-4 + Emek Kartı + metrik tablosu. Faz 4-5 içerikleri rapora girmez, finale girer |

---

## Zaman planı

### Faz 0 — 8–10 Ağustos (3 gün): İskelet ve risk kapatma
- `C:\Users\HAMZA\Desktop\N-Emek` deposu, monorepo iskeleti, `CLAUDE.md`
- Veri modeli ve API sözleşmesi (OpenAPI)
- **Riskli parçaların PoC'si önce:** C2PA imzala/doğrula, CLIP+FAISS indeksleme, ORB+RANSAC homography → alan oranı. Bunlar çalışmazsa alternatiflere burada geçilir.

### Faz 1 — 11–16 Ağustos (6 gün): Çekirdek çalışan hat
- Yükleme + remix stüdyosu (kırp, yazı, çizim, filtre, kolaj)
- 5 aşamalı köken kurtarma hattı, kanıt üretimi dahil
- Katkı payı motoru + Emek Kartı veri katmanı
- Zincir DAG görünümü; akış ve gönderi detay ekranları

### Faz 2 — 17–22 Ağustos (6 gün): Rapor için gereken her şey
- Değerlendirme seti + saldırı senaryoları + metrik tablosu üretimi
- Emek Kartı arayüzü (eşleşen bölge maskesi dahil), güven rozetleri
- Mimari diyagramlar, ekran görüntüleri, senaryo anlatısı
- **Teknik raporun yazımı** (KYS'deki resmî şablona birebir uygun)

### Faz 3 — 23–24 Ağustos: Teslim
- 23 Ağustos: rapor son okuma, şablon uygunluk kontrolü, ekler
- **24 Ağustos 17:00'dan en az 6 saat önce KYS'ye yükleme.** Son gün son saate bırakılmayacak.

### Faz 4 — 25 Ağustos – 22 Ağustos: Ürünleştirme (gerçekleşen)
- İtiraz akışı, moderatör inceleme kuyruğu, kampanya paneli — tamamlandı
- Erişilebilirlik değerlendirmesi (WCAG 2.1 AA) — tamamlandı, on bir kusurun onu düzeltildi
- 5 kullanıcıyla kullanılabilirlik testi (20-22 Ağu) — koşuldu, SUS 60,0, yedi bulgu
- 10 görüşmeyle kullanıcı araştırması (22 Ağu) — koşuldu
- İş/gelir modeli, YZ mimarisi, veri-model-etik-performans dokümanları — tamamlandı

**Not (11 Eylül):** Bu fazdan sonra 23 Ağustos'tan 11 Eylül'e kadar **19 gün depoda
ilerleme olmadı**. Mentörlük tarihi de şartnamenin "2–7 Eylül" penceresinden **12 Eylül
13:00**'e kaydı (bkz. `CLAUDE.md` takvim notu, `docs/MENTORLUK.md`) — final teslimine
36 saat kala. Aşağıdaki Faz 4b bu gerçeği yansıtan sıkıştırılmış plan; ayrıntılı iş
listesi ve doğrulama adımları görüşme öncesi hazırlanan yol haritasında
(`~/.claude/plans/teknofest-i-leti-im-iletisim-teknofest-dapper-phoenix.md`).

### Faz 4b — 11–14 Eylül: Sıkıştırılmış final hazırlığı (mentörlük 12 Eylül'e kaydığı için)
- 11 Eyl gece: duman testi (backend 130 test, arayüz 124 test <!-- sayim: backend, arayuz -->, `dokuman_denetimi.py`), mentör hazırlık paketi
  (`docs/MENTORLUK.md`), belge hizalaması (bu dosya dahil)
- 12 Eyl 13:00–15:00: mentör görüşmesi; geri bildirimler `docs/MENTORLUK.md` §4'teki
  tabloya kaydedilir, her satır bir iş maddesine bağlanır veya gerekçesiyle reddedilir
- 12 Eyl akşam – 13 Eyl: kullanılabilirlik testinin yedi bulgusunun kapatılması
  (`docs/KULLANILABILIRLIK-SONUCLARI.md`) — dördü yüksek ağırlıklı ve zorunlu
- 13 Eyl: demo videosu çekimi (`docs/DEMO-SENARYOSU.md`, düzeltilmiş arayüzle) + sunum
  dosyasının üretimi (`docs/SUNUM.md` → Marp PDF)
- 13 Eyl akşam: jüri makinesi tatbikatı (`docker compose down -v && up --build` sıfırdan)
- **14 Eylül ≤ 11:00: final paketi teslim** (17:00 sınırına 6 saat marj)

### Faz 5 — 15–19 Eylül: Sunum provası
- Jüri soru-cevap hazırlığı
- Yedek plan: internet/GPU olmayan ortam için önceden kaydedilmiş demo videosu kullanılır

### Faz 6 — 20 Eylül: Canlı sunum
- Jüri ve katılımcılara sunum, şartnamede ilan edilen tarih

---

## Doğrulama

**Her fazda çalıştırılacak:**

1. **Uçtan uca senaryo testi:** `docker-compose up` → tarayıcıda altın senaryoyu baştan sona koş. Her fazın sonunda bu akışın o ana kadarki kısmı kesintisiz çalışmalı.
2. **Köken kurtarma doğruluğu:** `python -m eval.run_benchmark` → saldırı senaryoları üzerinde Top-1 doğruluk, precision/recall, yanlış atıf oranı, gecikme. Hedef: kırpma ≤%50 ve JPEG q30'da Top-1 ≥ %90; ağır düzenlemede (filtre + kolaj) ≥ %70.
3. **Alan oranı ölçüm doğruluğu:** bilinen kırpma oranlarıyla üretilmiş türevlerde MAE hedefi ≤ 0.05.
4. **Katkı payı tutarlılığı:** birim testler — paylar toplamı her zaman 1.0; zincir derinliği arttıkça sönümleme monoton; kampanya taban/tavan kuralları ihlal edilmiyor.
5. **API testleri:** pytest ile router başına sözleşme testleri.
6. **Arayüz:** Lighthouse erişilebilirlik skoru ≥ 90; klavye ile tüm akış tamamlanabiliyor.
7. **Jüri makinesi tatbikatı:** temiz bir makinede (veya temiz Docker ortamında) README'yi takip ederek sıfırdan kurulum — 15 dakikadan uzun sürerse kurulum sadeleştirilir.

---

## İlk adımlar (onay sonrası)

1. `C:\Users\HAMZA\Desktop\N-Emek` deposunu ve monorepo iskeletini kur
2. Takım kaptanı KYS'den **resmî teknik rapor şablonunu** indirsin ve `docs/` altına koysun — rapor yapısını buna göre kuracağım
3. Faz 0 PoC'lerini yaz ve üç riski de kapat
4. Google Groups iletişim kanalına takımdan en az bir kişi katılsın (şartname zorunlu tutuyor)
