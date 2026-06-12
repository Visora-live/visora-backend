from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Rol(Base):
    __tablename__ = "rol"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)

    usuarios: Mapped[list["Usuario"]] = relationship("Usuario", back_populates="rol")
