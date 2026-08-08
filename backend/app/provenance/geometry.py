"""Geometrik eslesme ve kullanilan icerik orani olcumu.

N-Emek'in temel teknik iddiasi burada: bir turev icerikte kaynagin
"ne kadar" kullanildigini tahmin etmiyoruz, **olcuyoruz**.

Yontem
------
1. Yerel ozellik cikarimi (ORB varsayilan, SIFT opsiyonel) ve Lowe oran testi
   ile eslestirme.
2. RANSAC ile homografi kestirimi -> kaynak gorselin turev icindeki
   geometrik konumu.
3. Kaynak kosegenlerinin turev duzlemine izdusumu ve turev cercevesiyle
   kesisimi -> *geometrik kapsama*.
4. Kaynagin turev cercevesine warp edilmesi ve yerel normalize edilmis
   capraz korelasyon (ZNCC) ile piksel dogrulamasi -> *gorsel kapsama*.
   Bu adim, uzerine yazi/sticker/cizim eklenerek kapatilan bolgeleri
   kapsamadan duser; salt homografi bunu goremez.

Katki payi motoru `visual_coverage` degerini kullanir: turev icerigin
yuzde kaci gercekten bu kaynaktan geliyor.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

import cv2
import numpy as np

# Islem hizini sabit tutmak icin gorseller bu uzun kenara olceklenir.
WORK_MAX_SIDE = 1000
# Lowe oran testi esigi.
RATIO_TEST = 0.75
# Homografi icin gereken en az iyi eslesme sayisi.
MIN_GOOD_MATCHES = 12
# RANSAC yeniden izdusum toleransi (piksel).
RANSAC_REPROJ_THRESHOLD = 4.0
# Piksel dogrulamasinda "korunmus" sayilmasi icin gereken yerel ZNCC.
ZNCC_RETAINED_THRESHOLD = 0.45
# ZNCC pencere boyutu (tek sayi).
ZNCC_WINDOW = 11
# Bu degerin altindaki yerel varyans "dokusuz/duz" sayilir.
FLAT_VARIANCE = 12.0


@dataclass
class GeometricMatch:
    """Bir (kaynak, turev) cifti icin geometrik olcum sonucu."""

    matched: bool
    reason: str
    keypoints_source: int = 0
    keypoints_derivative: int = 0
    good_matches: int = 0
    inlier_count: int = 0
    inlier_ratio: float = 0.0
    # Turev icerigin yuzde kaci bu kaynaktan geliyor (homografi ile).
    geometric_coverage: float = 0.0
    # Ayni oran, piksel dogrulamasi sonrasi (ustu kapatilan bolgeler dusulur).
    visual_coverage: float = 0.0
    # Kaynak gorselin yuzde kaci turevde goruntuleniyor (kirpma orani = 1 - bu).
    source_usage: float = 0.0
    scale: float = 0.0
    rotation_deg: float = 0.0
    homography: np.ndarray | None = field(default=None, repr=False)
    # Turev cozunurlugunde, kaynaktan gelen pikselleri isaretleyen maske.
    # Arayuzdeki "eslesen bolge" vurgusu bundan uretilir.
    retained_mask: np.ndarray | None = field(default=None, repr=False)
    source_quad: np.ndarray | None = field(default=None, repr=False)

    def as_evidence(self) -> dict:
        """Emek Karti'nda gosterilecek kanit satiri."""
        if self.matched:
            coverage = f"%{self.visual_coverage * 100:.1f}".replace(".", ",")
            aciklama = (
                f"Kaynak, türev içerikte {self.inlier_count} noktada geometrik "
                f"olarak eşleşti. Piksel doğrulamasından sonra içeriğin bu "
                f"kaynaktan gelen oranı {coverage} olarak ölçüldü"
            )
            if self.source_usage:
                usage = f"%{self.source_usage * 100:.1f}".replace(".", ",")
                aciklama += f"; kaynağın kullanılan bölümü {usage}"
            aciklama += "."
        else:
            aciklama = f"Geometrik doğrulama yapılamadı: {self.reason}."

        return {
            "stage": "geometry",
            "matched": self.matched,
            "reason": self.reason,
            "aciklama": aciklama,
            "good_matches": self.good_matches,
            "inlier_count": self.inlier_count,
            "inlier_ratio": round(self.inlier_ratio, 4),
            "geometric_coverage": round(self.geometric_coverage, 4),
            "visual_coverage": round(self.visual_coverage, 4),
            "source_usage": round(self.source_usage, 4),
            "scale": round(self.scale, 4),
            "rotation_deg": round(self.rotation_deg, 2),
        }


def _to_working_gray(image: np.ndarray) -> tuple[np.ndarray, float]:
    """Gri tona cevirir ve calisma cozunurlugune olcekler. Olcek katsayisini doner."""
    if image.ndim == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image
    longest = max(gray.shape[:2])
    if longest <= WORK_MAX_SIDE:
        return gray, 1.0
    scale = WORK_MAX_SIDE / longest
    resized = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
    return resized, scale


def _build_detector(kind: str):
    if kind == "sift":
        return cv2.SIFT_create(nfeatures=4000), cv2.NORM_L2
    return cv2.ORB_create(nfeatures=4000, scaleFactor=1.2, nlevels=10), cv2.NORM_HAMMING


def _polygon_area(points: np.ndarray) -> float:
    """Kapali coklu genin alani (ayakkabi bagi formulu)."""
    if points is None or len(points) < 3:
        return 0.0
    x = points[:, 0]
    y = points[:, 1]
    return float(abs(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1))) / 2.0)


def _clip_to_rect(quad: np.ndarray, width: int, height: int) -> tuple[np.ndarray | None, float]:
    """Dortgeni goruntu cercevesiyle kesistirir; kesisim coklu geni ve alanini doner."""
    rect = np.array(
        [[0, 0], [width, 0], [width, height], [0, height]], dtype=np.float32
    )
    quad32 = quad.astype(np.float32).reshape(-1, 2)
    try:
        area, inter = cv2.intersectConvexConvex(quad32, rect)
    except cv2.error:
        return None, 0.0
    if inter is None or area <= 0:
        return None, 0.0
    return inter.reshape(-1, 2), float(area)


def _pixel_retention(a: np.ndarray, b: np.ndarray, window: int = ZNCC_WINDOW) -> np.ndarray:
    """Piksel basina "bu bolge hala kaynaktan mi geliyor" karari.

    Yerel normalize capraz korelasyon (ZNCC) kullanilir; parlaklik ve
    kontrast degisimlerine dayanikli oldugu icin filtre uygulanmis
    remixlerde de yapisal benzerligi yakalar.

    Doku durumuna gore uc ayri karar verilir:
      * ikisi de dokulu  -> ZNCC karar verir (asil olcum)
      * kaynak dokulu, turev duz -> uzeri kapatilmis, korunmamis sayilir
        (yazi bandi, sticker, opak cizim bu dala duser)
      * ikisi de duz     -> yapisal olarak ayirt edilemez; hicbir yontem
        duz bir alanin uzerine ayni tonda duz bir alan konulup
        konulmadigini soyleyemez. Bu durumda geometrik karar korunur.
    """
    a = a.astype(np.float32)
    b = b.astype(np.float32)
    ksize = (window, window)

    def box(x: np.ndarray) -> np.ndarray:
        return cv2.boxFilter(x, -1, ksize, normalize=True, borderType=cv2.BORDER_REFLECT)

    mu_a, mu_b = box(a), box(b)
    saa = box(a * a) - mu_a * mu_a
    sbb = box(b * b) - mu_b * mu_b
    sab = box(a * b) - mu_a * mu_b
    denom = np.sqrt(np.maximum(saa, 0.0) * np.maximum(sbb, 0.0)) + 1e-6
    ncc = np.clip(sab / denom, -1.0, 1.0)

    flat_source = saa < FLAT_VARIANCE
    flat_derivative = sbb < FLAT_VARIANCE

    # Varsayilan: yapisal korelasyon karari.
    # Mutlak deger, kontrasti tersine ceviren filtrelere karsi tolerans saglar.
    retained = np.abs(ncc) >= ZNCC_RETAINED_THRESHOLD
    # Kaynak dokulu ama turev duz: kapatilmis.
    retained[~flat_source & flat_derivative] = False
    # Ikisi de duz: olculemez, geometriye birakilir.
    retained[flat_source & flat_derivative] = True
    return retained


def _decompose(homography: np.ndarray) -> tuple[float, float]:
    """Homografinin dogrusal kisminden olcek ve donme acisini kestirir."""
    a = homography[:2, :2]
    det = float(np.linalg.det(a))
    scale = math.sqrt(abs(det)) if det != 0 else 0.0
    rotation = math.degrees(math.atan2(a[1, 0], a[0, 0]))
    return scale, rotation


def measure_usage(
    source: np.ndarray,
    derivative: np.ndarray,
    detector: str = "orb",
    verify_pixels: bool = True,
) -> GeometricMatch:
    """Kaynagin turev icerikteki kullanim oranini olcer.

    Args:
        source: Kaynak gorsel (BGR veya gri, OpenCV dizisi).
        derivative: Turev gorsel.
        detector: "orb" (hizli, varsayilan) veya "sift" (daha hassas).
        verify_pixels: Piksel dogrulamasi yapilsin mi. Kapatilirsa
            `visual_coverage`, `geometric_coverage` ile ayni olur.

    Returns:
        GeometricMatch
    """
    src_gray, src_scale = _to_working_gray(source)
    dst_gray, dst_scale = _to_working_gray(derivative)

    det, norm = _build_detector(detector)
    kp_src, des_src = det.detectAndCompute(src_gray, None)
    kp_dst, des_dst = det.detectAndCompute(dst_gray, None)

    base = GeometricMatch(
        matched=False,
        reason="",
        keypoints_source=len(kp_src) if kp_src else 0,
        keypoints_derivative=len(kp_dst) if kp_dst else 0,
    )

    if des_src is None or des_dst is None or len(kp_src) < 2 or len(kp_dst) < 2:
        base.reason = "yeterli yerel özellik bulunamadı"
        return base

    matcher = cv2.BFMatcher(norm, crossCheck=False)
    raw = matcher.knnMatch(des_src, des_dst, k=2)
    good = [m for pair in raw if len(pair) == 2 for m, n in [pair] if m.distance < RATIO_TEST * n.distance]
    base.good_matches = len(good)

    if len(good) < MIN_GOOD_MATCHES:
        base.reason = f"yetersiz eşleşme ({len(good)} < {MIN_GOOD_MATCHES})"
        return base

    src_pts = np.float32([kp_src[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
    dst_pts = np.float32([kp_dst[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)

    homography, mask = cv2.findHomography(
        src_pts, dst_pts, cv2.RANSAC, RANSAC_REPROJ_THRESHOLD, maxIters=5000, confidence=0.995
    )
    if homography is None:
        base.reason = "homografi kestirilemedi"
        return base

    inliers = int(mask.sum()) if mask is not None else 0
    base.inlier_count = inliers
    base.inlier_ratio = inliers / len(good)
    if inliers < MIN_GOOD_MATCHES:
        base.reason = f"yetersiz RANSAC inlier ({inliers})"
        return base

    sh, sw = src_gray.shape[:2]
    dh, dw = dst_gray.shape[:2]

    # --- Geometrik kapsama: kaynak cercevesinin turevdeki izdusumu -----------
    src_corners = np.float32([[0, 0], [sw, 0], [sw, sh], [0, sh]]).reshape(-1, 1, 2)
    projected = cv2.perspectiveTransform(src_corners, homography).reshape(-1, 2)
    inter_poly, inter_area = _clip_to_rect(projected, dw, dh)
    derivative_area = float(dw * dh)
    geometric_coverage = min(inter_area / derivative_area, 1.0) if derivative_area else 0.0
    base.geometric_coverage = geometric_coverage
    base.source_quad = projected * (1.0 / dst_scale)

    if geometric_coverage <= 0.0:
        base.reason = "izdüşüm türev çerçevesinin dışında"
        return base

    # --- Kaynak kullanim orani: turev cercevesinin kaynaktaki karsiligi ------
    try:
        inverse = np.linalg.inv(homography)
        dst_corners = np.float32([[0, 0], [dw, 0], [dw, dh], [0, dh]]).reshape(-1, 1, 2)
        back = cv2.perspectiveTransform(dst_corners, inverse).reshape(-1, 2)
        _, back_area = _clip_to_rect(back, sw, sh)
        base.source_usage = min(back_area / float(sw * sh), 1.0)
    except np.linalg.LinAlgError:
        base.source_usage = 0.0

    base.scale, base.rotation_deg = _decompose(homography)

    # --- Gorsel kapsama: piksel dogrulamasi ----------------------------------
    if verify_pixels:
        warped = cv2.warpPerspective(src_gray, homography, (dw, dh))
        valid = cv2.warpPerspective(
            np.full((sh, sw), 255, np.uint8), homography, (dw, dh)
        ) > 127
        retained = valid & _pixel_retention(warped, dst_gray)
        # Kucuk delikleri kapat: yazi kenarlarindaki tek piksel gurultusu
        # gercek bir "kapatma" degildir.
        retained_u8 = cv2.morphologyEx(
            retained.astype(np.uint8) * 255,
            cv2.MORPH_OPEN,
            cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)),
        )
        retained_u8 = cv2.morphologyEx(
            retained_u8, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))
        )
        base.retained_mask = retained_u8
        base.visual_coverage = float((retained_u8 > 127).sum()) / derivative_area
    else:
        base.visual_coverage = geometric_coverage

    base.matched = True
    base.homography = homography
    base.reason = "homografi doğrulandı"
    return base
