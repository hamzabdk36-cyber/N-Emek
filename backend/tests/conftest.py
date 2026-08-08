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


@pytest.fixture(scope="session")
def temp_root() -> Path:
    return _TMP
