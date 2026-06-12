from typing import Generator, Optional

from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

engine: Optional[Engine] = (
    create_engine(settings.DATABASE_URL, pool_pre_ping=True)
    if settings.DATABASE_URL
    else None
)

SessionLocal = (
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
    if engine is not None
    else None
)


def get_db() -> Generator[Session, None, None]:
    if SessionLocal is None:
        raise RuntimeError("DATABASE_URL is not configured")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
