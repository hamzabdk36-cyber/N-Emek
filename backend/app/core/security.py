"""Imzali, kisa omurlu oturum jetonlari.

Neden parola yok
----------------
N-Emek bagimsiz bir sosyal ag degil; N'Sosyal'in *icine* giren bir emek
katmani. Kimlik dogrulama ana platformun isi - parola saklamak,
sifirlamak, iki adimli dogrulama kurmak bu prototipin cozdugu problemin
disinda ve juri karsisinda savunulacak bir sey de degil.

Bu yuzden `POST /api/oturum` bir **demo kimlik saglayicisi**: kullanici
kimligini alir, imzali bir jeton doner. Gercek dagitimda bu ucun yerini
N'Sosyal'in kendi kimlik saglayicisi alir ve geri kalan her sey aynen
calisir, cunku uclar jetonun *nereden geldigini* degil gecerli olup
olmadigini soruyor.

Cozdugu somut sorun
-------------------
Once `owner_id` form alanindan geliyordu: herkes herkes adina icerik
yukleyebiliyor, baskasinin payina itiraz edebiliyor ve baskasinin
icerigi uzerinde gelir degistirebiliyordu. Yetki kurallarinin
tutunabilecegi bir kimlik yoktu.

Jeton bicimi
------------
    base64url(payload_json) + "." + base64url(hmac_sha256(secret, payload))

Harici bagimlilik yok (PyJWT/itsdangerous eklenmedi): imza HMAC-SHA256,
tamami standart kutuphaneden. Bagimlilik eklemek Docker imajini ve CI
kurulumunu da degistirirdi; kazanci yoktu.
"""

from __future__ import annotations

import base64
import binascii
import hmac
import json
import secrets
import time
from dataclasses import dataclass
from functools import lru_cache
from hashlib import sha256

from app.core.config import get_settings


class TokenError(Exception):
    """Jeton okunamadi, imzasi tutmadi ya da suresi doldu."""


@dataclass(frozen=True)
class TokenPayload:
    user_id: str
    expires_at: int


@lru_cache(maxsize=1)
def _secret() -> bytes:
    """Imzalama anahtari.

    Ayarlarda yoksa surec basina rastgele uretilir. Depoya sahte bir
    anahtar koymak yerine bu tercih edildi: yanlislikla uretimde
    kullanilabilecek, herkesin bildigi bir varsayilan anahtar
    birakmiyoruz.

    Bedeli, sunucu yeniden baslayinca eski jetonlarin gecersiz olmasi.
    Arayuz bunu zaten kaldiriyor: 401 alinca oturumu sessizce yeniden
    aciyor (bkz. frontend/src/api.ts).
    """
    configured = get_settings().token_secret
    if configured:
        return configured.encode("utf-8")
    return secrets.token_bytes(32)


def _b64(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def _unb64(text: str) -> bytes:
    padding = "=" * (-len(text) % 4)
    return base64.urlsafe_b64decode(text + padding)


def _sign(payload: bytes) -> str:
    return _b64(hmac.new(_secret(), payload, sha256).digest())


def encode_token(user_id: str) -> tuple[str, int]:
    """Jetonu ve son gecerlilik anini (unix saniye) doner."""
    expires_at = int(time.time()) + get_settings().token_ttl_seconds
    payload = json.dumps(
        {"sub": user_id, "exp": expires_at}, separators=(",", ":")
    ).encode("utf-8")
    return f"{_b64(payload)}.{_sign(payload)}", expires_at


def decode_token(token: str) -> TokenPayload:
    """Jetonu dogrular. Gecersizse `TokenError` firlatir."""
    try:
        encoded_payload, signature = token.split(".", 1)
        payload_bytes = _unb64(encoded_payload)
    except (ValueError, TypeError, binascii.Error) as exc:
        raise TokenError("Oturum jetonu okunamadı.") from exc

    # Sabit zamanli karsilastirma: imzayi bayt bayt sizdirmayalim.
    if not hmac.compare_digest(_sign(payload_bytes), signature):
        raise TokenError("Oturum jetonunun imzası geçersiz.")

    try:
        payload = json.loads(payload_bytes)
        user_id = str(payload["sub"])
        expires_at = int(payload["exp"])
    except (ValueError, KeyError, TypeError) as exc:
        raise TokenError("Oturum jetonunun içeriği okunamadı.") from exc

    if expires_at <= int(time.time()):
        raise TokenError("Oturum süresi doldu; yeniden oturum açın.")

    return TokenPayload(user_id=user_id, expires_at=expires_at)
