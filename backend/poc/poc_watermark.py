"""Faz 0 PoC - Gorunmez filigranin dayanikliligi.

Olculen: 30 gorsele kimlik gomulur, her senaryo icin turev uretilir ve
kimligin geri okunup okunmadigi sayilir. Ayrica gorsel bozulma (PSNR)
raporlanir - filigran gozle gorulmemelidir.

Beklenti gercekcidir: filigran yeniden sikistirmaya dayanir, agir
geometrik donusume (kirpma, dondurme) dayanmaz. Zaten hattin 3-5.
asamalari bu durumlar icin var. Burada olctugumuz sey, filigranin
hangi senaryolarda "kesin kanit" saglayabildigi.

Calistirma:  .venv/Scripts/python.exe backend/poc/poc_watermark.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.provenance import watermark  # noqa: E402
from eval.attacks import ATTACKS  # noqa: E402

RAW = Path(__file__).resolve().parents[2] / "data" / "raw"
SAMPLE = 30


def psnr(a: np.ndarray, b: np.ndarray) -> float:
    mse = float(np.mean((a.astype(np.float64) - b.astype(np.float64)) ** 2))
    if mse == 0:
        return 99.0
    return 10 * float(np.log10(255.0**2 / mse))


def main() -> int:
    paths = sorted(RAW.glob("*.jpg"))[:SAMPLE]
    if not paths:
        raise SystemExit("Korpus bos. Once: python scripts/fetch_eval_images.py")

    marked: list[tuple[str, np.ndarray]] = []
    psnrs: list[float] = []
    for path in paths:
        img = cv2.imread(str(path))
        if img is None:
            continue
        cid = path.stem
        wm = watermark.embed(img, cid)
        psnrs.append(psnr(img, wm))
        marked.append((cid, wm))

    print(f"Filigranlanan gorsel: {len(marked)}")
    print(f"Gorsel bozulma (PSNR): ort {np.mean(psnrs):.1f} dB, en dusuk {min(psnrs):.1f} dB")
    print("  (40 dB uzeri = gozle ayirt edilemez)\n")

    header = f"{'senaryo':<18}{'geri okuma':>12}{'yanlis':>9}{'oy guveni':>12}"
    print(header)
    print("-" * len(header))

    dayanikli: list[str] = []
    yanlis_toplam = 0
    for name, attack in ATTACKS.items():
        ok = 0
        yanlis = 0
        confidences: list[float] = []
        for cid, wm in marked:
            derivative = attack(wm)
            hit, confidence = watermark.matches(derivative, cid)
            if hit:
                ok += 1
                confidences.append(confidence)
            elif confidence > 0:
                # Esigi gecti ama baska bir kimlik okundu: yanlis pozitif.
                yanlis += 1
        yanlis_toplam += yanlis
        rate = ok / len(marked) * 100
        if rate >= 80:
            dayanikli.append(name)
        avg_conf = f"{np.mean(confidences):.2f}" if confidences else "-"
        print(f"{name:<18}{rate:>11.0f}%{yanlis:>9}{avg_conf:>12}")

    print("\n" + "=" * 62)
    print("PoC SONUCU")
    print("=" * 62)
    print(f"  Ortalama PSNR                 : {np.mean(psnrs):.1f} dB")
    print(f"  Dayanikli oldugu senaryolar   : {len(dayanikli)}/{len(ATTACKS)}")
    print(f"    {', '.join(dayanikli) if dayanikli else 'yok'}")
    print(f"  Yanlis kimlik okumasi         : {yanlis_toplam}")
    # Filigran, hattin destekleyici bir asamasi. Sikistirma ve olcekleme
    # senaryolarinda calismasi yeterli; geometrik saldirilar (kirpma,
    # dondurme) hattin 3-5. asamalarinin isi.
    kritik = {"orijinal", "jpeg_q50", "jpeg_q30", "olcek_%50"}
    ok = kritik.issubset(set(dayanikli)) and yanlis_toplam == 0
    print(f"\n  RISK 4 (filigran) {'KAPANDI' if ok else 'ACIK - asama 2 devre disi birakilabilir'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
