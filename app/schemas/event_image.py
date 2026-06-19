from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class EventImageBase(BaseModel):
    storage_ref: str
    evento_id: int
    es_frame_representativo: bool = False
    confianza_arma: float = 0.0
    confianza_rostro: float = 0.0
    storage_provider: str = "local"
    filename: Optional[str] = None
    content_type: Optional[str] = None


class EventImageCreate(EventImageBase):
    pass


class EventImageUpdate(BaseModel):
    storage_ref: Optional[str] = None
    es_frame_representativo: Optional[bool] = None
    confianza_arma: Optional[float] = None
    confianza_rostro: Optional[float] = None
    storage_provider: Optional[str] = None
    filename: Optional[str] = None
    content_type: Optional[str] = None


class EventImageResponse(EventImageBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
