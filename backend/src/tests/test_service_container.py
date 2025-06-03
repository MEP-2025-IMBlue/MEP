import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from services.container_management.service_container import ContainerService
from utils.event_logger import log_event


# Diese Tests überprüfen die Methoden der ContainerService-Klasse.
# Ziel: Sicherstellen, dass Logging und Verhalten korrekt funktionieren.

class TestContainerService(unittest.TestCase):
    def setUp(self):
        # Wird vor jedem einzelnen Test ausgeführt
        self.service = ContainerService()
        self.valid_container = "mep-backend"  # Ein existierender Container
        self.invalid_container = "container_does_not_exist"  # Ein absichtlich ungültiger Container

    def test_get_container_logs(self):
        """
        Testet das Abrufen von Container-Logs.
        Erwartung: Rückgabe ist ein String mit Log-Zeilen.
        """
        try:
            logs = self.service.get_container_logs(self.valid_container, tail=5)
            self.assertIsInstance(logs, str)
            self.assertIn("INFO", logs)
        except Exception as e:
            self.fail(f"Fehler beim Abrufen der Logs: {str(e)}")

    def test_get_container_status_and_health(self):
        """
        Testet das Abrufen von Containerstatus und Health.
        Erwartung: Rückgabe enthält 'status' und 'health'.
        """
        result = self.service.get_container_status_and_health(self.valid_container)
        self.assertIn("status", result)
        self.assertIn("health", result)

    def test_list_containers(self):
        """
        Testet das Auflisten aller Container.
        Erwartung: Liste von Container-Namen (inkl. mep-backend).
        """
        names = self.service.list_containers()
        self.assertIsInstance(names, list)
        self.assertIn(self.valid_container, names)

    def test_list_running_containers(self):
        """
        Testet das Auflisten nur laufender Container.
        Erwartung: Liste enthält aktive Container-Namen.
        """
        names = self.service.list_running_containers()
        self.assertIsInstance(names, list)

    def test_stop_invalid_container(self):
        """
        Testet das Stoppen eines ungültigen Containers.
        Erwartung: Exception wird geworfen und Logging erfolgt.
        """
        with self.assertRaises(Exception):
            self.service.stop_container(self.invalid_container)

    def test_start_invalid_container(self):
        """
        Testet das Starten eines ungültigen Containers.
        Erwartung: Exception wird geworfen und Logging erfolgt.
        """
        with self.assertRaises(Exception):
            self.service.start_container(self.invalid_container)

    def test_get_container_resource_usage(self):
        """
        Testet das Abrufen von CPU- und Speicherverbrauch eines Containers.
        Erwartung: Rückgabe enthält cpu_usage und memory_usage.
        """
        try:
            usage = self.service.get_container_resource_usage(self.valid_container)
            self.assertIn("cpu_usage", usage)
            self.assertIn("memory_usage", usage)
        except Exception as e:
            self.fail(f"Fehler beim Abrufen der Nutzung: {str(e)}")


if __name__ == '__main__':
    unittest.main()
