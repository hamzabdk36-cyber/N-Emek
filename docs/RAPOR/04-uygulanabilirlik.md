# 4 · UYGULANABİLİRLİK

## 4.1. Verimlilik ve Etkinlik

**Bugün elle yapılamayan bir iş otomatikleşiyor.** Bir türev içeriğin kaynağını bulmak
ve ne kadarının kullanıldığını belirlemek bugün ya hiç yapılmıyor ya da elle yapılıyor:
insan gözüyle karşılaştırma, kaynak arama, müzakere. Bu iş içerik başına dakikalar sürer
ve ölçekte imkânsızdır. N-Emek aynı işi ölçülmüş sürelerde yapar:

| İşlem | Ölçülen süre | Ne zaman ödenir |
|---|--:|---|
| Kimliksiz içerik yükleme — tam köken kurtarma | 476 ms | İçerik başına bir kez |
| Özgün içerik yükleme | 666 ms | İçerik başına bir kez |
| Emek Kartı üretimi | 6 ms | Her görüntülemede |
| Kampanya havuzunun tüm zincire dağıtımı | 31 ms | Kampanya başına bir kez |
| İtiraz çözümü — daha hassas dedektörle yeniden ölçüm | 79 ms | İtiraz başına |
| Uçtan uca köken kurtarma (6.400 sorgu) | p50 386 ms · p95 703 ms | Sorgu başına |

Bu ölçümlerden iki tanesi tasarım açısından belirleyicidir. **En ağır adım kimliksiz
yükleme değil, özgün yüklemedir** — sebebi anlamlıdır: özgün bir içerikte doğrulanacak
adayların hepsi yanlış çıkar ve her biri elenene kadar tam maliyetini ödetir. Gerçek
kaynak varsa eşleşme erken ve güçlüdür. Sistem yükleyenin sözüne değil ölçüme bakar;
kaynak *olmadığını* doğrulamak da kaynak bulmak kadar iştir. İkincisi, **pay hesabı
tarafı ihmal edilebilir düzeydedir** (Emek Kartı ve dağıtım toplam 37 ms). Maliyetin
tamamı köken kurtarmadadır, dolayısıyla ölçeklendirmenin nereden yapılacağı ölçümle
belirlenmiştir.

**Etkinlik: ölçülebilir doğruluk.** Verimlilik tek başına yeterli değildir; hızlı ama
yanlış bir atıf sistemi işe yaramaz. Doğruluk 6.400 sorguluk bir değerlendirmede
ölçüldü: Top-1 %98,7, F1 0,9753, yanlış atıf oranı %0,86, kapsama ölçüm hatası (MAE)
0,0241. Kapsama hatasının 0,05 hedefinin yarısından küçük olması, pay hesabının girdisinin
güvenilir olduğu anlamına gelir.

**Kullanıcı deneyimi açısından anlamlı sonuç,** yükleme adımlarının yarım saniye
civarında kalmasıdır: zincir önerisi yüklemeden hemen sonra, kullanıcı beklemeden
gösterilebilir. Köken kurtarma arka planda çalışan ve saatler sonra sonuç veren bir
toplu iş değil, akışın içinde bir adımdır.

**Ekonomik verimlilik.** Aynı içerik ne kadar çok kampanyaya girerse birim maliyeti o
kadar düşer: maliyet içerik başına tek seferlik, gelir ise kampanya havuzuyla doğrusal
büyür. Depolama tarafındaki ek yük de ölçüldü ve küçüktür (bkz. 6.2).

## 4.2. Hedef Kitle

**Doğrudan hedef kitle dört gruptur:**

| Aktör | Bugünkü sorunu | N-Emek ne veriyor |
|---|---|---|
| Özgün içerik üreticisi | İçeriği kırpılıp yeniden paylaşılınca izi kayboluyor | Zincirde yaşadığı sürece gelir; remix artık kayıp değil kazanç |
| Remix üreticisi | "Ya hiç anmam ya da her şeyi ona veririm" ikilemi | Kaynağı anmak payını sıfırlamıyor; kendi katkısı ayrıca ölçülüyor |
| Marka | Havuzun kime neden gittiği belirsiz | Her ödemenin altında ölçüm ve kanıt; denetlenebilir kampanya raporu |
| Platform | Üretici kaçışı, marka bütçesini çekememe | Üreticiyi elde tutan, kanıtlanabilir paylaşım altyapısı |

**Kitlenin büyüklüğü.** Türkiye'de 16-74 yaş grubundaki bireylerin %90,9'u internet
kullanıyor; %72,9'u YouTube, %68,1'i Instagram gibi içerik paylaşım platformlarında [1].
Bu oranlar, ürünün hitap ettiği tabanın Türkiye nüfusunun büyük çoğunluğu olduğunu
gösteriyor. Küresel ölçekte içerik üretici sayısı 50 milyon mertebesinde ve yıllık %10-20
büyüyor; pazar büyüklüğü 2027 için 480 milyar dolar öngörülüyor [2].

Ancak asıl hedef kitle bu tabanın **içindeki dar bir dilim değil, tamamıdır**. Sistem,
profesyonel üreticiyi de bir kez fotoğraf paylaşan sıradan kullanıcıyı da aynı
mekanizmayla korur: pay, takipçi sayısına veya sözleşmeye değil, içeriğin zincirde
ölçülen kullanımına bağlıdır.

**Uyumun kanıtı.** Ürünün hedef kitleye uygunluğu üç yerde somutlaşır. Birincisi,
üreticinin gelir tablosundaki değişimin ölçülmüş olması: demo kampanyasında zincirin
başındaki üretici, hiç remix yapmadan ve tek içerik yükleyerek havuzun **%69'unu** aldı;
üç ödemesinin ikisi hiç haberi olmadığı gönderilerden geldi. İkincisi, remix üreticisinin
cezalandırılmaması: üretici tabanı kuralı gereği kaynak bulunmasına rağmen son paylaşan
da pay alır. Üçüncüsü, sistemin teknik olmayan kullanıcı için tasarlanmış olması —
akıştaki bir gönderinin kökeni tek satır düz metinle özetlenir, ayrıntı isteyen kullanıcı
Emek Kartı'na iner, hiçbir ekran kullanıcıdan eşik değeri veya model adı bilmesini
beklemez.

## 4.3. Teknolojik Yenilik ve Uygulanabilirlik

**Yeniliğin düzeyi.** Projenin teknik katkısı tek bir cümlede toplanabilir: *kullanılan
içerik oranının ölçülmesi.* Literatürdeki bileşenler (algısal hash [8], gömme tabanlı
benzerlik [9], yerel özellik eşleme [11][12], RANSAC [13], normalize çapraz korelasyon
[14], yayılı spektrum filigranı [7], C2PA [6]) tek tek bilinen yöntemlerdir; bunları
bir **karar füzyonu** altında birleştirip çıktısını bir **gelir bölüşümüne** çevirmek
yenidir.

Yeniliğin teknik ayrıntısı şudur: aşama güvenleri gürültülü-VEYA ile birleştirilir,
çünkü her aşama kaynağı bağımsız bir fiziksel izden bulur — üstveri, bayt özeti, frekans
alanı, piksel istatistiği, yerel geometri. Aynı sonuca farklı yollardan varmaları güveni
artırmalıdır; toplamsal bir model bu bağımsızlığı ifade edemezdi. Üstüne iki emniyet
supabı konur: yalnızca benzerlikten gelen güven 0,80 ile sınırlanır (benzerlik "aynı
sahne" ile "aynı içerik"i ayırmaz) ve geometrik doğrulamayı geçemeyen bir adayın güveni
0,40 ile çarpılır. Her ikisinin de tek gerekçesi vardır: yanlış atıf, kaçırılmış atıftan
ağır bir hatadır.

**Hayata geçirilebilirliğin kanıtı fikir değil, çalışan prototiptir.** Sistem bugün
çalışır durumdadır: referans sosyal medya istemcisi, remix stüdyosu, Emek Kartı, atıf
zinciri görselleştirmesi, marka kampanya paneli, itiraz akışı ve moderasyon kuyruğu
dahil. `docker compose up --build` ile tek komutta ayağa kalkar ve altın senaryo baştan
sona koşulabilir. Doğrulama otomatiktir: backend ve arayüz test paketleri, tip denetimi,
üretim derlemesi ve doküman tutarlılık denetimi her itmede sürekli tümleştirmede koşar.

**Ölçeklenebilirlik.** Prototip tek makinede, SQLite ve kaba kuvvet indekslerle çalışır.
On binler mertebesinde bu kurulum fazlasıyla hızlıdır ve %100 geri getirme garantilidir.
Gecikme ölçümü, büyümede hangi düğmelerin çevrileceğini açıkça gösterir:

| Darboğaz | Bugün | Ölçekte |
|---|---|---|
| Aday arama | Kaba kuvvet ikili ve iç çarpım indeksleri | IVF-PQ / HNSW — indeks arayüzü aynı kalır |
| Geometrik doğrulama | Aday başına ~90 ms, en fazla 8 aday | Aday sayısı ayarlanabilir; kuyruk üzerinden asenkron |
| CLIP gömme | Tek GPU, yığın 32 | Gömme çevrimdışı; yatay ölçeklenir |
| Veritabanı | SQLite | PostgreSQL — veri modeli değişmez |

Bu geçişleri kolaylaştıran şey mimarinin kendisidir: `provenance/` ve `attribution/`
katmanları veritabanını tanımaz. Köken kurtarma bir protokol arayüzü alır, pay hesabı saf
bir fonksiyondur. Dolayısıyla ölçeklenme bir yeniden yazım değil, bir bileşen
değişikliğidir.
