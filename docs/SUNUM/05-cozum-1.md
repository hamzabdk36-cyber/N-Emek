# 05 · Çözüm Önerisi (1/2)

<!-- Rakamlar ekran görüntüleriyle aynı koşumdan (docs/gorseller, 11 Eylül
2026, Docker demo verisi). Geometrik doğrulama RANSAC kullandığı için başka
bir koşumda binde birkaç oynayabilir; slayttaki yazı ile görsel çelişmesin
diye metin görselin koşumuna bağlandı. -->

## ana
Kaynağı bulmak yetmez: pay, kaynaktan **ne kadar** kullanıldığına göre belirlenmeli.

## bolge_gorsel
![Burak Demir'in içeriği ve Ceyda'nın gönderisinde kaynaktan geldiği ölçülen bölge](../gorseller/05-olculen-bolge-oran.jpg){kirp=598,42,1330,382}

## bolge_aciklama
Solda kaynak, sağda türev. Kaynaktan geldiği piksel piksel doğrulanan bölge parlak kalır; türevi yapanın eklediği yazı bandı ve çizim griye düşer.

## olcum
### Ölçüm nasıl yapılıyor
- Kaynak ile türev arasında yerel özellik noktaları eşlenir, homografi kestirilir.
- Kaynak türevin çerçevesine yerleştirilir ve her bölge piksel düzeyinde doğrulanır.
- Çıkan sayı **kapsama**: türevin kaynaktan geldiği kanıtlanan alan oranı. Bu örnekte %12,5.

## formul
pay = kapsama × güven × zincir sönümlemesi

## kart_gorsel
![Emek Kartı'nda Ayşe Yılmaz satırı: kapsama, güven, sönümleme ve formül](../gorseller/03-pay-gerekcesi.jpg){kirp=614,442,1316,612}

## carpanlar
- **Kapsama %87,2** · Ayşe'nin fotoğrafından gelen, ölçümle doğrulanmış alan.
- **Güven 0,95** · bu bağı destekleyen kanıtların birleşik gücü.
- **Sönümleme 0,85** · Ayşe zincirde iki adım geride; her adımda pay azalır.
- **Sonuç** · ham ağırlık 0,706; dağıtılan tutardan Ayşe'ye düşen pay %68,2.
> Her rakamın altında düz Türkçe bir gerekçe cümlesi durur; kullanıcı formülü okumak zorunda kalmaz.

## kaynak
Ekran görüntüleri çalışan prototipten, demo senaryosu (11 Eylül 2026).

## not
Çözümün özü tek cümle: kaynağı bulmak yetmez, pay kaynaktan ne kadar kullanıldığına göre belirlenmeli. Soldaki görüntü bunu gösteriyor. Solda Burak'ın içeriği, sağda Ceyda'nın gönderisi. Parlak kalan bölge, Burak'ın içeriğinden geldiği piksel piksel doğrulanan alan; kararan yazı bandı ve çizim o kaynaktan gelmiyor. Bunu yerel özellik eşleme, homografi ve piksel doğrulamasıyla yapıyoruz ve ortaya bir sayı çıkıyor: kapsama. Sağda bu sayının paya nasıl dönüştüğü var: pay eşittir kapsama çarpı güven çarpı zincir sönümlemesi. Ayşe için kapsama yüzde 87,2, güven 0,95, iki adım geride olduğu için sönümleme 0,85; dağıtılan tutarın yüzde 68,2'si Ayşe'ye gidiyor. Ekranda bu formülün yanında düz Türkçe bir gerekçe cümlesi de yazıyor.
