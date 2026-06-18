from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import Usuario
from app.schemas.auth import CurrentUserResponse, LoginRequest, TokenResponse
from app.services import auth_service

router = APIRouter()


@router.post("/auth/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    token = auth_service.login(db, payload.username_or_email, payload.password)
    return TokenResponse(access_token=token)


@router.get("/auth/me", response_model=CurrentUserResponse)
def get_me(current_user: Usuario = Depends(get_current_user)):
    return CurrentUserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        estado=current_user.estado,
        rol_id=current_user.rol_id,
        rol_nombre=current_user.rol.nombre if current_user.rol else None,
    )
