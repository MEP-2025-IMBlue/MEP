import logging
import docker
from docker.errors import DockerException, NotFound, ImageNotFound

from src.api.py_models.py_models import ContainerResponse
from src.db.crud import crud_kiImage
from sqlalchemy.orm import Session

from utils.event_logger import log_event  # Eigenes Logging-Tool

logger = logging.getLogger(__name__)

class ContainerService:
    def __init__(self):
        self.client = docker.from_env()

    # Startet einen User-Container (entweder bestehenden oder neuen)
    def start_user_container(self, db: Session, user_id: int, image_id: int) -> ContainerResponse:
        """Startet einen pro-User-Container; startet existierenden oder erstellt neuen."""
        try:
            # --- Vorgangsstart loggen
            log_event(
                "CONTAINER", "start_user_container",
                f"Starte Container für user_id={user_id}, image_id={image_id}", "DEBUG",
                user_id=user_id, image_id=image_id
            )
            ki_image = crud_kiImage.get_ki_image_by_id(db, image_id)
            image_reference = f"{ki_image.image_name}:{ki_image.image_tag}"

            base_name = ki_image.image_name.replace("/", "_")
            container_name = f"user_{user_id}_{base_name}_{ki_image.image_tag}"

            logger.info(f"Trying to start container: {container_name}")

            try:
                container = self.client.containers.get(container_name)
                if container.status != "running":
                    # --- Existierenden Container starten
                    container.start()
                    container.reload()
                    logger.info(f"Started existing container {container_name}")
                    log_event(
                        "CONTAINER", "start_existing",
                        f"Vorhandener Container gestartet: {container_name}", "INFO",
                        user_id=user_id, container_name=container_name, image_id=image_id
                    )
                else:
                    # --- Container läuft bereits
                    logger.info(f"Container {container_name} already running")
                    log_event(
                        "CONTAINER", "already_running",
                        f"Container bereits läuft: {container_name}", "INFO",
                        user_id=user_id, container_name=container_name, image_id=image_id
                    )
            except NotFound:
                # --- Neuen Container erstellen & starten
                logger.info(f"Creating new container {container_name}")
                log_event(
                    "CONTAINER", "create_container",
                    f"Erstelle neuen Container: {container_name}", "INFO",
                    user_id=user_id, container_name=container_name, image_id=image_id
                )
                container = self.client.containers.run(
                    image=image_reference,
                    name=container_name,
                    command="tail -f /dev/null",  # Hintergrundprozess, damit Container aktiv bleibt
                    detach=True
                )
                container.reload()
                logger.info(f"Started new container {container_name}")
                log_event(
                    "CONTAINER", "create_and_start",
                    f"Neuer Container erstellt & gestartet: {container_name}", "INFO",
                    user_id=user_id, container_name=container_name, image_id=image_id, container_id=container.id
                )

            # --- Erfolgsmeldung am Ende loggen
            log_event(
                "CONTAINER", "start_user_container_success",
                f"Container gestartet: {container.name} ({container.id})", "INFO",
                user_id=user_id, container_name=container.name, image_id=image_id, container_id=container.id
            )
            return ContainerResponse(
                container_id=container.id,
                name=container.name,
                status=container.status
            )
        except ImageNotFound:
            # --- Fehler: Image nicht gefunden
            log_event(
                "CONTAINER", "image_not_found",
                f"Image nicht gefunden: {image_reference}", "ERROR",
                user_id=user_id, image_reference=image_reference, image_id=image_id
            )
            raise Exception(f"Image {image_reference} not found in Docker daemon.")
        except DockerException as e:
            # --- Fehler beim Starten des Containers
            log_event(
                "CONTAINER", "docker_exception",
                f"Fehler beim Container-Start: {str(e)}", "ERROR",
                user_id=user_id, image_id=image_id
            )
            raise Exception(f"Failed to start container: {str(e)}")

    # Stoppt einen Container (per Name oder ID)
    def stop_container(self, container_id_or_name: str) -> dict:
        """Stoppt einen Container anhand ID oder Name."""
        try:
            # --- Start des Stopp-Vorgangs loggen
            log_event(
                "CONTAINER", "stop_container",
                f"Versuche Container zu stoppen: {container_id_or_name}", "DEBUG",
                container_id=container_id_or_name
            )
            container = self.client.containers.get(container_id_or_name)
            container.stop()
            # --- Erfolg loggen
            log_event(
                "CONTAINER", "stop_container_success",
                f"Container {container_id_or_name} erfolgreich gestoppt", "INFO",
                container_id=container_id_or_name
            )
            return {"container_id": container.id, "name": container.name, "status": "stopped"}
        except NotFound:
            # --- Fehler: Container nicht gefunden
            log_event(
                "CONTAINER", "stop_container_not_found",
                f"Container nicht gefunden: {container_id_or_name}", "WARNING",
                container_id=container_id_or_name
            )
            raise Exception(f"Container {container_id_or_name} not found")
        except DockerException as e:
            # --- Fehler beim Stoppen
            log_event(
                "CONTAINER", "stop_container_error",
                f"Fehler beim Stoppen: {str(e)}", "ERROR",
                container_id=container_id_or_name
            )
            raise Exception(f"Failed to stop container: {str(e)}")

    # Löscht einen Container (per Name oder ID)
    def remove_container(self, container_id_or_name: str) -> dict:
        """Löscht einen Container anhand ID oder Name."""
        try:
            # --- Start des Löschvorgangs loggen
            log_event(
                "CONTAINER", "remove_container",
                f"Versuche Container zu löschen: {container_id_or_name}", "DEBUG",
                container_id=container_id_or_name
            )
            container = self.client.containers.get(container_id_or_name)
            container.remove(force=True)
            # --- Erfolg loggen
            log_event(
                "CONTAINER", "remove_container_success",
                f"Container {container_id_or_name} erfolgreich gelöscht", "INFO",
                container_id=container_id_or_name
            )
            return {"container_id": container.id, "name": container.name, "status": "removed"}
        except NotFound:
            # --- Fehler: Container nicht gefunden
            log_event(
                "CONTAINER", "remove_container_not_found",
                f"Container nicht gefunden: {container_id_or_name}", "WARNING",
                container_id=container_id_or_name
            )
            raise Exception(f"Container {container_id_or_name} not found")
        except DockerException as e:
            # --- Fehler beim Löschen
            log_event(
                "CONTAINER", "remove_container_error",
                f"Fehler beim Löschen: {str(e)}", "ERROR",
                container_id=container_id_or_name
            )
            raise Exception(f"Failed to remove container: {str(e)}")

    # Gibt den Status eines Containers zurück (per Name oder ID)
    def get_container_status(self, container_id_or_name: str) -> dict:
        """Gibt Status eines Containers (ID oder Name) zurück."""
        try:
            # --- Start der Statusabfrage loggen
            log_event(
                "CONTAINER", "get_container_status",
                f"Frage Status ab für: {container_id_or_name}", "DEBUG",
                container_id=container_id_or_name
            )
            container = self.client.containers.get(container_id_or_name)
            result = {
                "container_id": container.id,
                "name": container.name,
                "status": container.status
            }
            # --- Erfolg loggen
            log_event(
                "CONTAINER", "get_container_status_success",
                f"Status erfolgreich abgefragt: {container_id_or_name} | Status: {container.status}", "INFO",
                container_id=container_id_or_name
            )
            return result
        except NotFound:
            # --- Fehler: Container nicht gefunden
            log_event(
                "CONTAINER", "get_container_status_not_found",
                f"Container nicht gefunden: {container_id_or_name}", "WARNING",
                container_id=container_id_or_name
            )
            raise Exception(f"Container {container_id_or_name} not found")
        except DockerException as e:
            # --- Fehler beim Abfragen
            log_event(
                "CONTAINER", "get_container_status_error",
                f"Fehler beim Statusabruf: {str(e)}", "ERROR",
                container_id=container_id_or_name
            )
            raise Exception(f"Failed to get container status: {str(e)}")

    # Listet alle Container (optional gefiltert nach user_id)
    def list_containers(self, user_id: int = None) -> list:
        """Listet alle Container, optional gefiltert nach user_id."""
        try:
            # --- Start der Auflistung loggen
            log_event(
                "CONTAINER", "list_containers",
                "Liste alle Container (optional gefiltert)", "DEBUG",
                user_id=user_id
            )
            containers = self.client.containers.list(all=True)
            result = []
            for c in containers:
                if user_id:
                    if not c.name.startswith(f"user_{user_id}_"):
                        continue
                result.append({
                    "container_id": c.id,
                    "name": c.name,
                    "status": c.status
                })
            # --- Erfolg loggen
            log_event(
                "CONTAINER", "list_containers_success",
                f"Anzahl gefundener Container: {len(result)}", "INFO",
                user_id=user_id
            )
            return result
        except DockerException as e:
            # --- Fehler bei der Auflistung
            log_event(
                "CONTAINER", "list_containers_error",
                f"Fehler bei der Container-Auflistung: {str(e)}", "ERROR",
                user_id=user_id
            )
            raise Exception(f"Failed to list containers: {str(e)}")
#   # Nur laufende Container abrufen
    def list_running_containers(self):
        try:
            log_event("DEBUG", "list_running_containers", "Suche laufende Container", level="DEBUG")
            containers = self.client.containers.list()
            names = [container.name for container in containers]
            log_event("CONTAINER", "list_running_containers", f"{len(names)} laufende Container gefunden: {names}", level="INFO")
            return names
        except Exception as e:
            log_event("ERROR", "list_running_containers", f"Fehler beim Abruf: {str(e)}", level="ERROR")
            raise
    # Container-Logs abrufen
    def get_container_logs(self, container_id_or_name, tail=100, stdout=True, stderr=True, timestamps=True):
        try:
            log_event("DEBUG", "get_container_logs", f"Rufe Logs ab für Container: {container_id_or_name} | tail={tail}, stdout={stdout}, stderr={stderr}, timestamps={timestamps}", level="DEBUG")
            container = self.client.containers.get(container_id_or_name)
            logs = container.logs(tail=tail, stdout=stdout, stderr=stderr, timestamps=timestamps).decode("utf-8")
            log_event("CONTAINER", "get_container_logs", f"Logs erfolgreich abgerufen für: {container_id_or_name}", level="INFO")
            return logs
        except Exception as e:
            log_event("ERROR", "get_container_logs", f"Fehler beim Log-Abruf ({container_id_or_name}): {str(e)}", level="ERROR")
            raise

    # Status und Health abrufen
    def get_container_status_and_health(self, container_id_or_name):
        try:
            log_event("DEBUG", "get_container_status_and_health", f"Rufe Status & Health ab: {container_id_or_name}", level="DEBUG")
            container = self.client.containers.get(container_id_or_name)
            status = container.status
            health = container.attrs.get("State", {}).get("Health", {}).get("Status", "nicht definiert")
            log_event("CONTAINER", "get_container_status_and_health", f"Container: {container_id_or_name} | Status: {status}, Health: {health}", level="INFO")
            return {"status": status, "health": health}
        except Exception as e:
            log_event("ERROR", "get_container_status_and_health", f"Fehler beim Abruf: {str(e)}", level="ERROR")
            raise

    # Ressourcennutzung eines Containers abrufen
    def get_container_resource_usage(self, container_id_or_name):
        try:
            log_event("DEBUG", "get_container_resource_usage", f"Fetching resource usage: {container_id_or_name}", level="DEBUG")
            container = self.client.containers.get(container_id_or_name)

            # Check if container is running
            container.reload()
            if container.status != "running":
                log_event("WARNING", "get_container_resource_usage", f"Container is not running: {container_id_or_name}", level="WARNING", container_id=container_id_or_name)
                return {"cpu_usage": None, "memory_usage": None}

            stats = container.stats(stream=False)

            # Extract CPU and memory safely
            cpu_percent = stats.get('cpu_stats', {}).get('cpu_usage', {}).get('total_usage')
            mem_usage = stats.get('memory_stats', {}).get('usage')

            log_event(
                "CONTAINER",
                "get_container_resource_usage",
                f"Container: {container_id_or_name} | CPU: {cpu_percent}, RAM: {mem_usage}",
                level="INFO",
                container_id=container_id_or_name,
                cpu=cpu_percent,
                ram=mem_usage
            )

            return {"cpu_usage": cpu_percent, "memory_usage": mem_usage}

        except Exception as e:
            log_event("ERROR", "get_container_resource_usage", f"Error while fetching resource usage: {str(e)}", level="ERROR", container_id=container_id_or_name)
            raise        