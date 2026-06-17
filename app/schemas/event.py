from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class EventBase(BaseModel):
    tipo: str = "desconocido"
    severidad: str = "media"
    estado: str = "abierto"
    fecha_hora: Optional[datetime] = None
    comentario: Optional[str] = None
    camara_id: int


class EventCreate(EventBase):
    pass


class EventUpdate(BaseModel):
    tipo: Optional[str] = None
    severidad: Optional[str] = None
    estado: Optional[str] = None
    fecha_hora: Optional[datetime] = None
    comentario: Optional[str] = None
    camara_id: Optional[int] = None


class EventResponse(EventBase):
    id: int
    fecha_hora: datetime  # always set by DB default
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
