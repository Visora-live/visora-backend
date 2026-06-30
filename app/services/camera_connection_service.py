import httpx

from app.adapters.ip_webcam_adapter import IPWebcamAdapter


class CameraConnectionService:

    def get_camera_connection(self, camera) -> dict:
        adapter = IPWebcamAdapter(host=camera.direccion_ip, port=camera.puerto)
        snapshot_url = adapter.get_snapshot_url()
        stream_url = adapter.get_mjpeg_url()
        base = {
            "camera_id": camera.id,
            "nombre_cam": camera.nombre_cam,
            "direccion_ip": camera.direccion_ip,
            "puerto": camera.puerto,
            "snapshot_url": snapshot_url,
            "stream_url": stream_url,
        }
        try:
            resp = httpx.get(snapshot_url, timeout=5.0)
            reachable = resp.status_code == 200
            return {
                **base,
                "reachable": reachable,
                "status_code": resp.status_code,
                "content_type": resp.headers.get("content-type"),
                "message": (
                    "Cámara alcanzable"
                    if reachable
                    else f"Cámara respondió con código {resp.status_code}"
                ),
            }
        except httpx.TimeoutException:
            return {**base, "reachable": False, "status_code": None, "content_type": None,
                    "message": "Tiempo de espera agotado"}
        except httpx.ConnectError:
            return {**base, "reachable": False, "status_code": None, "content_type": None,
                    "message": "No se pudo conectar a la cámara"}
        except Exception:
            return {**base, "reachable": False, "status_code": None, "content_type": None,
                    "message": "Error al probar conexión con la cámara"}
