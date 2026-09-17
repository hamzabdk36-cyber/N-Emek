# Mentörlük — Görüşme Hazırlığı ve Kayıt

Şartname takvimi mentörlük sürecini "2–7 Eylül" olarak duyurmuştu; ilk mentör görüşmesi
resmî e-postayla **12 Eylül Cumartesi 13:00–15:00**'e taşındı. Bu belge o görüşme için
hazırlandı: görüşme öncesi anlatım + demo sırası, görüşme sırasında doldurulacak kayıt
tablosu, görüşme sonrası bu kaydın iş listesine dönüştürülme kuralı.

**Güncelleme (12 Eylül, görüşme sonrası):** Görüşme, projeye özel bire bir bir mentörlük
değil, **22 takımın tamamının katıldığı genel bir tanışma ve idari soru-cevap turuydu**
(transkript: proje kökü dışında `../transkript-2026-09-12.md`). Bu yüzden §4'teki tablo
proje geri bildirimiyle değil, toplantıdan çıkan **bağlayıcı idari/biçimsel kararlarla**
dolduruldu. En önemli çıktı: final teslim tarihi şartnamedeki "14 Eylül 17:00" değil,
**sunum dosyasının 18 Eylül gecesi teslimi** — bkz. `CLAUDE.md` takvim notu,
`docs/PLAN.md` Faz 4c. Beklenen ikinci ve son genel toplantı **yapılmadı** (17 Eylül
itibarıyla); §6 bu yüzden "sorulacak sorular" listesi olmaktan çıkıp **cevapsız kalan
sorular ve aldığımız varsayımlar** listesine dönüştü.

## Toplantı bilgileri

| | |
|---|---|
| Tarih | 12 Eylül 2026 Cumartesi |
| Saat | 13:00–15:00 |
| Platform | Zoom — Toplantı Kimliği **819 6619 4277** · Parola **221522** |
| Bağlantı | https://us06web.zoom.us/j/81966194277 |

**Görüşme öncesi 30 dk (09:00–12:30 blok içinde):**
- `docker compose up --build -d` veya iki terminalle yerel çalıştırma — §1'deki [duman
  testi](../CLAUDE.md) tekrar koşulur, sistem canlı ayakta kanıtlanır.
- `curl localhost:8000/api/health` → `indexed_contents: 3` doğrulanır.
- Ekran paylaşımı önceden bir kez denenir (Zoom'da "ekranı paylaş" izni, sekme mi
  pencere mi paylaşılacağı önceden seçilir).

---

## 1 · Beş dakikalık anlatım metni

`docs/SUNUM.md`'deki 2–5. slaytların konuşma diline sıkıştırılmış hâli. Mentör görüşmesi
bir jüri sunumu değil, hızlı geri bildirim turu; bu yüzden slaytsız, doğrudan anlatılır.

> "N-Emek, TEKNOFEST İçerik Ekonomisi kategorisinde bir prototip. Çözdüğümüz sorun basit:
> bir fotoğraf kırpılıp üstüne yazı eklenip ekran görüntüsüyle paylaşıldığında ilk
> üreticinin emeği görünmez oluyor. Sorun kötü niyet değil — zincir teknik olarak
> kopuyor, ekran görüntüsü içerik kimliğini tek tıkla siliyor.
>
> Ayırt edici iddiamız şu: kaynağı *bulmak* değil, kullanılan içerik oranını *ölçmek*.
> Altı aşamalı bir köken kurtarma hattımız var — C2PA manifestinden başlayıp SHA-256,
> görünmez filigran, algısal parmak izi, görsel benzerlik modeli ve son olarak
> geometrik doğrulamaya kadar iniyor. Son aşama sadece 'bu kaynak mı' demiyor,
> homografi ve piksel doğrulamasıyla *ne kadarının* kullanıldığını ölçüyor.
>
> Bunu 6.400 sorguluk bir değerlendirmeyle test ettik: Top-1 doğruluk %98,7, F1 0,9753,
> yanlış atıf oranı %0,86. Alan oranı ölçüm hatası hedefin altında: 0,024, hedef 0,05.
>
> Katkı payı bu ölçüme dayanıyor — tahmine değil. Her rakamın altında gerekçesi var ve
> kullanıcı itiraz edebiliyor; sistem hiçbir zaman 'sahibi budur' demiyor, kanıtlı bir
> öneri sunuyor.
>
> Dürüst olmak gerekirse iki açığımız var: kullanılabilirlik testinde SUS puanımız
> 60 çıktı, hedefin (68) altında — yedi bulgu belirledik ve bugün-yarın kapatıyoruz.
> İkincisi, demo videosu henüz üretilmedi; içerik hazır, üretim bu hafta sonu."

*(Bu metin 12 Eylül görüşmesi için yazıldı ve o gün kullanıldı. Görüşme sonrası durum:
tasarlanmış sunum dosyası üretildi — `docs/gorseller/SUNUM.pdf` — yalnızca demo videosu
açık kaldı.)*

**Süre kontrolü:** yüksek sesle okunduğunda ~90 saniye; geri kalan zaman mentörün
sorularına ayrılır.

---

## 2 · Ekran paylaşımı demo sırası (6 dk)

`docs/DEMO-SENARYOSU.md`'nin canlı görüşmeye uyarlanmış kısaltması — replik metinleri
o dosyada birebir hazır, burada yalnızca sıra ve süre.

| Adım | Ekran | Süre | Vurgu |
|---|---|---|---|
| 1 | Akış | 20 sn | Üç gönderi: Ayşe orijinal, Burak remix, Ceyda ekran görüntüsü |
| 2 | Ceyda'nın Emek Kartı → Köken paneli | 60 sn | "Yüklenen dosyada kimlik yoktu" ama sistem iki kaynağı da buldu, güven 0,98 |
| 3 | Pay dağılımı → Ayşe satırını aç | 60 sn | Formül satırı: pay = kapsama × güven × sönümleme |
| 4 | Ölçülen bölge maskesi (Burak satırı) | 45 sn | Parlak = kaynaktan gelen, gri = üreticinin eklediği; "Kaynaktan gelen bölgeyi vurgula" kutusunu aç/kapat |
| 5 | Atıf zinciri grafiği | 20 sn | Ayşe → Burak → Ceyda, her bağda ölçülen oran |
| 6 | İtiraz kutusu (göster, **gönderme**) | 20 sn | Yalnızca payın sahibinde görünür; gönderilirse demo verisi bozulur |

**Yedek plan:** Zoom'da ekran paylaşımı veya localhost bağlantısı sorun çıkarırsa
`docs/gorseller/` altındaki on bir kare üzerinden aynı sıra anlatılır:
`02-emek-karti-koken.jpg` → `03-pay-gerekcesi.jpg` → `04-olculen-bolge.jpg` →
`06-atif-zinciri.jpg`.

---

## 3 · Mentöre sorulacak hedefli sorular

Genel "ne düşünüyorsunuz" sorusu değil — her biri doğrudan bir iş maddesine dönüşecek
şekilde nişanlı. Cevap alındıkça §4'teki tabloya not düşülür.

1. **Kullanılabilirlik.** "SUS 60,0 çıktı; en ağır bulgu, beş kişiden dördünün Kaynak
   Bul ekranını yardımsız bulamaması. İki gün içinde hangi tek değişiklik bu skoru en
   çok yukarı çeker — bilgi mimarisi mi, yoksa metin/etiket dili mi?"
2. **Anlatım önceliği.** "Jüri 15 dakikalık sunumdan tek bir şey hatırlayacaksa bu
   'ölçüm' iddiası mı olmalı, yoksa 'adil gelir paylaşımı' vaadi mi? Hangisi bu
   yarışmada daha çok karşılık buluyor?"
3. **İş modeli.** "Gelir modeli N'Sosyal komisyonu üzerine kurulu. Jüri
   sürdürülebilirlikte hangi soruyu soruyor — birim ekonomi mi, platform bağımlılığı mı?"
4. **Dürüst sınırlar.** "Bilinen sınırları (filigran kırpmaya dayanmaz, ödemesi olan
   içerik silinemez) raporda açıkça yazdık. Bu dürüstlük jüride artı mı, yoksa sunumda
   daha temkinli mi ifade edilmeli?"
5. **Prototip kalitesi.** "Docker ile tek komut çalışıyor. Jüri prototipi kendi
   makinesinde mi deneyecek, yoksa video üzerinden mi değerlendiriyor? Hangisine
   yatırım yapmalıyız?"
6. **Ölçek.** "SQLite + kaba kuvvet FAISS ile tek makinede çalışıyor. Jüri ölçeklenme
   sorusunu sorarsa, yol haritası anlatmak yeterli mi yoksa ölçüm mü bekleniyor?"

---

## 4 · Toplantı kararları kayıt tablosu

Görüşme proje bazlı bir mentörlük değil, genel bir idari soru-cevap turu olduğu için
bu tablo "mentör geri bildirimi" değil, **toplantıdan çıkan bağlayıcı kararları**
tutuyor (kaynak: `../transkript-2026-09-12.md`).

| # | Karar | Etkilediği kalem | Aksiyon | Karar |
|---|---|---|---|---|
| 1 | Sunum dosyası son teslim **18 Eylül gecesi**, şartnamedeki "14 Eylül" değil | Takvim | `CLAUDE.md`, `docs/PLAN.md` güncellendi | Uygulandı |
| 2 | Sunum süresi **15 dk + 2–3 dk canlı prototip** + jüri soruları | `docs/SUNUM.md` | Hedef süre notu güncellendi; içerik genişletmesi şablon sonrasına ertelendi | Uygulandı (kısmi) |
| 3 | Prototip **video olarak gösterilemez**, canlı çalıştırma zorunlu | `docs/DEMO-SENARYOSU.md` | Videonun rolü "ana gösterim"den "gömülü klip + yedek"e çekildi | Uygulandı |
| 4 | Sunum dosyası **zorunlu şablonla** hazırlanacak | `docs/SUNUM/` | Şablon 14 Eyl'de geldi; içerik 14 sayfaya taşındı, betikle üretiliyor (`docs/SUNUM/_PLAN.md`) | Uygulandı (15 Eyl); revizyon ve PDF sürüyor |
| 5 | Ulaşım/konaklama formu son gün **14 Eylül**, doldurmayan alana giremez | İdari | `docs/PLAN.md` Faz 4c'ye eklendi | Uygulandı (belge); form takımın kendi işi |
| 6 | 20 Eylül İstanbul'da, 09:00 kura, ~60-80 kişi, izleyici yok | Takvim, lojistik | `CLAUDE.md`, `docs/PLAN.md` Faz 6 güncellendi | Uygulandı |
| 7 | Şanlıurfa yalnızca **dereceye giren 3 takım** için (30 Eyl–4 Eki) | Takvim | Koşul belgelere eklendi | Uygulandı |
| 8 | AI kategorisinde lokalde çalışan model sonucu yeterli, deploy zorunlu değil | Ürün kararı | Değişiklik gerekmiyor — sistem zaten lokalde çalışıyor | Bilgi alındı |
| 9 | Kendi veri seti oluşturmak serbest | Ürün kararı | Değişiklik gerekmiyor | Bilgi alındı |
| 10 | İkinci (son) genel toplantı **~16 Eylül**, şablon sonrası | Takvim | §6'ya açık sorular eklendi | Uygulandı |

**Not:** Bu turda proje-özel bir teknik geri bildirim alınmadı (§3'teki hedefli sorular
bire bir bir mentöre değil, genel soru-cevap ortamına soruldu; görüşme kaydında
projeye özel bir yanıt yoktur). §6, bunun yerine 16 Eylül toplantısına taşınacak açık
soruları listeliyor.

---

## 5 · Görüşme sonrası kontrol

- [x] Tablo tamamen dolduruldu (boş satır kalmadı)
- [x] Her karar bir iş maddesine bağlandı
- [x] `docs/PLAN.md` Faz 4c güncellendi
- [x] Ekip içi senkron (15 Eyl): sunum Berra Özer, sistem ve canlı demo Hamza Budak

---

## 6 · Cevapsız kalan sorular ve aldığımız varsayımlar

**İkinci genel toplantı yapılmadı.** 12 Eylül toplantısında "~16 Eylül'de son bir tur
daha" denmişti; 17 Eylül itibarıyla böyle bir toplantı olmadı. Aşağıdaki sorular bu
yüzden hiç sorulamadı.

Cevapsız soruyla sahneye çıkılmaz. Her biri için **en kötü senaryo varsayımı** alındı ve
hazırlık ona göre yapıldı; varsayım yanlış çıkarsa hepsi *bizim lehimize* yanılır
(fazladan süre, çalışan internet, tanınan kurulum payı).

| Cevapsız soru | Varsayım | Buna göre yapılan |
|---|---|---|
| Canlı prototip 2 dk mı 3 dk mı | **2 dk** | Akış 2:00'a kurgulandı; +1:00'lık uzatma (itiraz → zincir → tampon) hazırda bekliyor — `DEMO-SENARYOSU.md` "3 dakika verilirse" |
| Jüri gösterimin içeriğini yönlendirecek mi | **Yönlendirebilir** | "Kendi görselimizle deneyelim" ve "yükleme/remix de gösterin" soru tablosunda cevaplı; Kaynak Bul kayıt yapmadığı için jürinin görseli demo verisini bozmuyor |
| Salonda internet var mı | **Yok** | `HF_HUB_OFFLINE=1` ile tam koşum ölçüldü (17 Eyl): model yerel önbellekten yükleniyor, sonuçlar birebir aynı. Değişken jüri gününde de verilecek |
| Kendi bilgisayarımıza geçiş için kurulum süresi tanınıyor mu | **Tanınmıyor** | Sistem sıra gelmeden ayakta ve **ısıtılmış** olacak; ilk sorgunun ~6–9 saniyesi sahnede değil, kulis sırasında harcanıyor |
| HDMI kablo/anahtarlayıcı salonda mı | **Getireceğiz** | Kendi kablomuz ve adaptörümüz çantada; Windows "Çoğalt" (Win+P) önceden ayarlı |
| Ekran çözünürlüğü / bağlantı tipi | **Bilinmiyor, düşük olabilir** | Düzen zaten duyarlı; mobil düzen açılırsa "devam et" talimatı arıza tablosunda |
| 15 dakika jüri sorularını içeriyor mu | **İçeriyor** | Sunum notları bu varsayımla kısa tutulmalı — Berra'ya iletilecek bulgu (`docs/SUNUM/_PLAN.md` "Süre" satırı) |
| Jüriye sunumun kopyası veriliyor mu | **Verilmiyor** | Punto kararı "perdeden okunur" varsayımıyla alınır; küçük punto riski Berra'nın B1/B2/B3 kararında |
| Bire bir proje geri bildirimi kanalı | **Olmayacak** | Geri bildirim beklemeden ilerliyoruz; açık kalan teknik sorular kendi ölçümlerimizle kapatıldı |

~~Şablonun başlık yapısı eski 17 slaytla örtüşüyor mu~~ → şablon geldi, içerik yeniden
kurgulandı (`docs/SUNUM/_PLAN.md`).
