# Kullanılabilirlik Oturumu — Kayıt Formu

Her katılımcı için **bir nüsha** doldurulur. Protokolün tamamı
[`KULLANILABILIRLIK-PROTOKOL.md`](KULLANILABILIRLIK-PROTOKOL.md) içinde; bu form onun
oturum sırasında elde tutulan hâlidir.

Doldurulduktan sonra veriler `data/kullanilabilirlik/oturumlar.json` dosyasına girilir ve
`scripts/kullanilabilirlik_sonuclari.py` çalıştırılır. **Sonuç belgesindeki hiçbir sayı
elle yazılmaz**; hepsi bu formdaki ham değerlerden hesaplanır.

---

## Oturum künyesi

| | |
|---|---|
| Katılımcı kodu | K___ |
| Tarih / saat | ___ |
| Oturumu yöneten | ___ |
| Cihaz ve tarayıcı | ___ |
| Dokunmatik oturum mu | ☐ Evet ☐ Hayır |
| Prototip sürümü (commit) | ___ |

**Katılımcının adı bu forma yazılmaz.**

## Tarama soruları

Oturumdan **önce** sorulur.

| # | Soru | Cevap |
|--:|---|---|
| 1 | Haftada kaç kez sosyal medyaya içerik yüklüyorsunuz? | ___ |
| 2 | Başkasının içeriğini düzenleyip paylaştığınız oldu mu? | ___ |
| 3 | Paylaştığınız bir içeriğin kaynağını bulmaya çalıştınız mı? Nasıl? | ___ |
| 4 | Atıf veya telif konusunda bir araç kullandınız mı? | ___ |
| 5 | **Bu projeyi veya N-Emek'i daha önce duydunuz mu?** | ☐ Hayır ☐ **Evet → oturum iptal** |

**Profil** (birini işaretle): ☐ İçerik üreticisi ☐ Sıradan paylaşan ☐ Marka / topluluk yöneticisi

## Onam

Kayıt başlamadan **sesli okunur**, onayı kayda alınır:

> Bu oturumda N-Emek adlı bir prototipi denemenizi isteyeceğiz. **Sizi değil, arayüzü
> test ediyoruz** — takıldığınız her yer bizim için bir kusur, sizin için bir hata değil.
> Ekran ve sesiniz kaydedilecek; kayıt yalnızca takım içinde kullanılacak, yarışma
> teslimatında yalnızca isimsiz özet yer alacak. İstediğiniz an durabilir, kaydın
> silinmesini isteyebilirsiniz. Devam edelim mi?

☐ Onam alındı, kayıt başladı

**Moderatör kuralları — oturum boyunca:** yardım yok · ekran adı söylenmez ("Emek
Kartı'na girin" denmez) · sesli düşünme hatırlatılır · görev 3 dakikada biter · katılımcının
kendi kelimeleri **birebir** not edilir.

---

## Görevler

Başarı: **T** tam · **Y** yardımla · **B** başarısız (3 dk doldu).
Süre saniye. "Yanlış tıklama" = hedefe götürmeyen tıklama.

### Görev 1 · hedef 45 sn

> Bu uygulamada insanlar fotoğraf paylaşıyor. Başkasının içeriğinden türetilmiş, yani
> sıfırdan çekilmemiş bir gönderi bulun.

*Başarı ölçütü:* köken rozeti "türetilmiş" olan bir gönderiyi işaret eder.

| Başarı | Süre (sn) | Yanlış tıklama |
|---|---|---|
| ☐ T ☐ Y ☐ B | ___ | ___ |

Birebir alıntı: ___

### Görev 2 · hedef 90 sn — **oturumun en önemli görevi**

> Bu içerikten gelen para birden fazla kişiye bölünmüş. Az önce bulduğunuz gönderide,
> birine neden o kadar düştüğünü bana kendi cümlenizle anlatın.

*Başarı ölçütü:* pay satırını açar ve gerekçeyi **kendi kelimeleriyle** doğru özetler.
Ekrandaki cümleyi okumak sayılmaz.

| Başarı | Süre (sn) | Yanlış tıklama |
|---|---|---|
| ☐ T ☐ Y ☐ B | ___ | ___ |

Katılımcının kurduğu cümle (**birebir**): ___

### Görev 3 · hedef 60 sn

> Sistem bu kararı verirken görselin bir bölümünü ölçmüş. Hangi bölümü ölçtüğünü ekranda
> gösterin ve ne anlama geldiğini söyleyin.

*Başarı ölçütü:* ölçülen bölge görünümünü açar; maskenin "kaynaktan gelen alan" olduğunu söyler.

| Başarı | Süre (sn) | Yanlış tıklama |
|---|---|---|
| ☐ T ☐ Y ☐ B | ___ | ___ |

Maskeyi ters yorumladı mı (ör. "değiştirilen yer" dedi mi): ___

### Görev 4 · hedef 3 dk

> Beğendiğiniz bir gönderiyi alıp kendinize göre değiştirin — kırpın, üstüne yazı yazın,
> ne isterseniz — ve yayınlayın.

*Başarı ölçütü:* en az iki düzenleme yapıp yayınlar; yayınlanan içerikte kaynağın payı görünür.

| Başarı | Süre (sn) | Yanlış tıklama | Geri alma ihtiyacı |
|---|---|---|---|
| ☐ T ☐ Y ☐ B | ___ | ___ | ☐ Evet ☐ Hayır |

Kaynağa pay gittiğini fark etti mi, sürpriz mi oldu: ___

### Görev 5 · hedef 90 sn

> *(Katılımcıya hazırlanmış kırpılmış ekran görüntüsü dosyası verilir.)*
> Bu görsel elinize WhatsApp'tan geldi, kimin çektiğini bilmiyorsunuz. Uygulamayı
> kullanarak kaynağını bulun.

*Başarı ölçütü:* Kaynak Bul ekranını bulur, görseli yükler, en üst eşleşmenin kaynak
içerik olduğunu söyler.

| Başarı | Süre (sn) | Yanlış tıklama |
|---|---|---|
| ☐ T ☐ Y ☐ B | ___ | ___ |

Kanıt satırlarının aşama adları anlaşıldı mı: ___

### Görev 6 · hedef 90 sn

> Bu dağılımın haksız olduğunu düşünüyorsunuz: size göre payınız az. İtiraz edin ve ne
> olduğunu anlatın.

*Başarı ölçütü:* pay satırından itirazı açar, gönderir, sonucun **yeniden ölçüm**
olduğunu söyler.

| Başarı | Süre (sn) | Yanlış tıklama |
|---|---|---|
| ☐ T ☐ Y ☐ B | ___ | ___ |

İtirazı "şikâyet" mi "yeniden ölçüm" mü sandı: ___

---

## Oturum sonu — SUS

Katılımcı **düşünmeden, ilk hissiyle** işaretler.
**1 = Kesinlikle katılmıyorum · 5 = Kesinlikle katılıyorum**

| # | Madde | 1 | 2 | 3 | 4 | 5 |
|--:|---|:-:|:-:|:-:|:-:|:-:|
| 1 | Bu sistemi sık sık kullanmak isterim. | ☐ | ☐ | ☐ | ☐ | ☐ |
| 2 | Sistemi gereksiz yere karmaşık buldum. | ☐ | ☐ | ☐ | ☐ | ☐ |
| 3 | Sistemin kullanımı kolaydı. | ☐ | ☐ | ☐ | ☐ | ☐ |
| 4 | Bu sistemi kullanabilmek için teknik destek almam gerekeceğini düşünüyorum. | ☐ | ☐ | ☐ | ☐ | ☐ |
| 5 | Sistemdeki farklı işlevlerin birbiriyle iyi bütünleştiğini düşünüyorum. | ☐ | ☐ | ☐ | ☐ | ☐ |
| 6 | Sistemde gereğinden fazla tutarsızlık olduğunu düşünüyorum. | ☐ | ☐ | ☐ | ☐ | ☐ |
| 7 | Çoğu kişinin bu sistemi çok çabuk öğreneceğini düşünüyorum. | ☐ | ☐ | ☐ | ☐ | ☐ |
| 8 | Sistemi kullanmayı hantal buldum. | ☐ | ☐ | ☐ | ☐ | ☐ |
| 9 | Sistemi kullanırken kendime güvendim. | ☐ | ☐ | ☐ | ☐ | ☐ |
| 10 | Bu sistemi kullanmaya başlamadan önce çok şey öğrenmem gerekti. | ☐ | ☐ | ☐ | ☐ | ☐ |

> **Puanı formda hesaplama.** Ham cevaplar JSON'a girilir, puanı betik hesaplar.

## Oturum sonu — açık sorular

Cevaplar **birebir** yazılır, özetlenmez.

**1. Bu uygulama tam olarak ne yapıyor? Bir arkadaşınıza nasıl anlatırdınız?**

___

**2. Bugün gördüğünüz en kafa karıştırıcı şey neydi?**

___

**3. Kendi içeriğinizi buraya yükler miydiniz? Neden / neden değil?**

___

## Moderatör notu

Oturum sırasında fark edilen, göreve bağlanmayan gözlemler:

___
