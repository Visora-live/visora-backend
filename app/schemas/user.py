from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class UserBase(BaseModel):
    username: str = Field(..., min_length=1, max_length=150)
    email: Optional[str] = Field(None, max_length=200)
    estado_acceso: bool = True
    rol_id: int


class UserCreate(UserBase):
    password: Optional[str] = Field(None, max_length=200)


class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=1, max_length=150)
    email: Optional[str] = Field(None, max_length=200)
    estado_acceso: Optional[bool] = None
    rol_id: Optional[int] = None
    password: Optional[str] = Field(None, max_length=200)


class UserResponse(BaseModel):
    id: int
    username: str
    email: Optional[str] = None
    estado_acceso: bool
    rol_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
