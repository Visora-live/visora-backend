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
│   │   └── cameras.py                   # GET /api/cameras/test-ip-webcam, GET /api/cameras/test-ip-webcam/snapshot
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

> **Fase 12B:** tablas base (`rol`, `tienda`, `usuario`, `camara`) — migración `3f2a1b4c5d6e`. Aplicada.
>
> **Fase 12C:** tablas operativas (`tienda_usuario`, `evento`, `evidencia`, `identificacion`) — migración `7a8b9c0d1e2f`. Aplicada.
>
> **Fase 12C-fix:** índice `ix_tienda_usuario_usuario_id` + alineación de `server_default` en modelos — migración `a1b2c3d4e5f6`. Aplicada.
>
> **Fase 12D:** tabla `alerta` con FKs opcionales a `evento`, `camara` y `tienda` — migración `b2c3d4e5f6a7`. Aplicada.

### Execute migration

```bash
alembic upgrade head
```

### Revert last migration

```bash
alembic downgrade -1
```

### Check migration history

```bash
alembic history
alembic current
```

> Run all alembic commands from the `backend/` directory (where `alembic.ini` lives).

---

## Fase 13A — CRUD tiendas y cámaras

> Frontend no modificado. Sin auth. Sin IA. Sin WebSocket. Sin AWS real.

### Endpoints nuevos

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/api/stores` | Listar tiendas |
| `GET` | `/api/stores/{id}` | Obtener tienda |
| `POST` | `/api/stores` | Crear tienda |
| `PATCH` | `/api/stores/{id}` | Actualizar tienda (parcial) |
| `DELETE` | `/api/stores/{id}` | Borrado lógico (estado → inactiva) |
| `GET` | `/api/cameras` | Listar cámaras (filtra por `tienda_id`) |
| `GET` | `/api/cameras/{id}` | Obtener cámara |
| `POST` | `/api/cameras` | Crear cámara |
| `PATCH` | `/api/cameras/{id}` | Actualizar cámara (parcial) |
| `DELETE` | `/api/cameras/{id}` | Borrado lógico (estado → inactiva) |

---

## Fase 13B — CRUD roles y usuarios

> Frontend no modificado. Sin auth. Sin JWT. Sin login. Sin hashing real. Sin IA.
>
> `password_hash` no se expone en ninguna respuesta. Usuarios creados con placeholder interno hasta Fase de auth.

### Endpoints nuevos

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/api/roles` | Listar roles |
| `GET` | `/api/roles/{id}` | Obtener rol |
| `POST` | `/api/roles` | Crear rol |
| `PATCH` | `/api/roles/{id}` | Actualizar rol (parcial) |
| `DELETE` | `/api/roles/{id}` | Borrado físico (solo si sin usuarios) — 409 si en uso |
| `GET` | `/api/users` | Listar usuarios (filtra por `rol_id`, `estado`) |
| `GET` | `/api/users/{id}` | Obtener usuario |
| `POST` | `/api/users` | Crear usuario |
| `PATCH` | `/api/users/{id}` | Actualizar usuario (parcial) |
| `DELETE` | `/api/users/{id}` | Borrado lógico (estado → inactivo) |

### Ejemplo POST /api/roles

```json
{
  "nombre": "admin",
  "descripcion": "Administrador del sistema"
}
```

### Ejemplo POST /api/users

```json
{
  "username": "admin",
  "email": "admin@visora.local",
  "estado": "activo",
  "rol_id": 1
}
```

---

## Fase 13C — CRUD eventos y alertas

> Frontend no modificado. Sin IA. Sin WebSocket. Sin evidencias. Sin auth.

### Endpoints nuevos

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/api/events` | Listar eventos (filtra por `camara_id`, `estado`, `severidad`) |
| `GET` | `/api/events/{id}` | Obtener evento |
| `POST` | `/api/events` | Crear evento |
| `PATCH` | `/api/events/{id}` | Actualizar evento (parcial) |
| `DELETE` | `/api/events/{id}` | Borrado lógico (estado → cerrado) |
| `GET` | `/api/alerts` | Listar alertas (filtra por `estado`, `severidad`, `tipo`, `tienda_id`, `camara_id`, `evento_id`) |
| `GET` | `/api/alerts/{id}` | Obtener alerta |
| `POST` | `/api/alerts` | Crear alerta |
| `PATCH` | `/api/alerts/{id}` | Actualizar alerta — si estado = `resuelta`, asigna `resolved_at` automáticamente |
| `DELETE` | `/api/alerts/{id}` | Borrado lógico (estado → descartada) |

### Ejemplo POST /api/events

```json
{
  "tipo": "camara_offline",
  "severidad": "media",
  "estado": "abierto",
  "comentario": "Evento registrado manualmente para prueba",
  "camara_id": 1
}
```

### Ejemplo POST /api/alerts

```json
{
  "titulo": "Cámara sin conexión",
  "descripcion": "La cámara de entrada no responde",
  "tipo": "camara_offline",
  "severidad": "media",
  "estado": "abierta",
  "camara_id": 1,
  "tienda_id": 1
}
```

---

### password_hash

No se acepta ni se expone desde el cliente. El servicio asigna internamente `$pending$auth-not-configured` hasta que se implemente la fase de autenticación real.

---

### Ejemplo POST /api/stores

```json
{
  "nombre": "Tienda Central Lima",
  "direccion": "Av. Javier Prado 1234",
  "ruc": "20123456789",
  "estado": "activa"
}
```

### Ejemplo POST /api/cameras

```json
{
  "nombre": "Cámara Entrada",
  "host": "192.168.1.100",
  "puerto": 8080,
  "tienda_id": 1,
  "ubicacion": "Puerta principal"
}
```

### Endpoints anteriores (siguen funcionando)

- `GET /api/cameras/test-ip-webcam`
- `GET /api/cameras/test-ip-webcam/snapshot`

### Probar en Swagger

```
http://localhost:8000/api/docs
```

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
  "detail": "Database connection is not available"
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
