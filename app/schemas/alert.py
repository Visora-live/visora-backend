from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

AlertTipo = Literal["manual", "facial_recognition", "weapon_detection", "suspicious_activity", "system"]
AlertEstado = Literal["abierta", "reconocida", "resuelta", "descartada"]


class AlertBase(BaseModel):
    titulo: str = Field(..., max_length=500)
    descripcion: Optional[str] = Field(None, max_length=2000)
    tipo: str = "manual"
    estado: str = "abierta"
    leida: bool = False
    evento_id: Optional[int] = None
    camara_id: Optional[int] = None
    tienda_id: Optional[int] = None
    resolved_at: Optional[datetime] = None


class AlertCreate(AlertBase):
    tipo: AlertTipo = "manual"
    estado: AlertEstado = "abierta"


class AlertUpdate(BaseModel):
    titulo: Optional[str] = Field(None, max_length=500)
    descripcion: Optional[str] = Field(None, max_length=2000)
    tipo: Optional[AlertTipo] = None
    estado: Optional[AlertEstado] = None
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
