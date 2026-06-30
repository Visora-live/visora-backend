from __future__ import annotations

import os
import signal
import subprocess
import sys
from pathlib import Path

# ── Weapon worker ─────────────────────────────────────────────────────────────
_WEAPON_PROCESSES: dict[int, subprocess.Popen] = {}
_WEAPON_PAUSED: set[int] = set()  # cameras with detection explicitly stopped

_WEAPON_PYTHON = os.getenv("DETECTION_PYTHON", r"C:\visora_venv\Scripts\python.exe")
_WEAPON_SCRIPT = os.getenv(
    "DETECTION_SCRIPT",
    str(
        Path(__file__).resolve().parents[3]
        / "models" / "package_weapon_webcam" / "run_weapon_webcam.py"
    ),
)

# ── Face worker ───────────────────────────────────────────────────────────────
_FACE_PROCESSES: dict[int, subprocess.Popen] = {}
_FACE_PAUSED: set[int] = set()  # cameras with face detection explicitly stopped

_FACE_PYTHON = os.getenv("DETECTION_FACE_PYTHON", r"C:\visora_venv\Scripts\python.exe")
_FACE_SCRIPT = os.getenv(
    "DETECTION_FACE_SCRIPT",
    str(
        Path(__file__).resolve().parents[3]
        / "models" / "package_face_webcam" / "run_face_rtsp.py"
    ),
)

# ── Shared config ─────────────────────────────────────────────────────────────
_VISORA_USER = os.getenv("DETECTION_VISORA_USER", "admin")
_VISORA_PASS = os.getenv("DETECTION_VISORA_PASS", "")
_API_BASE    = os.getenv("DETECTION_API_BASE", "http://localhost:8000/api")
_MEDIAMTX    = os.getenv("DETECTION_MEDIAMTX_HOST", "localhost")
_PAUSE_DIR   = Path(os.getenv("SNAPSHOT_DIR", r"C:\visora_snapshots"))


# ── PID files (survive backend restarts) ─────────────────────────────────────

def _pid_file(camera_id: int) -> Path:
    return _PAUSE_DIR / f"cam{camera_id}.weapon.pid"

def _face_pid_file(camera_id: int) -> Path:
    return _PAUSE_DIR / f"cam{camera_id}.face.pid"

def _write_pid(path: Path, pid: int) -> None:
    try:
        path.write_text(str(pid))
    except Exception:
        pass

def _read_pid(path: Path) -> int | None:
    try:
        return int(path.read_text().strip())
    except Exception:
        return None

def _kill_pid(pid: int) -> None:
    try:
        if sys.platform == "win32":
            subprocess.run(["taskkill", "/F", "/PID", str(pid)],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            os.kill(pid, signal.SIGTERM)
    except Exception:
        pass


# ── Pause files ───────────────────────────────────────────────────────────────

def _pause_file(camera_id: int) -> Path:
    return _PAUSE_DIR / f"cam{camera_id}.paused"

def _face_pause_file(camera_id: int) -> Path:
    return _PAUSE_DIR / f"cam{camera_id}.face_paused"


# ── Process lifecycle helpers ─────────────────────────────────────────────────

def _is_alive(proc_map: dict, camera_id: int) -> bool:
    proc = proc_map.get(camera_id)
    if not proc:
        return False
    if proc.poll() is not None:
        proc_map.pop(camera_id, None)
        return False
    return True


def _kill_stale(pid_file: Path) -> None:
    """Kill any leftover worker from a previous backend process using the PID file."""
    pid = _read_pid(pid_file)
    if pid is not None:
        _kill_pid(pid)
        pid_file.unlink(missing_ok=True)


def _spawn(
    proc_map: dict,
    python: str,
    script: str,
    camera_id: int,
    pid_file: Path,
    extra_env: dict | None = None,
) -> None:
    if not Path(python).exists():
        print(f"[detection_manager] Python not found: {python}", flush=True)
        return
    if not Path(script).exists():
        print(f"[detection_manager] Script not found: {script}", flush=True)
        return
    env = {
        **os.environ,
        "CAMERA_ID":   str(camera_id),
        "RTSP_URL":    f"rtsp://{_MEDIAMTX}:8554/cam{camera_id}",
        "API_BASE":    _API_BASE,
        "VISORA_USER": _VISORA_USER,
        "VISORA_PASS": _VISORA_PASS,
        "HEADLESS":    "1",
        **(extra_env or {}),
    }
    _PAUSE_DIR.mkdir(parents=True, exist_ok=True)
    log_out = open(_PAUSE_DIR / f"worker_{camera_id}_out.txt", "a", buffering=1)
    log_err = open(_PAUSE_DIR / f"worker_{camera_id}_err.txt", "a", buffering=1)
    try:
        proc = subprocess.Popen(
            [python, script],
            env=env,
            stdout=log_out,
            stderr=log_err,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
        )
        proc_map[camera_id] = proc
        _write_pid(pid_file, proc.pid)
        print(f"[detection_manager] Spawned cam {camera_id} PID={proc.pid}", flush=True)
    except OSError as exc:
        print(f"[detection_manager] Failed to spawn worker cam {camera_id}: {exc}", flush=True)
    finally:
        log_out.close()
        log_err.close()


def _kill_proc(proc_map: dict, camera_id: int, pid_file: Path) -> bool:
    proc = proc_map.get(camera_id)
    if proc:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
        proc_map.pop(camera_id, None)
    # Also kill by PID file in case proc_map lost track
    _kill_stale(pid_file)
    return True


# ── Weapon detection API ──────────────────────────────────────────────────────

def start(camera_id: int) -> bool:
    pf = _pause_file(camera_id)
    pid_f = _pid_file(camera_id)

    _WEAPON_PAUSED.discard(camera_id)
    _kill_stale(pid_f)

    if _is_alive(_WEAPON_PROCESSES, camera_id) and not pf.exists():
        return False

    _PAUSE_DIR.mkdir(parents=True, exist_ok=True)
    pf.unlink(missing_ok=True)
    if not _is_alive(_WEAPON_PROCESSES, camera_id):
        _spawn(_WEAPON_PROCESSES, _WEAPON_PYTHON, _WEAPON_SCRIPT, camera_id,
               pid_f, {"ALERT_COOLDOWN": "30", "FRAME_SKIP": "1", "CAPTURE_WINDOW": "1.0"})
    return True


def stop(camera_id: int) -> bool:
    _WEAPON_PAUSED.add(camera_id)
    _PAUSE_DIR.mkdir(parents=True, exist_ok=True)
    _pause_file(camera_id).touch()
    if _is_alive(_WEAPON_PROCESSES, camera_id):
        pass  # local subprocess will read pause file; cloud workers blocked via _WEAPON_PAUSED
    return True


def is_detection_active(camera_id: int) -> bool:
    return camera_id not in _WEAPON_PAUSED and not _pause_file(camera_id).exists()


def kill(camera_id: int) -> bool:
    _pause_file(camera_id).unlink(missing_ok=True)
    return _kill_proc(_WEAPON_PROCESSES, camera_id, _pid_file(camera_id))


def is_running(camera_id: int) -> bool:
    # Explicitly stopped by user — pause file is the source of truth (survives restarts)
    if _pause_file(camera_id).exists() or camera_id in _WEAPON_PAUSED:
        return False
    # Local subprocess running (dev/local mode)
    if camera_id in _WEAPON_PROCESSES:
        return _is_alive(_WEAPON_PROCESSES, camera_id)
    # No local process → cloud worker on separate instance; assume active unless paused
    return True


def status(camera_id: int) -> dict:
    return {"camera_id": camera_id, "running": is_running(camera_id)}


# ── Face detection API ────────────────────────────────────────────────────────

def start_face(camera_id: int) -> bool:
    pf = _face_pause_file(camera_id)
    pid_f = _face_pid_file(camera_id)

    _FACE_PAUSED.discard(camera_id)
    _kill_stale(pid_f)

    if _is_alive(_FACE_PROCESSES, camera_id) and not pf.exists():
        return False

    _PAUSE_DIR.mkdir(parents=True, exist_ok=True)
    pf.unlink(missing_ok=True)
    if not _is_alive(_FACE_PROCESSES, camera_id):
        _spawn(_FACE_PROCESSES, _FACE_PYTHON, _FACE_SCRIPT, camera_id, pid_f)
    return True


def stop_face(camera_id: int) -> bool:
    _FACE_PAUSED.add(camera_id)
    _PAUSE_DIR.mkdir(parents=True, exist_ok=True)
    _face_pause_file(camera_id).touch()
    return True


def is_face_active(camera_id: int) -> bool:
    return camera_id not in _FACE_PAUSED


def kill_face(camera_id: int) -> bool:
    _face_pause_file(camera_id).unlink(missing_ok=True)
    return _kill_proc(_FACE_PROCESSES, camera_id, _face_pid_file(camera_id))


def is_face_running(camera_id: int) -> bool:
    if _face_pause_file(camera_id).exists() or camera_id in _FACE_PAUSED:
        return False
    if camera_id in _FACE_PROCESSES:
        return _is_alive(_FACE_PROCESSES, camera_id)
    return True


def face_status(camera_id: int) -> dict:
    return {"camera_id": camera_id, "face_running": is_face_running(camera_id)}
