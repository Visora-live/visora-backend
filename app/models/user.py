from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Usuario(Base):
    __tablename__ = "usuario"
    __table_args__ = (Index("ix_usuario_rol_id", "rol_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    estado_acceso: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default=text("true")
    )
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    email: Mapped[str | None] = mapped_column(String(200), unique=True, nullable=True)
    contrasena: Mapped[str] = mapped_column(String(255), nullable=False)
    rol_id: Mapped[int] = mapped_column(Integer, ForeignKey("rol.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    rol: Mapped["Rol"] = relationship("Rol", back_populates="usuarios")
    asignaciones_tienda: Mapped[list["TiendaUsuario"]] = relationship(
        "TiendaUsuario", back_populates="usuario"
    )
