from typing import Optional

from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.infrastructure.storage.local_storage import LocalStorageService
from app.models.event import Evento
from app.models.evidence import Evidencia
from app.schemas.evidence import EvidenceCreate, EvidenceUpdate

_storage = LocalStorageService()


def list_evidences(
    db: Session,
    skip: int = 0,
    limit: int = 50,
    evento_id: Optional[int] = None,
    tipo: Optional[str] = None,
    storage_provider: Optional[str] = None,
) -> list[Evidencia]:
    query = db.query(Evidencia)
    if evento_id is not None:
        query = query.filter(Evidencia.evento_id == evento_id)
    if tipo is not None:
        query = query.filter(Evidencia.tipo == tipo)
    if storage_provider is not None:
        query = query.filter(Evidencia.storage_provider == storage_provider)
    return query.offset(skip).limit(limit).all()


def get_evidence(db: Session, evidence_id: int) -> Evidencia | None:
    return db.get(Evidencia, evidence_id)


def create_evidence(db: Session, payload: EvidenceCreate) -> Evidencia:
    if not db.get(Evento, payload.evento_id):
        raise HTTPException(status_code=404, detail="Event not found")
    evidence = Evidencia(**payload.model_dump())
    db.add(evidence)
    db.commit()
    db.refresh(evidence)
    return evidence


def update_evidence(db: Session, evidence_id: int, payload: EvidenceUpdate) -> Evidencia:
    evidence = db.get(Evidencia, evidence_id)
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")
    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(evidence, key, value)
    db.commit()
    db.refresh(evidence)
    return evidence


def delete_evidence(db: Session, evidence_id: int) -> Evidencia:
    """Physical delete — Evidencia has no estado field. File on disk not removed."""
    evidence = db.get(Evidencia, evidence_id)
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")
    db.delete(evidence)
    db.flush()
    db.expunge(evidence)
    db.commit()
    return evidence


async def create_evidence_from_upload(
    db: Session,
    evento_id: int,
    file: UploadFile,
    tipo: str = "snapshot",
) -> Evidencia:
    if not db.get(Evento, evento_id):
        raise HTTPException(status_code=404, detail="Event not found")
    data = await file.read()
    relative_path = _storage.save_file(
        data=data,
        original_filename=file.filename or "upload",
        subdir="evidences",
    )
    evidence = Evidencia(
        evento_id=evento_id,
        tipo=tipo,
        storage_provider="local",
        storage_path=relative_path,
        filename=file.filename,
        content_type=file.content_type,
    )
    db.add(evidence)
    db.commit()
    db.refresh(evidence)
    return evidence
