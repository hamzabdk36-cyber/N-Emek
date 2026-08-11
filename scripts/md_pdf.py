"""Bir Markdown dokumanini baskiya uygun PDF'e cevirir.

Neden var
---------
`KULLANILABILIRLIK-PROTOKOL.md` takima dagitilacak ve oturum sirasinda
**elle doldurulacak** bir belge. Markdown olarak paylasmak, protokolu
uygulayacak kisiden bir gorunturucu bekliyor; PDF herkeste ayni aciliyor
ve basilabiliyor.

Cikti kasitli olarak beyaz zeminli: ekran temasi koyu ama bu belge
yaziciya gidiyor.

Kullanim
--------
    .venv/Scripts/python.exe scripts/md_pdf.py docs/KULLANILABILIRLIK-PROTOKOL.md
    .venv/Scripts/python.exe scripts/md_pdf.py docs/X.md --cikti /tmp/x.pdf

Onkosul: `pip install markdown playwright`.
"""

from __future__ import annotations

import argparse
import io
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

try:
    import markdown
    from playwright.sync_api import sync_playwright
except ModuleNotFoundError as exc:  # pragma: no cover - kurulum yonlendirmesi
    print(f"eksik paket: {exc.name}")
    print("  .venv/Scripts/python.exe -m pip install markdown playwright")
    raise SystemExit(1)

# Baskiya gore: beyaz zemin, serifsiz govde, tablolar cerceveli.
# Doldurulacak `___` alanlari griye alinip alti cizili gosteriliyor -
# basilinca nereye yazilacagi belli olsun.
STIL = """
@page { size: A4; margin: 18mm 16mm 20mm 16mm; }
* { box-sizing: border-box; }
body {
  font-family: "Segoe UI", "Inter", system-ui, sans-serif;
  font-size: 10.5pt; line-height: 1.55; color: #14171a; margin: 0;
}
h1 { font-size: 20pt; margin: 0 0 4pt; letter-spacing: -0.4pt; }
h2 {
  font-size: 13pt; margin: 20pt 0 6pt; padding-bottom: 3pt;
  border-bottom: 1px solid #d8dde2; break-after: avoid;
}
h3 { font-size: 11.5pt; margin: 14pt 0 4pt; break-after: avoid; }
p, ul, ol { margin: 0 0 7pt; }
li { margin-bottom: 2pt; }
strong { font-weight: 650; }
code {
  font-family: "Consolas", ui-monospace, monospace; font-size: 9.5pt;
  background: #f2f4f6; padding: 1px 4px; border-radius: 3px;
}
blockquote {
  margin: 8pt 0; padding: 8pt 12pt; background: #f7f9fa;
  border-left: 3px solid #b9c2cc; break-inside: avoid;
}
blockquote p:last-child { margin-bottom: 0; }
table {
  width: 100%; border-collapse: collapse; margin: 8pt 0 12pt;
  font-size: 9.5pt; break-inside: avoid;
}
th, td { border: 1px solid #ccd3da; padding: 4.5pt 7pt; text-align: left; vertical-align: top; }
th { background: #eef1f4; font-weight: 620; }
hr { border: 0; border-top: 1px solid #dde2e7; margin: 16pt 0; }
a { color: #14171a; text-decoration: none; }

/* Elle doldurulacak alan: basilinca cizgi olarak gorunur.
   Genislik bilerek dar: "Hedef: 45 sn · Olculen: ___" satirinin sonuna
   sigmasi gerekiyor, yoksa cizgi tek basina alt satira dusuyor. */
.bosluk {
  display: inline-block; min-width: 58pt; border-bottom: 1px solid #9aa4ae;
}

/* Bir gorev bloguo sayfa ortasindan bolunmesin. */
h3 + p, h3 + table { break-before: avoid; }
"""


def bosluklari_isaretle(html: str) -> str:
    """`___` dizilerini cizgiye cevirir.

    Markdown `___` dizisini bazi baglamlarda yatay cizgi ya da vurgu
    olarak yorumluyor; donusturucuye birakmak yerine dogrudan
    isaretliyoruz.
    """
    return html.replace("___", '<span class="bosluk"></span>')


def cevir(kaynak: Path, cikti: Path) -> None:
    metin = kaynak.read_text(encoding="utf-8")
    govde = markdown.markdown(
        metin,
        extensions=["tables", "sane_lists", "attr_list"],
    )
    govde = bosluklari_isaretle(govde)

    sayfa_html = (
        "<!doctype html><html lang='tr'><head><meta charset='utf-8'>"
        f"<title>{kaynak.stem}</title><style>{STIL}</style></head>"
        f"<body>{govde}</body></html>"
    )

    gecici_html = cikti.with_suffix(".html")
    gecici_html.write_text(sayfa_html, encoding="utf-8")

    try:
        with sync_playwright() as p:
            try:
                tarayici = p.chromium.launch()
            except Exception:
                tarayici = p.chromium.launch(channel="chrome")
            sayfa = tarayici.new_page()
            sayfa.goto(gecici_html.resolve().as_uri(), wait_until="networkidle")
            sayfa.pdf(
                path=str(cikti),
                format="A4",
                print_background=True,
                margin={"top": "18mm", "bottom": "20mm", "left": "16mm", "right": "16mm"},
                display_header_footer=True,
                header_template="<div></div>",
                footer_template=(
                    "<div style='width:100%;font-size:8pt;color:#7a848e;"
                    "padding:0 16mm;display:flex;justify-content:space-between;'>"
                    f"<span>N-Emek · {kaynak.stem}</span>"
                    "<span class='pageNumber'></span></div>"
                ),
            )
            tarayici.close()
    finally:
        gecici_html.unlink(missing_ok=True)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("kaynak", type=Path, help="Markdown dosyasi")
    ap.add_argument("--cikti", type=Path, help="PDF yolu (varsayilan: kaynakla ayni ad)")
    args = ap.parse_args()

    if not args.kaynak.exists():
        raise SystemExit(f"bulunamadi: {args.kaynak}")

    cikti = args.cikti or args.kaynak.with_suffix(".pdf")
    cikti.parent.mkdir(parents=True, exist_ok=True)
    cevir(args.kaynak, cikti)
    print(f"✓ {cikti}  ({cikti.stat().st_size / 1024:.0f} kB)")


if __name__ == "__main__":
    main()
