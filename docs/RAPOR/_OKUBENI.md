# Teknik Rapor — kaynak dosyalar

Buradaki `.md` dosyaları raporun **tek kaynağıdır**. `.docx` üretilir, elle
düzenlenmez: bir düzeltme Word dosyasına yazılırsa bir sonraki üretimde kaybolur.

Alt çizgiyle başlayan dosyalar (`_OKUBENI.md` gibi) rapora girmez.

## Teslim edilen sürüm dondurulmuştur (11 Eyl 2026 notu)

`N-Emek-Teknik-Rapor.pdf` 23 Ağustos'ta KYS'ye yüklendi ve değerlendirmeye girdi;
o sürüm **içerik olarak dondurulmuştur** — yeniden üretilip tekrar yüklenmez. 11 Eylül'de
iki tür güncelleme yapıldı, ikisi de raporun anlatısını veya iddialarını değiştirmez:

1. `07-proje-takvimi.md`'deki **KT-8** satırı, yarışma takviminin mentörlük tarihini
   değiştirmesi (2-7 Eylül → 12 Eylül 13:00, bkz. `CLAUDE.md` takvim notu ve
   `docs/MENTORLUK.md`) nedeniyle **gerçekleşme kaydı** olarak güncellendi.
2. `03-teknoloji.md`'deki test sayıları (129/126/124), bu belgenin kendisinin
   söylediği kurala uyularak güncel tutuldu — "bu raporun kaynak metni de aynı
   denetimden geçmektedir" (`dokuman_denetimi.py`), yani `sayim:` işaretli sayılar
   burada da canlı kalır; yalnızca commit sayısı gibi "yazıldığı tarih itibarıyla"
   diye çerçevelenen tarihsel iddialar donuyor.

Basılan/yüklenen PDF dosyası bu güncellemelerden etkilenmez; yalnızca kaynak `.md`
metinleri, deponun geri kalanıyla aynı doğruluk kuralına tabi tutuldu.

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
