from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class EventBase(BaseModel):
    estado: str = "abierto"
    fecha_hora: Optional[datetime] = None
    comentario: Optional[str] = None
    camara_id: int
    tipo: str = "desconocido"
    severidad: str = "media"


class EventCreate(EventBase):
    pass


class EventUpdate(BaseModel):
    estado: Optional[str] = None
    fecha_hora: Optional[datetime] = None
    comentario: Optional[str] = None
    camara_id: Optional[int] = None
    tipo: Optional[str] = None
    severidad: Optional[str] = None


class EventResponse(EventBase):
    id: int
    fecha_hora: datetime
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
