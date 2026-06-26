# VISORA — Backend

API REST para el sistema de monitoreo de seguridad VISORA. Gestiona cámaras, eventos, alertas, tiendas y usuarios con autenticación JWT y control de acceso por roles.

## Stack

- **Python 3.11+** / **FastAPI**
- **SQLAlchemy** + **PostgreSQL**
- **JWT** (python-jose) + **bcrypt**
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
DATABASE_URL=postgresql+psycopg://usuario:contraseña@localhost:5432/visora_db
SECRET_KEY=tu_clave_secreta_jwt
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

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
├── api/routes/       # Endpoints: auth, cameras, events, alerts, stores, users
├── core/             # Configuración, seguridad, dependencias JWT
├── models/           # Modelos SQLAlchemy
├── schemas/          # Esquemas Pydantic (validación de input y output)
└── services/         # Lógica de negocio
```

## Endpoints principales

| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/api/auth/login` | Autenticación, devuelve JWT |
| GET | `/api/auth/me` | Usuario autenticado actual |
| GET | `/api/stores` | Tiendas (admin) |
| GET | `/api/cameras` | Cámaras filtradas por tienda |
| GET | `/api/events` | Eventos por tienda/cámara |
| GET | `/api/alerts` | Alertas por tienda/cámara |
| GET | `/api/users` | Usuarios (admin) |

Documentación interactiva: `http://localhost:8000/docs`

## Roles

| Rol | Acceso |
|-----|--------|
| `admin` | Total: tiendas, usuarios, cámaras, eventos, alertas |
| `propietario` | Solo sus tiendas asignadas y sus recursos |

## Despliegue con Docker

```bash
docker compose up --build
```
