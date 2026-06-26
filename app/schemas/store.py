from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class StoreBase(BaseModel):
    nombre: str = Field(..., max_length=200)
    direccion: Optional[str] = Field(None, max_length=500)
    ruc: Optional[str] = Field(None, max_length=20)
    estado_tienda: bool = True
    licencia_inicio: Optional[date] = None
    licencia_fin: Optional[date] = None


class StoreCreate(BaseModel):
    nombre: str = Field(..., max_length=200)
    direccion: Optional[str] = Field(None, max_length=500)
    ruc: str = Field(..., max_length=20)
    usuario_id: int
    licencia_inicio: Optional[date] = None
    licencia_fin: Optional[date] = None


class StoreUpdate(BaseModel):
    nombre: Optional[str] = Field(None, max_length=200)
    direccion: Optional[str] = Field(None, max_length=500)
    ruc: Optional[str] = Field(None, max_length=20)
    estado_tienda: Optional[bool] = None
    licencia_inicio: Optional[date] = None
    licencia_fin: Optional[date] = None


class StoreResponse(StoreBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class StoreUserAssign(BaseModel):
    usuario_id: int


class AssignedUserResponse(BaseModel):
    id: int
    username: str
    email: Optional[str] = None
    rol_tipo: Optional[str] = None
