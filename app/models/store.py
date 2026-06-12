from datetime import date, datetime

from sqlalchemy import Date, DateTime, Index, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Tienda(Base):
    __tablename__ = "tienda"
    __table_args__ = (Index("ix_tienda_estado", "estado"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    direccion: Mapped[str | None] = mapped_column(String(200), nullable=True)
    ruc: Mapped[str | None] = mapped_column(String(20), unique=True, nullable=True)
    estado: Mapped[str] = mapped_column(
        String(20), nullable=False, default="activa", server_default="activa"
    )
    licencia_inicio: Mapped[date | None] = mapped_column(Date, nullable=True)
    licencia_fin: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    camaras: Mapped[list["Camara"]] = relationship("Camara", back_populates="tienda")
