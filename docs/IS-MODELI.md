# İş ve Gelir Modeli

Bu belgedeki dağıtım rakamlarının tamamı **çalışan sistemden** okundu; hiçbiri örnek
amaçlı uydurulmadı. Kaynak: demo veritabanındaki kayıtlı `Payout` satırları
(`docker compose up --build` → Kampanyalar ekranı → `GET /api/users/{id}/earnings`).

Maliyet tarafındaki ölçümler `GECIKME.md` ve `ACILIS-SURESI.md`'den; para birimine
çevrilen her varsayım açıkça işaretlendi.

---

## 1. Tek cümlede

Marka, remix kampanyası için bir ödül havuzu koyar. N-Emek havuzu **son paylaşana değil,
içeriğin ölçülmüş katkısına göre zincirin tamamına** böler. Platform bu hizmet için
havuzdan komisyon alır.

---

## 2. Ölçülmüş dağıtım — demo kampanyası

**Anadolu Kahve · "Şehrin Renkleri Remix Kampanyası"** · havuz **₺50.000** · komisyon %10
· kaynak tabanı %15 · üretici tabanı %20.

Havuz önce gönderiler arasında bölünür (ölçüt: gönderinin kendi ürettiği gelir), sonra
her gönderinin payı **kendi atıf zincirine** dağıtılır.

| Gönderi | Gönderi geliri | Havuzdan payı |
|---|--:|--:|
| Sabah ışığı (Ayşe) | ₺1.200 | ₺7.500 |
| Şehrin Renkleri (Burak) | ₺2.600 | ₺16.250 |
| Bulduğum kare (Ceyda) | ₺4.200 | ₺26.250 |
| **Toplam** | **₺8.000** | **₺50.000** |

Her gönderinin payı zincire bölündüğünde ortaya çıkan kayıtlı ödemeler:

| Kişi | Üretici olarak | Kaynak olarak | **Toplam** | Ödeme sayısı |
|---|--:|--:|--:|--:|
| Ayşe Yılmaz | ₺6.750,00 | ₺27.795,80 | **₺34.545,80** | 3 |
| Burak Demir | ₺2.925,00 | ₺2.804,20 | **₺5.729,20** | 2 |
| Ceyda Aksoy | ₺4.725,00 | ₺0,00 | **₺4.725,00** | 1 |
| N'Sosyal (platform) | — | — | **₺5.000,00** | 3 |
| | | | **₺50.000,00** | |

> **Tezin tek rakamda özeti:** Ayşe kampanyaya **bir** içerik yükledi ve hiç remix
> yapmadı. Havuzun **%69'unu** aldı — çünkü içeriği zincirde yaşıyor ve bu ölçüldü.
> Üç ödemesinin ikisi, kendisinin hiç haberi olmadığı gönderilerden geldi.

---

## 3. Bugünkü modelle karşılaştırma — dürüst hâli

Bugünkü platformlarda kampanya havuzu **gönderiyi paylaşan kişiye** gider. Aynı havuz,
aynı gönderiler, iki model:

| Kişi | Bugünkü model | N-Emek ile | Fark |
|---|--:|--:|--:|
| Ayşe (özgün üretici) | ₺6.750,00 | ₺34.545,80 | **5,1×** |
| Burak (remixleyen) | ₺14.625,00 | ₺5.729,20 | 0,39× |
| Ceyda (paylaşan) | ₺23.625,00 | ₺4.725,00 | 0,20× |
| Platform | ₺5.000,00 | ₺5.000,00 | aynı |

**Havuz büyümüyor, yer değiştiriyor.** Bu modelde Burak ve Ceyda daha az alıyor ve bunu
saklamıyoruz. İddia "herkes kazanır" değil, **"ödeme ölçülmüş katkıya gider"**.

İki denge unsuru var, ikisi de kuralda yazılı:

- **Üretici tabanı %20.** Hiçbir remix "sıfır emek" değildir; seçim, çerçeveleme ve
  yayın da katkıdır. Ceyda kaynak bulunmasına rağmen ₺4.725 alıyor.
- **Üretici tavanı %80.** Kaynak varken kaynak payı tamamen silinemez.

---

## 4. Değer önermesi — kim neden kullanır

| Aktör | Bugünkü sorunu | N-Emek ne veriyor |
|---|---|---|
| **Özgün üretici** | İçeriği kırpılıp yeniden paylaşılınca izi kayboluyor | Zincirde yaşadığı sürece gelir; remix artık kayıp değil kazanç |
| **Remix üreticisi** | "Ya hiç anmam ya da her şeyi ona veririm" ikilemi | Kaynağı anmak payını sıfırlamıyor — kendi katkısı ayrıca ölçülüyor |
| **Marka** | Havuzun kime neden gittiği belirsiz | Her ödemenin altında ölçüm ve kanıt; kampanya sonunda denetlenebilir rapor |
| **Platform** | Üretici kaçışı, marka bütçesini çekememe | Üreticiyi elde tutan ve marka bütçesi çeken kanıtlanabilir altyapı |
| **Toplum** | Emeğin görünmezleşmesi | Atıf, iyi niyete değil ölçüme dayanıyor |

---

## 5. Gelir modeli

### Bugün prototipte çalışan akış

**Kampanya komisyonu.** Marka havuzunun **%10'u** platforma kalır. Demo kampanyasında
₺5.000. Kampanya başına yapılandırılabilir (`Campaign.commission`), yani marka ile
pazarlığa açık bir parametre.

Bu akış bilinçli olarak seçildi: platformun **zaten var olan** bir gelir kalemi (marka
işbirlikleri) üzerine kuruluyor. Yeni bir ödeme davranışı icat etmiyor — ne kullanıcıdan
abonelik istiyor, ne de reklam envanteri gerektiriyor.

### Aynı altyapıdan çıkabilecek akışlar

Bunlar prototipte **yok**; altyapının izin verdiği ama ölçülmemiş yönler olarak yazılıyor:

| Akış | Nasıl çalışır | Neden mümkün |
|---|---|---|
| Gönderi geliri paylaşımı | Kampanya dışı gelir (bahşiş, reklam payı) aynı zincire bölünür | Motor zaten `revenue` alanı üzerinden çalışıyor — kampanya şart değil |
| Atıf API'si | Üçüncü taraflara "bu görselin kaynağı ne" sorgusu | `/api/verify` ucu kaydetmeden yanıt veriyor |
| Kurumsal denetim | Ajans/yayıncı için telif öncesi köken taraması | Aynı hat, farklı arayüz |

---

## 6. Birim ekonomisi — ölçülmüş

Maliyetin **tamamı köken kurtarmada ve içerik başına bir kezlik.** Sonraki her dağıtım
hesabı milisaniyeler mertebesinde.

| Kalem | Ölçülen | Ne zaman ödenir |
|---|--:|---|
| Yükleme + köken kurtarma | 476–666 ms | İçerik başına **bir kez** |
| Emek Kartı üretimi | 6 ms | Her görüntülemede |
| Kampanya dağıtımı | 31 ms | Kampanya başına bir kez |
| İtiraz çözümü | 79 ms | İtiraz başına |
| Açılış (280 içerik, indeks önbellekli) | 16 ms | Süreç başına |

Depolama ek yükü (N-Emek'in içerik başına *eklediği*, görselin kendisi hariç):

| Veri | Boyut |
|---|--:|
| CLIP vektörü | 2.048 bayt |
| Algısal hash'ler + blok hash'leri | ~200 bayt |
| FAISS indeks girdisi | ~2,5 KB |
| Bağ kayıtları + kanıt JSON'u | değişken, demoda ~37 KB |

> **Varsayım (ölçüm değil):** bu ek yük içerik başına ~40 KB mertebesinde. Milyon içerik
> için ~40 GB — tek bir sunucunun diskine sığar. Para birimine çevirmedik çünkü bulut
> fiyatı sağlayıcıya ve bölgeye göre değişiyor; kararı etkileyen büyüklük mertebesi.

**Ölçek ekonomisinin yönü:** gelir kampanya havuzuyla doğrusal büyür, maliyet ise içerik
sayısıyla. İçerik başına maliyet sabit ve tek seferlik olduğu için, aynı içerik ne kadar
çok kampanyaya girerse birim maliyet o kadar düşer.

---

## 7. Neden sürdürülebilir

1. **Yeni davranış icat etmiyor.** Marka kampanyası zaten var olan bir uygulama; N-Emek
   yalnızca havuzun **bölünme kuralını** değiştiriyor.
2. **Teşvikler hizalı.** Üretici için remix artık kayıp değil; platform için üretici
   bağlılığı; marka için harcamasının nereye gittiğinin kanıtı.
3. **Maliyet tek seferlik.** İçerik bir kez işlenir, sonsuz kez dağıtıma girer.
4. **Katman olarak konumlanıyor.** Bağımsız bir sosyal ağ kurmuyor; N'Sosyal'in içine
   giriyor. Kimlik doğrulama bile ana platformun işi (bkz. `app/core/security.py`).

---

## 8. Benimseme yolu

| Aşama | Ne olur | Ölçülecek |
|---|---|---|
| 1 · Tek kampanya | Bir marka, sınırlı sayıda içerikle pilot | Zincirde kaç kaynak bulundu, kaç itiraz açıldı |
| 2 · Üretici tarafı | "İçeriğin şurada kullanılmış" bildirimi | Üreticinin platformda kalma oranı |
| 3 · Platform geneli | Kampanya dışı gelir de zincire bölünür | Yanlış atıf oranı ölçekte korunuyor mu |
| 4 · Dışa açılma | Atıf API'si üçüncü taraflara | Sorgu hacmi ve gecikme |

Her aşama bir öncekinin ölçümüne bağlı. Bu sıra, sistemin en riskli varsayımını (ölçekte
yanlış atıf oranı) en ucuz yerde sınıyor.

---

## 9. Alternatifler ve neden yetmiyor

| Yaklaşım | Neden tek başına yetmiyor |
|---|---|
| **Elle atıf / etiketleme** | İyi niyete bağlı; kırpma ve ekran görüntüsü zinciri koparıyor |
| **Yalnızca C2PA** | Metadata silinince zincir de gidiyor — ekran görüntüsü bunu bir tıkla yapıyor |
| **Yalnızca filigran** | Kırpmaya dayanmıyor; tek başına kapsama ölçemiyor |
| **Yalnızca benzerlik araması** | Kaynağı *bulur* ama **ne kadarının kullanıldığını ölçemez**; pay hesabı için yetersiz |
| **Telif takip şirketleri** | İhlal tespiti ve kaldırma odaklı; paylaşım ve remix ekonomisi için tasarlanmamış |

N-Emek'in farkı beş yolu birden kullanıp **kararı ölçüme bağlaması**: kaynağı bulmak
değil, kullanılan oranı ölçmek.

---

## 10. Riskler ve karşı önlemler

| Risk | Karşı önlem | Durum |
|---|---|---|
| Yanlış atıf birine haksız ödeme yapar | Eşikler yanlış atıfı kaçırılmış atıfa tercih edecek şekilde ayarlı; ölçülen yanlış atıf **%0,86** | Ölçüldü (`DEGERLENDIRME.md`) |
| Ölçüm yanlış çıkarsa üretici mağdur olur | İtiraz hakkı: daha hassas dedektörle yeniden ölçüm, sonuç değişirse zincir güncellenir | Çalışıyor |
| Sistem karar veremezse | İnsan moderatöre yükseltilir ve bu gizlenmez | Çalışıyor |
| Remix üreticisi cezalandırılmış hisseder | Üretici tabanı %20 garanti | Kuralda |
| Ölçekte maliyet | Maliyet içerik başına tek seferlik; indeks IVF-PQ/HNSW'ye taşınabilir | Yol haritasında (`MIMARI.md` §6) |
| Kötüye kullanım: sahte kaynak beyanı | Beyan pay vermiyor — **ölçüm** veriyor | Tasarımda |

---

## 11. Kanıtlanan ve varsayılan

Dürüstlük için ayrı yazıyoruz.

**Kanıtlanan (ölçüldü, çalışan sistemde):**
- Zincir kurma ve ölçme: Top-1 %98,7 · yanlış atıf %0,86 · kapsama MAE 0,0241
- Havuzun zincire bölünmesi: ₺50.000 tamamen dağıtıldı, kayıtları denetlenebilir
- Kampanya komisyonu: ₺5.000 (%10)
- Maliyet: içerik başına bir kez 476–666 ms; dağıtım 31 ms

**Varsayılan (henüz ölçülmedi):**
- Markanın bu modele bugünküyle aynı bütçeyi ayıracağı
- Üreticinin platformda kalma oranının artacağı
- Ölçekte (milyon içerik) yanlış atıf oranının korunacağı
- Bulut maliyetinin TL karşılığı

İlk üç varsayım §8'deki pilot aşamalarında ölçülebilir; dördüncüsü altyapı seçimine bağlı.
