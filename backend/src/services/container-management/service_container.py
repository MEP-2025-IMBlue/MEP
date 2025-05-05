import docker
from docker.errors import DockerException, NotFound

class ContainerService:
    def __init__(self):
        self.client = docker.from_env()  # Verbindet mit dem Docker-Daemon

    def run_container(self, image_path: str, container_name: str, env_vars: dict = None):
        """Startet einen Container mit dem angegebenen Image."""
        try:
            container = self.client.containers.run(
                image=image_path,
                name=container_name,
                detach=True,  # Läuft im Hintergrund
                environment=env_vars or {}
            )
            return {
                "container_id": container.id,
                "name": container.name,
                "status": container.status
            }
        except DockerException as e:
            raise Exception(f"Failed to run container: {str(e)}")

    def stop_container(self, container_id: str):
        """Stoppt einen Container anhand der ID."""
        try:
            container = self.client.containers.get(container_id)
            container.stop()
            return {"container_id": container_id, "status": "stopped"}
        except NotFound:
            raise Exception(f"Container {container_id} not found")
        except DockerException as e:
            raise Exception(f"Failed to stop container: {str(e)}")

    def remove_container(self, container_id: str):
        """Löscht einen Container anhand der ID."""
        try:
            container = self.client.containers.get(container_id)
            container.remove()
            return {"container_id": container_id, "status": "removed"}
        except NotFound:
            raise Exception(f"Container {container_id} not found")
        except DockerException as e:
            raise Exception(f"Failed to remove container: {str(e)}")

    def get_container_status(self, container_id: str):
        """Gibt den Status eines Containers zurück."""
        try:
            container = self.client.containers.get(container_id)
            return {
                "container_id": container.id,
                "name": container.name,
                "status": container.status
            }
        except NotFound:
            raise Exception(f"Container {container_id} not found")
        except DockerException as e:
            raise Exception(f"Failed to get container status: {str(e)}")

    def list_containers(self):
        """Listet alle laufenden Container auf."""
        try:
            containers = self.client.containers.list(all=True)
            return [
                {
                    "container_id": c.id,
                    "name": c.name,
                    "status": c.status
                }
                for c in containers
            ]
        except DockerException as e:
            raise Exception(f"Failed to list containers: {str(e)}")
