from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, is_admin, require_admin
from app.db.session import get_db
from app.models.user import Usuario
from app.schemas.alert import AlertCreate, AlertResponse, AlertUpdate
from app.services import alert_service

router = APIRouter()


@router.get("/alerts", response_model=list[AlertResponse])
def list_alerts(
    skip: int = 0,
    limit: int = 50,
    estado: Optional[str] = None,
    severidad: Optional[str] = None,
    tipo: Optional[str] = None,
    tienda_id: Optional[int] = None,
    camara_id: Optional[int] = None,
    evento_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    usuario_id = None if is_admin(current_user) else current_user.id
    return alert_service.list_alerts(
        db, skip=skip, limit=limit,
        estado=estado, severidad=severidad, tipo=tipo,
        tienda_id=tienda_id, camara_id=camara_id, evento_id=evento_id,
        usuario_id=usuario_id,
    )


@router.get("/alerts/{alert_id}", response_model=AlertResponse)
def get_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    alert = alert_service.get_alert(db, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert


@router.post("/alerts", response_model=AlertResponse, status_code=201)
def create_alert(
    payload: AlertCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    return alert_service.create_alert(db, payload)


@router.patch("/alerts/{alert_id}", response_model=AlertResponse)
def update_alert(
    alert_id: int,
    payload: AlertUpdate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    return alert_service.update_alert(db, alert_id, payload)


@router.delete("/alerts/{alert_id}", response_model=AlertResponse)
def delete_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    return alert_service.delete_alert(db, alert_id)
