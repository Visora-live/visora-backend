# VISORA — Backend

API REST del sistema de monitoreo de seguridad VISORA. Gestiona cámaras, eventos, alertas, tiendas, usuarios e identificaciones con autenticación JWT por cookie httpOnly y control de acceso por roles.

## Stack

- **Python 3.11+** / **FastAPI**
- **SQLAlchemy** + **PostgreSQL**
- **JWT** (python-jose) + **bcrypt** — entregado como cookie httpOnly en navegador; Bearer header para workers Python
- **Pydantic v2** para validación de esquemas
- **Docker** + **Docker Compose** para despliegue

## Requisitos previos

- Python 3.11+
- PostgreSQL corriendo localmente o en contenedor

## Instalación local

```bash
git clone https://github.com/Visora-live/visora-backend.git
cd visora-backend

python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux/Mac

pip install -r requirements.txt

cp .env.example .env
# Editar .env con tus valores

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Variables de entorno

```env
# Base
ENVIRONMENT=local                          # local | production
DATABASE_URL=postgresql+psycopg://user:pass@localhost:5432/visora_db
SECRET_KEY=clave-secreta-jwt-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Cookie auth
COOKIE_SECURE=false                        # true en producción (requiere HTTPS)
COOKIE_DOMAIN=                             # .tudominio.com para AWS con subdominios

# CORS
CORS_ORIGINS=["http://localhost:4200"]

# Detección (workers de IA)
VISORA_USER=admin
VISORA_PASS=tu_password_seguro
DETECTION_PREWARM_CAMERAS=               # IDs separados por coma, ej: "1,2"
```

> En producción `COOKIE_SECURE=true` y `COOKIE_DOMAIN=.tudominio.com` son obligatorios.

## Base de datos

```sql
CREATE USER visora_user WITH PASSWORD 'visora_password';
CREATE DATABASE visora_db OWNER visora_user;
GRANT ALL PRIVILEGES ON DATABASE visora_db TO visora_user;
```

```bash
alembic upgrade head
```

## Estructura

```
app/
├── api/routes/       # Endpoints: auth, cameras, events, alerts, stores, users, identifications
├── core/             # Config, dependencias JWT, helpers de autorización
├── models/           # Modelos SQLAlchemy
├── schemas/          # Esquemas Pydantic (validación de input/output)
├── services/         # Lógica de negocio + detection_manager (workers IA)
└── db/               # Sesión de base de datos
```

## Endpoints principales

| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/api/auth/login` | Login — setea cookie httpOnly + devuelve token para workers |
| POST | `/api/auth/logout` | Logout — borra la cookie httpOnly |
| GET | `/api/auth/me` | Usuario autenticado actual |
| GET | `/api/stores` | Tiendas (admin) |
| GET | `/api/cameras` | Cámaras filtradas por tienda |
| GET | `/api/cameras/{id}/snapshot` | Snapshot del stream (autenticado + ownership) |
| GET | `/api/events` | Eventos por tienda/cámara |
| GET | `/api/alerts` | Alertas por tienda/cámara |
| GET | `/api/identifications` | Identificaciones (requiere evento_id para no-admins) |
| GET | `/api/users` | Usuarios (admin) |
| GET | `/api/algorithm/report` | Reporte de rendimiento de detección (admin) |

Documentación interactiva (solo en local): `http://localhost:8000/api/docs`

## Roles y acceso

| Rol | Acceso |
|-----|--------|
| `admin` | Total: tiendas, usuarios, cámaras, eventos, alertas, identificaciones |
| `propietario` | Solo sus tiendas asignadas y sus recursos |

## Autenticación

El backend soporta dos modos en paralelo:

- **Navegador**: cookie `visora_token` (httpOnly, SameSite=Lax). JavaScript nunca toca el JWT.
- **Workers Python**: `Authorization: Bearer <token>` — los scripts de detección usan este modo.

## Despliegue con Docker

```bash
docker compose up --build
```
