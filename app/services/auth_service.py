from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.security import create_access_token, verify_password
from app.models.user import Usuario


def login(db: Session, username_or_email: str, password: str) -> str:
    user: Usuario | None = (
        db.query(Usuario)
        .filter(
            (Usuario.username == username_or_email) | (Usuario.email == username_or_email)
        )
        .first()
    )

    # Return 401 for both "not found" and "wrong password" — no user enumeration.
    if user is None or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if user.estado != "activo":
        raise HTTPException(status_code=403, detail="User account is inactive")

    return create_access_token({"sub": str(user.id), "username": user.username})
