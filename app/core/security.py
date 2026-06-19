from datetime import datetime, timedelta, timezone

import bcrypt
from jose import jwt

from app.core.config import settings

_PLACEHOLDER_PREFIX = "$pending$"


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, contrasena_hash: str) -> bool:
    if contrasena_hash.startswith(_PLACEHOLDER_PREFIX):
        return False
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), contrasena_hash.encode("utf-8"))
    except Exception:
        return False


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta if expires_delta is not None
        else timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode["exp"] = expire
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
