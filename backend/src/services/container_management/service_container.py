# Externe Libraries
import logging
import docker
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
            # Hole Image aus DB
            ki_image = crud_kiImage.get_ki_image_by_id(db, image_id)
            image_full_name = f"{ki_image.image_name}:{ki_image.image_tag}"

            # Container-Name definieren
            base_name = ki_image.image_name.replace("/", "_")
            container_name = f"user_{user_id}_{base_name}_{ki_image.image_tag}"

            logger.info(f"Trying to start container: {container_name}")

            try:
                # Prüfen ob Container existiert
                container = self.client.containers.get(container_name)
                if container.status != "running":
                    container.start()
                    container.reload()
                    logger.info(f"Started existing container {container_name}")
                else:
                    logger.info(f"Container {container_name} already running")
            except NotFound:
                # Neuer Container erstellen
                logger.info(f"Creating new container {container_name}")
                container = self.client.containers.run(
                    image=image_full_name,
                    name=container_name,
                    command="tail -f /dev/null", # eventuell nochmal relevant
                    detach=True
                )
                #container.start()
                container.reload()
                logger.info(f"Started existing container {container_name}")


            return ContainerResponse(
                container_id=container.id,
                name=container.name,
                status=container.status
            )
        except ImageNotFound:
            raise Exception(f"Image {image_full_name} not found in Docker daemon.")
        except DockerException as e:
            raise Exception(f"Failed to start container: {str(e)}")

    def stop_container(self, container_id_or_name: str) -> dict:
        """Stoppt einen Container anhand ID oder Name."""
        try:
            container = self.client.containers.get(container_id_or_name)
            container.stop()
            return {"container_id": container.id, "name": container.name, "status": "stopped"}
        except NotFound:
            raise Exception(f"Container {container_id_or_name} not found")
        except DockerException as e:
            raise Exception(f"Failed to stop container: {str(e)}")

    def remove_container(self, container_id_or_name: str) -> dict:
        """Löscht einen Container anhand ID oder Name."""
        try:
            container = self.client.containers.get(container_id_or_name)
            container.remove(force=True)
            return {"container_id": container.id, "name": container.name, "status": "removed"}
        except NotFound:
            raise Exception(f"Container {container_id_or_name} not found")
        except DockerException as e:
            raise Exception(f"Failed to remove container: {str(e)}")

    def get_container_status(self, container_id_or_name: str) -> dict:
        """Gibt Status eines Containers (ID oder Name) zurück."""
        try:
            container = self.client.containers.get(container_id_or_name)
            return {
                "container_id": container.id,
                "name": container.name,
                "status": container.status
            }
        except NotFound:
            raise Exception(f"Container {container_id_or_name} not found")
        except DockerException as e:
            raise Exception(f"Failed to get container status: {str(e)}")

    def list_containers(self, user_id: int = None) -> list:
        """Listet alle Container, optional gefiltert nach user_id."""
        try:
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
            return result
        except DockerException as e:
            raise Exception(f"Failed to list containers: {str(e)}")
