from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String, Text, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Evidencia(Base):
    __tablename__ = "evidencia"
    __table_args__ = (Index("ix_evidencia_evento_id", "evento_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    evento_id: Mapped[int] = mapped_column(Integer, ForeignKey("evento.id"), nullable=False)
    tipo: Mapped[str] = mapped_column(
        String(20), nullable=False, default="snapshot", server_default=text("'snapshot'")
    )
    storage_provider: Mapped[str] = mapped_column(
        String(20), nullable=False, default="local", server_default=text("'local'")
    )
    storage_path: Mapped[str] = mapped_column(Text, nullable=False)
    storage_bucket: Mapped[str | None] = mapped_column(String(200), nullable=True)
    filename: Mapped[str | None] = mapped_column(String(255), nullable=True)
    content_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    ai_processed: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default=text("false")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    evento: Mapped["Evento"] = relationship("Evento", back_populates="evidencias")
    identificaciones: Mapped[list["Identificacion"]] = relationship(
        "Identificacion", back_populates="evidencia"
    )
