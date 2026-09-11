# Mentörlük — Görüşme Hazırlığı ve Kayıt

Şartname takvimi mentörlük sürecini "2–7 Eylül" olarak duyurmuştu; ilk mentör görüşmesi
resmî e-postayla **12 Eylül Cumartesi 13:00–15:00**'e taşındı. Bu, final teslim
tarihinden (14 Eylül 17:00) yalnızca **36 saat önce**. Bu belge o pencerede azami değer
çıkarmak için var: görüşme öncesi anlatım + demo sırası, görüşme sırasında doldurulacak
kayıt tablosu, görüşme sonrası bu kaydın iş listesine dönüştürülme kuralı.

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
> İkincisi, demo videosu ve tasarlanmış sunum dosyası henüz üretilmedi; içerik hazır,
> üretim bu hafta sonu."

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
2. **Anlatım önceliği.** "Jüri 8–10 dakikada tek bir şey hatırlayacaksa bu 'ölçüm'
   iddiası mı olmalı, yoksa 'adil gelir paylaşımı' vaadi mi? Hangisi bu yarışmada daha
   çok karşılık buluyor?"
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

## 4 · Geri bildirim kayıt tablosu

Görüşme *sırasında* doldurulur — not tutan kişi ekran paylaşımını yapan kişiden farklı
olsun.

| # | Mentör ne dedi | Kim söyledi | Etkilediği kalem | Aksiyon | Süre | Karar |
|---|---|---|---|---|---|---|
| | | | | | | |
| | | | | | | |
| | | | | | | |
| | | | | | | |
| | | | | | | |

**Görüşme biter bitmez (15:00–16:00 bloğunda), her satır için:**
- Ya bu planın **§4 UI/UX bulguları** veya **§5/§6 final paketi** bölümüne bir iş
  maddesi olarak eklenir,
- Ya da burada **gerekçesiyle reddedilir** ("mentör X dedi, ama Y nedeniyle 36 saatlik
  pencerede yapmıyoruz") — sütunun boş kalması kabul edilmez; her geri bildirim ya
  ürüne girer ya da neden girmediği yazılı kalır.

Yeni maddeler eklenirse `docs/PLAN.md`'deki Faz 4b iş listesi bu tablodan güncellenir.

---

## 5 · Görüşme sonrası kontrol

- [ ] Tablo tamamen dolduruldu (boş satır kalmadı)
- [ ] Her satır bir iş maddesine bağlandı veya reddedildi
- [ ] `docs/PLAN.md` Faz 4b güncellendi
- [ ] Ekip içi 5 dakikalık senkron: kim hangi maddeyi alıyor (§4 UI/UX vs. §5 video vs. §6 sunum)
