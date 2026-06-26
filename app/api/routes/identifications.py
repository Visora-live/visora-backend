from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, require_admin
from app.db.session import get_db
from app.models.user import Usuario
from app.schemas.identification import (
    IdentificationCreate,
    IdentificationFuente,
    IdentificationResponse,
    IdentificationUpdate,
)
from app.services import identification_service

router = APIRouter()


@router.get("/identifications", response_model=list[IdentificationResponse])
def list_identifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    evento_imagen_id: Optional[int] = None,
    fuente: Optional[IdentificationFuente] = None,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    return identification_service.list_identifications(
        db, skip=skip, limit=limit,
        evento_imagen_id=evento_imagen_id, fuente=fuente,
    )


@router.get("/identifications/{identification_id}", response_model=IdentificationResponse)
def get_identification(
    identification_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
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
