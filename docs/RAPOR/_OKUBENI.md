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

## Kapak

Kapak, şablonun kendi metin kutusu ve `rapor_docx.py` her koşumda şablonu baştan
kopyalıyor. Bu yüzden kapak **Word'de elle doldurulmaz**: doldurulsaydı bir sonraki
üretimde sessizce silinirdi — gövdedeki yer tutucularla aynı tuzak.

Değerler betikteki `KAPAK` sözlüğünde, tek kaynakta:

| Alan | Değer |
|---|---|
| Proje Adı | N-Emek — Açıklanabilir İçerik Atıf ve Adil Gelir Paylaşım Sistemi |
| Takım Adı | ZENITH N |
| Takım ID | 1003461 |
| Başvuru ID | 5382505 |
| Tematik Alan | İçerik Ekonomisi *(şablondaki diğer iki tema düşüyor)* |

Betik her üretimde kaç alan doldurduğunu basar; biri tutmazsa `KAPAK EKSİK` der.

## Sayı disiplini

Rapordaki hiçbir performans sayısı elle yazılmaz; hepsi `docs/DEGERLENDIRME.md`,
`docs/GECIKME.md`, `docs/ACILIS-SURESI.md` veya `docs/IS-MODELI.md` üzerinden gelir ve
onlar da çalıştırılabilir betiklerin çıktısıdır. Ölçüm değişirse betik yeniden koşulur,
sayı elle düzeltilmez.
