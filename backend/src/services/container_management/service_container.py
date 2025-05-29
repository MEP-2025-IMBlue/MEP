import docker
from docker.errors import NotFound, APIError
from utils.event_logger import log_event


# Klasse zur Verwaltung von Docker-Containern
class ContainerService:
    def __init__(self):
        # Docker-Client initialisieren
        self.client = docker.from_env()

    # Container starten
    def start_container(self, container_id_or_name):
        try:
            log_event("DEBUG", "start_container", f"Versuche Container zu starten: {container_id_or_name}", level="DEBUG")
            container = self.client.containers.get(container_id_or_name)
            container.start()
            log_event("CONTAINER", "start_container", f"Container {container_id_or_name} erfolgreich gestartet", level="INFO")
            return {"message": f"Container {container_id_or_name} gestartet"}
        except NotFound:
            log_event("ERROR", "start_container", f"Container nicht gefunden: {container_id_or_name}", level="ERROR")
            raise
        except Exception as e:
            log_event("ERROR", "start_container", f"Allgemeiner Fehler: {str(e)}", level="ERROR")
            raise

    # Container stoppen
    def stop_container(self, container_id_or_name):
        try:
            log_event("DEBUG", "stop_container", f"Versuche Container zu stoppen: {container_id_or_name}", level="DEBUG")
            container = self.client.containers.get(container_id_or_name)
            container.stop()
            log_event("CONTAINER", "stop_container", f"Container {container_id_or_name} erfolgreich gestoppt", level="INFO")
            return {"message": f"Container {container_id_or_name} gestoppt"}
        except NotFound:
            log_event("WARNING", "stop_container", f"Container nicht gefunden (vielleicht bereits gestoppt?): {container_id_or_name}", level="WARNING")
            raise
        except Exception as e:
            log_event("ERROR", "stop_container", f"Fehler beim Stoppen des Containers: {str(e)}", level="ERROR")
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

    # Nur laufende Container abrufen
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

    # Alle Container (laufend & gestoppt) abrufen
    def list_containers(self):
        try:
            log_event("DEBUG", "list_containers", "Suche alle Container", level="DEBUG")
            containers = self.client.containers.list(all=True)
            names = [container.name for container in containers]
            log_event("CONTAINER", "list_containers", f"{len(names)} Container insgesamt gefunden: {names}", level="INFO")
            return names
        except Exception as e:
            log_event("ERROR", "list_containers", f"Fehler beim Abruf: {str(e)}", level="ERROR")
            raise
