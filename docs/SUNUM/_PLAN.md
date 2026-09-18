# Jüri Sunumu — Şablona Göre Sunum Planı

Zorunlu sunum şablonu 14 Eylül 2026'da geldi ve
`docs/NSosyal_Inovasyon_Yarısması_Sunum_Sablonu_1_2_2_TTN8G.pptx` konumuna taşındı
(teknik rapor şablonunun yanına). Bu belge sunumun **sayfa planı ve devir notudur**.
İçerik 15 Eylül'de yazıldı; güncel durum ve açık kararlar sondaki "Görev dağılımı ve
devir" bölümünde. `docs/SUNUM.md` şablondan önceki 17 slaytlık serbest taslaktır, bu
plan onun yerini alır. Taslağın soru-cevap bölümü korunur.

| | |
|---|---|
| Teslim | **18 Eylül gecesi**, KYS'ye PDF. İç hedefimiz 17 Eylül akşamı |
| Sunum | 20 Eylül, İstanbul. **15 dk sunum** + 2–3 dk canlı prototip + jüri soruları |
| Hedef | **14 sayfa**, sayfa başına yaklaşık 1 dakika |
| Üretim | Betikle. İçerik `docs/SUNUM/*.md` dosyalarında durur, `scripts/sunum_pptx.py` şablonun kopyasını doldurur, PowerPoint PDF'e çevirir |

---

## 1 · Şablon incelemesi

### Kurallar (şablonun son sayfasından)

- Kapak dahil **en fazla 19 sayfa**. Aşılırsa sistem dosyayı kabul etmez.
- Bölüm başına sayfa sınırı var. **Aşılan her sayfa için 3 ceza puanı.**
- Şablonun sabit unsurları değiştirilmez: kurumsal kimlik, sayfa ölçüsü, başlıklar, alt bilgi.
  Başlık altındaki içerik alanı tamamen serbest. Yazı tipi ve boyutu da serbest.
- Kırmızı yönerge metinleri silinir, "Sunum Hazırlama Kuralları" sayfası silinir.
- Takım adı, takım kimliği ve başvuru kimliği her sayfada aynı konumda ve biçimde durur.
- Her başlık altında yalnızca o konu anlatılır. **Sunum içinde tekrarlayan ya da birbirinin aynısı ifade bulunmaz.**
- Akademik bulgu, istatistik ve dış kaynaklı görseller ilgili sayfada kısa kaynak bilgisiyle verilir.
  Harici video veya bulut bağlantısı kaynak olarak kullanılmaz.
- PDF formatında, en fazla 75 MB. Son yükleme tarihinden sonra güncelleme yapılamaz.
- Sunumu yalnızca takım üyeleri yapar, en az bir üyenin katılımı zorunlu.

### Bölüm sınırları

| Bölüm | Sınır | Planımız |
|---|--:|--:|
| Kapak | 1 | 1 |
| Takım Tanıtımı | 1 | 1 |
| Proje Özeti ve Kapsamı | 1 | 1 |
| Problemin Tanımı | 2 | 1 |
| Çözüm Önerisi | 3 | 2 |
| Yöntem | 2 | 2 |
| Prototip / Uygulama Geliştirme Durumu | 1 | 1 |
| Uygulanabilirlik ve Sürdürülebilirlik | 2 | 2 |
| Özgünlük ve Yerlilik Yönü | 2 | 1 |
| Hedef Kitle ve Yaygın Etki | 1 | 1 |
| Proje Takvimi | 1 | 1 |
| **Toplam** | **17** | **14** |

### Yerleşim (PowerPoint'te çizdirilerek ölçüldü)

- Sayfa 50,8 × 28,575 cm (16:9). Yazı tipi Arial ve gömülü Arial Black.
  Renkler lacivert `#1A426A` / `#1C4C61`, açık maviler `#B7CCE4` / `#C5D8F1`, şerit noktaları turuncu `#F3A025`.
- **Kapak:** koyu uzay arka planı. "Proje Adı, Tematik Alan, Takım Adı, Takım ID, Başvuru ID" etiketleri
  hazır, değerler etiketlerin sağına yazılır.
- **İçerik sayfaları:** açık arka plan, üstte TEKNOFEST ve Milli Teknoloji Hamlesi logoları, ortada başlık, altında çizgi.
  Sağda bölüm gezinme şeridi var ve etkin bölüm vurgulu. **Kullanılabilir içerik alanı yaklaşık x 3,4–41 cm, y 4,2–25,3 cm.**
  Başlığı iki satıra taşan Prototip ve Uygulanabilirlik sayfalarında içerik y ≈ 6,5 cm'den başlar.
- **Alt bant:** "TAKIM ADI / TAKIM ID / BAŞVURU ID" etiketleri arka plan görselinin içinde, bandın sağında.
  Değerler (ZENITH N · 1003461 · 5382505) etiketlerin sağına, Türkiye Teknoloji Takımı logosundan önceki boşluğa yazılır.
- **Takım Tanıtımı:** solda danışman ve kaptan kutuları, sağda 5 üye kutusu, fotoğraf çerçeveleri ve bağlantı çizgileri.
- **Proje Takvimi:** 5 sütun × 7 satırlık örnek tablo (İş Paketi No, Adı, Alt Faaliyetler, Başlangıç, Bitiş).

### Şablonda bulunan hatalar (dokunulmayacak)

- "Hedef Kitle ve Yaygın Etki" sayfasının alt bilgisinde **"22026"** yazıyor.
- Sağ şeritte "PROTOTİP / UYGULAMA GELİŞTİRME DURUMU" ile "UYGULANABİLİRLİK VE" yazıları üst üste biniyor.
  Etkin sayfada binmiyor.
- "Uygulanabilirlik" sayfasının başlığında **"SÜRDÜRÜLEBİLİRİLİK"** yazıyor (fazladan "İ").

Sabit alanları değiştirmek kural ihlali sayılabileceği için ikisi de olduğu gibi bırakılır.

---

## 2 · Sayfa planı

**Tekrar yasağı:** her bilgi yalnızca bir sayfada geçer. Aşağıdaki "sahip olduğu bilgi"
sütunu bunun için var: bir sayı ya da iddia başka bir sayfaya taşınacaksa buradan
silinir. Sayılar yalnızca ölçüm belgelerinden alınır, elle yazılmaz (bkz. `CLAUDE.md`).

| # | Bölüm | Süre | Sahip olduğu bilgi | Görsel | Kaynak |
|--:|---|--:|---|---|---|
| 1 | Kapak | 0:15 | Proje adı: *N-Emek — Açıklanabilir İçerik Atıf ve Adil Gelir Paylaşım Sistemi* · İçerik Ekonomisi · ZENITH N · 1003461 · 5382505 | şablon | `RAPOR/_OKUBENI.md` |
| 2 | Takım Tanıtımı | 0:20 | Kaptan: **Hamza Budak**, yazılım mimarisi ve testler, Bursa Teknik Üniversitesi Fizik Lisans 3. sınıf · Üye: **Berra Özer**, kullanıcı deneyimi ve geliştirme, Bursa Teknik Üniversitesi Fizik Lisans 3. sınıf · danışman ve Üye 2–5 kutuları kaldırılır · **fotoğraf yok**, boş fotoğraf çerçeveleri de kaldırılır | şablon kutuları | takım |
| 3 | Proje Özeti ve Kapsamı | 0:50 | Konu ve amaç tek cümlede · tematik alan ve katkı sağladığı süreç (paylaşım ve remix zincirinde gelir dağıtımı) · yöntemin ana hatları | Yatay akış: yükleme → köken kurtarma → ölçüm → Emek Kartı → dağıtım → itiraz | `RAPOR/01` |
| 4 | Problemin Tanımı | 1:15 | Zincirin kopuşu (Ayşe → Burak → Ceyda) · üç bileşen: kimlik kırılganlığı, ölçüm yokluğu, açıklanamazlık · üretici ekonomisinin büyüklüğü ve gelir dengesizliği [2][3] · hukuki çerçeve: FSEK 5846, AB 2019/790 [4][5] · mevcut yaklaşımlar ve eksikleri tablosu | Üç adımlık kopuş şeması + tablo | `RAPOR/02` §2.1 |
| 5 | Çözüm Önerisi (1/2) | 1:15 | "Bulmak değil, ölçmek" iddiası · pay = kapsama × güven × sönümleme, gerçek bir pay satırıyla · kaynaktan gelen piksellerin görünür kılınması | `03-pay-gerekcesi.jpg`, `05-olculen-bolge-oran.jpg` | `SUNUM.md` 4, 8, 9 · rakamlar çalışan sistemden |
| 6 | Çözüm Önerisi (2/2) | 1:00 | Yetenek karşılaştırma matrisi: kaynağı bulur / oranı ölçer / kimlik silinse de çalışır / açıklanabilir / geliri böler · "sistem asla 'sahibi budur' demez" · itiraz → yeniden ölçüm → insan incelemesi · kullanıcıya ve ekosisteme katkı | Matris + itiraz akışı | `RAPOR/02` §2.2 · `VERI-MODEL-ETIK.md` §5–6 |
| 7 | Yöntem (1/2) | 1:15 | Sistem mimarisi · altı aşamalı köken kurtarma hattı ve aşama güvenleri · yapay zekânın rolü: CLIP aday üretir, kararı geometri verir, eğitim yok | Katmanlı mimari şeması (yerel şekiller) + aşama tablosu | `MIMARI.md` · `YZ-MIMARISI.md` §1, §4 |
| 8 | Yöntem (2/2) | 1:15 | Veri seti ve doğrulama: 320 görsel, 20 türev senaryosu, 6.400 sorgu, negatif kontrol · metrikler: Top-1, F1, yanlış atıf, kapsama MAE, gecikme · geçişli indirgeme ve özel kapsama · veri güvenliği, mahremiyet ve etik | Metrik tablosu | `DEGERLENDIRME.md` · `GECIKME.md` · `VERI-MODEL-ETIK.md` |
| 9 | Prototip / Uygulama Geliştirme Durumu | 1:15 | Tasarım → kodlama → entegrasyon → test, hepsi tamamlandı · kullanıcı akışı ve temel ekranlar · tasarım kararları (renk disiplini, kontrastla maske) · erişilebilirlik denetimi · kullanıcı araştırması ve kullanılabilirlik testi (SUS 60,0, bulguların durumu) · *canlı gösterim sunumun sonunda (12 Eyl transkripti)* | `01-akis.jpg`, `04-olculen-bolge.jpg`, `11-mobil.jpg` | `ERISILEBILIRLIK.md` · `KULLANILABILIRLIK-SONUCLARI.md` · `KULLANICI-ARASTIRMASI.md` |
| 10 | Uygulanabilirlik ve Sürdürülebilirlik (1/2) | 1:15 | İş ve gelir modeli: ₺50.000 kampanyanın ölçülmüş dağıtımı · bugünkü model ile N-Emek karşılaştırması ("havuz büyümüyor, yer değiştiriyor") · komisyon ve ticarileştirme akışları · benimseme yolu | Karşılaştırma tablosu | `IS-MODELI.md` §2–5, §8 |
| 11 | Uygulanabilirlik ve Sürdürülebilirlik (2/2) | 1:00 | Ölçeklenme: içerik başına tek seferlik maliyet, açılış süresi, indeks ve veritabanı geçiş yolu · birim ekonomi · finansal, teknik ve sosyal sürdürülebilirlik · riskler ve karşı önlemler | Ölçek yolu şeması | `ACILIS-SURESI.md` · `MIMARI.md` §6 · `IS-MODELI.md` §6, §10 · `RAPOR/06` §6.2 |
| 12 | Özgünlük ve Yerlilik Yönü | 1:00 | Takımın yazdığı özgün çekirdek: filigran (CRC-16), pay motoru, çok bölgeli sorgu · C2PA'nın ekonomik paylaşım için kullanılması · yerlilik (dürüst hâli): hangi bileşen açık kaynak, hangisi takımın · Türkçe arayüz ve N'Sosyal hedefi | "Hazır bileşen ve özgün katman" şeması | `RAPOR/02` §2.2 · `YZ-MIMARISI.md` §5 |
| 13 | Hedef Kitle ve Yaygın Etki | 0:50 | Dört aktör ve her birine sağlanan fayda (üretici, remixleyen, marka, platform) · erişim potansiyeli, TÜİK 2025 [1] · toplumsal ve yöntemsel etki | Aktör tablosu | `RAPOR/04` §4.2 · `RAPOR/05` |
| 14 | Proje Takvimi | 0:45 | 11 iş paketi, alt faaliyetleri, başlangıç ve bitiş tarihleri, durum | Şablon tablosu genişletilir | `scripts/rapor_takvim.py` `PAKETLER` · `RAPOR/07` |
| | **Toplam** | **≈ 14:30** | | | |

Puan ölçütleriyle eşleşme:

| Ölçüt | Sayfalar |
|---|---|
| Yenilikçilik %20 | 5, 12 |
| Teknik Yeterlilik %20 | 7, 8 |
| Problem Çözme %20 | 4, 6 |
| UI/UX %20 | 5, 9 |
| İş Modeli %10 | 10, 11 |
| Sunum ve Prototip %10 | 9 ve canlı gösterim |

### Çakışma riski olan bilgiler ve kararlar

| Bilgi | Hangi sayfada | Neden orada |
|---|---|---|
| Mevcut çözümlerin eksikleri | 4 (tablo) | Problem sayfası "mevcut çözümler ve eksikleri" istiyor. 6. sayfa aynı yöntemleri eksiklerini tekrar etmeden **yetenek matrisi** olarak karşılaştırır |
| TÜİK internet kullanımı [1] | 13 | Erişim potansiyelidir. 4. sayfa üretici ekonomisi verilerini [2][3] kullanır |
| Değerlendirme metrikleri | 8 | Özet sayfasına rakam konmaz |
| Geçişli indirgeme ve özel kapsama | 8 | 12. sayfa bunlara "özgün pay motoru" diye yalnızca adıyla atıf yapar |
| Açılış süresi (11,5 sn → 16 ms) | 11 | Ölçeklenme kanıtıdır, prototip sayfasına girmez |
| Kampanya rakamları | 10 | ₺34.548,96 `IS-MODELI.md`'den alınır. Eski taslaktaki ₺34.545,80 kullanılmaz |

---

## 3 · Üretim düzeni

Teknik raporla aynı ilke: **içerik tek kaynakta, dosya üretilir, sunum PowerPoint'te elle düzenlenmez.**

```
docs/NSosyal_Inovasyon_Yarısması_Sunum_Sablonu_1_2_2_TTN8G.pptx   şablon (elle açılmaz)
docs/SUNUM/NN-*.md          sayfa başına içerik + konuşmacı notu
scripts/sunum_pptx.py        şablon kopyası → docs/SUNUM/N-Emek-Sunum.pptx + denetim
scripts/sunum_powerpoint.ps1 PowerPoint ile çizim: taşma denetimi, PNG önizleme, PDF
```

Üreticinin yaptıkları:
- kuralları sayfasını siler
- Çözüm, Yöntem ve Uygulanabilirlik sayfalarını ikiler (sağ şerit vurgusu korunur)
- kırmızı yönergeleri siler
- kapağı, takım sayfasını ve alt banttaki değerleri doldurur
- içeriği yerleştirir

Denetim (biri tutmazsa betik durur):
- bölüm başına sayfa sınırı, toplam en fazla 19 sayfa
- kırmızı yönerge metni kalmamış
- "ÜYE 2", "(VARSA)" gibi yer tutucu kalmamış
- her içerik sayfasında takım değerleri var
- **sayfalar arasında aynı cümle yok**
- metin kutusu taşması yok
- PDF en fazla 75 MB
- takvim tarihleri `rapor_takvim.py` ile aynı

Punto: gövde 22–24 pt, tablolar 18–20 pt, kaynak satırı 14 pt. Sahnede okunaklı olması için 18 pt'nin altına inilmez
(kaynak satırı hariç).

---

## Durum (15 Eylül)

- İskelet ve 14 sayfanın içeriği üretildi. `sunum_pptx.py` denetimi temiz; `sunum_powerpoint.ps1` sonucunda taşma yok, `dokuman_denetimi.py` geçiyor.
- İçerik kaynağı `docs/SUNUM/03…14-*.md`, yerleşimler `scripts/sunum_sayfalar.py` içinde.
- Çözüm 1/2 sayfasındaki pay rakamları (%87,2 · 0,95 · 0,85 → %68,2) ekran görüntüleriyle aynı koşumdan alındı. Yerel demo veritabanı RANSAC oynaması nedeniyle %87,1 ve %68,1 veriyor.
- Konuşma notları toplam 1.187 kelime: 130 kelime/dk hızla yaklaşık 9 dk, kapak ve takım hariç. 15 dakikaya tamamlanması provada yapılacak.
- Eski belgeler (`SUNUM.md`, `CLAUDE.md`, `README.md`, `PLAN.md`, `MENTORLUK.md`) yeni düzene göre güncellendi.

## Görev dağılımı ve devir (15 Eylül akşamı)

**Sunum kısmını Berra Özer üstleniyor.** Hamza Budak sistem ve canlı demo tarafında.
Bu bölüm devir notudur: sunumu açan kişi buradan başlar.

**Önkoşul:** Windows + PowerPoint kurulu, `.venv/Scripts/python.exe -m pip install python-pptx`.

**Üretim döngüsü** (her içerik değişikliğinden sonra üçü birden):

```
.venv/Scripts/python.exe scripts/sunum_pptx.py                           # md -> pptx, denetim
powershell -ExecutionPolicy Bypass -File scripts/sunum_powerpoint.ps1    # tasma + onizleme
.venv/Scripts/python.exe scripts/dokuman_denetimi.py                     # sayisal iddialar
```

Teslimden önce ikinci komut `-Pdf` ile çalıştırılır. İçerik yalnızca `docs/SUNUM/NN-*.md`
dosyalarında düzenlenir; üretilen `.pptx` elle düzenlenirse bir sonraki üretimde kaybolur.

**15 Eylül incelemesinde düzeltilen:** 9. sayfa "canlı gösterim bu sayfanın ardından"
diyordu. 12 Eylül transkriptine göre sıra *sunum → kısa soru-cevap → jüri çağırınca 2–3 dk
prototip*; gösterim sunumun sonunda. Sayfa yazısı ve konuşma notu düzeltildi.

**Açık revizyon kararları (sunum sahibinin kararı):**

| Konu | Bulgu | Seçenekler |
|---|---|---|
| Okunabilirlik | Şablon 50,8 cm, yani standart geniş slaytın 1,5 katı: burada 12 pt, standartta 8 pt'ye denk. Yukarıdaki 18 pt kuralı uygulamada tutmadı; 32 yerde 11,5–13,5 pt, 31 yerde 14–16 pt var | B1 olduğu gibi · **B2 en az 16 pt, metin ~%25 kısalır, ayrıntı nota geçer** · B3 boş sayfa hakkı (Çözüm 3/3, Özgünlük 2/2) ile 16 sayfa |
| Süre | Notlar ~9 dk | ~1.700 kelimeye (13 dk) genişletip 2 dk pay bırakmak |
| Sayı tutarlılığı | 5. sayfa %87,2 · %68,2 · ₺2.576,30; yerel demo veritabanı %87,1 · %68,1 · ₺2.574,63. 10. sayfa ₺34.548,96; yerel veritabanı ₺34.541,45 | Demo yerel veritabanıyla yapılacak (15 Eyl kararı). Sayılar ondan okunup güncellenebilir ya da olduğu gibi bırakılır; demoda sayılar ekrandan okunuyor (`DEMO-SENARYOSU.md` başındaki durum notu) |
| Küçük | 6. sayfada "Kimlik silinse / de" başlığı bölünüyor · 9. sayfadaki üç ekran görüntüsü perdede okunmuyor, akış görüntüsü de üç gönderi gösteriyor; canlı demoda akışta 31 gönderi var (15 Eyl zenginleştirme, 18 Eyl türev zincirleri) · 13. sayfadaki "%69" ile 10. sayfadaki ₺34.548,96 aynı olguyu anlatıyor | — |

Şablon hataları dokunulmadan kalır: 13. sayfa alt bilgisinde "22026", Uygulanabilirlik
başlığında "SÜRDÜRÜLEBİLİRİLİK", sağ şeritte üst üste binen iki bölüm adı.

## 4 · İş sırası

| Gün | İş |
|---|---|
| 15 Eyl | Üreticinin iskeleti: sayfa ikileme, yönergelerin silinmesi, kapak, takım, alt bant. İçeriksiz 14 sayfanın önizlemesi |
| 15–16 Eyl | 14 sayfanın içerik dosyaları. Sayılar kaynak belgelerden, pay rakamları çalışan sistemden doğrulanır |
| 16 Eyl | Yerleştirme ve özel sayfalar (mimari şeması, takvim tablosu). Önizleme ve düzeltme döngüsü. ~16 Eylül toplantısında şablonla ilgili açık sorular sorulur |
| 17 Eyl | Konuşma notları, süre provası (15 dk), denetimler, PDF. **Akşam KYS'ye yükleme** |
| 18 Eyl | Yedek gün: yalnızca düzeltme, yeni içerik yok |

## 5 · Açık sorular

- ~~Eğitim bilgisine üniversite adı~~ → karar: Bursa Teknik Üniversitesi, Fizik Lisans, 3. sınıf.
- ~~Takım sayfasına fotoğraf~~ → karar: fotoğraf yok.
- 15 dakikaya jüri soruları dahil mi? 16 Eylül toplantısında sorulacak (`MENTORLUK.md` §6).
- Jüriye sunumun basılı ya da ekrandan kopyası veriliyor mu? Punto kararını etkiler.
