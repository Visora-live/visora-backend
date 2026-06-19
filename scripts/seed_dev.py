"""Seed development data for VISORA v20B schema."""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datetime import date, datetime, timezone

from app.db.session import SessionLocal
from app.core.security import hash_password
from app.models.role import Rol
from app.models.store import Tienda
from app.models.user import Usuario
from app.models.camera import Camara
from app.models.store_user import TiendaUsuario
from app.models.event import Evento
from app.models.event_image import EventoImagen
from app.models.identification import Identificacion
from app.models.alert import Alerta


def seed():
    db = SessionLocal()
    try:
        # ── Roles ────────────────────────────────────────────────────────────
        rol_admin = Rol(tipo="admin")
        rol_prop = Rol(tipo="propietario")
        db.add_all([rol_admin, rol_prop])
        db.flush()

        # ── Usuarios ─────────────────────────────────────────────────────────
        admin = Usuario(
            username="admin",
            email="admin@visora.pe",
            contrasena=hash_password("Admin1234!"),
            estado_acceso=True,
            rol_id=rol_admin.id,
        )
        propietario = Usuario(
            username="propietario_demo",
            email="propietario@visora.pe",
            contrasena=hash_password("Propietario1234!"),
            estado_acceso=True,
            rol_id=rol_prop.id,
        )
        db.add_all([admin, propietario])
        db.flush()

        # ── Tiendas ──────────────────────────────────────────────────────────
        tienda1 = Tienda(
            nombre="Tienda Central",
            direccion="Av. Lima 123, Miraflores",
            ruc="20123456789",
            estado_tienda=True,
            licencia_inicio=date(2025, 1, 1),
            licencia_fin=date(2026, 12, 31),
        )
        tienda2 = Tienda(
            nombre="Tienda Norte",
            direccion="Jr. Tacna 456, Los Olivos",
            ruc="20987654321",
            estado_tienda=True,
            licencia_inicio=date(2025, 3, 1),
            licencia_fin=date(2026, 12, 31),
        )
        db.add_all([tienda1, tienda2])
        db.flush()

        # ── TiendaUsuario ─────────────────────────────────────────────────────
        db.add(TiendaUsuario(tienda_id=tienda1.id, usuario_id=propietario.id))
        db.add(TiendaUsuario(tienda_id=tienda2.id, usuario_id=propietario.id))
        db.flush()

        # ── Cámaras ───────────────────────────────────────────────────────────
        cam1 = Camara(
            nombre_cam="Cam-Entrada-Central",
            direccion_ip="192.168.1.101",
            puerto=8080,
            ubicacion_camara="Entrada principal",
            estado=True,
            tienda_id=tienda1.id,
        )
        cam2 = Camara(
            nombre_cam="Cam-Caja-Norte",
            direccion_ip="192.168.2.201",
            puerto=8080,
            ubicacion_camara="Zona de caja",
            estado=False,
            tienda_id=tienda2.id,
        )
        db.add_all([cam1, cam2])
        db.flush()

        # ── Evento ────────────────────────────────────────────────────────────
        evento = Evento(
            estado="abierto",
            fecha_hora=datetime.now(timezone.utc),
            comentario="Detección de persona no autorizada",
            camara_id=cam1.id,
            tipo="intrusion",
            severidad="alta",
        )
        db.add(evento)
        db.flush()

        # ── EventoImagen ──────────────────────────────────────────────────────
        ev_img = EventoImagen(
            storage_ref="event_images/demo_frame_001.jpg",
            evento_id=evento.id,
            es_frame_representativo=True,
            confianza_arma=0.1200,
            confianza_rostro=0.8750,
            storage_provider="local",
            filename="demo_frame_001.jpg",
            content_type="image/jpeg",
        )
        db.add(ev_img)
        db.flush()

        # ── Identificacion ────────────────────────────────────────────────────
        ident = Identificacion(
            evento_imagen_id=ev_img.id,
            nombre="Juan",
            apellido="Pérez",
            dni="12345678",
            confianza_identificacion=0.8750,
            fuente="manual",
        )
        db.add(ident)
        db.flush()

        # ── Alerta ────────────────────────────────────────────────────────────
        alerta = Alerta(
            titulo="Intrusion detectada - Tienda Central",
            descripcion="Persona no autorizada detectada en entrada principal",
            tipo="intrusion",
            severidad="alta",
            estado="abierta",
            leida=False,
            evento_id=evento.id,
            camara_id=cam1.id,
            tienda_id=tienda1.id,
        )
        db.add(alerta)
        db.commit()

        print("✅ Seed completado exitosamente")
        print(f"   Roles: admin (id={rol_admin.id}), propietario (id={rol_prop.id})")
        print(f"   Usuarios: admin (id={admin.id}), propietario_demo (id={propietario.id})")
        print(f"   Tiendas: {tienda1.nombre} (id={tienda1.id}), {tienda2.nombre} (id={tienda2.id})")
        print(f"   Cámaras: {cam1.nombre_cam} (id={cam1.id}), {cam2.nombre_cam} (id={cam2.id})")
        print(f"   Evento id={evento.id}, EventoImagen id={ev_img.id}")
        print(f"   Identificacion id={ident.id}, Alerta id={alerta.id}")

    except Exception as e:
        db.rollback()
        print(f"❌ Seed falló: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
