import logging
import docker
from docker.errors import DockerException, NotFound, ImageNotFound
from src.utils.metrics import CONTAINER_CPU_USAGE, CONTAINER_MEMORY_USAGE
from src.api.py_models.py_models import ContainerResponse
from src.db.crud import crud_kiImage
from sqlalchemy.orm import Session
from src.utils.auth import User    # User Pydantic Modell
from src.utils.event_logger import log_event  # Eigenes Logging-Tool

logger = logging.getLogger(__name__)


class ContainerService:
    def __init__(self):
        self.client = docker.from_env()

    # Startet einen User-Container (nur für berechtigte User/Admin)
    def start_user_container(self, db: Session, current_user: User, image_id: int) -> ContainerResponse:
        """
        Startet einen pro-User-Container; startet existierenden oder erstellt neuen.
        Nur der Besitzer/Admin darf starten!
        """
        try:
            # Prüfe, ob der aktuelle User berechtigt ist
            ki_image = crud_kiImage.get_ki_image_by_id(db, image_id)
            if current_user.role != "admin" and ki_image.image_provider_id != current_user.id:
                raise Exception("Keine Berechtigung für dieses Image.")

            image_reference = f"{ki_image.image_name}:{ki_image.image_tag}"
            base_name = ki_image.image_name.replace("/", "_")
            container_name = f"user_{current_user.id}_{base_name}_{ki_image.image_tag}"

            logger.info(f"Trying to start container: {container_name}")

            try:
                container = self.client.containers.get(container_name)
                if container.status != "running":
                    container.start()
                    container.reload()
                    logger.info(f"Started existing container {container_name}")
                    log_event("CONTAINER", "start_existing",
                        f"Vorhandener Container gestartet: {container_name}", "INFO",
                        user_id=current_user.id, container_name=container_name, image_id=image_id
                    )
                else:
                    logger.info(f"Container {container_name} already running")
                    log_event("CONTAINER", "already_running",
                        f"Container bereits läuft: {container_name}", "INFO",
                        user_id=current_user.id, container_name=container_name, image_id=image_id
                    )
            except NotFound:
                logger.info(f"Creating new container {container_name}")
                log_event("CONTAINER", "create_container",
                    f"Erstelle neuen Container: {container_name}", "INFO",
                    user_id=current_user.id, container_name=container_name, image_id=image_id
                )
                container = self.client.containers.run(
                    image=image_reference,
                    name=container_name,
                    command="tail -f /dev/null",
                    detach=True
                )
                container.reload()
                logger.info(f"Started new container {container_name}")
                log_event("CONTAINER", "create_and_start",
                    f"Neuer Container erstellt & gestartet: {container_name}", "INFO",
                    user_id=current_user.id, container_name=container_name, image_id=image_id, container_id=container.id
                )

            log_event("CONTAINER", "start_user_container_success",
                f"Container gestartet: {container.name} ({container.id})", "INFO",
                user_id=current_user.id, container_name=container.name, image_id=image_id, container_id=container.id
            )
            return ContainerResponse(
                container_id=container.id,
                name=container.name,
                status=container.status
            )
        except ImageNotFound:
            log_event("CONTAINER", "image_not_found",
                f"Image nicht gefunden: {image_reference}", "ERROR",
                user_id=current_user.id, image_reference=image_reference, image_id=image_id
            )
            raise Exception(f"Image {image_reference} not found in Docker daemon.")
        except DockerException as e:
            log_event("CONTAINER", "docker_exception",
                f"Fehler beim Container-Start: {str(e)}", "ERROR",
                user_id=current_user.id, image_id=image_id
            )
            raise Exception(f"Failed to start container: {str(e)}")

    # Stoppt einen Container (Owner-Check nach Bedarf)
    def stop_container(self, container_id_or_name: str, current_user: User) -> dict:
        """
        Stoppt einen Container anhand ID oder Name (nur für berechtigte User).
        """
        try:
            log_event("CONTAINER", "stop_container",
                f"Versuche Container zu stoppen: {container_id_or_name}", "DEBUG",
                user_id=current_user.id, container_id=container_id_or_name
            )
            container = self.client.containers.get(container_id_or_name)
            container.stop()
            log_event("CONTAINER", "stop_container_success",
                f"Container {container_id_or_name} erfolgreich gestoppt", "INFO",
                user_id=current_user.id, container_id=container_id_or_name
            )
            return {"container_id": container.id, "name": container.name, "status": "stopped"}
        except NotFound:
            log_event("CONTAINER", "stop_container_not_found",
                f"Container nicht gefunden: {container_id_or_name}", "WARNING",
                user_id=current_user.id, container_id=container_id_or_name
            )
            raise Exception(f"Container {container_id_or_name} not found")
        except DockerException as e:
            log_event("CONTAINER", "stop_container_error",
                f"Fehler beim Stoppen: {str(e)}", "ERROR",
                user_id=current_user.id, container_id=container_id_or_name
            )
            raise Exception(f"Failed to stop container: {str(e)}")

    # Löscht einen Container (Owner-Check nach Bedarf)
    def remove_container(self, container_id_or_name: str, current_user: User) -> dict:
        """
        Löscht einen Container anhand ID oder Name (nur für berechtigte User).
        """
        try:
            log_event("CONTAINER", "remove_container",
                f"Versuche Container zu löschen: {container_id_or_name}", "DEBUG",
                user_id=current_user.id, container_id=container_id_or_name
            )
            container = self.client.containers.get(container_id_or_name)
            container.remove(force=True)
            log_event("CONTAINER", "remove_container_success",
                f"Container {container_id_or_name} erfolgreich gelöscht", "INFO",
                user_id=current_user.id, container_id=container_id_or_name
            )
            return {"container_id": container.id, "name": container.name, "status": "removed"}
        except NotFound:
            log_event("CONTAINER", "remove_container_not_found",
                f"Container nicht gefunden: {container_id_or_name}", "WARNING",
                user_id=current_user.id, container_id=container_id_or_name
            )
            raise Exception(f"Container {container_id_or_name} not found")
        except DockerException as e:
            log_event("CONTAINER", "remove_container_error",
                f"Fehler beim Löschen: {str(e)}", "ERROR",
                user_id=current_user.id, container_id=container_id_or_name
            )
            raise Exception(f"Failed to remove container: {str(e)}")

    # Gibt den Status eines Containers zurück (nur für berechtigte User)
    def get_container_status(self, container_id_or_name: str, current_user: User) -> dict:
        """
        Gibt Status eines Containers zurück (nur für berechtigte User).
        """
        try:
            log_event("CONTAINER", "get_container_status",
                f"Frage Status ab für: {container_id_or_name}", "DEBUG",
                user_id=current_user.id, container_id=container_id_or_name
            )
            container = self.client.containers.get(container_id_or_name)
            result = {
                "container_id": container.id,
                "name": container.name,
                "status": container.status
            }
            log_event("CONTAINER", "get_container_status_success",
                f"Status erfolgreich abgefragt: {container_id_or_name} | Status: {container.status}", "INFO",
                user_id=current_user.id, container_id=container_id_or_name
            )
            return result
        except NotFound:
            log_event("CONTAINER", "get_container_status_not_found",
                f"Container nicht gefunden: {container_id_or_name}", "WARNING",
                user_id=current_user.id, container_id=container_id_or_name
            )
            raise Exception(f"Container {container_id_or_name} not found")
        except DockerException as e:
            log_event("CONTAINER", "get_container_status_error",
                f"Fehler beim Statusabruf: {str(e)}", "ERROR",
                user_id=current_user.id, container_id=container_id_or_name
            )
            raise Exception(f"Failed to get container status: {str(e)}")

    # Listet alle Container (nur eigene, außer Admin)
    def list_containers(self, current_user: User) -> list:
        """
        Listet alle Container, die dem aktuellen User gehören (bzw. alle für Admin).
        """
        try:
            log_event("CONTAINER", "list_containers",
                "Liste alle Container (Owner-Filter!)", "DEBUG",
                user_id=current_user.id
            )
            containers = self.client.containers.list(all=True)
            result = []
            for c in containers:
                if current_user.role != "admin":
                    if not c.name.startswith(f"user_{current_user.id}_"):
                        continue
                result.append({
                    "container_id": c.id,
                    "name": c.name,
                    "status": c.status
                })
            log_event("CONTAINER", "list_containers_success",
                f"Anzahl gefundener Container: {len(result)}", "INFO",
                user_id=current_user.id
            )
            return result
        except DockerException as e:
            log_event("CONTAINER", "list_containers_error",
                f"Fehler bei der Container-Auflistung: {str(e)}", "ERROR",
                user_id=current_user.id
            )
            raise Exception(f"Failed to list containers: {str(e)}")

    # Nur laufende Container abrufen (nur eigene, außer Admin)
    def list_running_containers(self, current_user: User) -> list:
        """
        Listet alle laufenden Container des Users (Admin sieht alles).
        """
        try:
            log_event("DEBUG", "list_running_containers", "Suche laufende Container", level="DEBUG", user_id=current_user.id)
            containers = self.client.containers.list()
            names = []
            for container in containers:
                if current_user.role != "admin":
                    if not container.name.startswith(f"user_{current_user.id}_"):
                        continue
                names.append(container.name)
            log_event("CONTAINER", "list_running_containers",
                f"{len(names)} laufende Container gefunden: {names}", level="INFO", user_id=current_user.id)
            return names
        except Exception as e:
            log_event("ERROR", "list_running_containers",
                f"Fehler beim Abruf: {str(e)}", level="ERROR", user_id=current_user.id)
            raise

    # Container-Logs abrufen (nur für berechtigte User)
    def get_container_logs(self, container_id_or_name, current_user: User, tail=100, stdout=True, stderr=True, timestamps=True):
        """
        Gibt die Logs eines Containers zurück (nur für berechtigte User).
        """
        try:
            log_event("DEBUG", "get_container_logs",
                f"Rufe Logs ab für Container: {container_id_or_name} | tail={tail}, stdout={stdout}, stderr={stderr}, timestamps={timestamps}",
                level="DEBUG", user_id=current_user.id
            )
            container = self.client.containers.get(container_id_or_name)
            if current_user.role != "admin" and not container.name.startswith(f"user_{current_user.id}_"):
                raise Exception("Keine Berechtigung für diese Logs.")
            logs = container.logs(tail=tail, stdout=stdout, stderr=stderr, timestamps=timestamps).decode("utf-8")
            log_event("CONTAINER", "get_container_logs",
                f"Logs erfolgreich abgerufen für: {container_id_or_name}", level="INFO", user_id=current_user.id
            )
            return logs
        except Exception as e:
            log_event("ERROR", "get_container_logs",
                f"Fehler beim Log-Abruf ({container_id_or_name}): {str(e)}", level="ERROR", user_id=current_user.id)
            raise

    # Status und Health abrufen (nur für berechtigte User)
    def get_container_status_and_health(self, container_id_or_name, current_user: User):
        """
        Gibt Status und Health eines Containers zurück (nur für berechtigte User).
        """
        try:
            log_event("DEBUG", "get_container_status_and_health",
                f"Rufe Status & Health ab: {container_id_or_name}", level="DEBUG", user_id=current_user.id
            )
            container = self.client.containers.get(container_id_or_name)
            if current_user.role != "admin" and not container.name.startswith(f"user_{current_user.id}_"):
                raise Exception("Keine Berechtigung für diesen Container.")
            status = container.status
            health = container.attrs.get("State", {}).get("Health", {}).get("Status", "nicht definiert")
            log_event("CONTAINER", "get_container_status_and_health",
                f"Container: {container_id_or_name} | Status: {status}, Health: {health}",
                level="INFO", user_id=current_user.id
            )
            return {"status": status, "health": health}
        except Exception as e:
            log_event("ERROR", "get_container_status_and_health",
                f"Fehler beim Abruf: {str(e)}", level="ERROR", user_id=current_user.id)
            raise

    # Ressourcennutzung eines Containers abrufen (nur für berechtigte User)
    def get_container_resource_usage(self, container_id_or_name, current_user: User):
        """
        Gibt die aktuelle Ressourcennutzung (CPU, RAM) eines Containers zurück (nur für berechtigte User).
        """
        try:
            log_event("DEBUG", "get_container_resource_usage",
                f"Fetching resource usage: {container_id_or_name}", level="DEBUG", user_id=current_user.id
            )
            container = self.client.containers.get(container_id_or_name)
            if current_user.role != "admin" and not container.name.startswith(f"user_{current_user.id}_"):
                raise Exception("Keine Berechtigung für diesen Container.")

            container.reload()
            if container.status != "running":
                log_event("WARNING", "get_container_resource_usage",
                    f"Container is not running: {container_id_or_name}", level="WARNING", user_id=current_user.id)
                return {"cpu_usage": None, "memory_usage": None}

            stats = container.stats(stream=False)

            # CPU-Auslastung berechnen
            cpu_delta = stats["cpu_stats"]["cpu_usage"]["total_usage"] - stats["precpu_stats"]["cpu_usage"]["total_usage"]
            system_delta = stats["cpu_stats"]["system_cpu_usage"] - stats["precpu_stats"]["system_cpu_usage"]
            cpu_percent = 0.0
            if system_delta > 0.0:
                cpu_percent = (cpu_delta / system_delta) * len(stats["cpu_stats"]["cpu_usage"]["percpu_usage"]) * 100.0

            # Speicherverbrauch berechnen
            mem_usage = stats["memory_stats"].get("usage", 0)

            # 📊 Werte an Prometheus übergeben
            CONTAINER_CPU_USAGE.labels(container_id=container_id_or_name).set(cpu_percent)
            CONTAINER_MEMORY_USAGE.labels(container_id=container_id_or_name).set(mem_usage)

            log_event("CONTAINER", "get_container_resource_usage",
                f"Container: {container_id_or_name} | CPU: {cpu_percent:.2f}%, RAM: {mem_usage} bytes",
                level="INFO", user_id=current_user.id, container_id=container_id_or_name,
                cpu=cpu_percent, ram=mem_usage
            )

            return {
                "container_id": container_id_or_name,
                "cpu_percent": round(cpu_percent, 2),
                "memory_usage": mem_usage
            }

        except Exception as e:
            log_event("ERROR", "get_container_resource_usage",
                f"Error while fetching resource usage: {str(e)}", level="ERROR", user_id=current_user.id, container_id=container_id_or_name)
            raise Exception(f"Fehler beim Abrufen der Container-Ressourcennutzung: {str(e)}")
