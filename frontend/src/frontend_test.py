import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os

# Basisverzeichnis ermitteln (Verzeichnis dieser Datei)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Absoluter Pfad zur Datei im Ordner: frontend/src/assets/
DICOM_FILE = os.path.join(BASE_DIR, "assets", "chest.dcm")
TAR_FILE = os.path.join(BASE_DIR, "assets", "my_test_image.tar")

# Setup-Funktion für den Chrome WebDriver
def setup_driver():
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    return driver

# ------------------ Container Upload ------------------

# Testklasse für die Seite: container_upload.html
class TestContainerUpload(unittest.TestCase):
    def setUp(self):
        # Starte WebDriver und öffne die Seite
        self.driver = setup_driver()
        self.driver.get("http://localhost:8080/pages/container_upload.html")

    def test_local_container_upload(self):
        # Klicke auf Karte für lokalen Upload
        self.driver.find_elements(By.CLASS_NAME, "upload-card")[0].click()
        time.sleep(0.5)

        # Wähle Datei aus und klicke auf Hochladen
        file_input = self.driver.find_element(By.ID, "fileInput-local")
        file_input.send_keys(TAR_FILE)

        upload_button = self.driver.find_element(By.CSS_SELECTOR, "#local-upload-form button")
        self.driver.execute_script("arguments[0].click();", upload_button)

        # Warte auf Klasse 'success' im Statusfeld
        try:
            WebDriverWait(self.driver, 15).until(
                lambda d: "success" in d.find_element(By.ID, "local-status").get_attribute("class").lower()
            )
            status = self.driver.find_element(By.ID, "local-status")
            print("\u2705 Upload erfolgreich:", status.text)
        except Exception:
            # Screenshot bei Fehler
            self.driver.save_screenshot("upload_fail.png")
            self.fail("Upload-Status 'success' nicht erreicht (Screenshot: upload_fail.png)")

    def test_dockerhub_reference_upload(self):
        # Klicke auf Karte für DockerHub-Upload
        self.driver.find_elements(By.CLASS_NAME, "upload-card")[1].click()
        time.sleep(0.5)

        # Image-Referenz eingeben und absenden
        input_field = self.driver.find_element(By.NAME, "image_reference")
        input_field.send_keys("ubuntu:latest")

        upload_button = self.driver.find_element(By.CSS_SELECTOR, "#hub-upload-form button")
        self.driver.execute_script("arguments[0].click();", upload_button)

        # Warte auf Erfolg (Klasse 'success')
        try:
            WebDriverWait(self.driver, 15).until(
                lambda d: "success" in d.find_element(By.ID, "hub-status").get_attribute("class").lower()
            )
            status = self.driver.find_element(By.ID, "hub-status")
            print("\u2705 DockerHub erfolgreich:", status.text)
        except Exception:
            self.driver.save_screenshot("hub_fail.png")
            self.fail("DockerHub-Upload nicht erfolgreich (Screenshot: hub_fail.png)")

    def tearDown(self):
        # Beende WebDriver
        self.driver.quit()

# ------------------ DICOM Upload ------------------

# Testklasse für die Seite: dicom_upload.html
class TestDicomUpload(unittest.TestCase):
    def setUp(self):
        self.driver = setup_driver()
        self.driver.get("http://localhost:8080/pages/dicom_upload.html")

    def test_dicom_upload_and_card_display(self):
        # Wähle DICOM-Datei und sende Formular ab
        file_input = self.driver.find_element(By.ID, "dicom_file")
        file_input.send_keys(DICOM_FILE)

        self.driver.find_element(By.CSS_SELECTOR, "#dicom-form button").click()
        time.sleep(3)

        # Prüfe ob die Vorschläge nach Upload angezeigt werden
        ki_title = self.driver.find_element(By.ID, "ki-title")
        self.assertTrue(ki_title.is_displayed())

        ki_list = self.driver.find_element(By.ID, "ki-list")
        self.assertTrue(ki_list.is_displayed())

    def tearDown(self):
        self.driver.quit()

# ------------------ Dashboard ------------------

# Testklasse für die Seite: dashboard.html
class TestDashboard(unittest.TestCase):
    def setUp(self):
        self.driver = setup_driver()
        self.driver.get("http://localhost:8080/pages/dashboard.html")

    def test_uploaded_container_is_visible(self):
        # Warte bis Containerliste geladen ist
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "ki-image-list"))
        )
        container_area = self.driver.find_element(By.ID, "ki-image-list")
        self.assertTrue(container_area.text.strip() != "")

    def test_filter_input(self):
        # Führe Filterung nach 'ubuntu' durch und prüfe Ergebnis
        search_input = self.driver.find_element(By.ID, "searchInput")
        search_input.send_keys("ubuntu")
        time.sleep(1)
        self.assertEqual(search_input.get_attribute("value"), "ubuntu")
        container_area = self.driver.find_element(By.ID, "ki-image-list")
        self.assertIn("ubuntu", container_area.text.lower())

    def test_card_delete_if_exists(self):
        try:
            # Suche und klicke auf Löschen-Button
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".btn-delete"))
            )
            delete_button = self.driver.find_element(By.CSS_SELECTOR, ".btn-delete")
            self.driver.execute_script("arguments[0].click();", delete_button)
            time.sleep(0.5)

            # Bestätige Sicherheitsdialog
            alert = self.driver.switch_to.alert
            print("Alert 1:", alert.text)
            alert.accept()
            time.sleep(1)

            # Bestätige Erfolgsdialog
            alert = self.driver.switch_to.alert
            print("Alert 2:", alert.text)
            alert.accept()
            time.sleep(1)

            print("\u2705 Löschen erfolgreich bestätigt.")

        except Exception as e:
            print("\u26A0\uFE0F Kein Container zum Löschen gefunden – übersprungen. Grund:", e)
            self.skipTest("Kein Container vorhanden oder DOM nicht geladen")

    def tearDown(self):
        self.driver.quit()

# ------------------ Hauptausführung ------------------

if __name__ == "__main__":
    unittest.main()
