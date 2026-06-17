from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class IdentificationBase(BaseModel):
    evidencia_id: int
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    dni: Optional[str] = None
    confianza: Optional[float] = None
    fuente: str = "manual"


class IdentificationCreate(IdentificationBase):
    pass


class IdentificationUpdate(BaseModel):
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    dni: Optional[str] = None
    confianza: Optional[float] = None
    fuente: Optional[str] = None


class IdentificationResponse(IdentificationBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
