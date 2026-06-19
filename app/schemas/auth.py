from typing import Optional

from pydantic import BaseModel


class LoginRequest(BaseModel):
    username_or_email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class CurrentUserResponse(BaseModel):
    id: int
    username: str
    email: Optional[str] = None
    estado_acceso: bool
    rol_id: int
    rol_tipo: Optional[str] = None
