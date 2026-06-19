from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class StoreBase(BaseModel):
    nombre: str
    direccion: Optional[str] = None
    ruc: Optional[str] = None
    estado_tienda: bool = True
    licencia_inicio: Optional[date] = None
    licencia_fin: Optional[date] = None


class StoreCreate(StoreBase):
    pass


class StoreUpdate(BaseModel):
    nombre: Optional[str] = None
    direccion: Optional[str] = None
    ruc: Optional[str] = None
    estado_tienda: Optional[bool] = None
    licencia_inicio: Optional[date] = None
    licencia_fin: Optional[date] = None


class StoreResponse(StoreBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
