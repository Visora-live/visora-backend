from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models.user import Usuario

_bearer = HTTPBearer(auto_error=False)

_ADMIN_TYPES = {"admin"}


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: Session = Depends(get_db),
) -> Usuario:
    if credentials is None:
        raise HTTPException(status_code=401, detail="Not authenticated")

    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        sub: str | None = payload.get("sub")
        if sub is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    try:
        user_id = int(sub)
    except (ValueError, TypeError):
        raise HTTPException(status_code=401, detail="Invalid token")

    user: Usuario | None = db.query(Usuario).filter(Usuario.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    if not user.estado_acceso:
        raise HTTPException(status_code=403, detail="User account is inactive")
    return user


def require_admin(current_user: Usuario = Depends(get_current_user)) -> Usuario:
    role_tipo = (current_user.rol.tipo.strip().lower() if current_user.rol else "")
    if role_tipo not in _ADMIN_TYPES:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


def is_admin(user: Usuario) -> bool:
    return bool(user.rol and user.rol.tipo.strip().lower() in _ADMIN_TYPES)


def is_propietario(user: Usuario) -> bool:
    return bool(user.rol and user.rol.tipo.strip().lower() == "propietario")
