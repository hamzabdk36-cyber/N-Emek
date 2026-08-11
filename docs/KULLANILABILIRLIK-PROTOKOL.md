# Kullanılabilirlik Testi Protokolü

Şartnamenin teslimat listesinde **kullanılabilirlik testi sonuçları** var
(`docs/PLAN.md`). Bu belge o testin nasıl koşulacağını tarif eder; sonuçlar
[`KULLANILABILIRLIK-SONUCLARI.md`](KULLANILABILIRLIK-SONUCLARI.md) dosyasına yazılır.

**Bu belgede sonuç yoktur.** Ölçüm gerçek katılımcılarla yapılmadan sonuç bölümü
doldurulmaz. Projenin kuralı burada da geçerli: hiçbir sayı elle uydurulmaz.

## Neden beş katılımcı

Nielsen'in klasik bulgusu: beş katılımcı kullanılabilirlik kusurlarının yaklaşık
%85'ini ortaya çıkarır, sonrası azalan getiri. Beş kişi *istatistik* için yeterli
değildir — SUS puanı bir eğilim göstergesidir, kesin bir ölçüm değil. Bu sınır
sonuç belgesinde de yazılı kalır.

## Kimler

Beş katılımcı, üç profilden:

| Profil | Kaç kişi | Neden |
|---|--:|---|
| İçerik üreticisi (düzenli paylaşan) | 2 | Ayşe ve Burak rollerinin gerçek karşılığı |
| Sıradan paylaşan (üretmeyen kullanıcı) | 2 | Ceyda rolü — kritik an bu kişide yaşanıyor |
| Marka / topluluk yöneticisi | 1 | Kampanya panelini yalnızca bu profil kullanıyor |

Roller [`KULLANICI-AKISLARI.md`](KULLANICI-AKISLARI.md) §1'deki aktörlerden geliyor.

**Dışarıda kalması gerekenler:** projeyi daha önce görmüş kişiler, takım üyeleri ve
takım üyelerinin projeyi anlattığı yakınları. Bir katılımcı "atıf" kavramını
oturumdan önce bizden duyduysa oturum geçersizdir — ölçmek istediğimiz tam olarak
bu kavramın ekrandan anlaşılıp anlaşılmadığı.

### Tarama soruları

Katılımcıya oturumdan önce sorulur, cevaplar sonuç belgesine yazılır:

1. Haftada kaç kez sosyal medyaya içerik yüklüyorsunuz?
2. Başkasının içeriğini düzenleyip (kırpma, filtre, yazı ekleme) paylaştığınız oldu mu?
3. Paylaştığınız bir içeriğin kaynağını bulmaya çalıştığınız oldu mu? Nasıl?
4. "İçerik atfı" veya "telif" konusunda daha önce bir araç kullandınız mı?
5. Bu projeyi veya N-Emek'i daha önce duydunuz mu? *(Evet ise katılımcı alınmaz.)*

## Ortam

- Prototip `docker compose up --build -d` ile ayağa kaldırılır, `http://localhost` üzerinden.
- Demo verisi yüklü olmalı: Ayşe'nin özgün karesi, Burak'ın remixi, Ceyda'nın ekran
  görüntüsü ve en az bir açık itiraz. (Kurulum: [`BASLARKEN.md`](../BASLARKEN.md).)
- Her katılımcı **sıfırdan aynı veriyle** başlar; oturum arası veri sıfırlanır.
- Katılımcının kendi cihazı değil, hazırlanmış tarayıcı kullanılır. Masaüstü tarayıcı
  varsayılan; en az bir oturum **dokunmatik cihazda** koşulur.
- Kayıt: ekran + ses. Yüz kaydı alınmaz.
- Oturum başına 35–40 dakika, görevler için 25 dakika.

## Onam

Kayıt başlamadan önce sözlü olarak okunur ve onayı kayda alınır:

> Bu oturumda N-Emek adlı bir prototipi denemenizi isteyeceğiz. **Sizi değil, arayüzü
> test ediyoruz** — takıldığınız her yer bizim için bir kusur, sizin için bir hata değil.
> Ekran ve sesiniz kaydedilecek; kayıt yalnızca takım içinde kullanılacak, yarışma
> teslimatında yalnızca isimsiz özet yer alacak. İstediğiniz an durabilir, kaydın
> silinmesini isteyebilirsiniz. Devam edelim mi?

Katılımcı adı sonuç belgesine yazılmaz; K1–K5 kodlarıyla anılır.

## Oturumu yöneten kişinin kuralları

1. **Yardım edilmez.** Katılımcı takıldığında beklenir. "Ne yapmaya çalışıyorsunuz?"
   ve "Şu an ne görmeyi bekliyordunuz?" dışında yönlendirme yok.
2. **Ekran adı söylenmez.** "Emek Kartı'na girin" denmez; görev senaryosu okunur, yolu
   katılımcı bulur. Bulamaması bulgudur.
3. Sesli düşünme hatırlatılır: "Aklınızdan geçeni sesli söyleyin."
4. Görev, başarı ölçütü sağlandığında ya da **3 dakikada** biter. Süre dolarsa görev
   *başarısız* işaretlenir ve katılımcıya doğru yol gösterilip bir sonrakine geçilir.
5. Katılımcının kullandığı kelimeler birebir not edilir — ekrandaki terimlerle
   arasındaki fark, en değerli bulgu türü.

## Görevler

Her görev için kaydedilecekler: **süre**, **başarı** (tam / yardımla / başarısız),
**yanlış tıklama sayısı**, **sesli düşünme alıntısı**.

Süre hedefleri sistemin ölçülmüş gecikmesinden değil, kullanıcının karar süresinden
gelir; sistem tarafı [`GECIKME.md`](GECIKME.md)'de zaten ölçülü (Emek Kartı 6 ms).

---

### Görev 1 — Akıştan bir içerik bul

> Bu uygulamada insanlar fotoğraf paylaşıyor. Başkasının içeriğinden türetilmiş,
> yani sıfırdan çekilmemiş bir gönderi bulun.

**Başarı ölçütü:** Köken rozeti "türetilmiş" olan bir gönderiyi işaret eder.
**Hedef:** 45 sn · **Ölçülen:** ___

*Ne öğreniyoruz:* Rozet, açıklama okumadan anlaşılıyor mu? Akış kartındaki köken
durumu gerçekten "akışın doğal parçası" gibi mi duruyor, yoksa gözden mi kaçıyor?

---

### Görev 2 — Payın gerekçesini kendi cümlenizle söyleyin

> Bu içerikten gelen para birden fazla kişiye bölünmüş. Az önce bulduğunuz gönderide,
> **birine neden o kadar düştüğünü** bana kendi cümlenizle anlatın.

**Başarı ölçütü:** Katılımcı Emek Kartı'nda bir pay satırını açar ve gerekçeyi
*kendi kelimeleriyle* doğru özetler (ör. "resmin şu kadarını kullanmış").
Ekrandaki cümleyi okumak sayılmaz.
**Hedef:** 90 sn · **Ölçülen:** ___

*Ne öğreniyoruz:* Projenin ana iddiası — **açıklanabilirlik** — burada sınanıyor.
Katılımcı gerekçeyi okuyup da yeniden anlatamıyorsa açıklama katmanı işini görmüyor
demektir. Bu, bütün oturumun en önemli görevi.

---

### Görev 3 — Maskede neyin ölçüldüğünü gösterin

> Sistem bu kararı verirken görselin bir bölümünü ölçmüş. **Hangi bölümü ölçtüğünü**
> ekranda gösterin ve ne anlama geldiğini söyleyin.

**Başarı ölçütü:** Ölçülen bölge görünümünü açar; yeşil maskenin "kaynaktan gelen
alan" olduğunu söyler.
**Hedef:** 60 sn · **Ölçülen:** ___

*Ne öğreniyoruz:* Maske jüriye kanıt olarak sunuluyor. Kullanıcı yeşil alanı ters
yorumluyorsa (ör. "değiştirilen yer") görsel dilin kendisi yanlış.

---

### Görev 4 — Remix üretip yayınlayın

> Beğendiğiniz bir gönderiyi alıp kendinize göre değiştirin — kırpın, üstüne yazı
> yazın, ne isterseniz — ve yayınlayın.

**Başarı ölçütü:** Remix Stüdyosu'nda en az iki düzenleme yapıp yayınlar; yayınlanan
içerikte kaynağın payı görünür.
**Hedef:** 3 dk · **Ölçülen:** ___

*Ne öğreniyoruz:* Stüdyonun araç geçişleri, geri alma ihtiyacı ve dokunmatik davranışı.
**Dokunmatik oturumda bu görev özellikle izlenir.** Ayrıca: katılımcı yayınlarken
kaynağa pay gittiğini fark ediyor mu, yoksa sürpriz mi oluyor?

---

### Görev 5 — Elinizdeki görselin kaynağını bulun

> *(Katılımcıya, demo içeriğinden alınmış kırpılmış bir ekran görüntüsü dosyası verilir.)*
> Bu görsel elinize WhatsApp'tan geldi, kimin çektiğini bilmiyorsunuz. Uygulamayı
> kullanarak **kaynağını bulun**.

**Başarı ölçütü:** Kaynak Bul ekranını bulur, görseli yükler, dönen sonuçtaki en üst
eşleşmenin kaynak içerik olduğunu söyler.
**Hedef:** 90 sn · **Ölçülen:** ___

*Ne öğreniyoruz:* Bu, ürünün "kimlik silinmiş içerik" iddiasının kullanıcı tarafı.
Ayrıca kanıt satırlarının aşama adları (`phash`, `clip`, geometri) kullanıcıya bir şey
ifade ediyor mu — yoksa yalnızca jüriye mi hitap ediyor?

---

### Görev 6 — Bir paya itiraz edin

> Bu dağılımın haksız olduğunu düşünüyorsunuz: size göre payınız az. **İtiraz edin**
> ve ne olduğunu anlatın.

**Başarı ölçütü:** Pay satırından itirazı açar, gönderir, sonucun *yeniden ölçüm*
olduğunu ve payların değişmiş olabileceğini söyler.
**Hedef:** 90 sn · **Ölçülen:** ___

*Ne öğreniyoruz:* İtiraz, sistemin "yanılabilirim" dediği yer. Katılımcı bunu bir
şikâyet kutusu mu sanıyor, yoksa yeniden ölçüm olarak mı anlıyor? Otomatik çözülen
itirazın sonucu ekranda yeterince açık mı?

---

## Oturum sonu — SUS

On madde, her biri **1 = Kesinlikle katılmıyorum … 5 = Kesinlikle katılıyorum**.
Katılımcı düşünmeden, ilk hissiyle işaretler.

| # | Madde |
|--:|---|
| 1 | Bu sistemi sık sık kullanmak isterim. |
| 2 | Sistemi gereksiz yere karmaşık buldum. |
| 3 | Sistemin kullanımı kolaydı. |
| 4 | Bu sistemi kullanabilmek için teknik destek almam gerekeceğini düşünüyorum. |
| 5 | Sistemdeki farklı işlevlerin birbiriyle iyi bütünleştiğini düşünüyorum. |
| 6 | Sistemde gereğinden fazla tutarsızlık olduğunu düşünüyorum. |
| 7 | Çoğu kişinin bu sistemi çok çabuk öğreneceğini düşünüyorum. |
| 8 | Sistemi kullanmayı hantal buldum. |
| 9 | Sistemi kullanırken kendime güvendim. |
| 10 | Bu sistemi kullanmaya başlamadan önce çok şey öğrenmem gerekti. |

**Puanlama:** tek numaralı maddelerde `cevap − 1`, çift numaralı maddelerde
`5 − cevap`. On değer toplanır, **2,5 ile çarpılır** → 0–100 arası SUS puanı.
Bu bir yüzde değildir. Sektör ortalaması ≈ 68; **hedefimiz ≥ 68**.

## Oturum sonu — açık sorular

1. Bu uygulama tam olarak **ne yapıyor**? Bir arkadaşınıza nasıl anlatırdınız?
2. Bugün gördüğünüz **en kafa karıştırıcı** şey neydi?
3. Kendi içeriğinizi buraya yükler miydiniz? **Neden / neden değil?**

Birinci soru kritik: katılımcı ürünü "telif şikâyet aracı" ya da "filtre uygulaması"
olarak özetliyorsa arayüz ana iddiayı taşımıyor demektir.

## Sonuçlar nereye yazılır

Her oturumdan sonra ham notlar, oturumların tamamı bitince özet
[`KULLANILABILIRLIK-SONUCLARI.md`](KULLANILABILIRLIK-SONUCLARI.md)'ye işlenir. Bulgular
ağırlığa göre sıralanır ve düzeltilenler [`ERISILEBILIRLIK.md`](ERISILEBILIRLIK.md)
desenindeki gibi *bulgu → değişiklik → doğrulama* biçiminde kaydedilir.
