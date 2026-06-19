from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Camara(Base):
    __tablename__ = "camara"
    __table_args__ = (
        Index("ix_camara_tienda_id", "tienda_id"),
        Index("ix_camara_estado", "estado"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre_cam: Mapped[str] = mapped_column(String(100), nullable=False)
    direccion_ip: Mapped[str] = mapped_column(String(255), nullable=False)
    puerto: Mapped[int] = mapped_column(Integer, nullable=False, default=8080, server_default="8080")
    ubicacion_camara: Mapped[str | None] = mapped_column(String(200), nullable=True)
    estado: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default=text("false")
    )
    source_type: Mapped[str] = mapped_column(
        String(30), nullable=False, default="rtsp_h264", server_default=text("'rtsp_h264'")
    )
    protocolo: Mapped[str] = mapped_column(
        String(10), nullable=False, default="rtsp", server_default=text("'rtsp'")
    )
    tienda_id: Mapped[int] = mapped_column(Integer, ForeignKey("tienda.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    tienda: Mapped["Tienda"] = relationship("Tienda", back_populates="camaras")
    eventos: Mapped[list["Evento"]] = relationship("Evento", back_populates="camara")
    alertas: Mapped[list["Alerta"]] = relationship("Alerta", back_populates="camara")
