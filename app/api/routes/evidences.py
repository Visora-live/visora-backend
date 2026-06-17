from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.evidence import EvidenceCreate, EvidenceResponse, EvidenceUpdate
from app.services import evidence_service

router = APIRouter()


@router.get("/evidences", response_model=list[EvidenceResponse])
def list_evidences(
    skip: int = 0,
    limit: int = 50,
    evento_id: Optional[int] = None,
    tipo: Optional[str] = None,
    storage_provider: Optional[str] = None,
    db: Session = Depends(get_db),
):
    return evidence_service.list_evidences(
        db, skip=skip, limit=limit,
        evento_id=evento_id, tipo=tipo, storage_provider=storage_provider,
    )


@router.post("/evidences", response_model=EvidenceResponse, status_code=201)
def create_evidence(payload: EvidenceCreate, db: Session = Depends(get_db)):
    return evidence_service.create_evidence(db, payload)


@router.post("/evidences/upload", response_model=EvidenceResponse, status_code=201)
async def upload_evidence(
    evento_id: int = Form(...),
    tipo: str = Form("snapshot"),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    return await evidence_service.create_evidence_from_upload(
        db=db, evento_id=evento_id, file=file, tipo=tipo,
    )


@router.get("/evidences/{evidence_id}", response_model=EvidenceResponse)
def get_evidence(evidence_id: int, db: Session = Depends(get_db)):
    evidence = evidence_service.get_evidence(db, evidence_id)
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")
    return evidence


@router.patch("/evidences/{evidence_id}", response_model=EvidenceResponse)
def update_evidence(
    evidence_id: int,
    payload: EvidenceUpdate,
    db: Session = Depends(get_db),
):
    return evidence_service.update_evidence(db, evidence_id, payload)


@router.delete("/evidences/{evidence_id}", response_model=EvidenceResponse)
def delete_evidence(evidence_id: int, db: Session = Depends(get_db)):
    return evidence_service.delete_evidence(db, evidence_id)
