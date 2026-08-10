# Açılış Süresi — İndeks Kalıcılığı

**Tarih:** 2026-08-10  
**Ortam:** Windows AMD64, Python 3.13.12, cihaz `cuda`  
**Üreten:** `backend/eval/run_startup.py` — bu dosya elle düzenlenmez.

**280** içerikli bir veritabanıyla, açılışta indeksin kurulma süresi. Her kademe **3** kez ölçüldü; tabloda medyan var. Model yükleme maliyeti ölçüm dışında: her kademede önbellekten gelirdi ve en yavaş kademenin lehine yanıltırdı. Karşılaştırılan şey **içerik başına ödenen iş**.

| Kademe | Medyan | İçerik başına | Hızlanma | Ne yapılıyor |
|---|--:|--:|--:|---|
| Görseller | 11,5 sn | 40,92 ms | — | her içeriğin görseli okunur, parmak izi ve CLIP gömmesi yeniden hesaplanır |
| Veritabanı | 32 ms | 0,12 ms | 353× | parmak izi ve vektör sütunlardan okunur; görsele ve modele dokunulmaz |
| Anlık görüntü | 16 ms | 0,06 ms | 734× | diskteki FAISS dosyaları okunur |

## Ne değişti

Önce indeks her açılışta **görsellerden** kuruluyordu: her içerik için dosya okunuyor, parmak izi çıkarılıyor ve CLIP gömmesi yeniden hesaplanıyordu. Maliyet içerik başına bir model çıkarımı olduğu için açılış, içerik sayısıyla doğrusal büyüyordu.

Artık vektör ve blok hash'leri `contents` tablosunda saklanıyor, indeks de `data/index/snapshot/` altına yazılıyor. Açılışta önce anlık görüntü deneniyor; bayatsa veritabanı sütunlarından kuruluyor. Görsel okumak ve model çalıştırmak yalnızca vektörü eksik içerikler için gerekiyor — yani içerik başına **bir kez**.

Ölçülen kazanç: 280 içerikte açılış 11,5 sn yerine 16 ms sürüyor.

## Dürüst sınır

Anlık görüntü bir **önbellek**, kaynak doğru değil. Veritabanıyla kimlik kümesi uyuşmuyorsa sessizce atılıyor ve indeks veritabanından kuruluyor. Süreç aniden öldürülürse anlık görüntü bayat kalır; bu durumda açılış veritabanı kademesine düşer — hâlâ görsellerden hızlı, ama en hızlısı değil.

