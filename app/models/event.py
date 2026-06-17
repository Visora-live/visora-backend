from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Evento(Base):
    __tablename__ = "evento"
    __table_args__ = (
        Index("ix_evento_camara_id", "camara_id"),
        Index("ix_evento_estado", "estado"),
        Index("ix_evento_severidad", "severidad"),
        Index("ix_evento_fecha_hora", "fecha_hora"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tipo: Mapped[str] = mapped_column(
        String(30), nullable=False, default="desconocido", server_default=text("'desconocido'")
    )
    severidad: Mapped[str] = mapped_column(
        String(20), nullable=False, default="media", server_default=text("'media'")
    )
    estado: Mapped[str] = mapped_column(
        String(20), nullable=False, default="abierto", server_default=text("'abierto'")
    )
    fecha_hora: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    comentario: Mapped[str | None] = mapped_column(Text, nullable=True)
    camara_id: Mapped[int] = mapped_column(Integer, ForeignKey("camara.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    camara: Mapped["Camara"] = relationship("Camara", back_populates="eventos")
    evidencias: Mapped[list["Evidencia"]] = relationship("Evidencia", back_populates="evento")
