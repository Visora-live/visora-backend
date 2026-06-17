from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Alerta(Base):
    __tablename__ = "alerta"
    __table_args__ = (
        Index("ix_alerta_estado", "estado"),
        Index("ix_alerta_severidad", "severidad"),
        Index("ix_alerta_tipo", "tipo"),
        Index("ix_alerta_evento_id", "evento_id"),
        Index("ix_alerta_camara_id", "camara_id"),
        Index("ix_alerta_tienda_id", "tienda_id"),
        Index("ix_alerta_created_at", "created_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    titulo: Mapped[str] = mapped_column(String(200), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    tipo: Mapped[str] = mapped_column(
        String(40), nullable=False, default="manual", server_default=text("'manual'")
    )
    severidad: Mapped[str] = mapped_column(
        String(20), nullable=False, default="media", server_default=text("'media'")
    )
    estado: Mapped[str] = mapped_column(
        String(20), nullable=False, default="abierta", server_default=text("'abierta'")
    )
    evento_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("evento.id"), nullable=True
    )
    camara_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("camara.id"), nullable=True
    )
    tienda_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("tienda.id"), nullable=True
    )
    resolved_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    evento: Mapped[Optional["Evento"]] = relationship("Evento", back_populates="alertas")
    camara: Mapped[Optional["Camara"]] = relationship("Camara", back_populates="alertas")
    tienda: Mapped[Optional["Tienda"]] = relationship("Tienda", back_populates="alertas")
