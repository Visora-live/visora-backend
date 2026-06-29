from __future__ import annotations

import re
from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.dependencies import require_admin
from app.db.session import get_db
from app.models.camera import Camara
from app.models.event import Evento
from app.models.identification import Identificacion
from app.models.store import Tienda
from app.models.user import Usuario

router = APIRouter()

ALPHA = 0.7
BETA  = 0.3


# ── Helpers ───────────────────────────────────────────────────────────────────

def _parse_c_arma(comentario: str | None) -> float | None:
    if not comentario:
        return None
    # "confianza: 76%" or "confianza 0.80"
    m = re.search(r'confianza[:\s]+(\d+(?:\.\d+)?)%?', comentario, re.IGNORECASE)
    if not m:
        return None
    val = float(m.group(1))
    return val / 100.0 if val > 1 else val


def _is_still_analyzing(comentario: str | None) -> bool:
    if not comentario:
        return True
    return 'analizando' in comentario.lower()


def _score(c_arma: float, c_rostro: float, i_rostro: int) -> float:
    return round(ALPHA * c_arma + BETA * c_rostro * i_rostro, 4)


# ── Schemas ───────────────────────────────────────────────────────────────────

class EventScoreOut(BaseModel):
    event_id: int
    fecha_hora: str
    c_arma: float
    c_rostro: float
    i_rostro: int
    s_score: float
    infractor_nombre: Optional[str] = None
    infractor_apellido: Optional[str] = None
    infractor_dni: Optional[str] = None


class CameraReportOut(BaseModel):
    camera_id: int
    camera_name: str
    location: str
    tienda_nombre: str
    total_events: int
    identified_events: int
    avg_score: float
    max_score: float
    events: list[EventScoreOut]


class AlgorithmReportOut(BaseModel):
    alpha: float
    beta: float
    cameras: list[CameraReportOut]


# ── Route ─────────────────────────────────────────────────────────────────────

@router.get("/algorithm/report", response_model=AlgorithmReportOut)
def get_algorithm_report(
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    weapon_events = (
        db.query(Evento)
        .filter(
            Evento.tipo == "weapon_detection",
            Evento.eliminado == False,
            Evento.estado == "revisado",
        )
        .order_by(Evento.fecha_hora.desc())
        .all()
    )

    cameras: dict[int, dict] = {}

    for evt in weapon_events:
        if _is_still_analyzing(evt.comentario):
            continue

        c_arma = _parse_c_arma(evt.comentario)
        if c_arma is None:
            continue

        # Look up identification
        ident: Identificacion | None = (
            db.query(Identificacion)
            .filter(Identificacion.evento_id == evt.id)
            .first()
        )

        if ident:
            i_rostro           = 1
            c_rostro           = float(ident.confianza_identificacion or 0.0)
            infractor_nombre   = ident.nombre
            infractor_apellido = ident.apellido
            infractor_dni      = ident.dni
        else:
            m_rostro   = re.search(r'Confianza rostro[:\s]+(\d+)%', evt.comentario or '', re.IGNORECASE)
            m_portador = re.search(r'Portador identificado', evt.comentario or '', re.IGNORECASE)
            if m_portador and m_rostro:
                i_rostro  = 1
                c_rostro  = float(m_rostro.group(1)) / 100.0
                m_name = re.search(r'Portador identificado:\s+([^(]+)\(DNI:\s*([^)]+)\)', evt.comentario or '')
                infractor_nombre   = m_name.group(1).strip() if m_name else None
                infractor_apellido = None
                infractor_dni      = m_name.group(2).strip() if m_name else None
            else:
                i_rostro           = 0
                c_rostro           = 0.0
                infractor_nombre   = None
                infractor_apellido = None
                infractor_dni      = None

        s = _score(c_arma, c_rostro, i_rostro)

        ev_out = EventScoreOut(
            event_id           = evt.id,
            fecha_hora         = evt.fecha_hora.isoformat() if evt.fecha_hora else "",
            c_arma             = round(c_arma, 4),
            c_rostro           = round(c_rostro, 4),
            i_rostro           = i_rostro,
            s_score            = s,
            infractor_nombre   = infractor_nombre,
            infractor_apellido = infractor_apellido,
            infractor_dni      = infractor_dni,
        )

        cam_id = evt.camara_id
        if cam_id not in cameras:
            cam = db.get(Camara, cam_id)
            tienda = db.get(Tienda, cam.tienda_id) if cam else None
            cameras[cam_id] = {
                "camera_id":    cam_id,
                "camera_name":  cam.nombre_cam if cam else f"Cámara {cam_id}",
                "location":     cam.ubicacion_camara or "" if cam else "",
                "tienda_nombre": tienda.nombre if tienda else "—",
                "events":       [],
            }
        cameras[cam_id]["events"].append(ev_out)

    # Build camera reports
    cam_reports: list[CameraReportOut] = []
    for cam_data in cameras.values():
        evs: list[EventScoreOut] = cam_data["events"]
        scores = [e.s_score for e in evs]
        cam_reports.append(CameraReportOut(
            camera_id         = cam_data["camera_id"],
            camera_name       = cam_data["camera_name"],
            location          = cam_data["location"],
            tienda_nombre     = cam_data["tienda_nombre"],
            total_events      = len(evs),
            identified_events = sum(1 for e in evs if e.i_rostro),
            avg_score         = round(sum(scores) / len(scores), 4) if scores else 0.0,
            max_score         = round(max(scores), 4) if scores else 0.0,
            events            = evs,
        ))

    return AlgorithmReportOut(alpha=ALPHA, beta=BETA, cameras=cam_reports)
