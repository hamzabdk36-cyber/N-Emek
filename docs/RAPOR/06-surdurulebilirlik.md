# 6 · SÜRDÜRÜLEBİLİRLİK

## 6.1. Ticarileştirme Potansiyeli ve İş Modeli

**Gelir modeli — bugün prototipte çalışan akış.** Marka, remix kampanyası için bir ödül
havuzu koyar. N-Emek havuzu son paylaşana değil, içeriğin ölçülmüş katkısına göre
zincirin tamamına böler. Platform bu hizmet için havuzdan komisyon alır. Demo
kampanyasında havuz ₺50.000, komisyon %10 yani **₺5.000**. Komisyon kampanya başına
yapılandırılabilir, yani marka ile pazarlığa açık bir parametredir.

Bu akış bilinçli olarak seçildi: platformun **zaten var olan** bir gelir kalemi (marka
işbirlikleri) üzerine kuruluyor. Yeni bir ödeme davranışı icat etmiyor — ne kullanıcıdan
abonelik istiyor, ne yeni reklam envanteri gerektiriyor. Değiştirdiği tek şey havuzun
bölünme kuralı.

![Şekil 5 — Marka kampanya paneli: ödül havuzu, kaynak tabanı ve komisyon oranları; dağıtım kampanya kurallarıyla birlikte kayıt altına alınıyor.](docs/gorseller/08-kampanya-paneli.jpg)

**Ölçülmüş dağıtım.** Aşağıdaki rakamların tamamı çalışan sistemden, kayıtlı ödeme
satırlarından okundu:

| Kişi | Üretici olarak | Kaynak olarak | Toplam | Ödeme sayısı |
|---|--:|--:|--:|--:|
| Özgün üretici | ₺6.750,00 | ₺27.798,96 | **₺34.548,96** | 3 |
| Remixleyen | ₺2.925,00 | ₺2.801,04 | **₺5.726,04** | 2 |
| Paylaşan | ₺4.725,00 | ₺0,00 | **₺4.725,00** | 1 |
| Platform (komisyon) | — | — | **₺5.000,00** | 3 |
| **Toplam** | | | **₺50.000,00** | |

Kampanya kuralları da kayıtlıdır: kaynak tabanı %15, üretici tabanı %20, üretici tavanı
%80 (sistem varsayılanı %85, kampanya başına ayarlanabilir). Kaynak payları koşumlar
arasında birkaç lira oynayabilir — geometrik doğrulama rastgele örneklemeli bir kestirim
kullanır ve ölçülen alan oranı her koşumda tıpatıp aynı çıkmaz. Sabit olan, dağıtılan
toplamın havuza eşit olması ve payların sıralamasıdır.

**Sektöre ve ülke ekonomisine katma değer.** Model, marka bütçesinin nereye gittiğini
denetlenebilir hâle getirerek iki taraflı bir değer üretir. Marka için harcamanın kanıtı
oluşur; içerik üreticisi için ise remix bir kayıp olmaktan çıkıp gelir kaynağına döner.
Üretici tarafındaki bu teşvik değişimi, yerli bir platformun içerik üreticisini elde
tutma kabiliyetini doğrudan etkiler — bugün üreticilerin yabancı platformlara yönelmesinin
başlıca sebeplerinden biri gelir modelinin yetersizliğidir.

**Aynı altyapıdan çıkabilecek gelir akışları.** Bunlar prototipte **yoktur**; altyapının
izin verdiği ama henüz ölçülmemiş yönler olarak yazılıyor:

| Akış | Nasıl çalışır | Neden mümkün |
|---|---|---|
| Gönderi geliri paylaşımı | Kampanya dışı gelir (bahşiş, reklam payı) aynı zincire bölünür | Motor gelir alanı üzerinden çalışıyor; kampanya şart değil |
| Atıf API'si | Üçüncü taraflara "bu görselin kaynağı ne" sorgusu | Doğrulama ucu kayıt tutmadan yanıt veriyor |
| Kurumsal köken taraması | Ajans ve yayıncı için telif öncesi denetim | Aynı hat, farklı arayüz |

**İş ortaklıkları.** Model doğası gereği çok taraflıdır ve üç yönde işbirliği gerektirir:
platform tarafında entegrasyon, marka tarafında kampanya ortaklıkları, ekosistem tarafında
ise içerik kimliği standardını benimseyen üreticiler ve cihaz üreticileriyle uyum. C2PA
standardına uyum [6], projeyi tek bir platformun kapalı çözümü olmaktan çıkarıp
standartlaşmış bir ekosistemin parçası hâline getirir.

## 6.2. Finansal, Teknik ve Sosyal Sürdürülebilirlik

**Finansal sürdürülebilirlik.** Modelin finansal mantığı basittir: maliyet içerik başına
**tek seferliktir**, gelir ise kampanya havuzuyla doğrusal büyür. Bir içerik bir kez
işlenir (476-666 ms köken kurtarma), sonra sonsuz kez dağıtıma girer — her dağıtım 31 ms.
Aynı içerik ne kadar çok kampanyaya girerse birim maliyeti o kadar düşer.

Depolama tarafı da ölçüldü: N-Emek'in içerik başına *eklediği* yük 40 KB
mertebesindedir. Bir milyon içerik için yaklaşık 40 GB eder. Bunu para birimine
çevirmedik, çünkü bulut fiyatı sağlayıcıya ve bölgeye göre değişir; kararı etkileyen şey
büyüklük mertebesidir ve o mertebe tek bir sunucunun diskine sığar.

**Teknik sürdürülebilirlik.** Üç yapısal tercih bakımı ve büyümeyi mümkün kılıyor:

- **Katmanlar veritabanını tanımıyor.** Köken kurtarma bir protokol arayüzü alır, pay
  hesabı saf bir fonksiyondur. SQLite'tan PostgreSQL'e, kaba kuvvet indekslerden IVF-PQ
  veya HNSW'ye geçiş veri modelini değiştirmez.
- **Ölçüm otomatiktir.** Hiçbir performans sayısı elle yazılmaz; her biri çalıştırılabilir
  bir betiğin çıktısıdır ve bir denetim betiği dokümanlardaki iddiaları gerçek ölçümlerle
  karşılaştırıp uyuşmazlıkta hata verir. Bu, dokümantasyonun üründen sessizce ayrışmasını
  engelleyen yapısal bir önlemdir.
- **Yapay zekâ bileşeni dondurulmuştur.** Model eğitimi olmadığı için model kayması,
  yeniden eğitim maliyeti ve veri kümesi bakımı yükü yoktur. Ağırlıklar adlandırılmış bir
  kontrol noktasından gelir, yani ölçümler yıllar sonra da yeniden üretilebilir.

**Sosyal sürdürülebilirlik ve değişen ihtiyaçlara uyum.** Sistemin meşruiyeti, kararlarını
gerekçelendirebilmesine bağlıdır ve bu mimariye gömülüdür: her pay satırı açılabilir,
her bağ itiraza açıktır, çözülemeyen itiraz insan incelemesine düşer. Kullanıcı denetimi
de içerik düzeyindedir — her içerik, C2PA manifestine gömülü bir remix politikası taşır:
remixe izin verilip verilmediği, ticari remixe izin verilip verilmediği ve üreticinin
talep ettiği asgari kaynak payı. Tercihler platform veritabanına değil içeriğe bağlıdır,
yani içerikle birlikte seyahat eder.

Değişen ihtiyaçlara uyum, kuralların **veri** olarak tutulmasıyla sağlanır: kaynak tabanı,
üretici tabanı ve tavanı, komisyon oranı, minimum ödeme eşiği ve zincir sönümleme
katsayısı kod içinde sabit değil, kampanya başına yapılandırılabilir parametrelerdir.
Bir pazar koşulu değiştiğinde ya da bir üretici topluluğu farklı bir denge talep
ettiğinde, değişen şey kod değil kampanya kuralıdır.

**Benimseme yolu ve ölçülecekler.** Her aşama bir öncekinin ölçümüne bağlıdır; bu sıra,
sistemin en riskli varsayımını en ucuz yerde sınar:

| Aşama | Ne olur | Ölçülecek |
|---|---|---|
| 1 · Tek kampanya | Bir marka, sınırlı sayıda içerikle pilot | Zincirde kaç kaynak bulundu, kaç itiraz açıldı |
| 2 · Üretici tarafı | "İçeriğin şurada kullanılmış" bildirimi | Üreticinin platformda kalma oranı |
| 3 · Platform geneli | Kampanya dışı gelir de zincire bölünür | Yanlış atıf oranı ölçekte korunuyor mu |
| 4 · Dışa açılma | Atıf API'si üçüncü taraflara | Sorgu hacmi ve gecikme |

**Kanıtlanan ve varsayılan.** Kanıtlanan: zincir kurma ve ölçme doğruluğu, havuzun
eksiksiz dağıtılması ve denetlenebilirliği, komisyonun tahsili, içerik başına maliyet.
Varsayılan ve henüz ölçülmemiş: markanın bu modele bugünküyle aynı bütçeyi ayıracağı,
üreticinin platformda kalma oranının artacağı, ölçekte yanlış atıf oranının korunacağı ve
bulut maliyetinin Türk lirası karşılığı. İlk üçü yukarıdaki pilot aşamalarında ölçülebilir.
