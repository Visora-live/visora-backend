from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

_PROCESSES: dict[int, subprocess.Popen] = {}

_PYTHON = os.getenv("DETECTION_PYTHON", r"C:\visora_venv\Scripts\python.exe")
_SCRIPT = os.getenv(
    "DETECTION_SCRIPT",
    str(
        Path(__file__).resolve().parents[3]
        / "models"
        / "package_weapon_webcam"
        / "run_weapon_webcam.py"
    ),
)
_VISORA_USER = os.getenv("DETECTION_VISORA_USER", "admin")
_VISORA_PASS = os.getenv("DETECTION_VISORA_PASS", "Admin1234!")
_API_BASE    = os.getenv("DETECTION_API_BASE", "http://localhost:8000/api")
_MEDIAMTX    = os.getenv("DETECTION_MEDIAMTX_HOST", "localhost")
_PAUSE_DIR   = Path(os.getenv("SNAPSHOT_DIR", r"C:\visora_snapshots"))


def _pause_file(camera_id: int) -> Path:
    return _PAUSE_DIR / f"cam{camera_id}.paused"


def _is_process_alive(camera_id: int) -> bool:
    proc = _PROCESSES.get(camera_id)
    if not proc:
        return False
    if proc.poll() is not None:
        _PROCESSES.pop(camera_id, None)
        return False
    return True


def _spawn(camera_id: int) -> None:
    if not Path(_PYTHON).exists():
        return  # detection worker not available on this host (e.g. cloud server without GPU)
    env = {
        **os.environ,
        "CAMERA_ID":      str(camera_id),
        "RTSP_URL":       f"rtsp://{_MEDIAMTX}:8554/cam{camera_id}",
        "API_BASE":       _API_BASE,
        "VISORA_USER":    _VISORA_USER,
        "VISORA_PASS":    _VISORA_PASS,
        "ALERT_COOLDOWN": "60",
        "HEADLESS":       "1",
    }
    proc = subprocess.Popen(
        [_PYTHON, _SCRIPT],
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
    )
    _PROCESSES[camera_id] = proc


def start(camera_id: int) -> bool:
    """Unpause (and spawn if needed). Returns False if already active."""
    pf = _pause_file(camera_id)
    already_active = _is_process_alive(camera_id) and not pf.exists()
    if already_active:
        return False

    _PAUSE_DIR.mkdir(parents=True, exist_ok=True)
    pf.unlink(missing_ok=True)

    if not _is_process_alive(camera_id):
        _spawn(camera_id)

    return True


def stop(camera_id: int) -> bool:
    """Pause reporting without killing the process (models stay loaded)."""
    if not _is_process_alive(camera_id):
        return False
    _PAUSE_DIR.mkdir(parents=True, exist_ok=True)
    _pause_file(camera_id).touch()
    return True


def kill(camera_id: int) -> bool:
    """Fully terminate the worker process."""
    _pause_file(camera_id).unlink(missing_ok=True)
    proc = _PROCESSES.get(camera_id)
    if not proc:
        return False
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
    _PROCESSES.pop(camera_id, None)
    return True


def is_running(camera_id: int) -> bool:
    return _is_process_alive(camera_id) and not _pause_file(camera_id).exists()


def status(camera_id: int) -> dict:
    return {"camera_id": camera_id, "running": is_running(camera_id)}
