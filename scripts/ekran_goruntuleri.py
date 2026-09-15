"""`docs/gorseller/` altindaki kareleri calisan sistemden yeniden ceker.

Neden var
---------
Kareler 10 Agustos'ta elle cekilmisti. 11 Agustos'ta arayuzun yazi tipi
degisti (Inter pakete gomuldu; oncesinde her ekran Segoe UI ile
render ediliyordu) ve **onunun da** eskidigi anlasildi. Elle cekim her
tasarim degisikliginde ayni islemi tekrarlamayi gerektiriyor; kimse
tekrarlamayinca rapordaki gorseller sessizce urunle ayrisiyor.

Bu betik o dongoyu kapatiyor: tek komut, on bir kare, hepsi calisan
sistemden.

Kullanim
--------
    docker compose up --build -d
    .venv/Scripts/python.exe scripts/ekran_goruntuleri.py
    .venv/Scripts/python.exe scripts/ekran_goruntuleri.py --sadece 03,11

Onkosul: `playwright install chromium` (bir kez).

Mobil kare
----------
`11-mobil.jpg` 390x844 goruntu alaninda cekiliyor. Bu olcu bir tercih
degil zorunluluk: tarayici penceresi bu ortamda 382 pikselin altina
inmiyordu ve mobil duzen uzun sure *hic* olculememisti
(`docs/ERISILEBILIRLIK.md` 11 numarali bulgu). Playwright'in goruntu
alani pencereden bagimsiz kuruldugu icin olcu burada gercek.
"""

from __future__ import annotations

import argparse
import io
import sys
import time
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

try:
    from playwright.sync_api import Page, sync_playwright
except ModuleNotFoundError:  # pragma: no cover - kurulum yonlendirmesi
    print("playwright kurulu degil:")
    print("  .venv/Scripts/python.exe -m pip install playwright")
    print("  .venv/Scripts/python.exe -m playwright install chromium")
    raise SystemExit(1)

KOK = Path(__file__).resolve().parent.parent
HEDEF = KOK / "docs" / "gorseller"

TABAN = "http://localhost:5173"
API = "http://localhost:8000"

# Masaustu olcusu 10 Agustos'taki kareleri koruyor: rapor yerlesimi bu
# ene gore kuruldu, degistirmek butun sayfayi yeniden dizmek demek.
MASAUSTU = {"width": 1568, "height": 745}
MOBIL = {"width": 390, "height": 844}


def demo_icerikleri(page: Page) -> dict[str, str]:
    """Kimlikleri akistan okur - demo verisi her `--reset` ile degisiyor.

    Kimlikleri betige gomsek her yeniden tohumlamada kirilirdi.
    """
    veri = page.evaluate(
        f"fetch('{API}/api/feed').then(r => r.json())",
    )
    esleme = {}
    for icerik in veri:
        baslik = icerik["title"]
        if "Bulduğum" in baslik:
            esleme["ceyda"] = icerik["id"]
        elif "Şehrin" in baslik:
            esleme["burak"] = icerik["id"]
        elif "Sabah" in baslik:
            esleme["ayse"] = icerik["id"]
    eksik = {"ceyda", "burak", "ayse"} - set(esleme)
    if eksik:
        raise SystemExit(
            f"Demo verisi eksik ({eksik}). Once: python scripts/seed_demo.py --reset"
        )
    return esleme


def dur(page: Page, ms: int = 900) -> None:
    """Ag bosalmasi + cizim payi.

    `networkidle` tek basina yetmiyor: CLIP maskesi ve zincir yerlesimi
    veri geldikten sonra ciziliyor.
    """
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(ms)


def yazi_tipi_bekle(page: Page) -> None:
    """Inter inmeden cekilen kare yine Segoe UI gosterirdi.

    Betigin varlik sebebi tam olarak buydu; sessizce eskimemesi icin
    burada dogrulaniyor.
    """
    page.wait_for_function("document.fonts.ready.then(() => true)")
    if not page.evaluate("document.fonts.check('16px \"Inter Variable\"')"):
        raise SystemExit(
            "Inter yuklenmedi - kare eski yazi tipiyle cikacakti. "
            "Arayuz paketi guncel mi? (npm run build / docker compose up --build)"
        )


def pay_satirini_ac(page: Page, ad: str) -> None:
    """Emek Karti'nda verilen kisinin pay satirini acar.

    11 Eylul: ilk kaynak satiri artik varsayilan acik geliyor (bulgu
    B4, KULLANILABILIRLIK-SONUCLARI.md) - kortlemesine tiklamak o
    satirda *kapatma* etkisi yapabiliyordu. Once mevcut durumu okuyoruz.
    """
    dugme = page.locator("button[aria-expanded]").filter(has_text=ad).first
    if dugme.get_attribute("aria-expanded") != "true":
        dugme.click()
        page.wait_for_timeout(700)


def cek(page: Page, dosya: str, tam_sayfa: bool = False) -> None:
    yol = HEDEF / dosya
    page.screenshot(path=str(yol), type="jpeg", quality=88, full_page=tam_sayfa)
    print(f"  ✓ {dosya}")


# ---------------------------------------------------------------------------
# Kareler
# ---------------------------------------------------------------------------
def kare_01(page: Page, id: dict[str, str]) -> None:
    page.goto(f"{TABAN}/", wait_until="domcontentloaded")
    yazi_tipi_bekle(page)
    dur(page)
    cek(page, "01-akis.jpg")


def kare_02(page: Page, id: dict[str, str]) -> None:
    page.goto(f"{TABAN}/icerik/{id['ceyda']}", wait_until="domcontentloaded")
    dur(page)
    cek(page, "02-emek-karti-koken.jpg")


def kare_03(page: Page, id: dict[str, str]) -> None:
    """Raporun ana gorseli: payin gerekcesi acik.

    Kadraj bilerek formul satirina gore kuruluyor. Acilan satiri uste
    almak yetmiyordu: rakamlari birlestiren `pay = kapsama x guven x
    sonumleme` satiri ve altindaki kanitlar kadrajin disinda kaliyordu -
    oysa bu karenin anlatmasi gereken sey tam olarak *rakamin nereden
    geldigi*.
    """
    page.goto(f"{TABAN}/icerik/{id['ceyda']}", wait_until="domcontentloaded")
    dur(page)
    pay_satirini_ac(page, "Ayşe")
    formul = page.get_by_text("pay = kapsama", exact=False).first
    formul.scroll_into_view_if_needed()
    # Formulun ustunde kalan sey de gerekli: kimin payi, ne kadar, hangi
    # rozetle. Bir ekran yukari cekiyoruz.
    page.mouse.wheel(0, -230)
    page.wait_for_timeout(500)
    cek(page, "03-pay-gerekcesi.jpg")


def kare_04_05(page: Page, id: dict[str, str]) -> None:
    """Olculen bolge - maske yalnizca *dogrudan* olculen bagda var.

    Ayse zincirde iki adim geride ve yaprakla dogrudan bagi gecisli
    indirgemeyle dusuruldu; o satirda maske yok. Bu yuzden Burak
    seciliyken cekiliyor (bkz. gorseller/README.md).
    """
    page.goto(f"{TABAN}/icerik/{id['ceyda']}", wait_until="domcontentloaded")
    dur(page)
    pay_satirini_ac(page, "Burak")
    maske = page.get_by_text("Ölçülen bölge", exact=False).first
    if maske.count():
        maske.scroll_into_view_if_needed()
        page.wait_for_timeout(600)
    cek(page, "04-olculen-bolge.jpg")
    page.mouse.wheel(0, 420)
    page.wait_for_timeout(600)
    cek(page, "05-olculen-bolge-oran.jpg")


def kare_06(page: Page, id: dict[str, str]) -> None:
    page.goto(f"{TABAN}/icerik/{id['ceyda']}", wait_until="domcontentloaded")
    dur(page)
    page.locator("svg[role='img']").first.scroll_into_view_if_needed()
    page.mouse.wheel(0, -110)
    page.wait_for_timeout(500)
    cek(page, "06-atif-zinciri.jpg")


def kare_07(page: Page, id: dict[str, str]) -> None:
    page.goto(f"{TABAN}/remix/{id['burak']}", wait_until="domcontentloaded")
    dur(page, 1400)  # tuval kaynak gorseli indirip ciziyor
    cek(page, "07-remix-studyosu.jpg")


def kare_08(page: Page, id: dict[str, str]) -> None:
    page.goto(f"{TABAN}/kampanyalar", wait_until="domcontentloaded")
    dur(page)
    cek(page, "08-kampanya-paneli.jpg")


def kare_09(page: Page, id: dict[str, str]) -> None:
    page.goto(f"{TABAN}/inceleme", wait_until="domcontentloaded")
    dur(page)
    cek(page, "09-inceleme-kuyrugu.jpg")


def kare_10(page: Page, id: dict[str, str]) -> None:
    """Kaynak Bul - bos ekran degil, gercek bir sorgunun sonucu.

    Bos hali ekranin ne *yaptigini* anlatmiyordu. Burada Burak'in
    remixinin kirpilmis bir kopyasi sorgulaniyor: dosyada icerik kimligi
    yok, sistem kaynagi kanit hattiyla buluyor. Kanit satirlarindaki
    asama adlarinin Turkce oldugu da ancak boyle gorunuyor - eskiden
    burada `phash_blok` yaziyordu (bkz. ERISILEBILIRLIK.md 10).
    """
    import tempfile

    from PIL import Image

    ham = page.request.get(f"{API}/api/contents/{id['burak']}/image").body()
    with Image.open(io.BytesIO(ham)) as im:
        g, y = im.size
        # Kenarlardan kirp: kimlik tasiyan ust veri zaten kayboluyor,
        # geriye yalnizca piksellerin kendisi kaliyor.
        kirpik = im.convert("RGB").crop(
            (int(g * 0.12), int(y * 0.10), int(g * 0.88), int(y * 0.92))
        )
        gecici = Path(tempfile.gettempdir()) / "nemek-kaynak-bul-sorgu.jpg"
        kirpik.save(gecici, format="JPEG", quality=90)

    page.goto(f"{TABAN}/kaynak-bul", wait_until="domcontentloaded")
    dur(page)
    page.locator("input[type='file']").set_input_files(str(gecici))
    page.wait_for_timeout(500)
    page.get_by_role("button", name="Kökeni çöz").click()
    page.wait_for_timeout(2500)  # hat: kimlik -> ozet -> filigran -> phash -> clip -> geometri
    dur(page, 600)

    # Karenin iddiasini burada dogrula: ham anahtar adi ekranda kalmasin.
    metin = page.locator("body").inner_text()
    for ham_ad in ("phash_blok", "INLIER_COUNT", "VISUAL_COVERAGE"):
        if ham_ad in metin:
            raise SystemExit(f"Ekranda ham anahtar adi duruyor: {ham_ad}")

    cek(page, "10-kaynak-bul.jpg")
    try:
        gecici.unlink(missing_ok=True)
    except OSError:
        # Windows'ta dosya secicisi tutamagi birakana kadar kilitli
        # kalabiliyor; gecici dizinin temizligi bu betigin isi degil.
        pass


def kare_11_mobil(page: Page, id: dict[str, str]) -> None:
    """Mobil duzen - ayri goruntu alani gerektiriyor."""
    page.set_viewport_size(MOBIL)
    page.goto(f"{TABAN}/icerik/{id['ceyda']}", wait_until="domcontentloaded")
    dur(page)
    pay_satirini_ac(page, "Ayşe")
    page.locator("button[aria-expanded='true']").first.scroll_into_view_if_needed()
    page.mouse.wheel(0, -120)
    page.wait_for_timeout(500)

    # Kare cekilirken duzenin gercekten temiz oldugunu da dogrula:
    # goruntu iyi gorunup yatay kaymanin surmesi mumkun.
    tasma = page.evaluate(
        "document.documentElement.scrollWidth > window.innerWidth + 1"
    )
    cubuk = page.evaluate(
        "Math.round(document.querySelector('header').getBoundingClientRect().height)"
    )
    cek(page, "11-mobil.jpg")
    print(f"    (yatay kayma: {'VAR' if tasma else 'yok'} · üst çubuk: {cubuk} px)")
    if tasma:
        raise SystemExit("Mobilde yatay kayma var - kare cekildi ama duzen bozuk.")
    page.set_viewport_size(MASAUSTU)


KARELER = {
    "01": kare_01,
    "02": kare_02,
    "03": kare_03,
    "04": kare_04_05,
    "06": kare_06,
    "07": kare_07,
    "08": kare_08,
    "09": kare_09,
    "10": kare_10,
    "11": kare_11_mobil,
}


def main() -> None:
    ayristirici = argparse.ArgumentParser(description=__doc__)
    ayristirici.add_argument(
        "--sadece",
        help="Virgulle ayrilmis kare numaralari, orn. 03,11",
    )
    args = ayristirici.parse_args()

    istenen = set(args.sadece.split(",")) if args.sadece else set(KARELER)
    bilinmeyen = istenen - set(KARELER)
    if bilinmeyen:
        raise SystemExit(f"Bilinmeyen kare: {sorted(bilinmeyen)}")

    HEDEF.mkdir(parents=True, exist_ok=True)
    baslangic = time.time()

    with sync_playwright() as p:
        # Playwright'in kendi chromium'u yoksa sistemdeki Chrome'a dusuyoruz:
        # `playwright install` indirmesi her makinede sorunsuz gitmiyor ve
        # bu betigin bir indirmeye bagli olmasi icin sebep yok.
        try:
            tarayici = p.chromium.launch()
        except Exception:
            print("(playwright chromium'u yok - sistemdeki Chrome kullanılıyor)")
            tarayici = p.chromium.launch(channel="chrome")
        sayfa = tarayici.new_page(viewport=MASAUSTU, device_scale_factor=1)
        sayfa.set_default_timeout(20_000)

        sayfa.goto(TABAN, wait_until="domcontentloaded")
        try:
            kimlikler = demo_icerikleri(sayfa)
        except Exception as exc:
            raise SystemExit(
                f"Sistem ayakta mi? {TABAN} ve {API} yanit vermeli. ({exc})"
            ) from exc

        print(f"Kareler {HEDEF} altina yazilacak:")
        for anahtar in sorted(istenen):
            KARELER[anahtar](sayfa, kimlikler)

        tarayici.close()

    print(f"\nBitti - {time.time() - baslangic:.1f} sn")


if __name__ == "__main__":
    main()
