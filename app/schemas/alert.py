from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class AlertBase(BaseModel):
    titulo: str
    descripcion: Optional[str] = None
    tipo: str = "manual"
    severidad: str = "media"
    estado: str = "abierta"
    leida: bool = False
    evento_id: Optional[int] = None
    camara_id: Optional[int] = None
    tienda_id: Optional[int] = None
    resolved_at: Optional[datetime] = None


class AlertCreate(AlertBase):
    pass


class AlertUpdate(BaseModel):
    titulo: Optional[str] = None
    descripcion: Optional[str] = None
    tipo: Optional[str] = None
    severidad: Optional[str] = None
    estado: Optional[str] = None
    leida: Optional[bool] = None
    evento_id: Optional[int] = None
    camara_id: Optional[int] = None
    tienda_id: Optional[int] = None
    resolved_at: Optional[datetime] = None


class AlertResponse(AlertBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
