import bcrypt

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import Usuario

_TARGET_ROUNDS = 10


def login(db: Session, username_or_email: str, password: str) -> str:
    user: Usuario | None = (
        db.query(Usuario)
        .filter(
            (Usuario.username == username_or_email) | (Usuario.email == username_or_email)
        )
        .first()
    )

    if user is None or not verify_password(password, user.contrasena):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not user.estado_acceso:
        raise HTTPException(status_code=403, detail="User account is inactive")

    # Lazy re-hash: downgrade rounds to _TARGET_ROUNDS if stored hash uses more
    try:
        stored_rounds = int(user.contrasena.split("$")[2])
        if stored_rounds > _TARGET_ROUNDS:
            user.contrasena = hash_password(password)
            db.commit()
    except Exception:
        pass

    return create_access_token({"sub": str(user.id), "username": user.username})
