# 7 · PROJE TAKVİMİ

## 7.1. İş Paketleri ve Zamanlama

Proje 8 Ağustos 2026'da başladı ve 20 Eylül 2026'daki canlı sunumla tamamlanacaktır.
Takvim, yarışma takviminin dört sert tarihi etrafında kuruldu: **teknik rapor teslimi
24 Ağustos**, **mentörlük süreci 2-7 Eylül**, **final sunumu ve prototip teslimi
14 Eylül**, **jüri ve katılımcılara canlı sunum 20 Eylül**.

![Şekil 6 — İş paketleri ve zaman çizelgesi. Kırmızı işaretler yarışma takviminin sert tarihleri; renkler paketin durumunu gösterir.](docs/gorseller/12-takvim.png)

**İş paketleri ve alt faaliyetler.**

| Kod | İş paketi | Alt faaliyetler | Tarih | Durum |
|---|---|---|---|---|
| İP-1 | Altyapı ve risk kapatma | Monorepo iskeleti, veri modeli, API sözleşmesi; üç riskli bileşenin kavram kanıtı | 8-9 Ağu | Tamamlandı |
| İP-2 | Köken kurtarma hattı | Altı aşama, karar füzyonu, kanıt üretimi, eşik kalibrasyonu | 9-10 Ağu | Tamamlandı |
| İP-3 | Katkı payı ve gelir | Pay motoru, geçişli indirgeme, özel kapsama bölüntüsü, Emek Kartı, kampanya dağıtımı, itiraz akışı | 10-11 Ağu | Tamamlandı |
| İP-4 | Değerlendirme ve ölçüm | 20 türev senaryosu, korpus tekilleştirme, 6.400 sorguluk değerlendirme, gecikme ölçümleri | 8-11 Ağu | Tamamlandı |
| İP-5 | Arayüz ve erişilebilirlik | Referans istemci, remix stüdyosu, zincir görseli, tasarım sistemi, WCAG denetimi, mobil düzen | 10-11 Ağu | Tamamlandı |
| İP-6a | Kullanılabilirlik testi | Protokol, beş katılımcıyla oturumlar, SUS ölçeği, bulguların kaydı | 12-22 Ağu | Tamamlandı |
| İP-6b | Kullanıcı araştırması | Görüşme rehberi, on katılımcıyla görüşme, varsayımların sınanması | 22 Ağu | Tamamlandı |
| İP-7 | Teknik rapor | İçerik yazımı, kaynakça, görsellerin üretimi, biçim denetimi, KYS'ye yükleme | 14-23 Ağu | Sürüyor |
| İP-8 | Ürünleştirme ve mentörlük | Mentör geri bildirimleri, ölçeklenme hazırlıkları, bilinen açıkların kapatılması | 25 Ağu - 7 Eyl | Planlı |
| İP-9 | Final paketi | Demo videosu, sunum dosyası, kod temizliği, jüri makinesi tatbikatı | 8-14 Eyl | Planlı |
| İP-10 | Canlı sunum | Sunum provası, soru-cevap hazırlığı, internetsiz ortam için yedek demo kaydı | 15-20 Eyl | Planlı |

**Kilometre taşları.**

| # | Kilometre taşı | Tarih | Kanıtı |
|---|---|---|---|
| KT-1 | Üç teknik risk kapatıldı | 9 Ağu | Kavram kanıtı sonuçları belgelendi |
| KT-2 | Kimliği silinmiş içerikten zincir kuruldu | 10 Ağu | Altın senaryo uçtan uca koştu |
| KT-3 | Havuz ölçülmüş katkıya göre bölündü | 11 Ağu | Kayıtlı ödeme satırları, toplam havuza eşit |
| KT-4 | Değerlendirme tamamlandı | 11 Ağu | 6.400 sorgu, Top-1 %98,7, F1 0,9753 |
| KT-5 | Erişilebilirlik denetimi tamamlandı | 11 Ağu | On bir kusur bulundu; düzeltmelerden sonra altı rotada sıfır bulgu |
| **KT-6** | **Teknik rapor KYS'ye yüklendi** | **23 Ağu** | Şartname son tarihi 24 Ağustos 17:00 |
| KT-7 | Kullanılabilirlik testi sonuçlandı | 22 Ağu | Beş katılımcı · SUS 60,0 — hedef ≥68'in altında · yedi bulgu |
| KT-7b | Kullanıcı araştırması tamamlandı | 22 Ağu | On görüşme · üç varsayım sınandı |
| KT-8 | İlk mentör görüşmesi yapıldı | 12 Eyl | Yarışma takvimi değişti — bkz. `_OKUBENI.md` |
| **KT-9** | **Final paketi (sunum dosyası) teslim edildi** | **18 Eyl** | Yarışma takvimi değişti — bkz. `_OKUBENI.md` |
| KT-10 | Jüri önünde canlı sunum yapıldı | 20 Eyl | İstanbul, şartnamede ilan edilen canlı sunum tarihi |

**Takvimin gerçekçiliği ve yarışma takvimiyle uyumu.** Dört nokta bilinçlidir:

- **Rapor 24 Ağustos'a değil, 23 Ağustos'a planlandı.** Şartname geç yüklenen raporun
  değerlendirmeye alınmayacağını söylüyor; son günün son saatine bırakmak, kabul
  edilebilir olmayan tek riski üretirdi.
- **İP-6 ikiye ayrıldı.** Kullanıcı tarafındaki iki iş farklı sorular soruyor:
  kullanılabilirlik testi *ürün kullanılabiliyor mu* (İP-6a), kullanıcı araştırması
  *problem gerçek mi* (İP-6b). İkisi ayrı katılımcılarla koşuldu ve ikisi de rapordan
  önce tamamlandı.
- **25 Ağustos - 1 Eylül aralığı teknik rapor sonuçlarının beklendiği dönemdir.** Bu
  süre boş bırakılmadı; ürünleştirme çalışmaları bağımsız olarak sürüyor, mentörlük
  başladığında (2 Eylül) ürün geri bildirim alabilecek durumda oluyor.
- **Final teslimi ile canlı sunum arasındaki altı gün geliştirmeye ayrılmadı.**
  Prototip 14 Eylül'de teslim edileceği için 15-20 Eylül aralığında ürün dondurulacak;
  İP-10 yalnızca sunum provası, olası jüri sorularının hazırlığı ve yedek demo
  kaydından oluşuyor. Sunumun internet veya GPU bulunmayan bir ortamda da
  yapılabilmesi, canlı demonun tek noktaya bağlı kalmaması için gereklidir.

**Geliştirmenin sıkıştırılmış olması.** İlk beş iş paketi dört güne sığdırıldı; bu, ön
başvuru sonrası kalan sürenin kısalığından kaynaklanan bilinçli bir yoğunlaştırmadır.
Sıkıştırmanın mümkün olmasının nedeni, riskli bileşenlerin en başta kavram kanıtıyla
denenmesidir (İP-1): üç riskin de erken kapatılması, sonraki paketlerde geri dönüş
gerektirecek bir sürprizi engelledi. Bu tercihin izi commit geçmişinde takip edilebilir.
