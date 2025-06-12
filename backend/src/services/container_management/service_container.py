import logging
import docker
from docker.errors import DockerException, NotFound, ImageNotFound
from fastapi import HTTPException
from src.utils.metrics import CONTAINER_CPU_USAGE, CONTAINER_MEMORY_USAGE
from src.api.py_models.py_models import ContainerResponse
from src.db.crud import crud_kiImage
from sqlalchemy.orm import Session
from src.utils.auth import User
from src.utils.event_logger import log_event

logger = logging.getLogger(__name__)


class ContainerService:
    def __init__(self):
        self.client = docker.from_env()

    # Startet einen Benutzer-Container (nur für berechtigte Benutzer oder Admins)
    def start_user_container(self, db: Session, current_user: User, image_id: int) -> ContainerResponse:
        """
        Startet einen Benutzer-spezifischen Container. Falls er bereits existiert, wird er gestartet,
        andernfalls wird ein neuer erstellt. Nur der Besitzer oder ein Admin darf diesen starten.
        """
        try:
            ki_image = crud_kiImage.get_ki_image_by_id(db, image_id)
            if current_user.role != "admin" and ki_image.image_provider_id != current_user.id:
                raise Exception("Keine Berechtigung für dieses Image.")

            image_reference = f"{ki_image.image_name}:{ki_image.image_tag}"
            base_name = ki_image.image_name.replace("/", "_")
            container_name = f"user_{current_user.id}_{base_name}_{ki_image.image_tag}"

            logger.info(f"Versuche Container zu starten: {container_name}")

            try:
                # Container bereits vorhanden
                container = self.client.containers.get(container_name)
                if container.status != "running":
                    container.start()
                    container.reload()
                    log_event("CONTAINER", "start_existing", f"Vorhandener Container gestartet: {container_name}", "INFO", user_id=current_user.id, container_name=container_name, image_id=image_id)
                else:
                    log_event("CONTAINER", "already_running", f"Container bereits läuft: {container_name}", "INFO", user_id=current_user.id, container_name=container_name, image_id=image_id)
            except NotFound:
                # Neuer Container wird erstellt
                log_event("CONTAINER", "create_container", f"Erstelle neuen Container: {container_name}", "INFO", user_id=current_user.id, container_name=container_name, image_id=image_id)
                container = self.client.containers.run(
                    image=image_reference,
                    name=container_name,
                    command="tail -f /dev/null",
                    detach=True
                )
                container.reload()
                log_event("CONTAINER", "create_and_start", f"Neuer Container erstellt & gestartet: {container_name}", "INFO", user_id=current_user.id, container_name=container_name, image_id=image_id, container_id=container.id)

            log_event("CONTAINER", "start_user_container_success", f"Container gestartet: {container.name} ({container.id})", "INFO", user_id=current_user.id, container_name=container.name, image_id=image_id, container_id=container.id)
            return ContainerResponse(container_id=container.id, name=container.name, status=container.status)
        except ImageNotFound:
            log_event("CONTAINER", "image_not_found", f"Image nicht gefunden: {image_reference}", "ERROR", user_id=current_user.id, image_reference=image_reference, image_id=image_id)
            raise Exception(f"Image {image_reference} nicht im Docker Daemon gefunden.")
        except DockerException as e:
            log_event("CONTAINER", "docker_exception", f"Fehler beim Container-Start: {str(e)}", "ERROR", user_id=current_user.id, image_id=image_id)
            raise Exception(f"Fehler beim Starten des Containers: {str(e)}")

    # Ermittelt CPU- und RAM-Auslastung für einen Container
    def get_container_resource_usage(self, container_id: str, current_user: User) -> dict:
        """
        Gibt die aktuelle CPU- und RAM-Auslastung eines Containers zurück.
        Nur berechtigte Benutzer dürfen zugreifen. Daten werden zusätzlich an Prometheus übergeben.
        """
        try:
            container = self.client.containers.get(container_id)
            stats = container.stats(stream=False)

            cpu_percent = self.calculate_cpu_percent(stats)
            mem_usage = stats['memory_stats'].get('usage', 0)
            mem_limit = stats['memory_stats'].get('limit', 1)
            mem_percent = (mem_usage / mem_limit) * 100 if mem_limit else 0

            # Werte an Prometheus senden
            CONTAINER_CPU_USAGE.labels(container_id=container_id).set(cpu_percent)
            CONTAINER_MEMORY_USAGE.labels(container_id=container_id).set(mem_usage)

            logger.debug(f"[{current_user.id}] Ressourcenabfrage: CPU {cpu_percent:.2f}%, RAM {mem_percent:.2f}%")
            log_event("CONTAINER", "read_resources", f"Ressourcen von {container_id} gelesen (CPU {cpu_percent:.2f}%, RAM {mem_percent:.2f}%)", "INFO", user_id=current_user.id)

            return {
                "container_id": container_id,
                "cpu_percent": round(cpu_percent, 2),
                "mem_percent": round(mem_percent, 2)
            }

        except docker.errors.NotFound:
            logger.warning(f"[{current_user.id}] Container {container_id} nicht gefunden.")
            log_event("CONTAINER", "error_read_resources", f"Container {container_id} nicht gefunden", "WARNING", user_id=current_user.id)
            raise HTTPException(status_code=404, detail="Container nicht gefunden.")
        except Exception as e:
            logger.error(f"[{current_user.id}] Fehler bei Ressourcenerfassung: {e}")
            log_event("CONTAINER", "error_read_resources", f"Fehler bei Ressourcenerfassung für {container_id}: {e}", "ERROR", user_id=current_user.id)
            raise HTTPException(status_code=500, detail="Ressourcenerfassung fehlgeschlagen.")

    @staticmethod
    def calculate_cpu_percent(stats: dict) -> float:
        """
        Berechnet die CPU-Auslastung basierend auf Docker-Statistiken.
        Falls Daten unvollständig oder undefiniert, wird 0.0 zurückgegeben.
        """
        try:
            cpu_delta = stats["cpu_stats"]["cpu_usage"]["total_usage"] - stats["precpu_stats"]["cpu_usage"]["total_usage"]
            system_delta = stats["cpu_stats"].get("system_cpu_usage", 0) - stats["precpu_stats"].get("system_cpu_usage", 0)
            if system_delta > 0.0 and cpu_delta > 0.0:
                cpu_count = len(stats["cpu_stats"]["cpu_usage"].get("percpu_usage", [])) or 1
                return (cpu_delta / system_delta) * cpu_count * 100.0
        except Exception:
            pass
        return 0.0
