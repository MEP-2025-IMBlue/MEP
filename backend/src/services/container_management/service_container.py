# Externe Libraries
import logging
import docker
import datetime
from docker.errors import DockerException, NotFound, ImageNotFound

# API Models (Pydantic)
from src.api.py_models.py_models import ContainerResponse

# Datenbank (SQLAlchemy)
from src.db.crud import crud_kiImage
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

class ContainerService:
    def __init__(self):
        self.client = docker.from_env()

    def start_user_container(self, db: Session, user_id: int, image_id: int) -> ContainerResponse:
        """Startet einen pro-User-Container; startet existierenden oder erstellt neuen."""
        try:
            ki_image = crud_kiImage.get_ki_image_by_id(db, image_id)
            image_reference = f"{ki_image.image_name}:{ki_image.image_tag}"
            base_name = ki_image.image_name.replace("/", "_")
            container_name = f"user_{user_id}_{base_name}_{ki_image.image_tag}"

            logger.info(f"Versuche Container zu starten: {container_name}")
    
            try:
                container = self.client.containers.get(container_name)
                if container.status != "running":
                    container.start()
                    container.reload()
                    logger.info(f"[Konfiguration] Vorhandener Container '{container_name}' wurde gestartet.")
                else:
                     logger.info(f"[Konfiguration] Container '{container_name}' ist bereits aktiv.")
            except NotFound:
                logger.info(f"[Konfiguration] Neuer Container '{container_name}' wurde erstellt und gestartet.")
                container = self.client.containers.run(
                    image=image_reference,
                    name=container_name,
                    command="tail -f /dev/null",
                    detach=True
                )
                container.reload()
                logger.info(f"[Konfiguration] Neuer Container '{container_name}' wurde erstellt und gestartet.")

            return ContainerResponse(
                container_id=container.id,
                name=container.name,
                status=container.status
            )

        except ImageNotFound:
            raise Exception(f"Image {image_reference} nicht im Docker-Daemon gefunden.")
        except DockerException as e:
            raise Exception(f"Containerstart fehlgeschlagen: {str(e)}")

    def stop_container(self, container_id_or_name: str) -> dict:
        try:
            container = self.client.containers.get(container_id_or_name)
            container.stop()
            logger.info(f"[Konfiguration] Container '{container.name}' (ID: {container.id}) wurde gestoppt.")
            return {
                "container_id": container.id,
                "name": container.name,
                "status": "stopped"
            }
        except NotFound:
            raise Exception(f"Container {container_id_or_name} nicht gefunden")
        except DockerException as e:
            raise Exception(f"Fehler beim Stoppen des Containers: {str(e)}")

    def remove_container(self, container_id_or_name: str) -> dict:
        try:
            container = self.client.containers.get(container_id_or_name)
            container.remove(force=True)
            logger.info(f"[Konfiguration] Container '{container.name}' (ID: {container.id}) wurde entfernt.")
            return {
                "container_id": container.id,
                "name": container.name,
                "status": "removed"
            }
        except NotFound:
            raise Exception(f"Container {container_id_or_name} nicht gefunden")
        except DockerException as e:
            raise Exception(f"Fehler beim Löschen des Containers: {str(e)}")

    def get_container_status_and_health(self, container_id_or_name: str) -> dict:
        try:
            container = self.client.containers.get(container_id_or_name)
            status = container.status
            health = container.attrs.get("State", {}).get("Health", {}).get("Status", "nicht definiert")
            return {
                "container_id": container.id,
                "name": container.name,
                "status": status,
                "health": health
            }
        except NotFound:
            raise Exception(f"Container {container_id_or_name} nicht gefunden")
        except DockerException as e:
            raise Exception(f"Fehler beim Abrufen des Status: {str(e)}")

    def list_containers(self, user_id: int = None) -> list:
        try:
            containers = self.client.containers.list(all=True)
            result = []
            for c in containers:
                health = c.attrs.get("State", {}).get("Health", {}).get("Status", "nicht definiert")
                result.append({
                    "container_id": c.id,
                    "name": c.name,
                    "status": c.status,
                    "health": health
                })
            return result
        except DockerException as e:
            raise Exception(f"Fehler beim Auflisten der Container: {str(e)}")

    def get_container_logs(       
        self,
        container_id_or_name: str,
        tail: int = 100,
        stdout: bool = True,
        stderr: bool = True,
        timestamps: bool = True
    ) -> str:
        try:
            container = self.client.containers.get(container_id_or_name)
            log_bytes = container.logs(
                tail=tail,
                stdout=stdout,
                stderr=stderr,
                timestamps=timestamps
            )
            if not log_bytes:
                return "Keine Logs verfügbar."
            return log_bytes.decode("utf-8")
        except NotFound:
            logger.warning(f"[ContainerLogs] Container nicht gefunden: {container_id_or_name}")
            raise Exception(f"Container '{container_id_or_name}' nicht gefunden.")
        except DockerException as e:
            logger.error(f"[ContainerLogs] Docker API-Fehler: {str(e)}")
            raise Exception(f"Fehler beim Abrufen der Logs: {str(e)}")
        except Exception as e:
            logger.exception(f"[ContainerLogs] Unerwarteter Fehler bei Container: {container_id_or_name}")
            raise Exception(f"Unbekannter Fehler: {str(e)}")

    def list_running_containers(self, user_id: int = None) -> list:
        try:
            containers = self.client.containers.list(filters={"status": "running"})
            result = []
            for c in containers:
                if user_id and not c.name.startswith(f"user_{user_id}_"):
                    continue
                result.append(c.name)
            return result
        except DockerException as e:
            raise Exception(f"Fehler beim Auflisten laufender Container: {str(e)}")
        
    def get_container_resource_usage(self, container_id_or_name: str) -> dict:
        """
        Retrieves real-time CPU and memory usage of a container.

        Gibt die CPU- und Speicherauslastung eines Containers zurück.
        """
        try:
            container = self.client.containers.get(container_id_or_name)
            stats = container.stats(stream=False)

            cpu_delta = stats["cpu_stats"]["cpu_usage"]["total_usage"] - stats["precpu_stats"]["cpu_usage"]["total_usage"]
            system_delta = stats["cpu_stats"]["system_cpu_usage"] - stats["precpu_stats"]["system_cpu_usage"]
            cpu_usage_percent = 0.0
            if system_delta > 0.0:
                cpu_usage_percent = (cpu_delta / system_delta) * len(stats["cpu_stats"]["cpu_usage"]["percpu_usage"]) * 100.0

            memory_usage = stats["memory_stats"].get("usage", 0)
            memory_limit = stats["memory_stats"].get("limit", 1)
            memory_percent = (memory_usage / memory_limit) * 100.0

            return {
                "container_id": container.id,
                "name": container.name,
                "cpu_usage_percent": round(cpu_usage_percent, 2),
                "memory_usage_mb": round(memory_usage / (1024 ** 2), 2),
                "memory_limit_mb": round(memory_limit / (1024 ** 2), 2),
                "memory_usage_percent": round(memory_percent, 2),
                "timestamp": datetime.datetime.utcnow().isoformat()
            }

        except Exception as e:
            log_event("ERROR", "ContainerService", f"Fehler beim Ressourcenabruf für Container {container_id_or_name}: {str(e)}")
            raise Exception(f"Failed to retrieve resource usage for container {container_id_or_name}.")