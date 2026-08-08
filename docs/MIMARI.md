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
        detay["İçerik Detay<br/>(Emek Kartı)"]
        studyo["Remix Stüdyo<br/>kırp · yazı · çizim · filtre"]
        dogrula["Doğrula"]
        kampanya["Kampanya Paneli"]
        moderasyon["Moderasyon Kuyruğu"]
    end

    subgraph api["FastAPI — 20 uç"]
        rest["routes.py + schemas.py"]
    end

    subgraph servis["Servis katmanı"]
        ingest["ingest<br/>yükleme ve remix"]
        payoutsvc["payout<br/>dağıtım"]
        disputesvc["dispute<br/>itiraz ve moderasyon"]
        registry["registry<br/>indeks yaşam döngüsü"]
    end

    subgraph motor["N-Emek motoru"]
        prov["provenance/<br/>köken kurtarma hattı"]
        attr["attribution/<br/>zincir ve pay hesabı"]
    end

    subgraph depo["Depolama"]
        db[("SQLite<br/>Content · Edge · Campaign<br/>Payout · Dispute")]
        faiss[("FAISS<br/>pHash · blok · CLIP")]
        disk[("Dosya sistemi<br/>yayınlanmış görseller · maskeler")]
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
    giris["Yüklenen görsel<br/>(baytlar + piksel dizisi)"]

    subgraph aday["Aday üretimi — milisaniyeler"]
        s0["0 · C2PA manifest<br/>güven 0,99"]
        s1["1 · SHA-256 tam eşleşme<br/>güven 0,99"]
        s2["2 · Görünmez filigran<br/>CRC-16 doğrulamalı · güven 0,90"]
        s3["3 · pHash + blok hash<br/>Hamming ≤ 12 · güven 0,45–0,80"]
        s4["4 · CLIP ViT-B/32<br/>çok bölgeli · güven 0,30–0,75"]
    end

    havuz{{"Aday havuzu<br/>en umut vaat eden 8 tanesi"}}

    s5["5 · Homografi + ZNCC<br/><b>kullanılan alanı ÖLÇER</b><br/>güven 0,60–0,95"]

    fuzyon["Karar füzyonu<br/>gürültülü-VEYA: 1 − Π(1 − güvenᵢ)"]
    cikti["Kanıtlı zincir önerisi<br/>bağ + güven + kapsama + maske"]

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
    A["Yalnızca benzerlikten<br/>gelen güven"] --> B{"tavan 0,80"}
    B --> C["'aynı sahne' ile 'aynı içerik'<br/>ayrımını benzerlik yapamaz"]
    D["Geometrik doğrulama<br/>başarısız"] --> E["× 0,40 ceza"]
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
    q["Sorgu görseli"] --> t["tam"] & m["merkez"] & c["4 çeyrek"] & y["4 yarım"] & k["düz çerçevesi<br/>kırpılmış hâli"]
    t & m & c & y & k --> emb["tek GPU yığını<br/>11 bölge"]
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
    edges[("AttributionEdge kayıtları<br/>kapsama + güven + kanıt")]
    alt["Alt grafiği topla<br/>derinlik ≤ 5"]
    ind["<b>Geçişli indirgeme</b><br/>P→C bağı, P⇢…⇢C yolu varsa düşülür"]
    ozel["<b>Özel kapsama bölüntüsü</b><br/>özel(A) = toplam(A) − Σ toplam(A'nın kaynakları)"]
    formul["Ağırlık = kapsama^a × güven^b × sönümleme^(derinlik−1)"]
    kural["Kampanya kuralları<br/>üretici tabanı/tavanı · kaynak tabanı · ödeme eşiği"]
    dagitim["Dağıtım<br/>paylar + tutarlar + kural günlüğü"]
    kart["Emek Kartı<br/>her rakamın altında gerekçesi"]

    edges --> alt --> ind --> ozel --> formul --> kural --> dagitim --> kart
```

### Geçişli indirgeme neden gerekli

```mermaid
flowchart LR
    A["Ayşe"] -->|"%87 ölçüldü"| B["Burak"]
    B -->|"%99 ölçüldü"| C["Ceyda"]
    A -.->|"%84 — geometri bunu da bulur"| C

    classDef dropped stroke-dasharray: 5 5
```

Geometri, Ayşe'nin içeriğini Ceyda'nın gönderisinde de bulur — pikseller oraya Burak
üzerinden gelmiştir. Kesikli bağ pay hesabına girerse aynı emek iki kez ödüllendirilir.
Veritabanında kanıt olarak kalır, hesaba girmez.

**Bu düzeltmeden önce kaynakların toplamı %182 çıkıyordu.**

### Özel kapsama neden gerekli

Ölçülen kapsamalar iç içedir: Burak'ın %97'si Ayşe'nin %84'ünü de kapsar. Her düğüme
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
    Note over R: kullanıcının getirdiği şey ne ise onun<br/>üzerinde çalışırız: manifesti silinmiş,<br/>ekran görüntüsü alınmış, kırpılmış hâli
    R-->>A: bağlar + kanıtlar + maskeler
    A->>W: 2· filigran göm, manifest imzala
    W-->>A: yayınlanacak dosya (baytlar değişti)
    A->>I: 3· YAYINLANAN dosya üzerinden indeksle
    Note over I: başkaları bu hâli indirip remixleyecek;<br/>indekste duran parmak izi de bu olmalı
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
        c1["ekran görüntüsü<br/><b>C2PA silinir</b>"]
    end

    a1 -->|"C2PA ingredient<br/>güven 0,99 · kapsama %87"| b1
    b1 -->|"kurtarıldı: filigran + CLIP + homografi<br/>güven 0,99 · kapsama %99"| c1

    c1 --> pay["Emek Kartı<br/>Ayşe %68,0 · Burak %12,0<br/>Ceyda %20,0 · N'Sosyal %10,0"]
    pay --> itiraz["Ayşe itiraz eder<br/>→ SIFT ile yeniden ölçüm<br/>→ paylar güncellenir"]
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
