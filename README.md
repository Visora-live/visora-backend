# VISORA Backend

FastAPI backend for the VISORA security platform.

## Structure

```
backend/
├── app/
│   ├── main.py                          # FastAPI app + CORS + routers
│   ├── core/config.py                   # Settings via pydantic-settings
│   ├── api/routes/
│   │   ├── health.py                    # GET /api/health, GET /api/health/db
│   │   └── cameras.py                   # GET /api/cameras/test-ip-webcam
│   ├── adapters/ip_webcam_adapter.py    # URL builder for IP Webcam Android
│   ├── schemas/camera.py                # Pydantic schemas
│   ├── services/
│   │   ├── camera_connection_service.py # Prepares camera connection data
│   │   └── detection_service.py         # AI detection placeholder
│   ├── infrastructure/storage/
│   │   ├── local_storage.py             # Local storage placeholder
│   │   └── s3_storage_placeholder.py    # AWS S3 placeholder
│   ├── db/
│   │   ├── base.py                      # SQLAlchemy DeclarativeBase for future models
│   │   └── session.py                   # Engine, SessionLocal, get_db()
│   └── models/                          # DB models (future phases)
├── alembic/                             # Database migrations
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
├── alembic.ini
├── requirements.txt
├── .env.example
└── README.md
```

## Setup

### 1. Create virtual environment

```bash
cd backend
python -m venv venv
```

Activate (Windows PowerShell):
```powershell
.\venv\Scripts\Activate.ps1
```

Activate (Windows CMD):
```cmd
venv\Scripts\activate.bat
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Create .env file

```bash
copy .env.example .env
```

Edit `.env` and set `DATABASE_URL` with your local PostgreSQL credentials.

### 4. Run backend

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend running at: http://localhost:8000

Interactive docs: http://localhost:8000/api/docs

---

## Database (PostgreSQL)

PostgreSQL must be running locally to use `/api/health/db` and all future
database features. Required for any phase that uses models or CRUD.

### Create user and database

Run in `psql` or pgAdmin:

```sql
CREATE USER visora_user WITH PASSWORD 'visora_password';
CREATE DATABASE visora_db OWNER visora_user;
GRANT ALL PRIVILEGES ON DATABASE visora_db TO visora_user;
```

### Configure .env

```
DATABASE_URL=postgresql+psycopg://visora_user:visora_password@localhost:5432/visora_db
```

### Run migrations (once models exist)

```bash
alembic upgrade head
```

Create a new migration after changing models:

```bash
alembic revision --autogenerate -m "describe change"
```

> `alembic/versions/` is empty until final table models are created in a future phase.

---

## Test endpoints

### GET /api/health

```bash
curl http://localhost:8000/api/health
```

Expected response:
```json
{
  "status": "ok",
  "service": "VISORA Backend",
  "version": "0.1.0",
  "environment": "local"
}
```

### GET /api/health/db

Requires PostgreSQL running and `.env` configured with a valid `DATABASE_URL`.

```bash
curl http://localhost:8000/api/health/db
```

Expected response (connected):
```json
{
  "status": "ok",
  "database": "connected"
}
```

Expected response (disconnected — HTTP 503):
```json
{
  "status": "error",
  "database": "disconnected",
  "detail": "Database connection failed"
}
```

### GET /api/cameras/test-ip-webcam

```bash
curl "http://localhost:8000/api/cameras/test-ip-webcam?host=192.168.18.84&port=8080"
```

Expected response:
```json
{
  "camera_type": "ip_webcam_android",
  "connection_mode": "local_rtsp",
  "input": { "host": "192.168.18.84", "port": 8080 },
  "base_url": "http://192.168.18.84:8080",
  "rtsp_h264_url": "rtsp://192.168.18.84:8080/h264.sdp",
  "snapshot_url": "http://192.168.18.84:8080/shot.jpg",
  "mjpeg_url": "http://192.168.18.84:8080/video",
  "message": "IP Webcam URLs generated successfully. Real stream connection is not enabled yet."
}
```

### GET /api/cameras/test-ip-webcam/snapshot

Tests real connectivity to an IP Webcam device. Makes an HTTP GET to `http://host:port/shot.jpg`
and reports whether the camera responded correctly.

**Requirements:**
- Android device running IP Webcam app, same local network as this PC.
- Replace `192.168.18.84` with the IP shown in the IP Webcam app.
- The IP changes when the device reconnects to Wi-Fi — always check the app.
- No AI, no OpenCV, no image processing — only connectivity check.

```bash
curl "http://localhost:8000/api/cameras/test-ip-webcam/snapshot?host=192.168.18.84&port=8080"
```

Expected response (camera reachable):
```json
{
  "camera_type": "ip_webcam_android",
  "connection_mode": "local_snapshot",
  "input": { "host": "192.168.18.84", "port": 8080 },
  "snapshot_url": "http://192.168.18.84:8080/shot.jpg",
  "reachable": true,
  "status_code": 200,
  "content_type": "image/jpeg",
  "message": "IP Webcam snapshot is reachable"
}
```

Expected response (camera not reachable — timeout or wrong IP):
```json
{
  "camera_type": "ip_webcam_android",
  "connection_mode": "local_snapshot",
  "input": { "host": "192.168.18.84", "port": 8080 },
  "snapshot_url": "http://192.168.18.84:8080/shot.jpg",
  "reachable": false,
  "status_code": null,
  "content_type": null,
  "message": "IP Webcam is not reachable at the given host and port"
}
```

---

## Notes

### IP Webcam host changes
The camera IP (`192.168.X.X`) changes depending on the network. It is always
passed as a query parameter — never hardcoded. When cameras are registered via
the web interface (future phase), each camera will store its own editable
`host` and `port`.

### Local testing only
Everything runs on `localhost` for now. The frontend (Angular, port 4200) and
this backend (port 8000) communicate locally. No cloud connectivity required.

### Database tables not created yet
Final table schema (Tienda, Usuario, Rol, Camara, Evento, Identificacion) will
be designed from the project database diagram in a future phase.
`alembic/versions/` is intentionally empty until then.

### AWS is prepared, not implemented
- `STORAGE_PROVIDER=s3` activates `S3StoragePlaceholder` (boto3 not installed yet).
- `CAMERA_CONNECTION_MODE=cloud_ingest` reserved for future AWS Kinesis Video Streams.
- `AWS_REGION` and `AWS_S3_BUCKET` variables exist in `.env.example` but are empty.
- No AWS credentials are stored or required at this stage.
- Future: local PostgreSQL will migrate to **Amazon RDS PostgreSQL** when moving to AWS.

### What is NOT implemented yet
- Real camera stream consumption (no OpenCV)
- Authentication
- AI detection models (facial recognition, firearm detection)
- WebSocket events
- AWS S3 upload
- boto3
