# 8 · TAKIM YAPISI

## 8.1. Takım Organizasyonu ve Roller

Değerlendirme esasları gereği takım üyelerinin isim, fotoğraf ve benzeri kişisel
bilgilerine bu raporda yer verilmemiştir. Aşağıdaki tablo görev dağılımını rollerle
tanımlar.

| # | Rol / disiplin | Sorumlu olduğu iş paketleri | Projeye katkısı |
|---|---|---|---|
| 1 | Tam yığın geliştirme — birincil sorumluluk: köken kurtarma motoru, ölçüm ve altyapı | İP-1, İP-2, İP-3, İP-4 birincil; İP-5 – İP-10 ortak | Köken kurtarma hattının altı aşaması, karar füzyonu ve güven eşiklerinin ölçümle kalibrasyonu; katkı payı motoru (geçişli indirgeme ve özel kapsama bölüntüsü dahil); backend servisleri, veri modeli ve katmanların veritabanından ayrıştırılması; 20 türev senaryosu, korpus tekilleştirmesi ve 6.400 sorguluk değerlendirme düzeneği |
| 2 | Tam yığın geliştirme — birincil sorumluluk: arayüz, erişilebilirlik ve ürün | İP-5, İP-6 birincil; İP-1 – İP-4 ve İP-7 – İP-10 ortak | Referans istemci, Emek Kartı ve açıklanabilirlik ekranları, remix stüdyosu, tasarım sistemi ve zincir görselleştirmesi; WCAG 2.1 AA denetimi ve mobil düzen ölçümü; iş ve gelir modeli, kampanya kuralları; kullanıcı araştırması ile kullanılabilirlik testinin yürütülmesi |

**Disiplinlerin projeye katkısı.** Proje tek bir uzmanlıkla çözülemeyecek bir problem
tanımı üzerine kuruludur; iki kişilik takımda bu, keskin bir uzmanlık ayrımı yerine iki
birincil sorumluluk alanı olarak tanımlandı. Her iki üye de yığının her katmanında
çalıştı, birincil sorumluluk ise paketin kritik kararını kimin verdiğini gösterir:

- **Motor, ölçüm ve altyapı.** Köken kurtarma hattının aşamaları, karar füzyonu ve
  eşiklerin kalibrasyonu (İP-2); katkı payı motoru ve gelir dağıtımı (İP-3); backend
  mimarisi, Docker ile dağıtım ve sürekli tümleştirme (İP-1); saldırı senaryosu
  üreticisi, değerlendirme düzeneği ve metrik üretimi (İP-4). Bu alanın ayırt edici
  zorluğu model seçmek değildi; yöntemlerin hangi koşulda hangisine devredeceğine
  ölçümle karar vermek, korpustaki veri sızıntısını bulup temizlemek ve beklenen
  kapsama değerlerini elle etiketlemek yerine geometriden türetmekti.
- **Arayüz, erişilebilirlik ve ürün.** Referans istemci, Emek Kartı ve
  açıklanabilirlik ekranları, tasarım sistemi, erişilebilirlik denetimi ve mobil düzen
  ölçümü (İP-5); iş ve gelir modeli, kampanya kuralları, benimseme yolu, kullanıcı
  araştırması ve kullanılabilirlik testinin yürütülmesi (İP-6). Bu alanın ayrı bir
  birincil sorumluluk olarak tanımlanmasının sebebi, puanlamada kullanıcı deneyiminin
  yapay zekâ bileşeniyle eşit ağırlıkta olması ve gelir dağıtan bir sistemde
  açıklanabilirliğin bir arayüz süsü değil meşruiyet koşulu olmasıdır.

**Ekip büyüklüğü.** Takım iki kişiden oluşmaktadır; şartnamenin öngördüğü 2-5 kişilik
aralıktadır. Paketlerin tamamı takım içinde karşılık bulmakta, dışarıdan hizmet alımı
gerektiren bir kalem bulunmamaktadır.

**Ortak çalışma yöntemi.** Kod tek bir depoda tutulur ve her değişiklik commit
geçmişinde gerekçesiyle kayıtlıdır. Ölçüm sonuçları ve dokümanlar da aynı depodadır;
bir doküman ile ürün arasında sayı uyuşmazlığı oluştuğunda sürekli tümleştirme bunu
hata olarak bildirir. Bu düzen, iş paketleri arasında bilgi kaybını önlemek ve her
iddianın kaynağına geri izlenebilmesini sağlamak için kuruldu. İki kişilik bir takımda
aynı düzen ikinci bir işlev daha görür: doğrulama yükünü kişiden betiğe aktardığı için
her iddianın gözden geçirilmesi ekip büyüklüğüne bağlı kalmaz.
