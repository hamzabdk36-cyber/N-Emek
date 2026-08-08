"""Geliştirme ortamı için C2PA uyumlu ES256 sertifika zinciri üretir.

C2PA imzalama sertifikasının uyması gereken profil (C2PA 2.x, madde 14.x):
  - Anahtar: ECDSA P-256 (ES256)
  - keyUsage: digitalSignature (kritik)
  - extendedKeyUsage: emailProtection veya documentSigning (kritik)
  - basicConstraints: CA:FALSE (yaprak), CA:TRUE (kök)

Üretilenler (backend/certs/):
  root_ca.pem   kök sertifika (yalnızca geliştirme; güven listesine eklenmez)
  chain.pem     yaprak + kök, imzalamada kullanılan zincir
  private.key   yaprak özel anahtarı (PKCS#8, şifresiz)

Üretim ortamında bu anahtarlar bir HSM/KMS'te tutulur; burada yalnızca
prototipin uçtan uca çalıştığını göstermek için dosya tabanlı kullanılıyor.
"""

from __future__ import annotations

import datetime as dt
from pathlib import Path

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.x509.oid import ExtendedKeyUsageOID, NameOID

CERT_DIR = Path(__file__).resolve().parents[1] / "backend" / "certs"
VALID_DAYS = 3650


def _name(common_name: str, org_unit: str) -> x509.Name:
    return x509.Name(
        [
            x509.NameAttribute(NameOID.COUNTRY_NAME, "TR"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "N-Emek"),
            x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, org_unit),
            x509.NameAttribute(NameOID.COMMON_NAME, common_name),
        ]
    )


def build_chain() -> tuple[bytes, bytes, bytes]:
    now = dt.datetime.now(dt.timezone.utc)
    not_after = now + dt.timedelta(days=VALID_DAYS)

    # --- Kök CA ---
    root_key = ec.generate_private_key(ec.SECP256R1())
    root_subject = _name("N-Emek Development Root CA", "Provenance")
    root_cert = (
        x509.CertificateBuilder()
        .subject_name(root_subject)
        .issuer_name(root_subject)
        .public_key(root_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - dt.timedelta(minutes=5))
        .not_valid_after(not_after)
        .add_extension(x509.BasicConstraints(ca=True, path_length=1), critical=True)
        .add_extension(
            x509.KeyUsage(
                digital_signature=True,
                content_commitment=False,
                key_encipherment=False,
                data_encipherment=False,
                key_agreement=False,
                key_cert_sign=True,
                crl_sign=True,
                encipher_only=False,
                decipher_only=False,
            ),
            critical=True,
        )
        .add_extension(
            x509.SubjectKeyIdentifier.from_public_key(root_key.public_key()),
            critical=False,
        )
        .sign(root_key, hashes.SHA256())
    )

    # --- Yaprak (imzalama) sertifikası ---
    leaf_key = ec.generate_private_key(ec.SECP256R1())
    leaf_cert = (
        x509.CertificateBuilder()
        .subject_name(_name("N-Emek Content Signer", "Provenance"))
        .issuer_name(root_subject)
        .public_key(leaf_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - dt.timedelta(minutes=5))
        .not_valid_after(not_after)
        .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
        .add_extension(
            x509.KeyUsage(
                digital_signature=True,
                content_commitment=False,
                key_encipherment=False,
                data_encipherment=False,
                key_agreement=False,
                key_cert_sign=False,
                crl_sign=False,
                encipher_only=False,
                decipher_only=False,
            ),
            critical=True,
        )
        # C2PA yaprak sertifikasında EKU kritik ve emailProtection olmalı
        .add_extension(
            x509.ExtendedKeyUsage([ExtendedKeyUsageOID.EMAIL_PROTECTION]),
            critical=True,
        )
        .add_extension(
            x509.SubjectKeyIdentifier.from_public_key(leaf_key.public_key()),
            critical=False,
        )
        .add_extension(
            x509.AuthorityKeyIdentifier.from_issuer_public_key(root_key.public_key()),
            critical=False,
        )
        .sign(root_key, hashes.SHA256())
    )

    root_pem = root_cert.public_bytes(serialization.Encoding.PEM)
    leaf_pem = leaf_cert.public_bytes(serialization.Encoding.PEM)
    key_pem = leaf_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    return root_pem, leaf_pem + root_pem, key_pem


def main() -> None:
    CERT_DIR.mkdir(parents=True, exist_ok=True)
    root_pem, chain_pem, key_pem = build_chain()
    (CERT_DIR / "root_ca.pem").write_bytes(root_pem)
    (CERT_DIR / "chain.pem").write_bytes(chain_pem)
    (CERT_DIR / "private.key").write_bytes(key_pem)
    print(f"Sertifika zinciri uretildi: {CERT_DIR}")
    for f in ("root_ca.pem", "chain.pem", "private.key"):
        print(f"  {f}  ({(CERT_DIR / f).stat().st_size} bayt)")


if __name__ == "__main__":
    main()
