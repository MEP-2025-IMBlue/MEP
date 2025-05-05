import logging
from fastapi import APIRouter, HTTPException
from ..schemas.container import ContainerCreate, ContainerResponse
from typing import List
import docker

# Logging konfigurieren
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/containers", tags=["containers"])
docker_client = docker.from_env()

@router.post("/create", response_model=ContainerResponse)
async def create_container(container_data: ContainerCreate):
    try:
        if not container_data.image_path and not container_data.local_image_name:
            logger.error("Neither image_path nor local_image_name provided")
            raise HTTPException(status_code=422, detail="Either image_path or local_image_name must be provided")

        image = container_data.local_image_name or container_data.image_path
        logger.info(f"Creating container with image: {image}, name: {container_data.container_name}")

        # Erstelle den Container
        container = docker_client.containers.create(
            image=image,
            name=container_data.container_name,
            environment=container_data.env_vars,
            command="bash -c 'sleep infinity'",
            detach=True,
            tty=True
        )

        # Lade den Container neu, um den aktuellen Status zu erhalten
        #container.reload()

        response = ContainerResponse(
            container_id=container.id,
            name=container.name,
            status=container.status  # Jetzt sollte "running" erscheinen
        )
        logger.info(f"Container started: {response.dict()}")
        return response
    except docker.errors.ImageNotFound as e:
        logger.error(f"Image not found: {str(e)}")
        raise HTTPException(status_code=404, detail=f"Image not found: {str(e)}")
    except docker.errors.APIError as e:
        logger.error(f"Docker API error: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Failed to create container: {str(e)}")
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")


@router.get("/", response_model=List[ContainerResponse])
async def list_containers():
    try:
        containers = docker_client.containers.list(all=True)
        return [
            ContainerResponse(
                container_id=c.id,
                name=c.name,
                status=c.status
            ) for c in containers
        ]
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@router.get("/{container_id}", response_model=ContainerResponse)
async def get_container(container_id: str):
    try:
        container = docker_client.containers.get(container_id)
        return ContainerResponse(
            container_id=container.id,
            name=container.name,
            status=container.status
        )
    except docker.errors.NotFound:
        raise HTTPException(status_code=404, detail="Container not found")
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@router.post("/{container_id}/start", response_model=ContainerResponse)
async def start_container(container_id: str):
    try:
        container = docker_client.containers.get(container_id)
        container.start()
        
        # Lade den Container neu, um den aktuellen Status zu erhalten
        container.reload()

        return ContainerResponse(
            container_id=container.id,
            name=container.name,
            status=container.status
        )
    except docker.errors.NotFound:
        raise HTTPException(status_code=404, detail="Container not found")
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")


@router.post("/{container_id}/stop", response_model=ContainerResponse)
async def stop_container(container_id: str):
    try:
        container = docker_client.containers.get(container_id)
        container.stop()

        # Lade den Container neu, um den aktuellen Status zu erhalten
        container.reload()

        return ContainerResponse(
            container_id=container.id,
            name=container.name,
            status=container.status
        )
    except docker.errors.NotFound:
        raise HTTPException(status_code=404, detail="Container not found")
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@router.delete("/{container_id}", response_model=ContainerResponse)
async def delete_container(container_id: str):
    try:
        container = docker_client.containers.get(container_id)
        container.remove(force=True)
        return ContainerResponse(
            container_id=container.id,
            name=container.name,
            status="removed"
        )
    except docker.errors.NotFound:
        raise HTTPException(status_code=404, detail="Container not found")
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")