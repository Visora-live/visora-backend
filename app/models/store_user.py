from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class TiendaUsuario(Base):
    __tablename__ = "tienda_usuario"

    tienda_id: Mapped[int] = mapped_column(Integer, ForeignKey("tienda.id"), primary_key=True)
    usuario_id: Mapped[int] = mapped_column(Integer, ForeignKey("usuario.id"), primary_key=True)
    estado: Mapped[str] = mapped_column(
        String(20), nullable=False, default="activo", server_default="activo"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    tienda: Mapped["Tienda"] = relationship("Tienda", back_populates="asignaciones_usuario")
    usuario: Mapped["Usuario"] = relationship("Usuario", back_populates="asignaciones_tienda")
