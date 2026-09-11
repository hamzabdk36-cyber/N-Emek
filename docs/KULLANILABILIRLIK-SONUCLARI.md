# Kullanılabilirlik Testi Sonuçları

> Bu belge elle düzenlenmez. Ham kayıtlar
> `data/kullanilabilirlik/oturumlar.json` içindedir; buradaki her türetilmiş sayı
> `scripts/kullanilabilirlik_sonuclari.py` tarafından hesaplanır.

## Koşum bilgileri

| | |
|---|---|
| Koşum türü | Dış katılımcı |
| Tarih aralığı | 20-22 Ağustos 2026 |
| Oturumu yöneten | Takım üyesi — beş oturumun tamamı aynı moderatör |
| Prototip sürümü (commit) | e1db5d9 |
| Ortam | iPhone 13 Safari · MacBook Air M2 Chrome 124 · Windows 11 Edge 125 · Galaxy A34 Chrome · Redmi 14 Chrome — beş oturumun üçü dokunmatik |
| Katılımcı sayısı | **5** |

## Katılımcılar

İsim yazılmaz. Tarama soruları protokol §"Tarama soruları"nda.

| Kod | Profil | Haftalık paylaşım | Düzenleyip paylaştı | Atıf aracı deneyimi | Cihaz |
|---|---|---|---|---|---|
| K1 | Sıradan paylaşan | 1-2 kez, genelde hikâye | Evet, kaynak belirtmeden | Hayır | iPhone 13 · Safari |
| K2 | İçerik üreticisi | 5-6 kez, Reels ve fotoğraf | Evet, genelde kaynak etiketi koyuyor | Evet, Creative Commons arama filtreleri | MacBook Air M2 · Chrome 124 |
| K3 | Marka / topluluk yöneticisi | 10'dan fazla, marka hesabı | Evet, izin ve etiketle | Evet, telif kontrolü için SaaS araçları | Windows 11 · Edge 125 |
| K4 | Sıradan paylaşan | Ayda bir civarı | Hayır, yalnızca hikâyede paylaştı | Hayır | Samsung Galaxy A34 · Chrome |
| K5 | İçerik üreticisi | 4-5 kez, fotoğraf serisi | Evet, kaynak belirtmeye çalışıyor | Hayır, elle etiketliyor | Redmi 14 · Chrome |

Dokunmatik cihazda koşulan oturum: **3** / 5

## Görev sonuçları

Başarı: **T** tam · **Y** yardımla · **B** başarısız (3 dk doldu).
Başarısız görevlerde süre 3 dakikalık sınıra (180 sn) sabitlenir; ortalamalar bu
değerle hesaplanır, yani gerçek süreyi değil **en iyi ihtimali** gösterir.

### Görev 1 — Akıştan türetilmiş içerik bul · hedef 45 sn

| | K1 | K2 | K3 | K4 | K5 | Ortalama |
|---|---|---|---|---|---|---|
| Başarı | T | T | T | Y | T | 4/5 tam |
| Süre (sn) | 38 | 24 | 30 | 52 | 20 | 32,8 |
| Yanlış tıklama | 2 | 1 | 0 | 6 | 0 | 1,8 |

- **K1:** "Türetilmiş rozeti olan bir gönderi var, galiba bu."
- **K2:** "Türetilmiş rozeti hemen gördüm."
- **K3:** "Rozetler ana sayfada net, türetilmiş olanı seçtim."
- **K4:** "Şu turuncu yazılı olan mı?" Rozeti kendi başına ayırt edemedi.
- **K5:** "Türetilmiş rozeti ana sayfada göze çarptı."

### Görev 2 — Payın gerekçesini kendi cümlesiyle söyle · hedef 90 sn

> Oturumun en önemli görevi: açıklanabilirlik iddiası burada sınanıyor.

| | K1 | K2 | K3 | K4 | K5 | Ortalama |
|---|---|---|---|---|---|---|
| Başarı | Y | T | T | B | T | 3/5 tam |
| Süre (sn) | 88 | 55 | 80 | 180 | 61 | 92,8 |
| Yanlış tıklama | 4 | 2 | 3 | 5 | 2 | 3,2 |

- **K1:** Kurduğu cümle: "Para bölünmüş, çünkü birisi fotoğrafı çekmiş, öbürü düzenlemiş… e haliyle çekene daha çok düşmüş." Gerekçeyi kısmen kurdu, ölçüme değinmedi.
- **K2:** Kurduğu cümle: "Fotoğrafı çeken kişiyle düzenleyen kişi arasında emek oranı farklı; o yüzden biri daha yüksek pay almış."
- **K3:** Kurduğu cümle: "Görselin sahibi ile editör arasında katkı oranına göre bölünmüş; o yüzden asıl fotoğrafçı daha yüksek pay almış."
- **K4:** "Para bölünmüş işte, biri daha çok almış. Nedenini tam bilmiyorum." Forma hedef süre (90 sn) yazılmış; protokol gereği 180 alındı.
- **K5:** Kurduğu cümle: "Fotoğrafı çeken kişiyle düzenleyen kişinin emeği farklı; sistem buna göre pay oranı vermiş."

### Görev 3 — Ölçülen bölgeyi göster · hedef 60 sn

| | K1 | K2 | K3 | K4 | K5 | Ortalama |
|---|---|---|---|---|---|---|
| Başarı | B | T | T | B | T | 3/5 tam |
| Süre (sn) | 180 | 40 | 52 | 180 | 44 | 99,2 |
| Yanlış tıklama | 5 | 1 | 2 | 6 | 1 | 3,0 |

- **K1:** Maskeyi ters yorumladı: "Sarı yer değiştirilen alan herhalde." Forma gerçek süre yerine hedef süre (60 sn) yazılmış; protokol gereği 180 alındı.
- **K2:** Maskeyi doğru okudu: "Ölçülen yer kaynaktan gelen alan, yani orijinal görüntünün korunduğu bölge."
- **K3:** Maskeyi doğru okudu: "Ölçülen bölge kaynaktan gelen alan; değiştirilen yer değil."
- **K4:** Maskeyi ters yorumladı: "Mavi yer silinen bölge mi?" Forma hedef süre (60 sn) yazılmış; protokol gereği 180 alındı.
- **K5:** Maskeyi doğru okudu: "Ölçülen bölge kaynaktan gelen alan, yani orijinalin korunduğu kısım."

### Görev 4 — Remix üretip yayınla · hedef 180 sn

| | K1 | K2 | K3 | K4 | K5 | Ortalama |
|---|---|---|---|---|---|---|
| Başarı | T | T | T | B | T | 4/5 tam |
| Süre (sn) | 150 | 115 | 175 | 180 | 130 | 150,0 |
| Yanlış tıklama | 6 | 3 | 5 | 8 | 4 | 5,2 |

- **K1:** Geri alma ihtiyacı duydu. Kaynağa pay gittiğini yayın öncesi fark etti: "biraz şaşırdım ama sorun değil."
- **K2:** Geri almaya ihtiyaç duymadı. Kaynak payını yayın öncesi gördü, şaşırmadı. Kırpma yerine yazı eklemeyi denedi, arayüz izin verdi.
- **K3:** Geri alma ihtiyacı duydu. "Kaynağa pay gittiğini gördüm ama oranın hangi işleme göre değiştiğini tam çözemedim."
- **K4:** Geri alma ihtiyacı duydu. Kaynağa pay gideceğini görünce tedirgin oldu: "bu parayı mı alacak?" ve yayınlamaktan vazgeçti.
- **K5:** Geri almaya ihtiyaç duymadı. "Kaynak payı otomatik eklendi, mantıklı geldi."

### Görev 5 — Elindeki görselin kaynağını bul · hedef 90 sn

| | K1 | K2 | K3 | K4 | K5 | Ortalama |
|---|---|---|---|---|---|---|
| Başarı | Y | T | Y | B | Y | 1/5 tam |
| Süre (sn) | 85 | 50 | 88 | 180 | 74 | 95,4 |
| Yanlış tıklama | 3 | 2 | 4 | 5 | 3 | 3,4 |

- **K1:** Üstteki eşleşmeyi buldu ama kanıt satırlarını sonuç sandı.
- **K2:** Aşamaları kendi cümlesiyle özetledi: "yükleme, eşleşme, kaynak." Bunlar ekrandaki etiketler değil, katılımcının kendi özeti.
- **K3:** "Kanıt aşamaları mantıklı ama 'algı' terimi sektörde farklı kullanıldığı için kafa karıştırdı."
- **K4:** Kaynak Bul ekranını bulamadı; aşama adlarını değerlendiremedi. Forma hedef süre (90 sn) yazılmış; protokol gereği 180 alındı.
- **K5:** "Genel olarak anlaşıldı ama 'hash' benzeri teknik ifade yadırgattı." Yükleme sonrası önizleme aradı.

### Görev 6 — Bir paya itiraz et · hedef 90 sn

| | K1 | K2 | K3 | K4 | K5 | Ortalama |
|---|---|---|---|---|---|---|
| Başarı | B | T | T | Y | T | 3/5 tam |
| Süre (sn) | 180 | 70 | 65 | 85 | 58 | 91,6 |
| Yanlış tıklama | 2 | 1 | 2 | 7 | 2 | 2,8 |

- **K1:** İtirazı şikâyet sandı: "mesaj mı atıyorum?" Forma hedef süre (90 sn) yazılmış; protokol gereği 180 alındı.
- **K2:** "İtiraz edince sistem yeniden ölçüm başlattı, şikâyet gibi değil."
- **K3:** "İtiraz sonucu yeniden ölçüm olduğunu anladım, ancak süreç biraz uzun."
- **K4:** İtirazı şikâyet sandı; yeniden ölçüm kavramını moderatör söyleyince anladı.
- **K5:** "İtiraz edince sistem yeniden ölçüm başlattı; doğru anladım."

### Toplu görev tablosu

| Görev | Tam | Yardımla | Başarısız | Ortalama süre | Hedef |
|---|--:|--:|--:|--:|--:|
| 1 · Akıştan türetilmiş içerik bul | 4 | 1 | 0 | 32,8 sn | 45 sn |
| 2 · Payın gerekçesini kendi cümlesiyle söyle | 3 | 1 | 1 | 92,8 sn ⚠ | 90 sn |
| 3 · Ölçülen bölgeyi göster | 3 | 0 | 2 | 99,2 sn ⚠ | 60 sn |
| 4 · Remix üretip yayınla | 4 | 0 | 1 | 150,0 sn | 180 sn |
| 5 · Elindeki görselin kaynağını bul | 1 | 3 | 1 | 95,4 sn ⚠ | 90 sn |
| 6 · Bir paya itiraz et | 3 | 1 | 1 | 91,6 sn ⚠ | 90 sn |

**Görev başarı oranı:** 18/30 tam = **%60,0** (yardımla tamamlananlar dahil edilirse %80,0).
Rapora giren sayı, yardımsız tamamlanan orandır — daha katı olan budur.

## SUS

Ham cevaplar (1 = kesinlikle katılmıyorum … 5 = kesinlikle katılıyorum):

| Madde | K1 | K2 | K3 | K4 | K5 |
|---|---|---|---|---|---|
| 1 · Sık kullanmak isterim | 3 | 4 | 3 | 2 | 4 |
| 2 · Gereksiz karmaşık | 3 | 1 | 2 | 4 | 2 |
| 3 · Kullanımı kolaydı | 3 | 5 | 4 | 2 | 4 |
| 4 · Teknik destek gerekir | 2 | 1 | 2 | 5 | 1 |
| 5 · İşlevler bütünleşik | 3 | 4 | 3 | 2 | 4 |
| 6 · Tutarsızlık fazla | 3 | 2 | 2 | 4 | 2 |
| 7 · Çabuk öğrenilir | 3 | 4 | 4 | 2 | 5 |
| 8 · Hantal | 4 | 1 | 2 | 5 | 2 |
| 9 · Kendime güvendim | 2 | 5 | 3 | 1 | 4 |
| 10 · Önce çok şey öğrenmem gerekti | 4 | 1 | 2 | 5 | 1 |

| | K1 | K2 | K3 | K4 | K5 | **Ortalama** |
|---|---|---|---|---|---|---|
| SUS puanı | 45,0 | 90,0 | 67,5 | 15,0 | 82,5 | **60,0** |

Puanlama: tek numaralı maddelerde `cevap − 1`, çift numaralı maddelerde
`5 − cevap`; on değer toplanıp 2,5 ile çarpılır. Bu bir yüzde değildir.

Hedef ≥ 68 (sektör ortalaması). Sonuç: **60,0** — hedefin altında.

## Açık sorular

**"Bu uygulama ne yapıyor?"** — her katılımcının cevabı birebir:

- K1: "Fotoğraf paylaşma uygulaması ama kaynağın kim olduğunu ve paranın nasıl bölüşüldüğünü gösteriyor."
- K2: "Görselin kaynağını doğrulayan ve gelir paylaşımını şeffaf yapan bir platform."
- K3: "İçerik kaynağını ve gelir paylaşımını şeffaflaştıran bir araç; markalar için lisans takibi faydalı olur."
- K4: "Fotoğraf atıp kaynağını buluyor ama ben çok zorlandım."
- K5: "Görsel kaynağını doğrulayan ve emek payını gösteren bir uygulama."

**"En kafa karıştırıcı şey neydi?"**

- K1: "Para bölümü çok karışık geldi. Oranların neden öyle olduğunu anlamadım."
- K2: "En kafa karıştıran kısım yok gibi; sadece bazı terimler açıklansa daha iyi olur."
- K3: "Raporlama tarafı yok gibi; toplu içerik girişinde nasıl davranacağı belirsiz."
- K4: "Neredeyse her şey kafa karıştırıcıydı; özellikle para oranları."
- K5: "Kanıt ekranındaki teknik terimler biraz ağır; normal kullanıcıya açıklama gerek."

**"Kendi içeriğinizi yükler miydiniz? Neden?"**

- K1: "Bilmiyorum, belki. Kaynak işi güzel ama başkalarıyla uğraşmak istemem."
- K2: "Evet, çünkü hem kaynak güvenliği hem de gelir paylaşımı net."
- K3: "Evet, özellikle kullanıcı üretimli içerik paylaşırken kaynak ve hak yönetimi için."
- K4: "Hayır, çünkü çok teknik geliyor ve yanlış bir şey yapmaktan korkarım."
- K5: "Evet, çünkü kaynak bulma kısmı işimi kolaylaştırır, ama mobil arayüz biraz küçük."

## Bulgular

Ağırlık sırasına göre. Düzeltilenler `ERISILEBILIRLIK.md`'deki
*bulgu → değişiklik → doğrulama* deseniyle kaydedilir.

| # | Bulgu | Kaç katılımcı | Ağırlık | Durum |
|--:|---|--:|---|---|
| 1 | Kaynak Bul ekranı yardımsız bulunamıyor: beş katılımcının yalnızca biri görevi kendi başına tamamladı | 4 | Yüksek | Düzeltildi (11 Eyl 2026) — akışın başına sabit giriş eklendi, yeniden ölçülmedi |
| 2 | İtiraz bir şikâyet kutusu sanılıyor; yeniden ölçüm başlattığı ekrandan anlaşılmıyor | 2 | Yüksek | Düzeltildi (11 Eyl 2026) — düğme metni ve üç adımlık önizleme eklendi, yeniden ölçülmedi |
| 3 | Ölçülen bölge maskesi ters okunuyor: parlak alan kaynaktan gelen bölge değil, değiştirilen bölge sanılıyor | 2 | Yüksek | Düzeltildi (11 Eyl 2026) — kaynak adını söyleyen lejant eklendi, yeniden ölçülmedi |
| 4 | Pay oranlarının hangi ölçüme göre değiştiği anlaşılmıyor; kullanıcı sayıyı görüyor, gerekçeyi bağlayamıyor | 3 | Yüksek | Düzeltildi (11 Eyl 2026) — düz Türkçe gerekçe cümlesi eklendi, ilk kaynak satırı varsayılan açık, yeniden ölçülmedi |
| 5 | Kanıt satırlarındaki teknik terimler ağır geliyor ("algı", "hash"); bir katılımcı kanıt satırını sonuç sandı | 3 | Orta | Düzeltildi (11 Eyl 2026) — terimler sadeleştirildi, ayrı sonuç kutusu eklendi, yeniden ölçülmedi |
| 6 | Mobilde metinler küçük okunuyor; iki katılımcı ekranı yakınlaştırma ihtiyacı duydu | 2 | Orta | Düzeltildi (11 Eyl 2026) — küçük punto mobilde büyütüldü, yeniden ölçülmedi |
| 7 | Marka profili toplu işlem, raporlama ve dışa aktarma bekliyor; bunlar prototipte yok | 1 | Düşük | Kapsam dışı — 36 saatlik pencerede yüksek ağırlıklı bulgular önceliklendirildi, sonraki sürüm maddesi (IS-MODELI.md) |

## Bu sonuçların sınırları

- **5 katılımcı istatistik vermez.** SUS puanı bir eğilim göstergesidir;
  güven aralığı hesaplanacak kadar örneklem yok.
- **Katılımcılar tanıdık çevreden geliyor.** Nezaket yanlılığı SUS'u yukarı
  çeker. Görev başarısı ve süre bu yanlılıktan daha az etkilenir; asıl ağırlık
  onlarda.

