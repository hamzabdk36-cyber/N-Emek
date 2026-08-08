"""C2PA manifest olusturma, imzalama ve dogrulama.

Hattin 0. asamasi. Manifest varsa koken bir kanit meselesi degil, bir
okuma meselesidir - kriptografik olarak imzalanmis bir beyan vardir.
Bu yuzden en yuksek guven skoru buradan gelir.

Manifeste projeye ozel `org.nemek.remix_policy` assertion'i yazilir:
ureticinin remix izinleri ve asgari kaynak payi talebi. Boylece
tercihler icerikle birlikte seyahat eder; platform veritabanina
bagimli kalmaz.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import c2pa

from app.core.config import get_settings

CLAIM_GENERATOR = {"name": "N-Emek", "version": "0.1.0"}
REMIX_POLICY_LABEL = "org.nemek.remix_policy"
DIGITAL_CAPTURE = "http://cv.iptc.org/newscodes/digitalsourcetype/digitalCapture"
# Manifestten gelen kanitin guven skoru. Imza dogrulandiysa bu bir
# tahmin degil, beyandir.
C2PA_CONFIDENCE = 0.99


@dataclass
class ManifestInfo:
    """Bir dosyadan okunan C2PA manifestinin ozeti."""

    present: bool
    urn: str | None = None
    title: str | None = None
    issuer: str | None = None
    validation_state: str | None = None
    # Manifestteki ingredient'lerden cikarilan kaynak icerik kimlikleri.
    parent_content_ids: list[str] = None  # type: ignore[assignment]
    remix_policy: dict | None = None
    error: str | None = None

    def __post_init__(self) -> None:
        if self.parent_content_ids is None:
            self.parent_content_ids = []


def _signer() -> c2pa.Signer:
    settings = get_settings()
    info = c2pa.C2paSignerInfo(
        alg=b"es256",
        sign_cert=(settings.cert_dir / "chain.pem").read_bytes(),
        private_key=(settings.cert_dir / "private.key").read_bytes(),
        # DIKKAT: bos bytes (b"") verilirse c2pa-rs "Signature: empty string"
        # hatasi firlatir. Zaman damgasi sunucusu kullanmiyoruz.
        ta_url=None,
    )
    return c2pa.Signer.from_info(info)


def certs_available() -> bool:
    settings = get_settings()
    return (settings.cert_dir / "chain.pem").exists() and (
        settings.cert_dir / "private.key"
    ).exists()


def _remix_policy_assertion(
    content_id: str,
    remix_allowed: bool,
    commercial_remix_allowed: bool,
    min_source_share: float,
    parent_content_id: str | None = None,
) -> dict:
    data = {
        "content_id": content_id,
        "remix_allowed": remix_allowed,
        "commercial_remix_allowed": commercial_remix_allowed,
        "min_source_share": min_source_share,
    }
    if parent_content_id:
        data["parent_content_id"] = parent_content_id
    return {"label": REMIX_POLICY_LABEL, "data": data}


def sign_original(
    source: Path,
    dest: Path,
    *,
    content_id: str,
    author: str,
    title: str,
    remix_allowed: bool = True,
    commercial_remix_allowed: bool = True,
    min_source_share: float = 0.0,
) -> str | None:
    """Ozgun icerigi imzalar. Manifest URN'ini doner."""
    manifest = {
        "claim_generator_info": [CLAIM_GENERATOR],
        "title": title,
        "format": "image/jpeg",
        "assertions": [
            {
                "label": "c2pa.actions.v2",
                "data": {
                    "actions": [
                        {"action": "c2pa.created", "digitalSourceType": DIGITAL_CAPTURE}
                    ]
                },
            },
            {
                "label": "stds.schema-org.CreativeWork",
                "data": {
                    "@context": "https://schema.org",
                    "@type": "CreativeWork",
                    "author": [{"@type": "Person", "name": author}],
                },
            },
            _remix_policy_assertion(
                content_id, remix_allowed, commercial_remix_allowed, min_source_share
            ),
        ],
    }
    dest.parent.mkdir(parents=True, exist_ok=True)
    with c2pa.Builder(manifest) as builder:
        builder.sign_file(source, dest, _signer())
    return read(dest).urn


def sign_remix(
    source: Path,
    dest: Path,
    *,
    content_id: str,
    author: str,
    title: str,
    parent_path: Path,
    parent_title: str,
    parent_content_id: str,
    actions: list[str],
    remix_allowed: bool = True,
) -> str | None:
    """Turev icerigi imzalar ve kaynagina baglar.

    Args:
        actions: Remix studyosunda uygulanan islemler
            ("c2pa.cropped", "c2pa.edited", "c2pa.color_adjustments" ...).
    """
    action_list: list[dict] = [
        {"action": "c2pa.opened", "parameters": {"org.nemek.parent": parent_content_id}}
    ]
    action_list.extend({"action": a} for a in actions)
    action_list.append(
        {"action": "c2pa.edited", "softwareAgent": {"name": "N-Emek Remix Studio"}}
    )

    manifest = {
        "claim_generator_info": [CLAIM_GENERATOR],
        "title": title,
        "format": "image/jpeg",
        "assertions": [
            {"label": "c2pa.actions.v2", "data": {"actions": action_list}},
            {
                "label": "stds.schema-org.CreativeWork",
                "data": {
                    "@context": "https://schema.org",
                    "@type": "CreativeWork",
                    "author": [{"@type": "Person", "name": author}],
                },
            },
            _remix_policy_assertion(
                content_id, remix_allowed, True, 0.0, parent_content_id=parent_content_id
            ),
        ],
    }
    dest.parent.mkdir(parents=True, exist_ok=True)
    with c2pa.Builder(manifest) as builder:
        with open(parent_path, "rb") as parent_stream:
            builder.add_ingredient(
                {"title": parent_title, "relationship": "parentOf"},
                "image/jpeg",
                parent_stream,
            )
        builder.sign_file(source, dest, _signer())
    return read(dest).urn


def read(path: Path) -> ManifestInfo:
    """Dosyadaki manifesti okur. Yoksa `present=False` doner."""
    try:
        with c2pa.Reader(str(path)) as reader:
            payload = json.loads(reader.json())
            state = reader.get_validation_state()
    except Exception as exc:
        # Manifest yok, bozuk veya format desteklenmiyor. Koken kurtarma
        # hatti icin normal bir durum - burasi hata degil, sinyal.
        return ManifestInfo(present=False, error=f"{type(exc).__name__}: {exc}")

    active_id = payload.get("active_manifest")
    manifests = payload.get("manifests", {})
    if not active_id or active_id not in manifests:
        return ManifestInfo(present=False, error="etkin manifest yok")

    active = manifests[active_id]
    parents: list[str] = []
    policy: dict | None = None

    for assertion in active.get("assertions", []):
        label = assertion.get("label", "")
        data = assertion.get("data", {})
        if label == REMIX_POLICY_LABEL:
            policy = data
            if data.get("parent_content_id"):
                parents.append(data["parent_content_id"])
        elif label.startswith("c2pa.actions"):
            for action in data.get("actions", []):
                parent = (action.get("parameters") or {}).get("org.nemek.parent")
                if parent:
                    parents.append(parent)

    return ManifestInfo(
        present=True,
        urn=active_id,
        title=active.get("title"),
        issuer=(active.get("signature_info") or {}).get("issuer"),
        validation_state=str(state) if state is not None else None,
        parent_content_ids=list(dict.fromkeys(parents)),
        remix_policy=policy,
    )
