# N-Emek — Sistem Mimarisi

Bu belge sistemin nasıl kurulduğunu ve verinin nasıl aktığını anlatır. Ölçüm sonuçları
için `DEGERLENDIRME.md` ve `FAZ0-SONUCLARI.md`, gecikmeler için `GECIKME.md`.

---

## 1. Katmanlar

N-Emek bir sosyal platformun yerine geçmez; ona takılan bir **emek katmanı**dır. Prototipte
platformun kendisi de var, çünkü katmanın nereye takılacağını göstermek gerekiyor.

```mermaid
flowchart TB
    subgraph istemci["Referans istemci — React 19 + Vite + Tailwind"]
        akis["Akış"]
        detay["İçerik Detay — Emek Kartı"]
        studyo["Remix Stüdyo: kırp, yazı, çizim, filtre"]
        dogrula["Doğrula"]
        kampanya["Kampanya Paneli"]
        moderasyon["Moderasyon Kuyruğu"]
    end

    subgraph api["FastAPI — 22 uç"]
        %% sayim: uc
        rest["routes.py + schemas.py"]
    end

    subgraph servis["Servis katmanı"]
        ingest["ingest — yükleme ve remix"]
        payoutsvc["payout — dağıtım"]
        disputesvc["dispute — itiraz ve moderasyon"]
        registry["registry — indeks yaşam döngüsü"]
    end

    subgraph motor["N-Emek motoru"]
        prov["provenance/ — köken kurtarma hattı"]
        attr["attribution/ — zincir ve pay hesabı"]
    end

    subgraph depo["Depolama"]
        db[("SQLite: Content, Edge, Campaign, Payout, Dispute")]
        faiss[("FAISS: pHash, blok, CLIP")]
        disk[("Dosya sistemi: yayınlanmış görseller, maskeler")]
    end

    istemci -->|"/api"| rest
    rest --> ingest & payoutsvc & disputesvc
    ingest --> prov
    payoutsvc --> attr
    disputesvc --> prov & attr
    registry --> faiss
    prov --> registry
    prov --> disk
    attr --> db
    ingest --> db
```

**Neden bu ayrım:** `provenance/` ve `attribution/` veritabanını tanımaz. `recovery.recover()`
bir `ContentStore` protokolü alır, `contribution.compute_shares()` saf bir fonksiyondur.
Bu sayede değerlendirme betikleri (`eval/`) motoru SQLAlchemy olmadan koşturabiliyor ve
pay formülü 22 birim testiyle sabitlenebiliyor.

---

## 2. Köken kurtarma hattı

Projenin ayırt edici parçası. Mantığı iki aşamalı: **ucuz aday üretimi**, ardından
**pahalı doğrulama**.

```mermaid
flowchart TB
    giris["Yüklenen görsel — baytlar ve piksel dizisi"]

    subgraph aday["Aday üretimi — milisaniyeler"]
        s0["0 · C2PA manifest — güven 0,99"]
        s1["1 · SHA-256 tam eşleşme — güven 0,99"]
        s2["2 · Görünmez filigran, CRC-16 doğrulamalı — güven 0,90"]
        s3["3 · pHash + blok hash, Hamming ≤ 12 — güven 0,45–0,80"]
        s4["4 · CLIP ViT-B/32, çok bölgeli — güven 0,30–0,75"]
    end

    havuz{{"Aday havuzu — en umut vaat eden 8 tanesi"}}

    s5["5 · Homografi + ZNCC — KULLANILAN ALANI ÖLÇER, güven 0,60–0,95"]

    fuzyon["Karar füzyonu, gürültülü-VEYA: 1 − Π(1 − güvenᵢ)"]
    cikti["Kanıtlı zincir önerisi: bağ, güven, kapsama, maske"]

    giris --> s0 & s1 & s2 & s3 & s4
    s0 & s1 & s2 & s3 & s4 --> havuz
    havuz --> s5
    s5 --> fuzyon --> cikti
```

### Neden gürültülü-VEYA

Her aşama kaynağı **bağımsız bir fiziksel izden** buluyor: metadata, bayt özeti, frekans
alanı, piksel istatistiği, yerel geometri. Aynı sonuca farklı yollardan varmaları güveni
artırmalı; toplamsal bir model bunu ifade edemezdi.

### İki emniyet supabı

```mermaid
flowchart LR
    A["Yalnızca benzerlikten gelen güven"] --> B{"tavan 0,80"}
    B --> C["'aynı sahne' ile 'aynı içerik' ayrımını benzerlik yapamaz"]
    D["Geometrik doğrulama başarısız"] --> E["× 0,40 ceza"]
    E --> F["genelde eşiğin altına düşer"]
```

Yanlış atıf, kaçırılmış atıftan ağırdır. Eşikler bu yönde hata payı bırakacak şekilde
ayarlandı.

### Çok bölgeli sorgu

Ölçüm sonucu eklenen bir tasarım kararı. Kaynak, türev tuvalinin yalnızca bir bölümünü
kapladığında (meme, kolaj, kırpma+yazı) global tanımlayıcılar tüm tuvali görüyor ve
kaçırıyordu. Sorgu görseli sabit bir bölge kümesine ayrılıp her bölge ayrı aranıyor.

```mermaid
flowchart LR
    q["Sorgu görseli"] --> t["tam"] & m["merkez"] & c["4 çeyrek"] & y["4 yarım"] & k["düz çerçevesi kırpılmış hâli"]
    t & m & c & y & k --> emb["tek GPU yığını — 11 bölge"]
    emb --> ara["pHash + CLIP araması"]
```

Ortalama geri getirme %88,5 → %99,2. İndeks tarafı değişmedi; maliyet yalnızca sorgu anında.

---

## 3. Katkı payı: ölçümden paya

Sistemin ikinci yarısı. Buradaki iki kural (**geçişli indirgeme** ve **özel kapsama
bölüntüsü**) sonradan "sadeleştirme" diye kaldırılmamalı; ikisi de ölçümdeki gerçek bir
hatayı düzeltiyor.

```mermaid
flowchart TB
    edges[("AttributionEdge kayıtları: kapsama, güven, kanıt")]
    alt["Alt grafiği topla — derinlik ≤ 5"]
    ind["GEÇİŞLİ İNDİRGEME — P→C bağı, P⇢…⇢C yolu varsa düşülür"]
    ozel["ÖZEL KAPSAMA BÖLÜNTÜSÜ — özel(A) = toplam(A) − Σ toplam(A'nın kaynakları)"]
    formul["Ağırlık = kapsama^a × güven^b × sönümleme^(derinlik−1)"]
    kural["Kampanya kuralları: üretici tabanı ve tavanı, kaynak tabanı, ödeme eşiği"]
    dagitim["Dağıtım: paylar, tutarlar, kural günlüğü"]
    kart["Emek Kartı — her rakamın altında gerekçesi"]

    edges --> alt --> ind --> ozel --> formul --> kural --> dagitim --> kart
```

### Geçişli indirgeme neden gerekli

```mermaid
flowchart LR
    A["Ayşe"] -->|"%87,5 ölçüldü"| B["Burak"]
    B -->|"%97,5 ölçüldü"| C["Ceyda"]
    A -.->|"%87,6 — geometri bunu da bulur"| C

    classDef dropped stroke-dasharray: 5 5
```

Geometri, Ayşe'nin içeriğini Ceyda'nın gönderisinde de bulur — pikseller oraya Burak
üzerinden gelmiştir. Kesikli bağ pay hesabına girerse aynı emek iki kez ödüllendirilir.
Veritabanında kanıt olarak kalır, hesaba girmez.

**Bu düzeltmeden önce kaynakların toplamı %182 çıkıyordu.**

### Özel kapsama neden gerekli

Ölçülen kapsamalar iç içedir: Burak'ın yapraktaki %97,5'i Ayşe'nin %85,2'sini de kapsar. Her düğüme
yalnızca kendi kattığı pikseller yazılır. Böylece kapsamalar görselin tam bir bölüntüsü
olur ve **doğal olarak 1,0'a toplanır** — pay normalizasyona değil ölçüme dayanır.

Bu düzeltmenin bir sonucu oldu: `chain_damping` 0,50'den **0,85**'e çıkarıldı. Agresif
sönümleme, tam da bu projenin düzeltmeye çalıştığı haksızlığı üretiyordu — ilk üretici,
başkaları remixlediği için cezalandırılmış oluyordu.

---

## 4. Yükleme akışı: neden iki kez parmak izi

```mermaid
sequenceDiagram
    participant K as Kullanıcı
    participant A as API
    participant R as recovery
    participant W as watermark + C2PA
    participant I as indeks

    K->>A: görsel yükler
    A->>R: 1· GELEN dosya üzerinde köken kurtarma
    Note over R: kullanıcının getirdiği şey ne ise onun üzerinde çalışırız — manifesti silinmiş, ekran görüntüsü alınmış, kırpılmış hâli
    R-->>A: bağlar + kanıtlar + maskeler
    A->>W: 2· filigran göm, manifest imzala
    W-->>A: yayınlanacak dosya (baytlar değişti)
    A->>I: 3· YAYINLANAN dosya üzerinden indeksle
    Note over I: başkaları bu hâli indirip remixleyecek — indekste duran parmak izi de bu olmalı
    A-->>K: içerik + zincir önerisi
```

Bu ayrımı atlamak, kendi yayınladığımız içeriğin birebir kopyasını tanıyamamamıza yol açar.

---

## 5. Altın senaryo — demoda görülen zincir

```mermaid
flowchart LR
    subgraph ayse["1 · Ayşe"]
        a1["özgün fotoğraf"]
    end
    subgraph burak["2 · Burak"]
        b1["kırpma + yazı + çizim"]
    end
    subgraph ceyda["3 · Ceyda"]
        c1["ekran görüntüsü — C2PA SİLİNİR"]
    end

    a1 -->|"C2PA ingredient — güven 0,97 · kapsama %87,5"| b1
    b1 -->|"kurtarıldı: filigran, CLIP, homografi — güven 0,99 · kapsama %97,5"| c1

    c1 --> pay["Emek Kartı: Ayşe %68,1 · Burak %11,9 · Ceyda %20,0 · N'Sosyal %10,0"]
    pay --> itiraz["Ayşe itiraz eder → SIFT ile yeniden ölçüm → paylar güncellenir"]
```

Üçüncü adım senaryonun kritik anıdır: içerik sisteme "kaynağı yokmuş" gibi girer, hat
Burak'ı **ve** onun üzerinden Ayşe'yi bulur, eşleşen bölge maskeyle gösterilir.

---

## 6. Ölçeklenebilirlik

Prototipte iki FAISS indeksi de "flat" (kaba kuvvet). On binler mertebesinde fazlasıyla
hızlı ve %100 geri getirme garantili. `GECIKME.md`, maliyetin tamamen köken kurtarmada
olduğunu gösteriyor; büyümede iki düğme var:

| Darboğaz | Bugün | Ölçekte |
|---|---|---|
| Aday arama | `IndexBinaryFlat` + `IndexFlatIP` | IVF-PQ / HNSW — `ProvenanceIndex` arayüzü aynı kalır |
| Geometrik doğrulama | aday başına ~90 ms, en fazla 8 aday | `max_geometry_candidates` ayarı; kuyruk üzerinden asenkron |
| CLIP gömme | tek GPU, yığın 32 | gömme çevrimdışı; yatay ölçeklenir |
| Veritabanı | SQLite | PostgreSQL — SQLAlchemy modeli değişmez |
