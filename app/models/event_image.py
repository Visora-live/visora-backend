from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Index, Integer, String, Text, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class EventoImagen(Base):
    __tablename__ = "evento_imagen"
    __table_args__ = (Index("ix_evento_imagen_evento_id", "evento_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    storage_ref: Mapped[str] = mapped_column(Text, nullable=False)
    evento_id: Mapped[int] = mapped_column(Integer, ForeignKey("evento.id"), nullable=False)
    es_frame_representativo: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default=text("false")
    )
    confianza_arma: Mapped[float] = mapped_column(
        Float, nullable=False, default=0.0, server_default=text("0")
    )
    confianza_rostro: Mapped[float] = mapped_column(
        Float, nullable=False, default=0.0, server_default=text("0")
    )
    storage_provider: Mapped[str] = mapped_column(
        String(20), nullable=False, default="local", server_default=text("'local'")
    )
    filename: Mapped[str | None] = mapped_column(String(255), nullable=True)
    content_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    evento: Mapped["Evento"] = relationship("Evento", back_populates="evento_imagenes")
    identificaciones: Mapped[list["Identificacion"]] = relationship(
        "Identificacion", back_populates="evento_imagen"
    )
