"""Mevcut veritabaninda bir kullaniciya rol atar.

Rol modelde ve uclarda vardi ama atama yolu yoktu: elle SQL yazmak
disinda kimse moderator yapilamiyordu. Yeni kurulumlarda `seed_demo.py`
Ceyda'yi moderator olarak yaratiyor; bu betik *var olan* bir veritabani
icin - ornegin Docker biriminde duran demo verisini `down -v` yapmadan
duzeltmek icin.

Calistirma:
    .venv/Scripts/python.exe scripts/set_role.py ceyda moderator
    .venv/Scripts/python.exe scripts/set_role.py --liste

Docker calisirken:
    docker compose exec backend python /app/scripts/set_role.py ceyda moderator
"""

from __future__ import annotations

import sys
from pathlib import Path

# Windows konsolu varsayilan olarak cp1254 kullaniyor; Turkce ciktinin
# bozulmamasi icin akisi UTF-8'e sabitliyoruz.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from sqlalchemy import select  # noqa: E402

from app.core.database import SessionLocal, create_schema  # noqa: E402
from app.models.entities import User  # noqa: E402

ROLLER = ("uye", "moderator")


def liste(session) -> int:
    kullanicilar = list(session.scalars(select(User).order_by(User.created_at)))
    if not kullanicilar:
        print("Kayıtlı kullanıcı yok. Önce: python scripts/seed_demo.py --reset")
        return 1
    print(f"{'kullanıcı':<12} {'ad':<20} rol")
    print("-" * 44)
    for user in kullanicilar:
        print(f"{user.handle:<12} {user.display_name:<20} {user.role}")
    return 0


def main() -> int:
    args = sys.argv[1:]
    create_schema()
    session = SessionLocal()
    try:
        if not args or args[0] in ("--liste", "--list"):
            return liste(session)

        if len(args) != 2:
            print(__doc__)
            return 2

        handle, role = args
        if role not in ROLLER:
            print(f"Geçersiz rol: {role}. Seçenekler: {', '.join(ROLLER)}")
            return 2

        user = session.scalar(select(User).where(User.handle == handle))
        if user is None:
            print(f"Kullanıcı bulunamadı: {handle}")
            liste(session)
            return 1

        onceki = user.role
        if onceki == role:
            print(f"{user.display_name} zaten “{role}” rolünde; değişiklik yapılmadı.")
            return 0

        user.role = role
        session.commit()
        print(f"{user.display_name}: {onceki} → {role}")
        return 0
    finally:
        session.close()


if __name__ == "__main__":
    raise SystemExit(main())
