from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class UserBase(BaseModel):
    username: str
    email: Optional[str] = None
    estado_acceso: bool = True
    rol_id: int


class UserCreate(UserBase):
    password: Optional[str] = None


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    estado_acceso: Optional[bool] = None
    rol_id: Optional[int] = None
    password: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    username: str
    email: Optional[str] = None
    estado_acceso: bool
    rol_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
