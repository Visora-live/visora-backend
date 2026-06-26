from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models.user import Usuario

_bearer = HTTPBearer(auto_error=False)

_ADMIN_TYPES = {"admin", "administrador"}


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


def user_owns_tienda(db: Session, user: Usuario, tienda_id: int) -> bool:
    """True if user is admin or is linked to the given tienda."""
    from app.models.store_user import TiendaUsuario

    if is_admin(user):
        return True
    return (
        db.query(TiendaUsuario)
        .filter(
            TiendaUsuario.usuario_id == user.id,
            TiendaUsuario.tienda_id == tienda_id,
        )
        .first()
        is not None
    )


def user_owns_camera(db: Session, user: Usuario, camera_id: int) -> bool:
    """True if user is admin or owns the tienda the camera belongs to."""
    from app.models.camera import Camara
    from app.models.store_user import TiendaUsuario

    if is_admin(user):
        return True
    owned = (
        db.query(TiendaUsuario.tienda_id)
        .filter(TiendaUsuario.usuario_id == user.id)
        .subquery()
    )
    return (
        db.query(Camara)
        .filter(Camara.id == camera_id, Camara.tienda_id.in_(owned))
        .first()
        is not None
    )
