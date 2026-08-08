"""Faz 0 PoC - Kullanilan icerik oraninin olculebilirligi.

Bilinen dogru cevapla (ground truth) turevler uretir ve
`geometry.measure_usage` ciktisini bu cevapla karsilastirir.

Olculen sey: turev icerigin yuzde kaci kaynaktan geliyor
(`visual_coverage`). Katki payi motoru bu sayiyi kullanacagi icin
hedef hata payi MAE <= 0.05.

Calistirma:  .venv/Scripts/python.exe backend/poc/poc_geometry.py
"""

from __future__ import annotations

import sys
import time
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.provenance.geometry import measure_usage  # noqa: E402

OUT = Path(__file__).resolve().parents[2] / "data" / "poc" / "geometry"
MAE_TARGET = 0.05


# --------------------------------------------------------------------------
# Test gorselleri
# --------------------------------------------------------------------------
def load_photos() -> list[tuple[str, np.ndarray]]:
    """Dokulu gercek fotograflar. scikit-image varsa ondan, yoksa sentetik."""
    try:
        from skimage import data  # type: ignore

        photos = [
            ("astronaut", data.astronaut()),
            ("coffee", data.coffee()),
            ("chelsea", data.chelsea()),
            ("rocket", data.rocket()),
        ]
        return [(n, cv2.cvtColor(img, cv2.COLOR_RGB2BGR)) for n, img in photos]
    except Exception:
        print("  (uyari) scikit-image yok, sentetik dokulu gorseller kullaniliyor")
        rng = np.random.default_rng(7)
        out = []
        for i in range(4):
            base = rng.integers(0, 255, (480, 640, 3), dtype=np.uint8)
            base = cv2.GaussianBlur(base, (0, 0), 3)
            for _ in range(40):
                c = tuple(int(v) for v in rng.integers(0, 255, 3))
                p1 = tuple(int(v) for v in rng.integers(0, 480, 2))
                p2 = tuple(int(v) for v in rng.integers(0, 480, 2))
                cv2.line(base, p1, p2, c, int(rng.integers(1, 6)))
            out.append((f"sentetik{i}", base))
        return out


def _paste(canvas: np.ndarray, patch: np.ndarray, x: int, y: int) -> np.ndarray:
    """Yamayi tuvale yapistirir ve kapladigi alanin maskesini doner."""
    h, w = patch.shape[:2]
    canvas[y : y + h, x : x + w] = patch
    mask = np.zeros(canvas.shape[:2], np.uint8)
    mask[y : y + h, x : x + w] = 255
    return mask


def _jpeg(img: np.ndarray, quality: int) -> np.ndarray:
    ok, buf = cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, quality])
    assert ok
    return cv2.imdecode(buf, cv2.IMREAD_COLOR)


# --------------------------------------------------------------------------
# Senaryolar: her biri (turev, gt_visual_coverage, gt_source_usage) doner
# --------------------------------------------------------------------------
@dataclass
class Case:
    name: str
    aciklama: str
    derivative: np.ndarray
    gt_coverage: float
    gt_usage: float
    should_match: bool = True


def build_cases(src: np.ndarray, other: np.ndarray) -> list[Case]:
    h, w = src.shape[:2]
    cases: list[Case] = []

    # 1) Saf kirpma: turevin tamami kaynaktan; kaynagin %50'si kullanilmis
    ch, cw = int(h * 0.707), int(w * 0.707)  # alanin ~%50'si
    y0, x0 = (h - ch) // 2, (w - cw) // 2
    crop = src[y0 : y0 + ch, x0 : x0 + cw]
    cases.append(
        Case("kirpma_50", "Merkezden %50 alan kirpma + 1.4x buyutme",
             cv2.resize(crop, None, fx=1.4, fy=1.4), 1.0, (ch * cw) / (h * w))
    )

    # 2) Agir kirpma + dusuk kaliteli JPEG
    ch2, cw2 = int(h * 0.55), int(w * 0.55)
    crop2 = src[10 : 10 + ch2, 20 : 20 + cw2]
    cases.append(
        Case("kirpma_30_jpeg40", "%30 alan kirpma + JPEG kalite 40",
             _jpeg(crop2, 40), 1.0, (ch2 * cw2) / (h * w))
    )

    # 3) Ustune opak bant (yazi seridi) - homografi goremez, piksel dogrulamasi gorur
    banner = src.copy()
    band_h = int(h * 0.18)
    banner[h - band_h :, :] = (18, 18, 18)
    cv2.putText(banner, "REMIX", (20, h - band_h // 3),
                cv2.FONT_HERSHEY_SIMPLEX, 1.4, (255, 255, 255), 3)
    cases.append(
        Case("yazi_bandi", f"Alt %{int(band_h / h * 100)} opak yazi bandi",
             banner, 1.0 - band_h / h, 1.0)
    )

    # 4) Kolaj: kaynak solda, ilgisiz icerik sagda
    canvas = np.zeros((h, w * 2, 3), np.uint8)
    canvas[:, w:] = cv2.resize(other, (w, h))
    _paste(canvas, src, 0, 0)
    cases.append(Case("kolaj_yarim", "Yan yana kolaj: kaynak sol yarida",
                      canvas, 0.5, 1.0))

    # 5) Dondurulmus ve kucultulmus yama, buyuk tuvalin bir kosesinde
    small = cv2.resize(src, None, fx=0.5, fy=0.5)
    sh, sw = small.shape[:2]
    rot_m = cv2.getRotationMatrix2D((sw / 2, sh / 2), 12, 1.0)
    rotated = cv2.warpAffine(small, rot_m, (sw, sh), borderValue=(0, 0, 0))
    rot_mask = cv2.warpAffine(np.full((sh, sw), 255, np.uint8), rot_m, (sw, sh))
    canvas2 = cv2.resize(other, (w, h)).copy()
    region = canvas2[20 : 20 + sh, 20 : 20 + sw]
    region[rot_mask > 127] = rotated[rot_mask > 127]
    gt5 = float((rot_mask > 127).sum()) / (h * w)
    cases.append(Case("dondurme_kolaj", "12 derece dondurulmus %25'lik yama",
                      canvas2, gt5, 1.0))

    # 6) Agir renk filtresi: gorsel tamamen kaynaktan, sadece renkler degismis
    filt = cv2.applyColorMap(cv2.cvtColor(src, cv2.COLOR_BGR2GRAY), cv2.COLORMAP_PLASMA)
    filt = cv2.addWeighted(src, 0.35, filt, 0.65, 0)
    cases.append(Case("agir_filtre", "Yogun renk derecelendirme", filt, 1.0, 1.0))

    # 7) Ekran goruntusu benzetimi: hafif kirpma + olcekleme + JPEG
    shot = src[15 : h - 15, 25 : w - 25]
    shot = cv2.resize(shot, None, fx=0.8, fy=0.8)
    cases.append(
        Case("ekran_goruntusu", "Kenar kirpma + %80 olcekleme + JPEG 55",
             _jpeg(shot, 55), 1.0, ((h - 30) * (w - 50)) / (h * w))
    )

    # 8) Ilgisiz gorsel: eslesmemeli (yanlis atif testi)
    cases.append(Case("ilgisiz", "Tamamen farkli gorsel",
                      cv2.resize(other, (w, h)), 0.0, 0.0, should_match=False))

    return cases


# --------------------------------------------------------------------------
def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    photos = load_photos()
    src_name, src = photos[0]
    other = photos[1][1]
    print(f"Kaynak gorsel: {src_name} {src.shape[1]}x{src.shape[0]}\n")

    cases = build_cases(src, other)
    rows = []
    errors: list[float] = []
    yanlis_atif = 0
    kacirilan = 0

    header = f"{'senaryo':<18}{'GT kaps.':>9}{'olculen':>9}{'hata':>8}{'inlier':>8}{'sure':>8}"
    print(header)
    print("-" * len(header))

    for case in cases:
        cv2.imwrite(str(OUT / f"{case.name}.jpg"), case.derivative)
        t0 = time.perf_counter()
        res = measure_usage(src, case.derivative, detector="orb")
        dt = (time.perf_counter() - t0) * 1000

        if case.should_match:
            if not res.matched:
                kacirilan += 1
                print(f"{case.name:<18}{case.gt_coverage:>9.3f}{'ESLESMEDI':>9}"
                      f"{'-':>8}{res.inlier_count:>8}{dt:>7.0f}ms   <- {res.reason}")
                rows.append((case, res, None))
                continue
            err = abs(res.visual_coverage - case.gt_coverage)
            errors.append(err)
            flag = "" if err <= 0.10 else "   <- sapma"
            print(f"{case.name:<18}{case.gt_coverage:>9.3f}{res.visual_coverage:>9.3f}"
                  f"{err:>8.3f}{res.inlier_count:>8}{dt:>7.0f}ms{flag}")
        else:
            if res.matched:
                yanlis_atif += 1
                print(f"{case.name:<18}{'-':>9}{res.visual_coverage:>9.3f}"
                      f"{'-':>8}{res.inlier_count:>8}{dt:>7.0f}ms   <- YANLIS ATIF")
            else:
                print(f"{case.name:<18}{'-':>9}{'red':>9}{'-':>8}"
                      f"{res.inlier_count:>8}{dt:>7.0f}ms   (dogru reddedildi)")
        rows.append((case, res, None))

        # Eslesen bolge maskesini gorsellestir (arayuzde kullanilacak katman)
        if res.retained_mask is not None and case.should_match:
            overlay = case.derivative.copy()
            mask = cv2.resize(res.retained_mask, (overlay.shape[1], overlay.shape[0]))
            tint = np.zeros_like(overlay)
            tint[:] = (80, 220, 120)
            overlay = np.where(
                (mask > 127)[..., None],
                cv2.addWeighted(overlay, 0.72, tint, 0.28, 0),
                overlay,
            )
            cv2.imwrite(str(OUT / f"{case.name}_maske.jpg"), overlay)

    mae = float(np.mean(errors)) if errors else 1.0
    print("\n" + "=" * 62)
    print("PoC SONUCU")
    print("=" * 62)
    print(f"  Olculen senaryo sayisi        : {len(errors)}/{sum(c.should_match for c in cases)}")
    print(f"  Kapsama MAE                   : {mae:.4f}   (hedef <= {MAE_TARGET})")
    print(f"  Kacirilan eslesme             : {kacirilan}")
    print(f"  Yanlis atif                   : {yanlis_atif}")
    print(f"  Maske gorselleri              : {OUT}")
    ok = mae <= MAE_TARGET and yanlis_atif == 0 and kacirilan == 0
    print(f"\n  RISK 3 (alan olcumu) {'KAPANDI' if ok else 'ACIK - esikler ayarlanmali'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
