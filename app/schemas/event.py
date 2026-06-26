from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

EventSeveridad = Literal["baja", "media", "alta", "critica"]
EventTipo = Literal["facial_recognition", "weapon_detection", "suspicious_activity", "system", "desconocido"]
EventEstado = Literal["abierto", "revisado", "descartado", "cerrado"]


class EventBase(BaseModel):
    estado: str = "abierto"
    fecha_hora: Optional[datetime] = None
    comentario: Optional[str] = Field(None, max_length=2000)
    camara_id: int
    tipo: str = "desconocido"
    severidad: str = "media"


class EventCreate(EventBase):
    tipo: EventTipo = "desconocido"
    severidad: EventSeveridad = "media"
    estado: EventEstado = "abierto"


class EventUpdate(BaseModel):
    estado: Optional[EventEstado] = None
    fecha_hora: Optional[datetime] = None
    comentario: Optional[str] = Field(None, max_length=2000)
    camara_id: Optional[int] = None
    tipo: Optional[EventTipo] = None
    severidad: Optional[EventSeveridad] = None


class EventResponse(EventBase):
    id: int
    fecha_hora: datetime
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
