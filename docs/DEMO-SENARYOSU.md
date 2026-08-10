# Demo Videosu — Çekim Senaryosu

**Hedef:** 4 dakika 30 saniye, Türkçe anlatım, ekran kaydı.
**Anlatının omurgası:** kaynağı *bulmak* değil, kullanılan oranı **ölçmek**.

Replikler olduğu gibi okunabilir. Ekranda görülecek her sayı gerçek demo verisinden;
hiçbiri montajla değiştirilmemeli.

---

## Çekim öncesi kontrol listesi

Demonun canlı çökmesi, videonun kendisinden daha pahalıya mal olur.

```bash
docker compose up --build -d          # iki kapsayıcı da "healthy" olana kadar bekleyin
curl -s http://localhost:8000/api/health
```

- [ ] `indexed_contents: 3` ve `c2pa_signing: true` dönüyor mu
- [ ] `http://localhost:5173` açılıyor, akışta **üç** gönderi var
- [ ] Üstteki kullanıcı seçici **Ayşe Yılmaz**'da (itiraz sahnesi buna bağlı)
- [ ] "Bulduğum kare" gönderisinin geliri **₺4.200** — değiştiyse Gelir kutusundan geri alın
- [ ] Tarayıcı tam ekran, yer imleri çubuğu kapalı, bildirimler susturulmuş
- [ ] Ekran çözünürlüğü 1920×1080, tarayıcı yakınlaştırması **%100**
- [ ] Kayıt öncesi bir prova turu atın: fare hareketleri yavaş ve kararlı olmalı

> **Kritik:** Kayıt sırasında yeni içerik yüklemeyin. Yükleme zinciri değiştirir ve
> aşağıdaki bütün sayılar kayar. Yükleme göstermek isterseniz en sona bırakın.

---

## Sahne 1 — Problem · 0:00–0:25 (25 sn)

**Ekran:** Akış sayfası, sakin bir kaydırma.

> "Bir fotoğraf çekiyorsunuz. Biri onu kırpıp üstüne yazı ekliyor. Bir başkası o hâlinin
> ekran görüntüsünü alıp paylaşıyor. Üçüncü paylaşımda içerik binlerce kez görülüyor,
> marka sponsorluğu geliyor — ve sizin adınız hiçbir yerde yok.
>
> Sorun kötü niyet değil: zincir **teknik olarak kopuyor.** Ekran görüntüsü, içeriğin
> kimliğini tek tıkla siliyor."

**Yönerge:** Bu 25 saniyede ekran hareketi az olsun; izleyici sesi dinlesin.

---

## Sahne 2 — Çözüm, tek cümle · 0:25–0:50 (25 sn)

**Ekran:** Akış sayfasındaki üç kart sırayla vurgulanır (fareyle üzerlerinde durun).

> "N-Emek, bu zinciri geri kuran bir emek katmanı. Ayırt edici yanı şu: kaynağı
> **bulmakla** yetinmiyor, o kaynağın türev içerikte **ne kadar** kullanıldığını
> ölçüyor.
>
> Ekranda gördüğünüz üç gönderi aslında tek bir zincir: Ayşe'nin fotoğrafı, Burak'ın
> remixi, Ceyda'nın paylaşımı."

---

## Sahne 3 — Kritik an: kimliği silinmiş içerik · 0:50–1:45 (55 sn)

**Ekran:** "Bulduğum kare" → **Emek Kartı** → Köken paneli.

**Aksiyon:** Kartın "Emek Kartı →" bağlantısına tıklayın, Köken panelinde durun.

> "Ceyda'nın paylaştığı bu içerik sisteme 'kaynağı yokmuş' gibi girdi. Ekran görüntüsü
> alındığı için içerik kimliği silinmişti.
>
> Panelde yazan tam olarak bu: **yüklenen dosyada kimlik yoktu.** Ama sistem kaynağı yine
> de buldu — üstelik iki tanesini.
>
> Nasıl? Sırayla denedi: içerik kimliği yok, dosya özeti tutmuyor. Sonra piksellere
> gömülü görünmez filigranı okudu, algısal parmak izi ve görsel benzerlikle adayları
> daraltı, ve son adımda geometrik olarak doğruladı.
>
> Güven: **sıfır virgül doksan sekiz.**"

**Yönerge:** "Yüklenen dosyada kimlik / yoktu" ve "Yayınlanan sürüm / imzalandı"
alanlarını fareyle işaret edin. Güven rozetinde bir saniye durun.

---

## Sahne 4 — Payın gerekçesi · 1:45–2:45 (60 sn)

**Ekran:** Emek Kartı, pay dağılımı. **Ayşe Yılmaz** satırına tıklayıp açın.

> "Gönderi dört bin iki yüz lira kazandı. Kart bunu kime, neden verdiğini gösteriyor.
>
> Ayşe zincirde iki adım geride ama en büyük payı o alıyor: yüzde altmış sekiz virgül
> bir. Sebebi ekranda yazıyor.
>
> Satırı açalım. **Kapsama yüzde seksen beş virgül iki** — bu tahmin değil, ölçüm.
> **Güven sıfır virgül doksan beş. Sönümleme sıfır virgül seksen beş**, çünkü zincirde
> iki adım geride.
>
> Ve altındaki satır, bu üç sayıyı nasıl birleştirdiğimizi gösteriyor:
> pay eşittir kapsama çarpı güven çarpı sönümleme.
>
> Hiçbir rakam gerekçesiz gelmiyor."

**Yönerge:** Formül satırının üzerinde iki saniye durun. Bu, videonun en önemli karesi.

---

## Sahne 5 — Ölçüm görünür · 2:45–3:20 (35 sn)

**Ekran:** Aşağı kaydırın, **Burak Demir** satırına tıklayın → "Ölçülen bölge" paneli.

> "Peki 'ölçtük' derken ne demek istiyoruz? Bakın.
>
> Solda Burak'ın içeriği, sağda Ceyda'nın gönderisi. Yeşil alan, ölçümle o kaynaktan
> geldiği **doğrulanmış** piksel bölgesi. Kararan yerler Burak'tan gelmiyor.
>
> Sağ altta yazıyor: ölçülen kullanılan alan **yüzde on iki virgül iki.** Burak'ın
> gönderide toplam görünen oranı yüzde doksan yedi — ama bunun büyük kısmı zaten
> Ayşe'den geliyor. Her tarafa yalnızca **kendi kattığı** pikseller yazılıyor, yoksa
> aynı emek iki kez ödüllendirilirdi."

**Yönerge:** Maskeli görsele yakınlaşın. "Eşleşen bölgeyi vurgula" onay kutusunu bir kez
kapatıp açın — farkı izleyici görsün.

---

## Sahne 6 — Zincir · 3:20–3:40 (20 sn)

**Ekran:** Aşağı kaydırın, Atıf zinciri paneli.

> "Zincirin tamamı burada. Ayşe'den Burak'a yüzde seksen yedi, Burak'tan Ceyda'ya
> yüzde doksan yedi. Ok yönü türetme yönü. Kesikli bir çizgi görürseniz, o bağ henüz
> onaylanmamış demektir — sistem 'sahibi budur' demiyor, kanıtıyla birlikte **öneri**
> sunuyor."

---

## Sahne 7 — İtiraz · 3:40–4:05 (25 sn)

**Ekran:** Ayşe'nin satırına dönün, "Bu paya itiraz et" düğmesini gösterin. **Tıklamayın.**

> "Katılmıyorsanız itiraz edebilirsiniz. İtiraz, bağı daha hassas bir dedektörle yeniden
> ölçtürüyor. Sonuç değişirse zincirin **tüm payları** güncelleniyor.
>
> Dikkat edin: bu düğme yalnızca Ayşe'nin satırında var. İtirazı yalnızca payın sahibi
> açabilir; başkası denerse sunucu reddediyor.
>
> Ölçüm yine sonuç veremezse karar insana bırakılıyor. Sistem karar veremediği yeri
> gizlemiyor."

> **Yönerge:** İtirazı gerçekten göndermeyin — demo verisindeki payları değiştirir ve
> sonraki çekimlerde sayılar tutmaz. Göstermek isterseniz en sona bırakın.

---

## Sahne 8 — Marka tarafı · 4:05–4:25 (20 sn)

**Ekran:** Kampanyalar sayfası.

> "Marka tarafında da aynı mantık. Elli bin liralık ödül havuzu, son paylaşana değil,
> ölçülmüş katkıya göre zincirin tamamına bölünüyor.
>
> Bu kampanyada Ayşe otuz dört bin beş yüz lira aldı — **bir** içerik yükleyip hiç remix
> yapmadan. Çünkü içeriği zincirde yaşıyor ve bu ölçüldü."

---

## Sahne 9 — Kapanış · 4:25–4:30 (5 sn)

**Ekran:** Akış sayfasına dönün.

> "N-Emek. Emek görünür olsun diye — tahminle değil, ölçümle."

---

## Anlatım notları

- **Tempo:** dakikada ~140 kelime. Yukarıdaki metin bu tempoya göre yazıldı.
- **Sayıları okurken yavaşlayın.** "Yüzde seksen beş virgül iki" acele okunursa
  anlaşılmıyor.
- **Fare imleci anlatımı takip etsin.** Söylediğiniz şeyin üzerinde durun; rastgele
  gezinmeyin.
- **Sessizlik iyidir.** Sahne geçişlerinde yarım saniye boşluk bırakın.

## Süre daraltma (3 dakikaya inmek gerekirse)

Şu sırayla kısaltın — en az değer kaybettiren üstte:

1. Sahne 6 (zincir) → 20 sn yerine 10 sn
2. Sahne 8 (marka) → 20 sn yerine 12 sn
3. Sahne 1 (problem) → 25 sn yerine 15 sn

**Asla kısaltmayın:** Sahne 4 (payın gerekçesi) ve Sahne 5 (ölçüm görünür). Projenin
ayırt edici iddiası bu iki sahnede.

## Videoda söylenmemesi gerekenler

| Söylemeyin | Neden |
|---|---|
| "Yapay zekâ kaynağı buluyor" | Model aday üretiyor, kararı geometrik ölçüm veriyor |
| "Sistem sahibini buluyor" | Sistem öneri sunuyor; bu ayrım projenin etik omurgası |
| "%100 doğru" | Ölçülen Top-1 %98,7; yanlış atıf %0,86 — rakamı olduğu gibi söyleyin |
| "Blokzincir" | Projede yok |

## Kayıt sonrası

- [ ] Ses seviyesi eşitlenmiş, nefes sesleri temizlenmiş
- [ ] Ekrandaki her sayı anlatılanla **birebir** aynı
- [ ] Altyazı eklendi (jüri sessiz izleyebilir)
- [ ] Süre 3–5 dakika aralığında
