from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class EvidenceBase(BaseModel):
    evento_id: int
    tipo: str = "snapshot"
    storage_provider: str = "local"
    storage_path: str
    storage_bucket: Optional[str] = None
    filename: Optional[str] = None
    content_type: Optional[str] = None


class EvidenceCreate(EvidenceBase):
    pass


class EvidenceUpdate(BaseModel):
    tipo: Optional[str] = None
    storage_provider: Optional[str] = None
    storage_path: Optional[str] = None
    storage_bucket: Optional[str] = None
    filename: Optional[str] = None
    content_type: Optional[str] = None


class EvidenceResponse(EvidenceBase):
    id: int
    ai_processed: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
