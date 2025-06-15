# test_logger.py
from utils.event_logger import log_event

log_event(source="manual_test", action="startup", message="Logger manuel test edildi", user_id="testuser")
