from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import require_admin
from app.db.session import get_db
from app.models.user import Usuario
from app.schemas.identification import (
    IdentificationCreate,
    IdentificationResponse,
    IdentificationUpdate,
)
from app.services import identification_service

router = APIRouter()


@router.get("/identifications", response_model=list[IdentificationResponse])
def list_identifications(
    skip: int = 0,
    limit: int = 50,
    evidencia_id: Optional[int] = None,
    fuente: Optional[str] = None,
    db: Session = Depends(get_db),
):
    return identification_service.list_identifications(
        db, skip=skip, limit=limit,
        evidencia_id=evidencia_id, fuente=fuente,
    )


@router.get("/identifications/{identification_id}", response_model=IdentificationResponse)
def get_identification(identification_id: int, db: Session = Depends(get_db)):
    identification = identification_service.get_identification(db, identification_id)
    if not identification:
        raise HTTPException(status_code=404, detail="Identification not found")
    return identification


@router.post("/identifications", response_model=IdentificationResponse, status_code=201)
def create_identification(
    payload: IdentificationCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    return identification_service.create_identification(db, payload)


@router.patch("/identifications/{identification_id}", response_model=IdentificationResponse)
def update_identification(
    identification_id: int,
    payload: IdentificationUpdate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    return identification_service.update_identification(db, identification_id, payload)


@router.delete("/identifications/{identification_id}", response_model=IdentificationResponse)
def delete_identification(
    identification_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    return identification_service.delete_identification(db, identification_id)
