from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Index, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Identificacion(Base):
    __tablename__ = "identificacion"
    __table_args__ = (
        Index("ix_identificacion_evidencia_id", "evidencia_id"),
        Index("ix_identificacion_dni", "dni"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    evidencia_id: Mapped[int] = mapped_column(Integer, ForeignKey("evidencia.id"), nullable=False)
    nombre: Mapped[str | None] = mapped_column(String(100), nullable=True)
    apellido: Mapped[str | None] = mapped_column(String(100), nullable=True)
    dni: Mapped[str | None] = mapped_column(String(20), nullable=True)
    confianza: Mapped[float | None] = mapped_column(Float, nullable=True)
    fuente: Mapped[str] = mapped_column(
        String(50), nullable=False, default="manual", server_default="manual"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    evidencia: Mapped["Evidencia"] = relationship("Evidencia", back_populates="identificaciones")
