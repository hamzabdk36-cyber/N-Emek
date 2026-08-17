# Teknik Rapor — kaynak dosyalar

Buradaki `.md` dosyaları raporun **tek kaynağıdır**. `.docx` üretilir, elle
düzenlenmez: bir düzeltme Word dosyasına yazılırsa bir sonraki üretimde kaybolur.

Alt çizgiyle başlayan dosyalar (`_OKUBENI.md` gibi) rapora girmez.

## Üretim

```bash
.venv/Scripts/python.exe scripts/rapor_docx.py       # docx üret
.venv/Scripts/python.exe scripts/rapor_denetimi.py   # metin düzeyi denetim
powershell -File scripts/rapor_word.ps1              # içindekiler + sayfa sayısı + PDF
```

## Kural

Her `## ` başlığı, resmî şablondaki bir başlıkla **birebir** aynı olmak zorunda —
büyük/küçük harf ve noktalama dahil. Şablonda "1.1. Proje Konusu ve amacı" küçük "a"
ile yazılmış; düzeltmiyoruz, şablon neyse o. Eşleşmezse `rapor_docx.py` durur.

## Şablonun dayattığı biçim

Arial 12 pt · başlık Arial Black 14 pt · satır aralığı 1,15 · iki yana yaslı ·
kenar boşlukları 2,5 cm · **en fazla 30 sayfa** (kapak, içindekiler, kaynakça dahil).

Şablon dosyasının kendi `docDefaults` değeri satır aralığını 1,5 veriyor ve yaslamayı
hiç söylemiyor — yazılı kural kazanıyor, üretici bunu açıktan yazıyor.

## Elle yapılacak tek iş: kapak

Kapak bir metin kutusu; `rapor_docx.py` ona dokunmuyor. Word'de açıp doldurulacak:

| Alan | Ne yazılacak |
|---|---|
| Proje Adı | N-Emek — Açıklanabilir İçerik Atıf ve Adil Gelir Paylaşım Sistemi |
| Takım Adı | *(takımdan)* |
| Takım ID | *(KYS'den)* |
| Başvuru ID | *(KYS'den)* |
| Tematik Alan | Yalnızca **İçerik Ekonomisi** bırakılacak, diğer iki tema silinecek |

Aynı şekilde **8.1'deki rol tablosunun satırları** da boş bırakıldı. `rapor_denetimi.py`
bu alanlar dolmadan yeşile dönmez.

## Sayı disiplini

Rapordaki hiçbir performans sayısı elle yazılmaz; hepsi `docs/DEGERLENDIRME.md`,
`docs/GECIKME.md`, `docs/ACILIS-SURESI.md` veya `docs/IS-MODELI.md` üzerinden gelir ve
onlar da çalıştırılabilir betiklerin çıktısıdır. Ölçüm değişirse betik yeniden koşulur,
sayı elle düzeltilmez.
