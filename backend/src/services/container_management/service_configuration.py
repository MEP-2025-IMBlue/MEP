import os
from uuid import uuid4
from src.api.py_models import py_models
from src.db.db_models import db_models

#TODO: kein bool return Wert, sondern "raise ValueError("Missing field XY")"
def validate_configs(container_config: py_models.ContainerConfigInput) -> bool:
    """Validiert die Eingabe des Formulars des Providers:
    - ist input_dir und output_dir gleich?
    
    """
    return True

def db_model_to_run_params(container_config: db_models.ContainerConfiguration) -> dict:
    """Wandelt ein ContainerConfiguration-Objekt in ein Dictionary mit run()-Parametern."""

    os.makedirs(base_dir, exist_ok=True)
    os.makedirs(host_data_in, exist_ok=True)
    os.makedirs(host_data_out, exist_ok=True)
    job_id = str(uuid4())
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "container"))
    host_data_in = os.path.join(base_dir, f"data_in/{job_id}")
    host_data_out = os.path.join(base_dir, f"data_out/{job_id}")

    params = {
        "command": "tail -f /dev/null",  # Default-Leerlaufbefehl
        "volumes": {
            host_data_out: {"bind": container_config.input_dir, "mode": "ro"},
            host_data_in: {"bind": container_config.output_dir, "mode": "rw"}
        }
    }

    if container_config.environment:
        params["environment"] = container_config.environment
    if container_config.run_command:
        params["command"] = container_config.run_command
    if container_config.working_dir:
        params["working_dir"] = container_config.working_dir
    if container_config.entrypoint:
        params["entrypoint"] = container_config.entrypoint
    if container_config.gpu_required:
        params["device_requests"] = [...]  # Muss noch mit Inhalt befüllt werden

    return params



