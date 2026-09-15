# 10 · Uygulanabilirlik ve Sürdürülebilirlik (1/2)

<!-- Rakamlar: docs/IS-MODELI.md §2-§3 (seed_demo.py --reset sonrası kayıtlı
Payout satırları). -->

## model
### İş ve gelir modeli
Marka kampanya havuzu son paylaşana değil, **ölçülmüş katkıya göre zincirin tamamına** bölünür. Platform havuzdan komisyon alır: %10, kampanya başına ayarlanabilir.

## dagitim
| Kişi | Bugünkü model | N-Emek ile | Fark |
|---|---|---|---|
| Ayşe · özgün üretici | ₺6.750,00 | **₺34.548,96** | **5,1×** |
| Burak · remixleyen | ₺14.625,00 | ₺5.726,04 | 0,39× |
| Ceyda · paylaşan | ₺23.625,00 | ₺4.725,00 | 0,20× |
| N'Sosyal · platform | ₺5.000,00 | ₺5.000,00 | aynı |

## dagitim_not
Demo kampanyası: havuz ₺50.000, komisyon %10, kaynak tabanı %15, üretici tabanı %20. Tutarlar sistemin kayıtlı ödeme satırlarından okundu.

## havuz
### Havuz büyümüyor, yer değiştiriyor.
İddiamız herkesin daha çok kazanması değil, ödemenin ölçülmüş katkıya gitmesi. Denge kuralları kampanyada yazılı: üretici tabanı %20, üretici tavanı %80.

## ticari
### Ticarileştirme
- **Bugün çalışan:** kampanya komisyonu. Yeni bir ödeme davranışı icat etmez; mevcut marka işbirliklerinin bölünme kuralını değiştirir.
- **Aynı altyapının izin verdiği** (henüz ölçülmedi): kampanya dışı gönderi gelirinin paylaşımı, üçüncü taraflara atıf API'si, ajans ve yayıncılar için köken denetimi.

## benimseme
- **Tek kampanya pilotu** · kaç kaynak bulundu, kaç itiraz açıldı
- **Üreticiye bildirim** · "içeriğin şurada kullanıldı"; platformda kalma oranı
- **Platform geneli** · yanlış atıf oranı ölçekte korunuyor mu
- **Atıf API'si** · sorgu hacmi ve gecikme

## kaynak
N-Emek iş ve gelir modeli, demo kampanyasının kayıtlı ödemeleri (docs/IS-MODELI.md).

## not
Gelir modeli platformda zaten var olan bir şeyin üstüne kuruluyor: marka kampanyaları. Değiştirdiğimiz tek şey havuzun bölünme kuralı. Tablo aynı 50 bin liralık havuzun iki modelde nasıl dağıldığını gösteriyor. Bugün para gönderiyi paylaşana gidiyor ve Ceyda en çok alıyor. N-Emek ile Ayşe hiç remix yapmadan beş katından fazla alıyor, çünkü içeriği zincirde yaşıyor ve bu ölçüldü. Burak ve Ceyda daha az alıyor; bunu saklamıyoruz. Havuz büyümüyor, yer değiştiriyor. Platform yüzde 10 komisyonunu her iki modelde de alıyor. Sağda ticarileştirme ve benimseme yolu var: önce tek bir marka ile pilot, sonra üreticiye bildirim, platform geneli ve en son atıf API'si. Her aşama bir öncekinin ölçümüne bağlı.
