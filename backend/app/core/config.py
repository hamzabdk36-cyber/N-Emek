"""Uygulama yapilandirmasi.

Tum esikler ve katsayilar burada toplanir; hicbiri kod icine gomulmez.
Sebep: Emek Karti kullaniciya "bu pay su kurala gore hesaplandi" derken
o kurallarin tek ve denetlenebilir bir yerde durmasi gerekir. Ayrica
degerlendirme betikleri esikleri degistirerek duyarlilik analizi yapar.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="NEMEK_", env_file=".env", extra="ignore")

    # --- Yollar -----------------------------------------------------------
    data_dir: Path = ROOT / "data"
    upload_dir: Path = ROOT / "data" / "uploads"
    index_dir: Path = ROOT / "data" / "index"
    cert_dir: Path = ROOT / "backend" / "certs"
    database_url: str = f"sqlite:///{(ROOT / 'data' / 'nemek.db').as_posix()}"

    # --- Katki payi formulu ----------------------------------------------
    # Bir kaynagin ham agirligi uc carpanin urunudur:
    #
    #     agirlik = kapsama^a  x  guven^b  x  sonumleme^(derinlik-1)
    #
    # Carpimsal secildi cunku her carpan bagimsiz bir gerekce ve
    # kullaniciya tek cumleyle anlatilabiliyor: "icerigin %41'i senden
    # geldi, buna %92 eminiz, ve sen zincirde iki adim geridesin".
    # Toplamsal bir model, kapsamasi sifir olan bir kaynaga guven
    # bileseninden pay verirdi; carpimsal model vermez.
    coverage_exponent: float = 1.0
    confidence_exponent: float = 1.0

    # Zincir sonumlemesi: her bir ust seviyede agirlik bu katsayiyla carpilir.
    #
    # Bu bir *politika* dugmesidir, olcum degil. Ozel kapsama bolutlemesi
    # (bkz. chain.build_chain) her tarafi zaten yalnizca kendi kattigi
    # piksellerle odullendirdigi icin sonumlemenin gorevi sinirlidir:
    # zincirde ileri gitmis icerigin *yeniden dolasima sokulmasindaki*
    # emegi bir miktar tanimak. Agresif bir sonumleme (or. 0.5) tam da
    # bu projenin duzeltmeye calistigi haksizligi uretir - ilk uretici,
    # baskalari remixledigi icin cezalandirilmis olur. Bu yuzden hafif
    # tutuldu; 1.0 verilirse tamamen kapanir.
    chain_damping: float = 0.85
    # Bu derinlikten sonra kaynaklar zincire dahil edilmez.
    max_chain_depth: int = 5

    # Geometrik dogrulama yapilamadiginda kullanilan ihtiyatli kapsama
    # varsayimi. Olcemedigimiz seyi yuksek varsaymayiz; kaynak itiraz
    # edip kanit sunarsa yeniden olculur ve pay yukselir.
    unverified_coverage: float = 0.35

    # Son ureticiye her kosulda birakilan taban pay. Hicbir remix
    # "sifir emek" degildir; secim, cerceveleme ve yayin da katkidir.
    creator_floor: float = 0.20
    # Ureticiye verilebilecek en yuksek pay: kaynak varken kaynak payi
    # tamamen silinemez.
    creator_ceiling: float = 0.85
    # Bu esigin altindaki paylar odenmez; tutar diger taraflara dagitilir.
    min_payout_share: float = 0.01

    # --- Koken kurtarma ---------------------------------------------------
    # Bir kaynagin zincire "onerilen" olarak girmesi icin gereken en dusuk guven.
    min_link_confidence: float = 0.35
    # Bu guvenin ustundeki baglar otomatik onaylanir; altindakiler
    # kullanici onayina/itirazina acik kalir.
    auto_confirm_confidence: float = 0.85
    # Geometrik dogrulamaya gonderilecek en fazla aday sayisi.
    # Geometri pahali (~90 ms); aday uretimi ucuz. Bu sayi, gecikme ile
    # geri getirme arasindaki dengeyi belirler.
    max_geometry_candidates: int = 8
    # Bir kaynagin katki hesabina girmesi icin gereken en dusuk alan orani.
    min_coverage_for_share: float = 0.03

    # --- Yukleme ----------------------------------------------------------
    # En buyuk kabul edilen yukleme. Uc, dosyayi parca parca okuyup bu
    # siniri asinca 413 doner - `await file.read()` dosyanin tamamini
    # bellege aliyordu ve yerel calistirmada hicbir sinir yoktu.
    # Docker'daki nginx de ayni degeri kullaniyor (`client_max_body_size`);
    # ikisi ayrilirsa ayni istek ortama gore farkli yerde reddedilir.
    max_upload_mb: int = 32

    # --- Oturum -----------------------------------------------------------
    # Jeton imzalama anahtari. Bos birakilirsa surec basina rastgele
    # uretilir (bkz. core/security.py): depoya, yanlislikla uretimde
    # kullanilabilecek sahte bir varsayilan anahtar koymuyoruz.
    # Uretimde `NEMEK_TOKEN_SECRET` ile verilir.
    token_secret: str = ""
    # Jeton omru. Demo oturumu icin bir calisma gunu yeterli; kisa
    # tutulmasinin sebebi jetonun kalici bir kimlik belgesi gibi
    # dolasmamasi.
    token_ttl_seconds: int = 8 * 60 * 60

    # --- Platform ---------------------------------------------------------
    platform_commission: float = 0.10  # N'Sosyal kampanya yonetim payi
    platform_name: str = "N'Sosyal"

    def ensure_dirs(self) -> None:
        for path in (self.data_dir, self.upload_dir, self.index_dir):
            path.mkdir(parents=True, exist_ok=True)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    settings = Settings()
    settings.ensure_dirs()
    return settings
