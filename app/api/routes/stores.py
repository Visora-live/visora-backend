from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.store import StoreCreate, StoreResponse, StoreUpdate
from app.services import store_service

router = APIRouter()


@router.get("/stores", response_model=list[StoreResponse])
def list_stores(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    return store_service.list_stores(db, skip=skip, limit=limit)


@router.get("/stores/{store_id}", response_model=StoreResponse)
def get_store(store_id: int, db: Session = Depends(get_db)):
    store = store_service.get_store(db, store_id)
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    return store


@router.post("/stores", response_model=StoreResponse, status_code=201)
def create_store(payload: StoreCreate, db: Session = Depends(get_db)):
    return store_service.create_store(db, payload)


@router.patch("/stores/{store_id}", response_model=StoreResponse)
def update_store(
    store_id: int,
    payload: StoreUpdate,
    db: Session = Depends(get_db),
):
    return store_service.update_store(db, store_id, payload)


@router.delete("/stores/{store_id}", response_model=StoreResponse)
def delete_store(store_id: int, db: Session = Depends(get_db)):
    return store_service.delete_store(db, store_id)
