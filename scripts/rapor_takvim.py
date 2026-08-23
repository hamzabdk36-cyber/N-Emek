"""Proje zaman cizelgesini gorsel olarak uretir.

Neden var
---------
Sartnamenin rapor rubrigi 7.1'de takvimin "gorsel bir sema/tablo ile
sunulmasini" ayrica puanliyor. Elle cizilmis bir sema, is paketi
tarihleri degistiginde sessizce eskirdi - bu projede ayni sorun
`docs/gorseller/` altindaki ekran kareleriyle bir kez yasandi ve
cozumu ayni: kaynak veri burada, sema uretiliyor.

Is paketleri asagidaki `PAKETLER` listesinde tanimli. Tarih degisirse
tek yer degisiyor ve hem tablo hem sema ondan cikiyor.

Yarisma takvimindeki dort sert tarih (teknik rapor 24 Agustos, mentorluk
2-7 Eylul, final 14 Eylul, canli sunum 20 Eylul) semaya kilometre tasi
olarak ciziliyor;
boylece "takvim yarisma takvimiyle celismiyor" iddiasi gozle
dogrulanabiliyor.

Cikti: docs/gorseller/12-takvim.png

Kullanim
--------
    .venv/Scripts/python.exe scripts/rapor_takvim.py

Onkosul: `pip install playwright` (Playwright kendi Chromium'unu
indiremezse sistemdeki Chrome'a duser - `ekran_goruntuleri.py` ile ayni
davranis).
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

try:
    from playwright.sync_api import sync_playwright
except ModuleNotFoundError:  # pragma: no cover - kurulum yonlendirmesi
    print("eksik paket: playwright")
    print("  .venv/Scripts/python.exe -m pip install playwright")
    raise SystemExit(1)

ROOT = Path(__file__).resolve().parents[1]
CIKTI = ROOT / "docs" / "gorseller" / "12-takvim.png"

BASLANGIC = date(2026, 8, 8)
# Sartname V3 (17.08.2026) canli sunumu 20 Eylul olarak kesinlestirdi;
# cizelge o tarihe kadar uzuyor. BITIS tum konumlarin paydasi (_oran),
# yani degistirmek her cubugu ve kilometre tasini birlikte kaydiriyor.
BITIS = date(2026, 9, 20)

# (kod, ad, baslangic, bitis, durum)
# durum: "bitti" | "suruyor" | "planli"
PAKETLER = [
    ("İP-1", "Altyapı, veri modeli ve teknik risklerin kapatılması",
     date(2026, 8, 8), date(2026, 8, 9), "bitti"),
    ("İP-2", "Köken kurtarma hattı: altı aşama ve karar füzyonu",
     date(2026, 8, 9), date(2026, 8, 10), "bitti"),
    ("İP-3", "Katkı payı motoru, Emek Kartı, kampanya ve itiraz akışı",
     date(2026, 8, 10), date(2026, 8, 11), "bitti"),
    ("İP-4", "Değerlendirme düzeneği ve uçtan uca ölçümler",
     date(2026, 8, 8), date(2026, 8, 11), "bitti"),
    ("İP-5", "Arayüz, erişilebilirlik denetimi ve mobil düzen",
     date(2026, 8, 10), date(2026, 8, 11), "bitti"),
    ("İP-6a", "Kullanılabilirlik testi: beş katılımcı, altı görev, SUS",
     date(2026, 8, 12), date(2026, 8, 22), "bitti"),
    ("İP-6b", "Kullanıcı araştırması: dört profilden on kişiyle görüşmeler",
     date(2026, 8, 22), date(2026, 8, 22), "bitti"),
    ("İP-7", "Teknik raporun yazımı, denetimi ve teslimi",
     date(2026, 8, 14), date(2026, 8, 23), "suruyor"),
    ("İP-8", "Ürünleştirme ve mentörlük geri bildirimlerinin uygulanması",
     date(2026, 8, 25), date(2026, 9, 7), "planli"),
    ("İP-9", "Final paketi: demo videosu, sunum dosyası, prototip teslimi",
     date(2026, 9, 8), date(2026, 9, 14), "planli"),
    ("İP-10", "Canlı sunum: prova, jüri soru-cevap ve yedek demo hazırlığı",
     date(2026, 9, 15), date(2026, 9, 20), "planli"),
]

# Sartnamenin sert tarihleri.
KILOMETRE = [
    (date(2026, 8, 24), "Teknik rapor teslimi"),
    (date(2026, 9, 2), "Mentörlük başlangıcı"),
    (date(2026, 9, 14), "Final sunumu ve prototip"),
    (date(2026, 9, 20), "Jüriye canlı sunum"),
]

RENK = {
    "bitti": ("#2f6f4e", "#d8ebe0"),
    "suruyor": ("#8a5a12", "#f6e6c8"),
    "planli": ("#3d4c63", "#dde4ee"),
}

AY = {8: "Ağu", 9: "Eyl"}


def _oran(gun: date) -> float:
    toplam = (BITIS - BASLANGIC).days
    return (gun - BASLANGIC).days / toplam


def html_uret() -> str:
    toplam_gun = (BITIS - BASLANGIC).days

    satirlar = []
    for kod, ad, bas, son, durum in PAKETLER:
        sol = _oran(bas) * 100
        # Bir gunluk paket bile gorunur kalsin: en az %1,5 genislik.
        genislik = max(1.5, (_oran(son) - _oran(bas)) * 100)
        koyu, acik = RENK[durum]
        etiket = f"{bas.day} {AY[bas.month]} – {son.day} {AY[son.month]}"
        # Kisa paketlerin cubugu etiketi tasimiyor; etiket disari,
        # cubugun sagina cikiyor. Icinde birakmak, tek gunluk paketlerde
        # yaziyi cubugun kenarindan tasiriyordu.
        if genislik < 9:
            govde = (
                f'<div class="cubuk" style="left:{sol:.2f}%;width:{genislik:.2f}%;'
                f'background:{acik};border-color:{koyu}"></div>'
                f'<div class="dis-etiket" style="left:{sol + genislik:.2f}%;'
                f'color:{koyu}">{etiket}</div>'
            )
        else:
            govde = (
                f'<div class="cubuk" style="left:{sol:.2f}%;width:{genislik:.2f}%;'
                f'background:{acik};border-color:{koyu};color:{koyu}">{etiket}</div>'
            )
        satirlar.append(
            f'<div class="satir">'
            f'<div class="kod">{kod}</div>'
            f'<div class="ad">{ad}</div>'
            f'<div class="serit">{govde}</div>'
            f"</div>"
        )

    isaretler = []
    onceki_konum = None
    for gun, ad in KILOMETRE:
        konum = _oran(gun) * 100
        # Son kilometre tasi cizelgenin tam saginda (%100) ve ortalanmis
        # bir etiket sayfanin disina tasiyor. Kaydirma **yalnizca
        # etikete** uygulaniyor: nokta tarihin tam uzerinde kalmali,
        # yoksa sema iki gun yanlis gosterir.
        kaydir = "translateX(-50%)" if konum < 92 else "translateX(-88%)"

        # Birbirine yakin iki tas, etiketleri ust uste bindiriyor: 14 ve
        # 20 Eylul yalnizca %14 arayla duruyor ve "Final sunumu ve
        # prototip" etiketi "Juriye canli sunum"un uzerine biniyordu.
        # Cozum yatay degil **dikey**: gec kalan etiket alt siraya inip
        # kendi noktasina noktali bir cizgiyle baglaniyor. Olcut konum
        # farki oldugu icin yazi tipi genisligi tahmin edilmiyor ve yeni
        # bir tas eklendiginde kural kendiliginden calisiyor.
        alt_sira = onceki_konum is not None and (konum - onceki_konum) < 20
        onceki_konum = konum

        bag = f'<span class="km-bag"></span>' if alt_sira else ""
        sinif = "km-ad alt" if alt_sira else "km-ad"
        isaretler.append(
            f'<div class="km" style="left:{konum:.2f}%">'
            f'<span class="km-nokta"></span>'
            f"{bag}"
            f'<span class="{sinif}" style="transform:{kaydir}">'
            f"{ad}<br><b>{gun.day} {AY[gun.month]}</b></span>"
            f"</div>"
        )

    # Hafta baslangiclari eksen olarak.
    eksen = []
    for i in range(0, toplam_gun + 1, 7):
        gun = date.fromordinal(BASLANGIC.toordinal() + i)
        eksen.append(
            f'<div class="tik" style="left:{i / toplam_gun * 100:.2f}%">'
            f"{gun.day} {AY[gun.month]}</div>"
        )

    return f"""<!doctype html><html lang="tr"><head><meta charset="utf-8"><style>
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{
  font-family: Arial, "Segoe UI", sans-serif; background: #ffffff;
  color: #14171a; width: 1180px; padding: 22px 26px 16px;
}}
h1 {{ font-size: 17px; margin-bottom: 2px; }}
.altyazi {{ font-size: 12px; color: #5b6570; margin-bottom: 18px; }}
.satir {{ display: flex; align-items: center; height: 30px; }}
.kod {{ width: 46px; font-size: 12px; font-weight: 700; color: #3d4c63; }}
.ad {{ width: 400px; font-size: 12px; padding-right: 12px; }}
.serit {{
  position: relative; flex: 1; height: 22px;
  border-left: 1px solid #e3e7ec; border-right: 1px solid #e3e7ec;
  background: repeating-linear-gradient(
    to right, #fafbfc 0, #fafbfc calc(100%/38*7 - 1px),
    #eef1f4 calc(100%/38*7 - 1px), #eef1f4 calc(100%/38*7));
}}
.cubuk {{
  position: absolute; top: 2px; height: 18px; border-radius: 4px;
  border: 1px solid; font-size: 10px; line-height: 16px;
  white-space: nowrap; padding: 0 5px; overflow: visible;
}}
.eksen {{
  position: relative; height: 18px; margin-left: 446px; margin-top: 4px;
  border-top: 1px solid #cdd4db;
}}
.tik {{
  position: absolute; font-size: 10px; color: #5b6570;
  transform: translateX(-50%); padding-top: 3px;
}}
.km-serit {{ position: relative; height: 70px; margin-left: 446px; margin-top: 10px; }}
.dis-etiket {{
  position: absolute; top: 3px; font-size: 10px; line-height: 16px;
  padding-left: 6px; white-space: nowrap;
}}
.km {{ position: absolute; top: 0; }}
.km-nokta {{
  display: block; width: 9px; height: 9px; border-radius: 50%;
  background: #b3261e; margin-left: -4.5px;
}}
.km-ad {{
  position: absolute; top: 14px; display: block; font-size: 10px;
  color: #b3261e; line-height: 1.25; white-space: nowrap; text-align: center;
}}
.km-ad.alt {{ top: 44px; }}
.km-bag {{
  position: absolute; top: 9px; height: 33px;
  border-left: 1px dotted #d8968f;
}}
.gosterge {{ margin-top: 14px; font-size: 11px; color: #5b6570; }}
.kutu {{
  display: inline-block; width: 11px; height: 11px; border-radius: 3px;
  border: 1px solid; vertical-align: -1px; margin: 0 4px 0 14px;
}}
</style></head><body>
<h1>N-Emek — İş Paketleri ve Zaman Çizelgesi</h1>
<div class="altyazi">8 Ağustos – 20 Eylül 2026 · kırmızı işaretler yarışma takviminin sert tarihleri</div>
{"".join(satirlar)}
<div class="eksen">{"".join(eksen)}</div>
<div class="km-serit">{"".join(isaretler)}</div>
<div class="gosterge">
  <span class="kutu" style="background:#d8ebe0;border-color:#2f6f4e"></span>tamamlandı
  <span class="kutu" style="background:#f6e6c8;border-color:#8a5a12"></span>sürüyor
  <span class="kutu" style="background:#dde4ee;border-color:#3d4c63"></span>planlı
</div>
</body></html>"""


def main() -> int:
    gecici = CIKTI.with_suffix(".html")
    CIKTI.parent.mkdir(parents=True, exist_ok=True)
    gecici.write_text(html_uret(), encoding="utf-8")

    try:
        with sync_playwright() as p:
            try:
                tarayici = p.chromium.launch()
            except Exception:
                print("(playwright chromium'u yok - sistemdeki Chrome kullanılıyor)")
                tarayici = p.chromium.launch(channel="chrome")
            sayfa = tarayici.new_page(viewport={"width": 1180, "height": 640},
                                      device_scale_factor=2)
            sayfa.goto(gecici.resolve().as_uri(), wait_until="networkidle")
            sayfa.locator("body").screenshot(path=str(CIKTI))
            tarayici.close()
    finally:
        gecici.unlink(missing_ok=True)

    print(f"✓ {CIKTI.relative_to(ROOT).as_posix()}  ({CIKTI.stat().st_size / 1024:.0f} kB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
