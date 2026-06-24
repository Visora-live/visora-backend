from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class RecoveryRequestCreate(BaseModel):
    identificador: str = Field(..., min_length=1, max_length=150)
    celular: Optional[str] = Field(None, max_length=30)
    email: str = Field(..., min_length=1, max_length=200)
    descripcion: str = Field(..., min_length=1)


class RecoveryRequestUpdate(BaseModel):
    leida: Optional[bool] = None


class RecoveryRequestResponse(BaseModel):
    id: int
    identificador: str
    celular: Optional[str] = None
    email: str
    descripcion: str
    leida: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
