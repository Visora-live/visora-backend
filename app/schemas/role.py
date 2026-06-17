from typing import Optional

from pydantic import BaseModel, ConfigDict


class RoleBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None


class RoleCreate(RoleBase):
    pass


class RoleUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None


class RoleResponse(RoleBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
