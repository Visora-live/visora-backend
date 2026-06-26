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

_is_prod = settings.ENVIRONMENT == "production"

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url=None if _is_prod else f"{settings.API_PREFIX}/docs",
    redoc_url=None if _is_prod else f"{settings.API_PREFIX}/redoc",
    openapi_url=None if _is_prod else f"{settings.API_PREFIX}/openapi.json",
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
