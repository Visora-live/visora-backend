from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class AlertBase(BaseModel):
    titulo: str = Field(..., max_length=500)
    descripcion: Optional[str] = Field(None, max_length=2000)
    tipo: str = Field("manual", max_length=50)
    severidad: str = Field("media", max_length=50)
    estado: str = Field("abierta", max_length=50)
    leida: bool = False
    evento_id: Optional[int] = None
    camara_id: Optional[int] = None
    tienda_id: Optional[int] = None
    resolved_at: Optional[datetime] = None


class AlertCreate(AlertBase):
    pass


class AlertUpdate(BaseModel):
    titulo: Optional[str] = Field(None, max_length=500)
    descripcion: Optional[str] = Field(None, max_length=2000)
    tipo: Optional[str] = Field(None, max_length=50)
    severidad: Optional[str] = Field(None, max_length=50)
    estado: Optional[str] = Field(None, max_length=50)
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
