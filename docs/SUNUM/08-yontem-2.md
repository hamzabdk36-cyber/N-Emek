# 08 · Yöntem (2/2)

<!-- Sayılar: docs/DEGERLENDIRME.md (backend/eval/run_benchmark.py çıktısı).
Eşikler: docs/VERI-MODEL-ETIK.md §4. -->

## veri
### Veri seti ve doğrulama düzeneği
- **320 benzersiz görsel:** 280 tanesi indekse alındı, 40 tanesi hiç alınmadı (negatif kontrol).
- **20 türev senaryosu:** kırpma, ölçekleme, döndürme, ayna, yazı bandı, ekran görüntüsü, kolaj ve diğerleri; toplam 6.400 sorgu.
- Her sorgu üretimdeki kurtarma fonksiyonunun kendisinden geçer; C2PA ve üstveri silinmiş hâlde ölçülür.
- Beklenen kapsama elle etiketlenmez, türevi üreten dönüşümün geometrisinden hesaplanır.

## metrikler
- **%98,7** · Top-1 doğruluk, 20 senaryo ortalaması
- **%0,86** · yanlış atıf oranı (55 / 6.400), negatif kontrol dahil
- **0,0241** · kapsama ölçüm hatası (MAE), hedef ≤ 0,05
- **386 ms** · uçtan uca gecikme, medyan (p95 703 ms)

## indirgeme
### Geçişli indirgeme
Geometri Ayşe'nin içeriğini Ceyda'nın gönderisinde de bulur, oysa bu pikseller oraya Burak üzerinden gelmiştir. Doğrudan bağ pay hesabına girseydi aynı emek iki kez ödüllenirdi; bu yüzden hesaptan düşülür, kanıt olarak saklanır.

## ozel_kapsama
### Özel kapsama bölüntüsü
Ölçülen kapsamalar iç içedir. Her kaynağa yalnızca kendi kattığı alan yazılır; böylece kapsamalar görselin tam bir bölüntüsü olur ve paylar normalizasyonla değil ölçümle 1'e tamamlanır. Bu kural öncesinde kaynakların toplamı %182 çıkıyordu.

## etik
### Veri güvenliği, mahremiyet ve etik
- **Yanlış atıf, kaçırılmış atıftan ağır sayılır.** Kaçırılan bağ itirazla düzeltilir; haksız ödeme üçüncü kişiye zarar verir. Eşikler bu yönde: CLIP güveni en fazla 0,75, bağ eşiği 0,35, otomatik onay 0,85.
- **Kullanıcı kaydında** e-posta, parola, telefon, konum ve cihaz kimliği tutulmaz. Yüz tanıma, profilleme ve davranış takibi yoktur.
- **Silme hakkı:** içerik görsel, maske, parmak izi, bağ ve indeks iziyle birlikte silinir. Ödemesi olan içerikte mali kayıt silinemez; bu sınır açıkça belgelidir.
- **Oturum:** durum değiştiren her uç imzalı jeton ister; başkasının payına itiraz veya gelir değişikliği reddedilir.

## kaynak
N-Emek kapsamlı değerlendirmesi (backend/eval/run_benchmark.py); test görselleri Lorem Picsum üzerinden Unsplash lisanslı fotoğraflar, tekilleştirilmiş.

## not
Yöntemin doğrulanması için 320 benzersiz görsellik bir korpus kurduk. 280'ini indeksledik, 40'ını bilerek hiç indekslemedik: bu negatif kontrol. O görsellerin türevlerinde önerilen herhangi bir bağ yanlış atıf sayılıyor. Her görsel 20 türev senaryosundan geçti, toplam 6.400 sorgu. Sonuçlar sağda: Top-1 doğruluk yüzde 98,7; yanlış atıf yüzde 0,86; kapsama ölçüm hatası 0,024, hedefimiz 0,05'ti; medyan gecikme 386 milisaniye. Ortadaki iki kural pay hesabının doğruluğu için şart: geçişli indirgeme aynı emeğin iki kez ödüllenmesini engelliyor, özel kapsama da payların normalizasyona değil ölçüme dayanmasını sağlıyor. Altta etik tercihlerimiz var: yanlış atıfı kaçırılmış atıftan ağır sayıyoruz ve eşikleri bu yöne ayarladık; kişisel veri toplamıyoruz.
