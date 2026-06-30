from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.dependencies import require_admin
from app.core.rate_limit import recovery_rate_limit
from app.db.session import get_db
from app.models.recovery_request import SolicitudRecuperacion
from app.models.user import Usuario
from app.schemas.recovery_request import (
    RecoveryRequestCreate,
    RecoveryRequestResponse,
    RecoveryRequestUpdate,
)

router = APIRouter()


@router.post("/recovery-requests", response_model=RecoveryRequestResponse, status_code=201)
def create_recovery_request(
    payload: RecoveryRequestCreate,
    db: Session = Depends(get_db),
    _: None = Depends(recovery_rate_limit),
):
    """Public — submitted from /forgot-password. No auth required."""
    req = SolicitudRecuperacion(
        identificador=payload.identificador.strip(),
        email=payload.email.strip(),
        descripcion=payload.descripcion.strip(),
    )
    db.add(req)
    db.commit()
    db.refresh(req)
    return req


@router.get("/recovery-requests", response_model=list[RecoveryRequestResponse])
def list_recovery_requests(
    only_unread: bool = False,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    query = db.query(SolicitudRecuperacion)
    if only_unread:
        query = query.filter(SolicitudRecuperacion.leida.is_(False))
    return query.order_by(SolicitudRecuperacion.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/recovery-requests/unread-count")
def unread_recovery_count(
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    count = db.query(SolicitudRecuperacion).filter(SolicitudRecuperacion.leida.is_(False)).count()
    return {"count": count}


@router.patch("/recovery-requests/{request_id}", response_model=RecoveryRequestResponse)
def update_recovery_request(
    request_id: int,
    payload: RecoveryRequestUpdate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    req = db.get(SolicitudRecuperacion, request_id)
    if not req:
        raise HTTPException(status_code=404, detail="Recovery request not found")
    if payload.leida is not None:
        req.leida = payload.leida
    db.commit()
    db.refresh(req)
    return req
