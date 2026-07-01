import os
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, require_admin, user_owns_camera
from app.core.config import settings
from app.db.session import get_db
from app.models.event import Evento
from app.models.user import Usuario
from app.schemas.event_image import EventImageCreate, EventImageResponse, EventImageUpdate
from app.services import event_image_service

router = APIRouter()


@router.get("/event-images", response_model=list[EventImageResponse])
def list_event_images(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    evento_id: Optional[int] = None,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    return event_image_service.list_event_images(db, skip=skip, limit=limit, evento_id=evento_id)


@router.post("/event-images", response_model=EventImageResponse, status_code=201)
def create_event_image(
    payload: EventImageCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    return event_image_service.create_event_image(db, payload)


@router.post("/event-images/upload", response_model=EventImageResponse, status_code=201)
async def upload_event_image(
    evento_id: int = Form(...),
    es_frame_representativo: bool = Form(False),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    return await event_image_service.upload_event_image(
        db=db, evento_id=evento_id, file=file,
        es_frame_representativo=es_frame_representativo,
    )


@router.get("/event-images/by-event/{evento_id}/file")
def get_event_image_file_by_event(
    evento_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    images = event_image_service.list_event_images(db, skip=0, limit=1, evento_id=evento_id)
    if not images:
        raise HTTPException(status_code=404, detail="No image for this event")
    ev_img = images[0]
    event = db.get(Evento, ev_img.evento_id)
    if not event or not user_owns_camera(db, current_user, event.camara_id):
        raise HTTPException(status_code=403, detail="Access denied")
    full_path = os.path.join(settings.LOCAL_STORAGE_PATH, ev_img.storage_ref)
    if not os.path.exists(full_path):
        raise HTTPException(status_code=404, detail="Image file not found on disk")
    return FileResponse(
        full_path,
        media_type=ev_img.content_type or "image/jpeg",
        headers={"Cache-Control": "no-store, no-cache"},
    )


@router.get("/event-images/{event_image_id}/file")
def get_event_image_file(
    event_image_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    ev_img = event_image_service.get_event_image(db, event_image_id)
    if not ev_img:
        raise HTTPException(status_code=404, detail="Event image not found")
    event = db.get(Evento, ev_img.evento_id)
    if not event or not user_owns_camera(db, current_user, event.camara_id):
        raise HTTPException(status_code=403, detail="Access denied")
    full_path = os.path.join(settings.LOCAL_STORAGE_PATH, ev_img.storage_ref)
    if not os.path.exists(full_path):
        raise HTTPException(status_code=404, detail="Image file not found on disk")
    return FileResponse(
        full_path,
        media_type=ev_img.content_type or "image/jpeg",
        headers={"Cache-Control": "no-store, no-cache"},
    )


@router.get("/event-images/{event_image_id}", response_model=EventImageResponse)
def get_event_image(
    event_image_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    ev_img = event_image_service.get_event_image(db, event_image_id)
    if not ev_img:
        raise HTTPException(status_code=404, detail="Event image not found")
    event = db.get(Evento, ev_img.evento_id)
    if not event or not user_owns_camera(db, current_user, event.camara_id):
        raise HTTPException(status_code=403, detail="Access denied")
    return ev_img


@router.patch("/event-images/{event_image_id}", response_model=EventImageResponse)
def update_event_image(
    event_image_id: int,
    payload: EventImageUpdate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    return event_image_service.update_event_image(db, event_image_id, payload)


@router.delete("/event-images/{event_image_id}", response_model=EventImageResponse)
def delete_event_image(
    event_image_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    return event_image_service.delete_event_image(db, event_image_id)
