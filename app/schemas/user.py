from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class UserBase(BaseModel):
    username: str
    email: Optional[str] = None
    estado: str = "activo"
    rol_id: int


class UserCreate(UserBase):
    password: Optional[str] = None  # if omitted, account cannot log in until password is set


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    estado: Optional[str] = None
    rol_id: Optional[int] = None


class UserResponse(BaseModel):
    id: int
    username: str
    email: Optional[str] = None
    estado: str
    rol_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
