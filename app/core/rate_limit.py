import time
from collections import defaultdict
from threading import Lock

from fastapi import HTTPException, Request

_lock = Lock()
_WINDOW_SECONDS = 60

# Login: 10 attempts / 60s
_login_store: dict[str, list[float]] = defaultdict(list)
_LOGIN_MAX = 10

# Recovery-request: 5 submissions / 60s
_recovery_store: dict[str, list[float]] = defaultdict(list)
_RECOVERY_MAX = 5


def _check(store: dict[str, list[float]], ip: str, max_attempts: int, detail: str) -> None:
    now = time.monotonic()
    with _lock:
        store[ip] = [t for t in store[ip] if now - t < _WINDOW_SECONDS]
        if len(store[ip]) >= max_attempts:
            raise HTTPException(
                status_code=429,
                detail=detail,
                headers={"Retry-After": "60"},
            )
        store[ip].append(now)


def login_rate_limit(request: Request) -> None:
    ip = request.client.host if request.client else "unknown"
    _check(_login_store, ip, _LOGIN_MAX, "Too many login attempts. Try again in 60 seconds.")


def recovery_rate_limit(request: Request) -> None:
    ip = request.client.host if request.client else "unknown"
    _check(_recovery_store, ip, _RECOVERY_MAX, "Too many recovery requests. Try again in 60 seconds.")
