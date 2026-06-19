from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Index, Integer, String, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Identificacion(Base):
    __tablename__ = "identificacion"
    __table_args__ = (
        Index("ix_identificacion_evento_imagen_id", "evento_imagen_id"),
        Index("ix_identificacion_dni", "dni"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    evento_imagen_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("evento_imagen.id"), nullable=False
    )
    nombre: Mapped[str | None] = mapped_column(String(100), nullable=True)
    apellido: Mapped[str | None] = mapped_column(String(100), nullable=True)
    dni: Mapped[str | None] = mapped_column(String(20), nullable=True)
    confianza_identificacion: Mapped[float] = mapped_column(
        Float, nullable=False, default=0.0, server_default=text("0")
    )
    fuente: Mapped[str] = mapped_column(
        String(50), nullable=False, default="manual", server_default=text("'manual'")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    evento_imagen: Mapped["EventoImagen"] = relationship(
        "EventoImagen", back_populates="identificaciones"
    )
