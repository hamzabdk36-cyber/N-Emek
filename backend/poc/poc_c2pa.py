"""Faz 0 PoC - C2PA icerik kimligi: imzala, dogrula, turev zinciri kur.

Kanitlanmasi gereken uc sey:
  1. Orijinal gorsele imzali C2PA manifesti gomulebiliyor ve geri okunabiliyor.
  2. Remix (turev) icerik, ingredient + actions ile kaynagina baglanabiliyor.
  3. Manifest silindiginde (yeniden kaydetme/ekran goruntusu) Reader bunu
     "manifest yok" olarak raporluyor -> koken kurtarma hatti devreye girecek.

Calistirma:  .venv/Scripts/python.exe backend/poc/poc_c2pa.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw

import c2pa

ROOT = Path(__file__).resolve().parents[2]
CERT_DIR = ROOT / "backend" / "certs"
OUT = ROOT / "data" / "poc" / "c2pa"


def build_signer() -> c2pa.Signer:
    info = c2pa.C2paSignerInfo(
        alg=b"es256",
        sign_cert=(CERT_DIR / "chain.pem").read_bytes(),
        private_key=(CERT_DIR / "private.key").read_bytes(),
        # Zaman damgasi sunucusu yok (prototip cevrimdisi calisabilsin diye).
        # DIKKAT: bos bytes (b"") degil None verilmeli; c2pa-rs bos stringi
        # gecersiz sayip "Signature: empty string" hatasi firlatiyor.
        ta_url=None,
    )
    return c2pa.Signer.from_info(info)


def make_original(path: Path) -> None:
    """Orijinal icerik yerine gecen sentetik gorsel."""
    img = Image.new("RGB", (1024, 768), (28, 42, 74))
    d = ImageDraw.Draw(img)
    for i in range(0, 1024, 64):
        d.line([(i, 0), (i, 768)], fill=(40, 60, 110), width=2)
    d.ellipse([300, 200, 724, 560], fill=(232, 168, 56))
    d.text((60, 60), "AYSE - ORIJINAL ICERIK", fill=(255, 255, 255))
    img.save(path, quality=95)


def make_remix(src: Path, path: Path) -> None:
    """Burak'in remixi: kirpma + uzerine metin."""
    img = Image.open(src).convert("RGB")
    img = img.crop((200, 120, 900, 660)).resize((900, 700))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 600, 900, 700], fill=(12, 12, 12))
    d.text((30, 640), "BURAK'IN REMIXI", fill=(255, 255, 255))
    img.save(path, quality=92)


def manifest_original() -> dict:
    return {
        "claim_generator_info": [{"name": "N-Emek", "version": "0.1.0"}],
        "title": "Ayse - Orijinal Icerik",
        "format": "image/jpeg",
        "assertions": [
            {
                "label": "c2pa.actions.v2",
                "data": {
                    "actions": [
                        {
                            "action": "c2pa.created",
                            "digitalSourceType": "http://cv.iptc.org/newscodes/digitalsourcetype/digitalCapture",
                        }
                    ]
                },
            },
            {
                "label": "stds.schema-org.CreativeWork",
                "data": {
                    "@context": "https://schema.org",
                    "@type": "CreativeWork",
                    "author": [{"@type": "Person", "name": "Ayse Yilmaz"}],
                },
            },
            {
                # N-Emek'e ozel: remix izinleri ve gelir paylasim tercihleri
                "label": "org.nemek.remix_policy",
                "data": {
                    "remix_allowed": True,
                    "commercial_remix_allowed": True,
                    "min_source_share": 0.20,
                    "content_id": "nemek:content:0001",
                },
            },
        ],
    }


def manifest_remix(parent_id: str) -> dict:
    return {
        "claim_generator_info": [{"name": "N-Emek", "version": "0.1.0"}],
        "title": "Burak - Remix",
        "format": "image/jpeg",
        "assertions": [
            {
                "label": "c2pa.actions.v2",
                "data": {
                    "actions": [
                        {
                            "action": "c2pa.opened",
                            "parameters": {"org.nemek.parent": parent_id},
                        },
                        {"action": "c2pa.cropped"},
                        {"action": "c2pa.edited", "softwareAgent": {"name": "N-Emek Remix Studio"}},
                    ]
                },
            },
            {
                "label": "org.nemek.remix_policy",
                "data": {
                    "remix_allowed": True,
                    "content_id": "nemek:content:0002",
                    "parent_content_id": parent_id,
                },
            },
        ],
    }


def read_manifest(path: Path) -> dict | None:
    try:
        with c2pa.Reader(str(path)) as reader:
            return json.loads(reader.json())
    except Exception as exc:  # manifest yok veya bozuk
        print(f"    [Reader] manifest okunamadi: {type(exc).__name__}: {exc}")
        return None


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    signer = build_signer()

    # --- 1) Orijinali imzala -------------------------------------------------
    plain_original = OUT / "01_original_plain.jpg"
    signed_original = OUT / "02_original_signed.jpg"
    make_original(plain_original)

    with c2pa.Builder(manifest_original()) as builder:
        builder.sign_file(plain_original, signed_original, signer)
    print(f"[1] Orijinal imzalandi -> {signed_original.name}")

    data = read_manifest(signed_original)
    assert data, "Imzalanan orijinalden manifest okunamadi"
    active = data["manifests"][data["active_manifest"]]
    print(f"    baslik      : {active['title']}")
    print(f"    imzalayan   : {active['signature_info']['issuer']}")
    print(f"    assertion   : {[a['label'] for a in active['assertions']]}")

    # --- 2) Remix: ingredient ile kaynaga bagla -----------------------------
    plain_remix = OUT / "03_remix_plain.jpg"
    signed_remix = OUT / "04_remix_signed.jpg"
    make_remix(signed_original, plain_remix)

    ingredient = {
        "title": "Ayse - Orijinal Icerik",
        "relationship": "parentOf",
    }
    with c2pa.Builder(manifest_remix("nemek:content:0001")) as builder:
        with open(signed_original, "rb") as src:
            builder.add_ingredient(ingredient, "image/jpeg", src)
        builder.sign_file(plain_remix, signed_remix, signer)
    print(f"[2] Remix imzalandi -> {signed_remix.name}")

    data = read_manifest(signed_remix)
    assert data, "Remixten manifest okunamadi"
    active = data["manifests"][data["active_manifest"]]
    ingredients = active.get("ingredients", [])
    print(f"    ingredient sayisi: {len(ingredients)}")
    for ing in ingredients:
        print(
            f"      - {ing.get('title')} | iliski={ing.get('relationship')} "
            f"| kaynak manifest={ing.get('active_manifest')}"
        )
    actions = next(
        (a["data"]["actions"] for a in active["assertions"] if a["label"].startswith("c2pa.actions")),
        [],
    )
    print(f"    eylemler   : {[a['action'] for a in actions]}")

    zincir_kuruldu = bool(ingredients) and any(
        i.get("relationship") == "parentOf" for i in ingredients
    )

    # --- 3) Manifest'i sil (Ceyda'nin ekran goruntusu senaryosu) -------------
    stripped = OUT / "05_remix_stripped.jpg"
    img = Image.open(signed_remix).convert("RGB")
    img = img.crop((40, 30, img.width - 40, img.height - 30))
    img.save(stripped, quality=60)  # yeniden sikistirma + kirpma -> manifest gider
    print(f"[3] Manifest silinmis surum -> {stripped.name}")
    stripped_data = read_manifest(stripped)
    manifest_gitti = stripped_data is None

    # --- Ozet ----------------------------------------------------------------
    print("\n" + "=" * 62)
    print("PoC SONUCU")
    print("=" * 62)
    print(f"  Imzalama + dogrulama calisiyor    : {'EVET' if data else 'HAYIR'}")
    print(f"  Turev zinciri (ingredient) kuruldu: {'EVET' if zincir_kuruldu else 'HAYIR'}")
    print(f"  Manifest silinince tespit ediliyor: {'EVET' if manifest_gitti else 'HAYIR'}")
    ok = bool(data) and zincir_kuruldu and manifest_gitti
    print(f"\n  RISK 1 (C2PA) {'KAPANDI' if ok else 'ACIK - alternatife gecilmeli'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
