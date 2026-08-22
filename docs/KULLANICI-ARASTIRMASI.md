# Kullanıcı Araştırması

Şartnamenin teslimat listesinde **kullanıcı araştırması özeti** var (`docs/PLAN.md`).
Bu belge hem araştırmanın düzeneğini hem de özet şablonunu taşır.

Kullanılabilirlik testinden farkı: orada **ürünü kullanabiliyor mu** ölçülüyor, burada
**problem gerçek mi** sorusu soruluyor. İkisi ayrı oturumlar, ayrı kişiler.

## Ne öğrenmeye çalışıyoruz

Projenin dayandığı üç varsayım var. Araştırma bunları sınamak için var — doğrulamak
için değil. Bir varsayım çürürse bu belgeye çürüdüğü yazılır.

| # | Varsayım | Çürütecek bulgu |
|--:|---|---|
| V1 | Üreticiler içeriklerinin izinin kaybolmasından rahatsız | "Umursamıyorum, zaten yayılması iyi" yaygın çıkarsa |
| V2 | Remix üretenler kaynağı anmak istiyor ama nasıl yapacağını bilmiyor | Anmama tercihinin bilinçli olduğu çıkarsa |
| V3 | Paylaşan kişi mağduriyet yaratmak istemiyor, yalnızca kaynağı bilmiyor | Kaynağın kimseyi ilgilendirmediği çıkarsa |

## Kimlerle

Sekiz–on kişi, kullanılabilirlik testine **katılmayacak** kişilerden:

| Profil | Kaç kişi |
|---|--:|
| Düzenli içerik üreten (fotoğraf, illüstrasyon, video) | 4 |
| Başkasının içeriğini düzenleyip paylaşan | 3 |
| Yalnızca paylaşan, üretmeyen | 2 |
| Marka / topluluk yöneticisi | 1 |

Görüşme 20–25 dakika, yüz yüze ya da sesli. Not tutulur; kayıt isteğe bağlı ve izinli.

## Görüşme rehberi

Sorular açık uçlu ve **geçmişe** dair. "Şöyle bir araç olsa kullanır mıydınız?" diye
sorulmaz — hipotetik sorular herkesi evet dedirtir ve hiçbir şey öğretmez.

### Isınma

1. Sosyal medyada ne paylaşıyorsunuz? Ne sıklıkta?
2. En son ne paylaştınız? Anlatır mısınız?

### Üreticiye (V1)

3. Paylaştığınız bir içeriğin **başkasının hesabında** karşınıza çıktığı oldu mu?
   Anlatın — nasıl fark ettiniz, ne hissettiniz, ne yaptınız?
4. O an ne olmasını isterdiniz?
5. İçeriğinizin nereye gittiğini takip etmek için bir şey denediniz mi? Ne oldu?

### Remix üretene (V2)

6. Başkasının içeriğini düzenleyip paylaştığınız son seferi anlatın.
7. Kaynağı andınız mı? **Nasıl karar verdiniz?**
8. Anmadıysanız neden? Anmak isteseydiniz ne yapardınız?
9. Kendi katkınızın da sayılmasını ister miydiniz? Nasıl bir şey adil olurdu?

### Paylaşana (V3)

10. Elinize gelen bir görseli, kimin çektiğini bilmeden paylaştınız mı?
11. Kaynağını merak ettiğiniz oldu mu? Bulmaya çalıştınız mı, nasıl?
12. Sonradan "keşke paylaşmasaydım" dediğiniz oldu mu?

### Markaya

13. Bir kampanyada ödülü nasıl dağıttınız? Kime, neye göre?
14. Dağıtımın adil olmadığına dair geri dönüş aldınız mı?

### Kapanış

15. Bu konuda size en çok ne zor geliyor?
16. Sormadığım ama sormam gereken bir şey var mı?

## Bulgular

> Bu bölüm elle düzenlenmez. Ham görüşme kayıtları
> `data/kullanici-arastirmasi/gorusmeler.json` içindedir; buradaki her sayı
> `scripts/kullanici_arastirmasi.py` tarafından sayılır. Yargı görüşmecinin
> (etiket ve varsayım sonucu), sayım betiğin.

| | |
|---|---|
| Tarih | 22 Ağustos 2026 |
| Görüşmeyi yapan | Takım üyesi — on görüşmenin tamamı aynı görüşmeci |
| Yöntem | Sesli ve yüz yüze görüşme, kişi başı 20-25 dk; not tutuldu |
| Görüşme sayısı | **10** |

### Kimlerle konuşuldu

| Profil | Kaç kişi |
|---|--:|
| Düzenli içerik üreten | 4 |
| Başkasının içeriğini düzenleyip paylaşan | 3 |
| Yalnızca paylaşan | 2 |
| Marka / topluluk yöneticisi | 1 |
| **Toplam** | **10** |

Katılımcılar kullanılabilirlik testine katılmadı; iki grup ayrı kişilerden oluşuyor.

### Görüşme başına

Alıntılar birebir; özetlenmiş alıntı bulgu sayılmaz.

| Kod | Profil | Varsayım | Sonuç | Birebir alıntı |
|---|---|---|---|---|
| G1 | Düzenli içerik üreten | V1 | doğruladı | "Önce beğenmişler sandım, sonra baktım hiçbir yerde adım yok. Çok sinirlendim." |
| G2 | Düzenli içerik üreten | V1 | doğruladı | "Önce gururlandım, sonra bozuldum çünkü izin almamışlar. Tuhaf bir duygu." |
| G3 | Düzenli içerik üreten | V1 | doğruladı | "Kendi emeğim çöpe gitmiş gibi hissettim." |
| G4 | Düzenli içerik üreten | V1 | doğruladı | "Alıntı yapmak yerine çalmışlar." |
| G5 | Başkasının içeriğini düzenleyip paylaşan | V2 | sınanamadı | "Para değil de emek tanınsın." |
| G6 | Başkasının içeriğini düzenleyip paylaşan | V2 | doğruladı | "Anmadım çünkü kaynak çok dağınık. Genelde bilmediğim için yazmıyorum." |
| G7 | Başkasının içeriğini düzenleyip paylaşan | V2 | sınanamadı | ""Hazırlayan: ben" gibi bir not olsun isterdim. Küçük de olsa emek var." |
| G8 | Yalnızca paylaşan | V3 | doğruladı | "Bir kere sahte bir yardım kampanyası görselini paylaşmıştım, sonradan asılsız çıktı. Keşke paylaşmasaydım dedim, sildim." |
| G9 | Yalnızca paylaşan | V3 | doğruladı | "Görseli kimin çektiğini bilmiyorum, ama kaynak belirtmeden paylaşıyorum." |
| G10 | Marka / topluluk yöneticisi | — | kapsam dışı | "Benim fotoğrafım daha iyiydi ama çevrem olmadığı için kaybettim. Haklıydı aslında." |

- **G5:** Kaynak zaten biliniyordu (arkadaşının fotoğrafı); "bilmediği için anmama" durumu bu görüşmede test edilemedi.
- **G7:** Kaynak zaten biliniyordu (arkadaşının aile fotoğrafları); anmama durumu test edilemedi.
- **G10:** Marka profili V1-V3'ün dışında; kampanya dağıtımının ölçülememesi sorununu marka ağzından doğruluyor.

### Varsayımların durumu

| # | Varsayım | Doğruladı | Çürüttü | Sınanamadı |
|---|---|--:|--:|--:|
| V1 | Üreticiler içeriklerinin izinin kaybolmasından rahatsız | 4 | 0 | 0 |
| V2 | Remix üretenler kaynağı anmak istiyor ama nasıl yapacağını bilmiyor | 1 | 0 | 2 |
| V3 | Paylaşan kişi mağduriyet yaratmak istemiyor, yalnızca kaynağı bilmiyor | 2 | 0 | 0 |

Hiçbir görüşme bir varsayımı çürütmedi. Bu, varsayımların *kanıtlandığı*
anlamına gelmez: örneklem küçük ve seçilmiş, üstelik iki görüşmede
koşullar varsayımı sınamaya elverişli olmadı (yukarıdaki notlar).

### Tekrar eden örüntüler

Düzenek metnindeki eşik: **3 ve daha fazla** kişide görülen davranış.

| Örüntü | Kaç kişi | Kimde |
|---|--:|---|
| Talep edilen şey gelir değil; isim görünürlüğü, etiket veya bildirim | **7** / 10 | G1, G2, G3, G4, G5, G6, G7 |
| "Emek" kelimesini kendiliğinden kullandı | **6** / 10 | G1, G2, G3, G5, G6, G7 |
| Kaynağı bulmak için tersine görsel arama denendi (Google Görseller / Google Lens) | **5** / 10 | G1, G2, G4, G8, G9 |
| İçeriği başkasının hesabında izinsiz kullanılmış | **4** / 10 | G1, G2, G3, G4 |
| Takip girişimi sonuçsuz kaldı ve bırakıldı | **4** / 10 | G1, G3, G4, G8 |
| Kaynağı bilmemek ya paylaşımı durduruyor ya kaynaksız paylaşıma itiyor | **4** / 10 | G5, G6, G8, G9 |
| Düzenleyen kişi kendi katkısının da görünmesini istiyor | **3** / 10 | G5, G6, G7 |

Eşiğin altında kalanlar (örüntü sayılmaz, kayıt için): Gelir konusunu görüşmeci sormadan katılımcı açtı (2) · Doğruluğu şüpheli içeriği paylaşıp sonradan sildi (2)

### Kullanıcının kelimeleri, arayüzün kelimeleri

Katılımcıların **kendiliğinden** kullandığı terimler ve arayüzdeki karşılıkları.
Fark varsa arayüz terimi tartışmaya açılır.

| Katılımcı ne diyor | Kaç kişide | Arayüzde ne yazıyor |
|---|--:|---|
| kaynak | 8 / 10 | Köken |
| etiket / etiketlemek | 4 / 10 | Atıf |
| emek | 6 / 10 | Emek Kartı |
| çalıntı / çalmışlar | 2 / 10 | Türev içerik |
| adım / ismim görünsün | 2 / 10 | Pay dağılımı |
| bildirim / haberim olsa | 1 / 10 | (karşılığı yok) |

## Özet

**10 görüşme yapıldı.** 7 görüşme ilgili varsayımı doğruladı, 0 tanesi çürüttü, 2 tanesinde koşullar varsayımı sınamaya elverişli olmadı, 1 görüşme V1-V3'ün dışında bir soruyu sınadı.

**Ürüne yansıyanlar.** Görüşmelerden çıkan ve ürün kararına dönüşen maddeler;
her biri yukarıdaki sayılara dayanıyor.

- **Talep edilen birincil şey gelir değil, görünürlük.** Üreticiler ve düzenleyenler kendiliğinden isim, etiket ve bildirim istedi; gelir konusunu yalnızca iki kişi ve yalnızca "sormadığınız soru" olarak açtı. N-Emek gelir paylaşımını merkeze koyuyor — atıf ve bildirim katmanının en az onun kadar görünür olması gerekiyor. "İçeriğin şurada kullanıldı" bildirimi İP-8'e alındı.
- **Üretici tabanı kuralı kullanıcı tarafından doğrulandı.** Düzenleyen üç katılımcının üçü de kendi katkısının görünmesini istedi ("edit by", "derleme: ben", "hazırlayan: ben"). Kampanya kuralındaki %20 üretici tabanı bu talebin karşılığı; sadeleştirme adına kaldırılmayacak.
- **"Emek" kullanıcının kendi kelimesi.** Altı katılımcı kendiliğinden kullandı; buna karşılık "atıf" ve "köken" hiçbir görüşmede geçmedi. Emek Kartı adı doğru duruyor; arayüzdeki "Köken" başlığı için kullanıcının kelimesi "kaynak" ve bu terim gözden geçirilecek.
- **Paylaşan profili için kaynak aramanın motivasyonu atıf değil doğrulama.** İki paylaşanın ikisi de yanlış bilgi paylaşıp sildi; pişmanlıkları telif değil doğruluk üzerineydi. Kaynak Bul ekranı bu kitleye "bu görsel nereden geliyor" kadar "bu görsel doğru mu" vaadiyle de konumlanabilir.
- **Problem tanımı marka ağzından doğrulandı.** Kampanya ödülü beğeniye göre dağıtılmış, bir katılımcı "benim fotoğrafım daha iyiydi ama çevrem olmadığı için kaybettim" demiş ve marka bunu haklı bulmuş. Ölçülmüş katkıya göre dağıtım, uydurulmuş bir ihtiyaç değil.

**Çürüyen varsayım çıkmadı.** Bu iyi bir sonuç değil, *nötr* bir sonuçtur:
örneklem küçük ve kartopu yöntemiyle seçildi, dolayısıyla varsayımı
doğrulayan kişilere ulaşma eğilimi taşıyor. Asıl bilgi doğrulamanın
kendisinde değil, katılımcıların **ne istediğini söylediğinde**: talep
edilen şey ağırlıkla gelir değil görünürlük çıktı ve bu, ürünün vurgusunu
doğrudan etkiliyor.

## Sınırlar

- Örneklem seçilmiş (kartopu) — temsili değil, keşif amaçlı.
- Geçmişe dair sorular hatıra yanlılığı taşır; kişi olayı olduğundan çarpıcı
  anlatabilir.
- **Marka / topluluk yöneticisi** profilinde tek kişi var; o profilden gelen bulgular tek
  görüşmeye dayanıyor ve örüntü sayılamaz.
- Görüşmelerin tamamını tek kişi yürüttü; soru sorma biçiminden gelen yanlılık dağılmıyor.
- Görsel içerik ağırlıklı bir örneklem: video ve yazılı içerik üreten yalnızca ikişer kişiyle temsil edildi.

### Ham görüşme kayıtları

Her cevap birebir; soru numaraları düzenek metnindeki görüşme rehberinden.

#### G1 — Düzenli içerik üreten

**1.** Genelde doğa ve sokak fotoğrafı çekiyorum. Haftada bir ya da iki kez paylaşıyorum, hikaye de atıyorum ama post daha az.

**2.** En son geçen hafta sonu sahilde gün batımı fotoğrafı attım. Üç fotoğraflık bir seriydi, arabadan çektiğim bir kare de vardı. Çok beğenildi ama bir arkadaşım "bunu sen mi çektin?" diye sorunca hafif bozuldum. Yani emek verip çekiyorsun, insanlar şüphe ediyor.

**3.** Evet, oldu. Geçen sene bir fotoğrafımı bir kafe hesabı kendi postu gibi paylaşmış. Arkadaşım gördü, "senin fotoğrafın bu" diye yazdı. Önce beğenmişler sandım, sonra baktım hiçbir yerde adım yok. Çok sinirlendim. Yorumda "fotoğraf bana ait" yazdım, kaldırdılar ama bir daha da kullanmadılar.

**4.** O an otomatik etiket ya da en azından bana bildirim gelmesini isterdim. Biri kullanınca haberim olsa yeter.

**5.** Google Görseller'e yükledim, başka iki hesapta daha çıktı. Tek tek aramak çok yorucu, bir süre sonra bıraktım.

**15.** Takip kısmı. Bir şey paylaşıyorsun, nereye gidiyor belli olmuyor.

**16.** Bence "para kazanmak ister miydiniz?" sorusu önemli olabilir.

#### G2 — Düzenli içerik üreten

**1.** Çizim ve illüstrasyon yapıyorum, haftada 2-3 post atıyorum. Daha çok Twitter ve Instagram kullanıyorum.

**2.** En son bir anime karakteri çizimi attım. Üç gün uğraştım, detayları ince yaptım. Hikayede süreç videosu da paylaştım. Genelde süreç videosu daha çok ilgi çekiyor.

**3.** Oluyor. Geçen ay bir YouTube kanalı çizimimi video kapağı yapmış, ismimi yazmamış. Ben de yorumlarda gördüm. Önce gururlandım, sonra bozuldum çünkü izin almamışlar. Tuhaf bir duygu.

**4.** Hiç değilse kaynak belirtsinler ya da haber verseler. İdeal olan adımın görünmesi.

**5.** Google Lens'e yükledim, başka hesaplarda da çıktı. Birine DM attım, "kaldırır mısın" dedim, kaldırdı ama soğuk davrandı.

**15.** Emek karşılığı takdir görmek zor. İnsanlar ekran görüntüsü alınca her şeyi kendinin sanıyor.

**16.** Belki "bu işten gelir elde ediyor musunuz?" diye sorabilirdiniz.

#### G3 — Düzenli içerik üreten

**1.** Yemek tarifi videoları çekiyorum. Haftada 1-2 reel, bazen de blog yazısı atıyorum.

**2.** En son evde yaptığım kolay makarna tarifini attım. Kısa video, üstüne malzemeleri yazdım. Annem bile kaydetmiş, "ben de yapacağım" diye mesaj attı.

**3.** Bir tarif videom başka bir sayfada aynen paylaşılmış, üstüne kendi logosunu koymuşlar. Yorumlarda "çalıntı" yazanlar olmuş, öyle fark ettim. Kendi emeğim çöpe gitmiş gibi hissettim.

**4.** O an linkin altında "kaynak" görünsün ya da platform otomatik uyarsın isterdim.

**5.** Şikayet ettim ama sonuç çıkmadı. Bir daha da uğraşmadım, çünkü çok vakit alıyor.

**15.** Herkes paylaşıyor, kimse sormuyor. En zoru bu.

**16.** Yok, bence yeterli.

#### G4 — Düzenli içerik üreten

**1.** Kişisel deneyimlerimi yazıyorum, iş hayatına dair thread'ler. Haftada 3-4 tweet ve story atarım.

**2.** En son iş arama süreciyle ilgili bir thread yazdım. 40-50 tweet oldu, çok kişi mesaj attı. Bazıları "aynısını yaşıyorum" dedi, iyi hissettirdi.

**3.** Biri thread'imi ekran görüntüsü alıp başka platformda kendi yorumuyla paylaşmış, üstelik sanki kendi yaşadığı bir olay gibi. DM'den "bu senin yazın mı?" diye sordular, çok garip hissettim. Alıntı yapmak yerine çalmışlar.

**4.** Kaynağın otomatik görünmesini isterdim. Ya da en azından alıntı yapılsın.

**5.** Ekran görüntüsü üzerinden arama yaptım ama bulamadım, bıraktım. Zaten yazı olduğu için takip etmek daha zor.

**15.** Yazılı içeriklerde kaynak belirtme alışkanlığı hiç yok, o zor.

**16.** Belki "bu durum sizi duygusal olarak nasıl etkiledi?" diye daha derin sorabilirdiniz.

#### G5 — Başkasının içeriğini düzenleyip paylaşan

**1.** Komik editler ve meme yapıyorum. Haftada birkaç kez hikayeye atarım, bazen de post.

**2.** En son arkadaşımın fotoğrafını alıp üstüne yazı yazdım, şarkı ekledim, story olarak attım. Arkadaşım çok güldü, "keşke ben de atsaydım" dedi.

**6.** Arkadaşımın kedi fotoğrafını aldım, üstüne "pazartesi sendromu" yazdım, arka plana müzik koydum. İki dakika sürdü ama çok komik oldu.

**7.** Evet, arkadaşımı etiketledim çünkü foto onun kedisiydi. Başka kaynak yoktu zaten, etiketlemek doğal geldi.

**8.** Anmasaydım muhtemelen "bana ait değil" diye düşünürdüm. Ama yine de etiketlerdim, çok önemli değil.

**9.** Evet, edit'i ben yaptığım için "edit by" gibi bir ibare olmasını isterdim. Para değil de emek tanınsın.

**15.** Bazen fotoğrafın kime ait olduğunu bilmiyorum, o yüzden paylaşmıyorum. Belirsizlik yorucu.

**16.** Yok, teşekkürler.

#### G6 — Başkasının içeriğini düzenleyip paylaşan

**1.** Hayvan videoları, komik derlemeler. Haftada 3-4 kere paylaşıyorum.

**2.** En son pazar günü bir kedi videosu derlemesi attım. TikTok'tan ve Instagram'dan birkaç klip indirdim, üstüne müzik ekledim.

**6.** İki üç farklı hesaptan kedi köpek videosu indirdim, kestim, hızlandırdım, altyazı ekledim. Sonra story ve post olarak paylaştım.

**7.** Pek kaynak yazmadım. Sadece bir videonun sahibini biliyorsam etiketledim. Genelde bilmediğim için yazmıyorum.

**8.** Anmadım çünkü kaynak çok dağınık. Anmak isteseydim videonun altına "kaynak: @hesap" yazar ya da hikayede etiketlerdim.

**9.** Kendi katkımın sayılmasını isterdim. Mesela "derleme: ben" gibi. Adil olan, kaynak sahipleri de görünsün ama benim de emeğim görünsün.

**15.** Kaynak bulmak bazen çok zor, bazen imkansız. O yüzden ya paylaşmıyorum ya da kaynaksız atıyorum.

**16.** Belki "bu tür paylaşımlar yüzünden hiç sorun yaşadınız mı?" sorusu eklenebilir.

#### G7 — Başkasının içeriğini düzenleyip paylaşan

**1.** Fotoğraf editliyorum, eski fotoğrafları düzenleyip hikayede paylaşıyorum. Ayda birkaç kez.

**2.** En son arkadaşımın doğum günü için eski fotoğraflarından bir kolaj yaptım, müzikli video yaptım. Ona attım, o da kendi hesabında paylaştı.

**6.** Arkadaşımın çocukluk fotoğraflarını taradım, renkleri düzelttim, slayt yaptım, şarkı koydum. O da kendi hesabında paylaştı.

**7.** Sadece arkadaşımı etiketledim, fotoğraflar onun olduğu için başka kaynak gerekmedi.

**8.** Anmasaydım bile sorun olmazdı, çünkü aile içi. Ama yine de etiketledim.

**9.** Evet, "hazırlayan: ben" gibi bir not olsun isterdim. Küçük de olsa emek var.

**15.** Eski fotoğrafların kalitesi ve telifi belirsiz, o zor.

**16.** Yok.

#### G8 — Yalnızca paylaşan

**1.** Genelde WhatsApp'tan gelen ilginç şeyleri, haberleri, bazen komik videoları story olarak paylaşıyorum. Haftada 2-3 kez.

**2.** En son dün bir motivasyon sözü fotoğrafı paylaştım. WhatsApp grubundan gelmişti, hoşuma gitti, story attım.

**10.** Evet, çok oldu. Görsel kimin bilmiyorum, çoğu zaten internetten alınmış.

**11.** Bazen merak ediyorum, Google'a fotoğraf atıyorum ama çoğu zaman sonuç çıkmıyor. O yüzden bırakıyorum.

**12.** Bir kere sahte bir yardım kampanyası görselini paylaşmıştım, sonradan asılsız çıktı. Keşke paylaşmasaydım dedim, sildim.

**15.** Kaynak bilmemek ve yanlış bilgi paylaşmak zor geliyor.

**16.** Bence "doğrulama yapıyor musunuz?" diye sorulabilir.

#### G9 — Yalnızca paylaşan

**1.** Komik gönderiler, haber bağlantıları, tarif videoları paylaşıyorum. Haftada 5-6 hikaye atarım.

**2.** En son bir yemek videosunu hikayede paylaştım. Instagram'da gördüm, kaydetmek yerine paylaştım. Yapımı kolay görünüyordu.

**10.** Sürekli oluyor. Görseli kimin çektiğini bilmiyorum, ama kaynak belirtmeden paylaşıyorum.

**11.** Merak ettiğim oldu, özellikle bir fotoğraf çok güzelse. Google Lens'i deniyorum, bazen buluyor, bazen bulmuyor.

**12.** Bir kere "güncel" sandığım bir olayın eski fotoğrafını paylaştım, yorumlarda uyardılar. Utanç vericiydi, hemen sildim.

**15.** Görselin eski mi yeni mi, doğru mu yanlış mı ayırt etmek zor.

**16.** Yok, bence bu kadar yeterli.

#### G10 — Marka / topluluk yöneticisi

**1.** Şirketimizin ürün fotoğrafları, kampanyalar, kullanıcıların gönderdiği içerikler. Haftada 5-7 gönderi.

**2.** En son bir UGC yarışmasının kazananını açıkladım. Kullanıcılar fotoğraf yolladı, biz seçtik, kazananı duyurduk.

**13.** Ödülü, en çok beğeni alan ve jürinin seçtiği iki kriterle dağıttık. Ama çoğunlukla beğeniye göre oldu. Bazıları "haksızlık" dedi, çünkü arkadaşlarını çağırmışlar.

**14.** Evet, bir katılımcı "benim fotoğrafım daha iyiydi ama çevrem olmadığı için kaybettim" dedi. Haklıydı aslında. Bu yüzden bir sonraki yarışmada jüri ağırlığını artırdık.

**15.** En zor kısım adil dağıtım. Kimin ne kadar hak ettiğini ölçmek çok zor.

**16.** Belki "yarışma dışı kullanıcı içeriklerinde telif nasıl yönetiliyor?" diye sorabilirsiniz.

