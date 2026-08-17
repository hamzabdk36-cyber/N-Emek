# 8 · TAKIM YAPISI

## 8.1. Takım Organizasyonu ve Roller

Değerlendirme esasları gereği takım üyelerinin isim, fotoğraf ve benzeri kişisel
bilgilerine bu raporda yer verilmemiştir. Aşağıdaki tablo görev dağılımını rollerle
tanımlar.

| # | Rol / disiplin | Sorumlu olduğu iş paketleri | Projeye katkısı |
|---|---|---|---|
| 1 | ___ | ___ | ___ |
| 2 | ___ | ___ | ___ |
| 3 | ___ | ___ | ___ |
| 4 | ___ | ___ | ___ |
| 5 | ___ | ___ | ___ |

**Disiplinlerin projeye katkısı.** Proje, tek bir uzmanlıkla çözülemeyecek bir problem
tanımı üzerine kuruludur ve iş paketleri bu nedenle farklı disiplinlere dağıtılmıştır:

- **Yapay zekâ ve görüntü işleme.** Köken kurtarma hattının altı aşaması, karar füzyonu
  ve eşik kalibrasyonu (İP-2). Bu paketin ayırt edici zorluğu model seçmek değil,
  yöntemlerin hangi koşulda hangisine devredeceğine ölçümle karar vermekti.
- **Veri bilimi ve değerlendirme.** Saldırı senaryosu üreticisi, korpus hazırlığı,
  6.400 sorguluk değerlendirme düzeneği ve metrik üretimi (İP-4). Korpustaki veri
  sızıntısını bulup temizleyen ve beklenen kapsama değerlerini geometriden türeten
  çalışma bu pakettedir.
- **Yazılım geliştirme ve mimari.** Backend servisleri, veri modeli, katman ayrımı,
  Docker ile dağıtım ve sürekli tümleştirme kurulumu (İP-1, İP-3). `provenance/` ve
  `attribution/` katmanlarının veritabanını tanımaması bu paketin ölçeklenebilirliğe
  yaptığı yapısal katkıdır.
- **Kullanıcı deneyimi (UI/UX) ve tasarım.** Referans istemci, Emek Kartı,
  açıklanabilirlik ekranları, tasarım sistemi, erişilebilirlik denetimi ve mobil düzen
  (İP-5). Puanlamada UI/UX'in yapay zekâ bileşeniyle eşit ağırlıkta olması bu paketin
  ayrı bir sorumluluk olarak tanımlanmasının sebebidir.
- **Ürün yönetimi ve girişimcilik.** İş ve gelir modeli, kampanya kuralları, benimseme
  yolu, kullanıcı araştırması ve kullanılabilirlik testinin yürütülmesi (İP-6). Ölçülen
  dağıtım rakamlarının bugünkü modelle karşılaştırılması bu pakettedir.

**Ekip büyüklüğü.** Takım ___ kişiden oluşmaktadır; şartnamenin öngördüğü 2-5 kişilik
aralıktadır. Paketlerin tamamı takım içinde karşılık bulmakta, dışarıdan hizmet alımı
gerektiren bir kalem bulunmamaktadır.

**Ortak çalışma yöntemi.** Kod tek bir depoda tutulur ve her değişiklik commit
geçmişinde gerekçesiyle kayıtlıdır. Ölçüm sonuçları ve dokümanlar da aynı depodadır;
bir doküman ile ürün arasında sayı uyuşmazlığı oluştuğunda sürekli tümleştirme bunu
hata olarak bildirir. Bu düzen, iş paketleri arasında bilgi kaybını önlemek ve her
iddianın kaynağına geri izlenebilmesini sağlamak için kuruldu.
