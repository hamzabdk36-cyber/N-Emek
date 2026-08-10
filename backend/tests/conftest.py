"""Test ortami.

Ortam degiskenleri, uygulama modulleri yuklenmeden once ayarlanmali:
`app.core.database` icindeki motor modul duzeyinde olusturuluyor ve
yapilandirmayi o anda okuyor. conftest, test modullerinden once
calistigi icin dogru yer burasi.
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

_TMP = Path(tempfile.mkdtemp(prefix="nemek-test-"))
os.environ["NEMEK_DATA_DIR"] = str(_TMP)
os.environ["NEMEK_UPLOAD_DIR"] = str(_TMP / "uploads")
os.environ["NEMEK_INDEX_DIR"] = str(_TMP / "index")
os.environ["NEMEK_DATABASE_URL"] = f"sqlite:///{(_TMP / 'test.db').as_posix()}"

import pytest  # noqa: E402

RAW = Path(__file__).resolve().parents[2] / "data" / "raw"


@pytest.fixture(scope="session")
def temp_root() -> Path:
    return _TMP


def gorsel_korpusu(en_az: int = 4) -> list[Path]:
    """Degerlendirme korpusunu dondurur; yoksa yerelde atlar, CI'da durdurur.

    `en_az`: testler korpustan `photos[0]` ve `photos[3]`'u kullaniyor,
    yani dort dosya yetiyor. Eksik korpusta anlasilmaz bir IndexError
    yerine ne yapilmasi gerektigini soyleyen bir mesaj cikiyor.

    Sessiz atlama tehlikeli oldugu icin ikiye ayriliyor. Ilk CI kosumuz
    korpussuz calisti: `test_api_ucnoktalari` ve `test_e2e_altin_senaryo`
    modul fikstürlerinden atlandi, geriye yalnizca 22 saf pay testi kaldi
    ve is yine yesil yandi. Yani rozet, API sozlesmesini ve altin
    senaryoyu hic dogrulamadigi halde dogruluyormus gibi goruntu verdi.

    Yerelde atlama hala dogru davranis - korpus 320 dosya, depoda degil
    ve yeni klonlayan biri once onu indirmek zorunda kalmasin. Ama CI'da
    korpusun olmamasi kurulum hatasidir, gecerli bir durum degil.
    """
    photos = sorted(RAW.glob("*.jpg"))
    if len(photos) >= en_az:
        return photos

    mesaj = (
        f"gorsel korpusu eksik ({len(photos)}/{en_az}): "
        "python scripts/fetch_eval_images.py"
    )
    if os.getenv("CI"):
        pytest.fail(f"{mesaj} (CI'da korpus zorunlu)")
    pytest.skip(mesaj)
