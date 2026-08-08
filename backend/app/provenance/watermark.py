"""Gorunmez filigran: icerik kimligini piksellerin icine gomer.

Neden gerekli
-------------
C2PA manifesti dosya metadatasinda yasar; ekran goruntusu alindiginda,
platform yeniden kodladiginda veya biri kasten sildiginde yok olur.
Filigran ise piksellerin frekans alaninda tasinir.

Bu, koken kurtarma hattinin 2. asamasidir ve benzerlik aramasindan
kategorik olarak farklidir: benzerlik "buna benziyor" der, filigran
"bu, su kimlikli icerikten turemistir" der. Bu yuzden guven skoru yuksek.

Neden kendi uygulamamiz
-----------------------
Hazir `invisible-watermark` paketi (dwtDct / dwtDctSvd) bu ortamda
kayipsiz cevrimde bile guvenilir okuma vermedi (12 gorselde 6-9) ve
JPEG q70'te tamamen coktu. Olculen sonuclar backend/poc ciktilarindadir.
Bunun yerine klasik katsayi-cifti (Zhao-Koch turevi) yontemini kanonik
olcek + yuksek fazlalik ile uyguladik.

Yontem
------
1. Gorsel YCrCb'ye cevrilir; yalnizca parlaklik (Y) kanali kullanilir.
2. Y, sabit bir *kanonik* cozunurluge (512x512) olceklenir. Bu adim
   filigrani olcek degisimine karsi bagisik yapar: sorgu gorseli hangi
   boyutta olursa olsun cozmeden once ayni kanonik boyuta getirilir,
   boylece 8x8 blok hizasi geri kazanilir.
3. Kanonik goruntu 8x8 bloklara ayrilir. Anahtardan turetilen bir
   permutasyonla her yuk bitine cok sayida blok atanir (32 bit icin
   blok basina ~128 kat fazlalik).
4. Her blokta, ayni frekans bandindaki iki DCT katsayisi arasindaki
   isaret iliskisi bite gore zorlanir. Ayni banttaki katsayilar JPEG
   nicemleme tablosunda benzer agirliga sahip oldugu icin sikistirma
   ikisini de benzer olcude etkiler; iliski korunur.
5. Cozumde her bit icin bloklar arasi cogunluk oyu alinir.

Gomme, kanonik olcekte hesaplanan farkin (residual) ozgun cozunurluge
geri olceklenip eklenmesiyle yapilir; boylece gorselin ozgun boyutu ve
en-boy orani korunur.

Sinirlar (durust degerlendirme)
--------------------------------
Kirpma ve dondurme blok hizasini bozar; bu senaryolarda filigran
okunmaz. Zaten hattin 3-5. asamalari (pHash, CLIP, geometri) tam olarak
bu durumlar icin vardir. Filigranin gorevi, sikistirma/olcekleme ile
metadatasi silinmis ama piksel duzeni korunmus icerikte *kesin* kanit
saglamaktir.
"""

from __future__ import annotations

import hashlib

import cv2
import numpy as np

# Yuk yapisi: 40 bit kimlik + 16 bit CRC = 56 bit.
# CRC, yanlis kimlik okumasini elemek icindir. Cogunluk oyu tek basina
# yeterli degil: agir kirpilmis bir gorselde bloklar rastgele oy verir ve
# esigi tesadufen gecen bir "kimlik" uretebilir. Olculen deneyde CRC'siz
# 4, CRC-8 ile 3 yanlis okuma cikti; CRC-16 bu olasiligi 1/65536'ya
# indirir. Yanlis atif, bu projede kacirilmis atiftan cok daha agir bir
# hatadir - bu yuzden fazlaliktan (blok basina oy) feragat edip
# dogrulama gucunu artiriyoruz.
ID_BITS = 40
CRC_BITS = 16
PAYLOAD_BITS = ID_BITS + CRC_BITS
# Kanonik calisma cozunurlugu. 8'in kati olmali.
CANONICAL_SIZE = 512
BLOCK = 8
# Katsayi cifti: ayni frekans bandinda, JPEG'de benzer nicemlenen konumlar.
COEF_A = (3, 2)
COEF_B = (2, 3)
# Iki katsayi arasinda zorlanan en kucuk fark. Buyudukce dayaniklilik artar,
# gorsel kalite duser. 14, olculen en iyi denge (bkz. poc_watermark ciktisi).
DELTA = 14.0
# Cozumde bir bitin gecerli sayilmasi icin gereken en dusuk oy orani.
MIN_VOTE_RATIO = 0.62
# Bu boyutun altindaki gorsellerde yeterli blok yok.
MIN_SIDE = 160
# Filigrandan gelen kanitin guven skoru.
WATERMARK_CONFIDENCE = 0.90


def _crc(bits: np.ndarray) -> np.ndarray:
    """CRC-16/CCITT-FALSE, bit dizisi uzerinde hesaplanir."""
    crc = 0xFFFF
    for bit in bits:
        crc ^= int(bit) << 15
        crc = ((crc << 1) ^ 0x1021) & 0xFFFF if crc & 0x8000 else (crc << 1) & 0xFFFF
    return _int_to_bits(crc, CRC_BITS)


def _int_to_bits(value: int, width: int) -> np.ndarray:
    return np.array([(value >> (width - 1 - i)) & 1 for i in range(width)], dtype=np.int8)


def _bits_to_int(bits: np.ndarray) -> int:
    value = 0
    for bit in bits:
        value = (value << 1) | int(bit)
    return value


def content_id_to_bits(content_id: str) -> np.ndarray:
    """Icerik kimligini kimlik + CRC bitlerine cevirir."""
    digest = hashlib.sha256(content_id.encode("utf-8")).digest()
    id_value = int.from_bytes(digest[: ID_BITS // 8], "big")
    id_bits = _int_to_bits(id_value, ID_BITS)
    return np.concatenate([id_bits, _crc(id_bits)])


def bits_to_hex(bits: np.ndarray) -> str:
    """Kimlik kismini onaltilik olarak doner (CRC haric)."""
    return f"{_bits_to_int(bits[:ID_BITS]):0{ID_BITS // 4}x}"


def crc_valid(bits: np.ndarray) -> bool:
    return bool(np.array_equal(_crc(bits[:ID_BITS]), bits[ID_BITS:]))


def content_id_to_hex(content_id: str) -> str:
    return bits_to_hex(content_id_to_bits(content_id))


def _block_assignment(block_count: int, key: int = 0x4E454D45) -> np.ndarray:
    """Her bloga hangi bitin dusecegini belirler (anahtara bagli permutasyon)."""
    rng = np.random.default_rng(key)
    order = rng.permutation(block_count)
    return order % PAYLOAD_BITS


def _embed_canonical(plane: np.ndarray, bits: np.ndarray) -> np.ndarray:
    """Kanonik boyuttaki Y duzlemine filigrani gomer."""
    out = plane.copy()
    n = CANONICAL_SIZE // BLOCK
    assignment = _block_assignment(n * n)

    for idx in range(n * n):
        by, bx = divmod(idx, n)
        y0, x0 = by * BLOCK, bx * BLOCK
        block = out[y0 : y0 + BLOCK, x0 : x0 + BLOCK]
        coeffs = cv2.dct(block)

        bit = int(bits[assignment[idx]])
        a, b = coeffs[COEF_A], coeffs[COEF_B]
        mean = (a + b) / 2.0
        half = DELTA / 2.0
        # bit=1 -> a, b'den belirgin olcude buyuk; bit=0 -> tersi.
        if bit:
            coeffs[COEF_A], coeffs[COEF_B] = mean + half, mean - half
        else:
            coeffs[COEF_A], coeffs[COEF_B] = mean - half, mean + half

        out[y0 : y0 + BLOCK, x0 : x0 + BLOCK] = cv2.idct(coeffs)
    return out


def _decode_canonical(plane: np.ndarray) -> tuple[np.ndarray, float]:
    """Kanonik boyuttaki Y duzleminden bitleri cogunluk oyuyla cozer.

    Returns:
        (bitler, ortalama oy guveni)
    """
    n = CANONICAL_SIZE // BLOCK
    assignment = _block_assignment(n * n)
    votes = np.zeros((PAYLOAD_BITS, 2), dtype=np.int32)

    for idx in range(n * n):
        by, bx = divmod(idx, n)
        y0, x0 = by * BLOCK, bx * BLOCK
        coeffs = cv2.dct(plane[y0 : y0 + BLOCK, x0 : x0 + BLOCK])
        vote = 1 if coeffs[COEF_A] > coeffs[COEF_B] else 0
        votes[assignment[idx], vote] += 1

    bits = (votes[:, 1] > votes[:, 0]).astype(np.int8)
    totals = votes.sum(axis=1).clip(min=1)
    ratios = votes.max(axis=1) / totals
    return bits, float(ratios.mean())


def _to_canonical_plane(image_bgr: np.ndarray) -> np.ndarray:
    ycrcb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2YCrCb)
    y = ycrcb[:, :, 0].astype(np.float32)
    return cv2.resize(y, (CANONICAL_SIZE, CANONICAL_SIZE), interpolation=cv2.INTER_AREA)


def embed(image_bgr: np.ndarray, content_id: str) -> np.ndarray:
    """Icerik kimligini gorsele gomer.

    Gorselin ozgun boyutu ve en-boy orani korunur. Gorsel cok kucukse
    degistirilmeden doner.
    """
    h, w = image_bgr.shape[:2]
    if min(h, w) < MIN_SIDE:
        return image_bgr

    ycrcb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2YCrCb)
    y = ycrcb[:, :, 0].astype(np.float32)

    canonical = cv2.resize(y, (CANONICAL_SIZE, CANONICAL_SIZE), interpolation=cv2.INTER_AREA)
    marked = _embed_canonical(canonical, content_id_to_bits(content_id))

    # Farki ozgun cozunurluge tasi: boylece gorselin kendi boyutu bozulmaz.
    residual = cv2.resize(marked - canonical, (w, h), interpolation=cv2.INTER_CUBIC)
    ycrcb[:, :, 0] = np.clip(y + residual, 0, 255).astype(np.uint8)
    return cv2.cvtColor(ycrcb, cv2.COLOR_YCrCb2BGR)


def extract(image_bgr: np.ndarray) -> tuple[str, float] | None:
    """Gomulu kimligi okur.

    Returns:
        (onaltilik kimlik, oy guveni) veya guven esigin altindaysa None.
    """
    h, w = image_bgr.shape[:2]
    if min(h, w) < MIN_SIDE:
        return None
    bits, confidence = _decode_canonical(_to_canonical_plane(image_bgr))
    if confidence < MIN_VOTE_RATIO:
        return None
    # CRC gecmezse okunan sey bir kimlik degil, gurultudur.
    if not crc_valid(bits):
        return None
    return bits_to_hex(bits), confidence


def matches(image_bgr: np.ndarray, content_id: str) -> tuple[bool, float]:
    """Gorselde verilen kimligin filigrani var mi.

    Returns:
        (eslesti mi, oy guveni)
    """
    found = extract(image_bgr)
    if found is None:
        return False, 0.0
    tag, confidence = found
    return tag == content_id_to_hex(content_id), confidence
