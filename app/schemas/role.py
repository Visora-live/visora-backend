from typing import Optional

from pydantic import BaseModel, ConfigDict


class RoleBase(BaseModel):
    tipo: str


class RoleCreate(RoleBase):
    pass


class RoleUpdate(BaseModel):
    tipo: Optional[str] = None


class RoleResponse(RoleBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
