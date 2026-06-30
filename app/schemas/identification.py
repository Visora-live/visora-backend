from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

IdentificationFuente = Literal["manual", "ia", "automatica"]


class IdentificationBase(BaseModel):
    evento_imagen_id: Optional[int] = None
    evento_id: Optional[int] = None
    nombre: Optional[str] = Field(None, max_length=100)
    apellido: Optional[str] = Field(None, max_length=100)
    apellido_materno: Optional[str] = Field(None, max_length=100)
    dni: Optional[str] = Field(None, max_length=20)
    edad: Optional[int] = Field(None, ge=0, le=150)
    confianza_identificacion: float = Field(0.0, ge=0.0, le=1.0)
    fuente: IdentificationFuente = "manual"


class IdentificationCreate(IdentificationBase):
    pass


class IdentificationUpdate(BaseModel):
    nombre: Optional[str] = Field(None, max_length=100)
    apellido: Optional[str] = Field(None, max_length=100)
    apellido_materno: Optional[str] = Field(None, max_length=100)
    dni: Optional[str] = Field(None, max_length=20)
    edad: Optional[int] = Field(None, ge=0, le=150)
    confianza_identificacion: Optional[float] = Field(None, ge=0.0, le=1.0)
    fuente: Optional[IdentificationFuente] = None


class IdentificationResponse(IdentificationBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
