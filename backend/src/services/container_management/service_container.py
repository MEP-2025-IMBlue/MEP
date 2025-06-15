import logging
import docker
from docker.errors import DockerException, NotFound, ImageNotFound
from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.utils.metrics import CONTAINER_CPU_USAGE, CONTAINER_MEMORY_USAGE
from src.api.py_models.py_models import ContainerResponse
from src.db.crud import crud_kiImage
from src.utils.auth import User
from src.utils.event_logger import log_event
from src.db.db_models.db_models import KIImage

logger = logging.getLogger(__name__)


class ContainerService:
    def __init__(self):
        self.client = docker.from_env()

    def start_user_container(self, db: Session, current_user: User, image_id: int) -> ContainerResponse:
        """
        Startet einen benutzerspezifischen Container. Existiert er bereits, wird er gestartet,
        andernfalls neu erstellt. Nur der Besitzer oder Admin darf diesen starten.
        """
        try:
            ki_image = crud_kiImage.get_ki_image_by_id(db, image_id)
            if not ki_image:
                log_event("CONTAINER", "image_not_found_db", f"Image ID {image_id} nicht gefunden", "ERROR", user_id=current_user.id)
                raise HTTPException(status_code=404, detail="Image in der Datenbank nicht gefunden.")

            if current_user.role != "admin" and ki_image.image_provider_id != current_user.id:
                log_event("CONTAINER", "unauthorized_access", f"User {current_user.id} hat keinen Zugriff", "WARNING", user_id=current_user.id, image_id=image_id)
                raise HTTPException(status_code=403, detail="Keine Berechtigung für dieses Image.")

            image_reference = f"{ki_image.image_name}:{ki_image.image_tag}"
            base_name = ki_image.image_name.replace("/", "_")
            container_name = f"user_{current_user.id}_{base_name}_{ki_image.image_tag}"

            try:
                container = self.client.containers.get(container_name)
                if container.status != "running":
                    container.start()
                    container.reload()
                    log_event("CONTAINER", "start_existing", f"Container gestartet: {container_name}", "INFO", user_id=current_user.id)
                else:
                    log_event("CONTAINER", "already_running", f"Container läuft bereits: {container_name}", "INFO", user_id=current_user.id)
            except NotFound:
                container = self.client.containers.run(
                    image=image_reference,
                    name=container_name,
                    command="tail -f /dev/null",
                    detach=True
                )
                container.reload()
                log_event("CONTAINER", "create_and_start", f"Neuer Container gestartet: {container.name}", "INFO", user_id=current_user.id)

            return ContainerResponse(container_id=container.id, name=container.name, status=container.status)

        except ImageNotFound:
            log_event("CONTAINER", "image_not_found", f"Image {image_reference} nicht gefunden", "ERROR", user_id=current_user.id)
            raise HTTPException(status_code=404, detail=f"Image {image_reference} nicht gefunden.")
        except DockerException as e:
            log_event("CONTAINER", "docker_exception", str(e), "ERROR", user_id=current_user.id)
            raise HTTPException(status_code=500, detail="Docker-Fehler.")
        except Exception as e:
            log_event("CONTAINER", "unexpected_exception", str(e), "ERROR", user_id=current_user.id)
            raise HTTPException(status_code=500, detail="Unbekannter Fehler.")

    def get_container_resource_usage(self, container_id: str, current_user: User, db: Session) -> dict:
        """
        Gibt die aktuelle CPU- und RAM-Auslastung eines Containers zurück.
        Nur für Admins oder Besitzer des Containers zugänglich.
        """
        try:
            container = self.client.containers.get(container_id)
            meta = self.get_container_metadata(db, current_user, container_id)

            if current_user.role != "admin" and meta["image_provider_id"] != current_user.id:
                log_event("CONTAINER", "unauthorized_resource_check", "Unberechtigter Ressourcenzugriff", "WARNING", user_id=current_user.id, container_id=container_id)
                raise HTTPException(status_code=403, detail="Keine Berechtigung für diesen Container.")

            stats = container.stats(stream=False)
            cpu_percent = self.calculate_cpu_percent(stats)
            mem_usage = stats["memory_stats"].get("usage", 0)
            mem_limit = stats["memory_stats"].get("limit", 1)
            mem_percent = (mem_usage / mem_limit) * 100 if mem_limit else 0

            CONTAINER_CPU_USAGE.labels(container_id=container_id).set(cpu_percent)
            CONTAINER_MEMORY_USAGE.labels(container_id=container_id).set(mem_usage)

            log_event("CONTAINER", "get_container_resource_usage", f"CPU: {cpu_percent:.2f}%, RAM: {mem_percent:.2f}%", "INFO", user_id=current_user.id, container_id=container_id)
            return {
                "container_id": container_id,
                "cpu_percent": round(cpu_percent, 2),
                "mem_percent": round(mem_percent, 2)
            }

        except NotFound:
            raise HTTPException(status_code=404, detail="Container nicht gefunden.")
        except Exception as e:
            log_event("CONTAINER", "resource_usage_error", str(e), "ERROR", user_id=current_user.id, container_id=container_id)
            raise HTTPException(status_code=500, detail="Fehler beim Abrufen der Ressourcen.")

    def get_container_metadata(self, db: Session, current_user: User, container_id: str) -> dict:
        """
        Extrahiert Metadaten anhand des Containernamens und prüft Berechtigung.
        """
        try:
            container = self.client.containers.get(container_id)
            container_name = container.name
            parts = container_name.split("_")
            if len(parts) < 4 or parts[0] != "user":
                raise HTTPException(status_code=400, detail="Ungültiges Container-Namensformat.")

            user_id = parts[1]
            image_tag = parts[-1]
            image_name = "_".join(parts[2:-1]).replace("_", "/")

            ki_image = crud_kiImage.get_ki_image_by_name_and_tag(db, image_name, image_tag)
            if not ki_image:
                raise HTTPException(status_code=404, detail="Kein passendes KI-Image in der Datenbank gefunden.")

            if current_user.role != "admin" and ki_image.image_provider_id != current_user.id:
                log_event("CONTAINER", "unauthorized_metadata_access", "Unberechtigter Zugriff auf Container-Metadaten", "WARNING", user_id=current_user.id, container_id=container_id)
                raise HTTPException(status_code=403, detail="Keine Berechtigung für diesen Container.")

            return {
                "container_id": container_id,
                "container_name": container_name,
                "image_name": image_name,
                "image_tag": image_tag,
                "image_provider_id": ki_image.image_provider_id,
                "user_id_from_name": user_id,
            }

        except NotFound:
            raise HTTPException(status_code=404, detail="Container nicht gefunden.")
        except Exception as e:
            log_event("CONTAINER", "get_container_metadata_error", str(e), "ERROR", container_id=container_id, user_id=current_user.id)
            raise HTTPException(status_code=500, detail="Fehler beim Abrufen der Container-Metadaten.")

    @staticmethod
    def calculate_cpu_percent(stats: dict) -> float:
        """
        Berechnet die CPU-Auslastung basierend auf Docker-Statistiken.
        """
        try:
            cpu_delta = stats["cpu_stats"]["cpu_usage"]["total_usage"] - stats["precpu_stats"]["cpu_usage"]["total_usage"]
            system_delta = stats["cpu_stats"].get("system_cpu_usage", 0) - stats["precpu_stats"].get("system_cpu_usage", 0)
            if system_delta > 0.0 and cpu_delta > 0.0:
                cpu_count = len(stats["cpu_stats"]["cpu_usage"].get("percpu_usage", [])) or 1
                return (cpu_delta / system_delta) * cpu_count * 100.0
        except Exception as e:
            logger.debug(f"Fehler bei CPU-Berechnung: {e}")
        return 0.0

    def list_containers(self, db: Session, current_user: User):
        """
        Gibt alle Container eines Benutzers oder alle (für Admins) zurück.
        """
        try:
            if current_user.role == "admin":
                images = crud_kiImage.get_all_ki_images(db)
            else:
                images = db.query(KIImage).filter(KIImage.image_provider_id == current_user.id).all()

            return [
                {
                    "container_name": f"user_{img.image_provider_id}_{img.image_name.replace('/', '_')}_{img.image_tag}",
                    "image_id": img.image_id,
                    "image_name": img.image_name,
                    "image_tag": img.image_tag,
                    "image_description": img.image_description,
                    "image_provider_id": img.image_provider_id,
                    "image_created_at": img.image_created_at.isoformat()
                }
                for img in images
            ]
        except Exception as e:
            log_event("CONTAINER", "list_containers_error", str(e), "ERROR", user_id=current_user.id)
            raise HTTPException(status_code=500, detail="Fehler beim Abrufen der Container-Liste.")

    def stop_container(self, container_id: str, current_user: User, db: Session) -> dict:
        """
        Stoppt einen Container bei gültiger Berechtigung.
        """
        try:
            container = self.client.containers.get(container_id)
            meta = self.get_container_metadata(db, current_user, container_id)

            if current_user.role != "admin" and meta["image_provider_id"] != current_user.id:
                log_event("CONTAINER", "unauthorized_stop", "Unberechtigter Stopp-Versuch", "WARNING", user_id=current_user.id, container_id=container_id)
                raise HTTPException(status_code=403, detail="Keine Berechtigung für diesen Container.")

            container.stop()
            log_event("CONTAINER", "stopped", "Container gestoppt", "INFO", user_id=current_user.id, container_id=container_id)
            return {"container_id": container_id, "name": container.name, "status": "stopped"}

        except NotFound:
            raise HTTPException(status_code=404, detail="Container nicht gefunden.")
        except Exception as e:
            log_event("CONTAINER", "stop_error", str(e), "ERROR", user_id=current_user.id, container_id=container_id)
            raise HTTPException(status_code=500, detail="Fehler beim Stoppen des Containers.")

    def remove_container(self, container_id: str, current_user: User, db: Session) -> dict:
        """
        Entfernt einen Container bei gültiger Berechtigung.
        """
        try:
            container = self.client.containers.get(container_id)
            meta = self.get_container_metadata(db, current_user, container_id)

            if current_user.role != "admin" and meta["image_provider_id"] != current_user.id:
                log_event("CONTAINER", "unauthorized_remove", "Unberechtigter Löschversuch", "WARNING", user_id=current_user.id, container_id=container_id)
                raise HTTPException(status_code=403, detail="Keine Berechtigung für diesen Container.")

            container.remove(force=True)
            log_event("CONTAINER", "removed", "Container gelöscht", "INFO", user_id=current_user.id, container_id=container_id)
            return {"container_id": container_id, "name": container.name, "status": "removed"}

        except NotFound:
            raise HTTPException(status_code=404, detail="Container nicht gefunden.")
        except Exception as e:
            log_event("CONTAINER", "remove_error", str(e), "ERROR", user_id=current_user.id, container_id=container_id)
            raise HTTPException(status_code=500, detail="Fehler beim Löschen des Containers.")

    def get_container_logs(
        self,
        container_id_or_name: str,
        tail: int = 100,
        stdout: bool = True,
        stderr: bool = True,
        timestamps: bool = True
    ) -> list[str]:
        """
        Gibt die letzten Logzeilen eines Containers zurück (stdout/stderr).
        """
        try:
            container = self.client.containers.get(container_id_or_name)
        except NotFound:
            raise HTTPException(status_code=404, detail="Container nicht gefunden.")

        try:
            logs = container.logs(
                stdout=stdout,
                stderr=stderr,
                tail=tail,
                timestamps=timestamps
            )
            return logs.decode("utf-8").splitlines()
        except DockerException as e:
            raise HTTPException(status_code=500, detail=f"Fehler beim Abrufen der Logs: {str(e)}")
