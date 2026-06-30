from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.dependencies import get_current_user
from app.core.rate_limit import login_rate_limit
from app.db.session import get_db
from app.models.user import Usuario
from app.schemas.auth import CurrentUserResponse, LoginRequest, TokenResponse
from app.services import auth_service

router = APIRouter()

_COOKIE_NAME = "visora_token"
_COOKIE_OPTS = dict(
    httponly=True,
    samesite="lax",
    secure=settings.COOKIE_SECURE,
    domain=settings.COOKIE_DOMAIN or None,
)


@router.post("/auth/login", response_model=TokenResponse)
def login(
    payload: LoginRequest,
    response: Response,
    db: Session = Depends(get_db),
    _: None = Depends(login_rate_limit),
):
    token = auth_service.login(db, payload.username_or_email, payload.password)
    response.set_cookie(
        key=_COOKIE_NAME,
        value=token,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        **_COOKIE_OPTS,
    )
    return TokenResponse(access_token=token)


@router.post("/auth/logout", status_code=204)
def logout(response: Response):
    response.delete_cookie(_COOKIE_NAME, **_COOKIE_OPTS)


@router.get("/auth/me", response_model=CurrentUserResponse)
def get_me(current_user: Usuario = Depends(get_current_user)):
    return CurrentUserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        estado_acceso=current_user.estado_acceso,
        rol_id=current_user.rol_id,
        rol_tipo=current_user.rol.tipo if current_user.rol else None,
    )
