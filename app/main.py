import os
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.dependencies import get_current_user
from app.api.routes import (
    auth,
    health,
    cameras,
    stores,
    roles,
    users,
    events,
    alerts,
    event_images,
    identifications,
    recovery_requests,
)
from app.api.routes.cameras import public_router as cameras_public_router
from app.services import detection_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Pre-warm detector workers (paused) so models are loaded before user clicks button
    prewarm = os.getenv("DETECTION_PREWARM_CAMERAS", "1")
    for cam_str in prewarm.split(","):
        cam_str = cam_str.strip()
        if cam_str.isdigit():
            cam_id = int(cam_str)
            detection_manager._PAUSE_DIR.mkdir(parents=True, exist_ok=True)
            detection_manager._pause_file(cam_id).touch()
            detection_manager._spawn(cam_id)
    yield
    # Shutdown: kill all workers
    for cam_id in list(detection_manager._PROCESSES.keys()):
        detection_manager.kill(cam_id)


_is_prod = settings.ENVIRONMENT == "production"

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url=None if _is_prod else f"{settings.API_PREFIX}/docs",
    redoc_url=None if _is_prod else f"{settings.API_PREFIX}/redoc",
    openapi_url=None if _is_prod else f"{settings.API_PREFIX}/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def security_headers(request: Request, call_next) -> Response:
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["X-Permitted-Cross-Domain-Policies"] = "none"
    return response

_protected = {"dependencies": [Depends(get_current_user)]}

app.include_router(auth.router, prefix=settings.API_PREFIX)
app.include_router(health.router, prefix=settings.API_PREFIX)
app.include_router(cameras_public_router, prefix=settings.API_PREFIX)
app.include_router(cameras.router, prefix=settings.API_PREFIX, **_protected)
app.include_router(stores.router, prefix=settings.API_PREFIX, **_protected)
app.include_router(roles.router, prefix=settings.API_PREFIX, **_protected)
app.include_router(users.router, prefix=settings.API_PREFIX, **_protected)
app.include_router(events.router, prefix=settings.API_PREFIX, **_protected)
app.include_router(alerts.router, prefix=settings.API_PREFIX, **_protected)
app.include_router(event_images.router, prefix=settings.API_PREFIX, **_protected)
app.include_router(identifications.router, prefix=settings.API_PREFIX, **_protected)
# Public POST (forgot-password) + admin-only GET/PATCH enforced per-route inside.
app.include_router(recovery_requests.router, prefix=settings.API_PREFIX)
