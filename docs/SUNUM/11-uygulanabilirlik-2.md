# 11 · Uygulanabilirlik ve Sürdürülebilirlik (2/2)

<!-- Sayılar: docs/GECIKME.md, docs/ACILIS-SURESI.md, docs/IS-MODELI.md §6,
docs/MIMARI.md §6. -->

## olcek
| Darboğaz | Bugün | Ölçekte |
|---|---|---|
| Aday arama | FAISS düz indeks | IVF-PQ veya HNSW; arama arayüzü aynı |
| Geometrik doğrulama | içerik başına en fazla 8 aday | aday sınırı ve asenkron kuyruk |
| CLIP gömmesi | yükleme sırasında | çevrimdışı, yatay ölçeklenir |
| Veritabanı | SQLite | PostgreSQL; veri modeli değişmez |

## birim
- **476–666 ms** · içerik başına bir kez: yükleme ve köken kurtarma
- **31 ms** · bir kampanyanın tüm havuzunu dağıtma
- **11,5 sn → 16 ms** · 280 içerikte açılış, kalıcı indeksle

## birim_not
Maliyet içerik başına tek seferlik, gelir kampanya havuzuyla büyür. İçerik başına eklenen veri yaklaşık 40 KB; milyon içerikte yaklaşık 40 GB (kestirim, ölçüm değil).

## risk
| Risk | Karşı önlem |
|---|---|
| Yanlış atıf haksız ödemeye yol açar | Eşikler yanlış atıfı kaçırılmış atıfa tercih eder; her bağ itiraza açık |
| Sahte kaynak beyanı | Beyan pay vermez, yalnızca ölçüm verir |
| Sistem karar veremez | Moderatöre yükseltilir ve bu ekranda gizlenmez |
| Marka ve üretici benimsemesi | Varsayım olarak işaretli; pilot kampanyada ölçülecek |

## surdurulebilirlik
### Finansal
Aynı içerik ne kadar çok kampanyaya girerse birim maliyeti o kadar düşer. Gelir, platformun zaten sattığı marka işbirliklerinden gelir; kullanıcıdan abonelik istenmez.

### Teknik
- Motor katmanları veritabanını tanımaz; altyapı değişimi pay kurallarını etkilemez.
- Model eğitimi yok: model kayması, yeniden eğitim ve veri kümesi bakımı yükü yok.
- Dokümandaki her performans sayısı betik çıktısıdır; sürekli tümleştirme uyuşmazlığı hata sayar.

### Sosyal
- Kurallar kodda değil kampanya verisinde: taban, tavan, komisyon ve sönümleme ayarlanabilir.
- Üreticinin remix tercihleri içeriğin C2PA manifestinde taşınır; içerikle birlikte seyahat eder.
- Meşruiyet mimaride: her pay açılabilir, her bağ sorgulanabilir.

## kaynak
Ölçümler: backend/eval/run_latency.py ve run_startup.py çıktıları; ölçek yolu docs/MIMARI.md.

## not
Ölçeklenebilirlikte önce darboğazları ayırdık. Maliyetin tamamı köken kurtarmada; pay hesabı milisaniyeler sürüyor. Bugün kaba kuvvet FAISS ve SQLite kullanıyoruz; ölçekte IVF-PQ veya HNSW indeksine ve PostgreSQL'e geçiş, veri modelini ve arayüzü değiştirmiyor. Birim maliyet ölçüldü: bir içerik yükleme ve köken kurtarma yarım saniye civarında ve içerik başına bir kez ödeniyor; tüm kampanya havuzunu dağıtmak 31 milisaniye. İndeksi kalıcı yaptığımızda 280 içerikte açılış 11,5 saniyeden 16 milisaniyeye indi. Sürdürülebilirliği üç eksende düşünüyoruz: finansal olarak maliyet tek seferlik; teknik olarak model eğitimi olmadığı için kayma yok ve her sayı betikten geliyor; sosyal olarak kurallar kampanya verisi olarak değiştirilebiliyor. Riskleri ve karşı önlemleri de soldaki tabloda açıkça yazdık.
