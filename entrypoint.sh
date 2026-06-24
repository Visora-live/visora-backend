#!/bin/sh
set -e

echo "[entrypoint] waiting for the database..."
python - <<'PY'
import os, time
from sqlalchemy import create_engine, text
url = os.environ["DATABASE_URL"]
for i in range(40):
    try:
        with create_engine(url).connect() as c:
            c.execute(text("select 1"))
        print("[entrypoint] database is up")
        break
    except Exception:
        print(f"[entrypoint] db not ready, retry {i+1}/40")
        time.sleep(2)
else:
    raise SystemExit("[entrypoint] database not reachable")
PY

echo "[entrypoint] running migrations..."
alembic upgrade head

echo "[entrypoint] starting API..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
