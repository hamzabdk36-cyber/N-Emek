# 06 · Çözüm Önerisi (2/2)

## ana
Her yöntem sorunun bir parçasını çözüyor; N-Emek hepsini ölçüm katmanında birleştiriyor.

## matris
| Yöntem | Kaynağı bulur | Kimlik silinse de | Oranı ölçer | Gerekçe gösterir | Geliri böler |
|---|---|---|---|---|---|
| C2PA | var | yok | yok | kısmen | yok |
| Görünmez filigran | var | kısmen | yok | yok | yok |
| Algısal hash | var | kısmen | yok | yok | yok |
| CLIP benzerliği | var | var | yok | yok | yok |
| Telif eşleştirme | var | var | yok | yok | kısmen |
| N-Emek | var | var | var | var | var |

## matris_not
"Kısmen": C2PA imzalı bir köken beyanı taşır ama kullanım ölçmez; filigran ve hash hafif değişikliklerde çalışır; telif eşleştirme geliri hak sahibine yönlendirir, katkıya göre bölmez.

## itiraz
- **Payın sahibi itiraz eder** · yalnızca kendi payına
- **Bağ yeniden ölçülür** · daha hassas SIFT dedektörüyle
- **Paylar güncellenir** · sonuç değiştiyse dağıtım tekrarlanır
- **Çözülmezse insana** · moderatör inceleme kuyruğu

## asla
### Sistem asla şunu demez:
> "Bu içeriğin sahibi budur."
Bunun yerine kanıtlarıyla bir zincir **önerisi** sunar:
- Onaylanmamış bağ grafikte kesikli çizilir.
- Ölçülemeyen kapsama için sayı uydurulmaz; ekranda "ölçülemedi" yazar.
- Karar veremediği durumu gizlemez, insana devreder.

## katki
### Ekosisteme katkı
- **Atıf ölçüme taşınır:** kaynak anmak hatırlamaya ve iyi niyete bağlı kalmaz.
- **Marka bütçesi denetlenebilir:** her ödemenin altında hangi ölçümün durduğu görülür.
- **Anlaşmazlık ucuzlar:** tartışma hukuki süreçten önce tekrar üretilebilir bir ölçüme bağlanır.

## not
Mevcut yöntemleri tek tek karşılaştırdığımızda her biri sorunun bir parçasını çözüyor. C2PA kaynağı söylüyor ama kimlik silinince kör. Filigran ve algısal hash hafif değişikliklerde çalışıyor. CLIP ağır düzenlemede bile benzerliği buluyor ama oran ölçmüyor. Telif eşleştirme sistemleri geliri hak sahibine yönlendiriyor ama katkıya göre bölmüyor. N-Emek bunları yarıştırmak yerine iş bölümüne sokuyor ve üstüne ölçüm katmanını koyuyor; son satır bu yüzden tamamen dolu. Sağdaki kutu tasarımın etik çizgisi: sistem asla "sahibi budur" demiyor. Onaylanmamış bağ kesikli çiziliyor, ölçemediğimiz yerde sayı uydurmuyoruz. Altta itiraz akışı var: payın sahibi itiraz ediyor, bağ SIFT ile yeniden ölçülüyor, paylar güncelleniyor; çözülemezse moderatöre gidiyor.
