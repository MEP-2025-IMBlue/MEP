import logging
import pydicom
from pydicom.errors import InvalidDicomError

# Diese Funktion prüft, ob die angegebene Datei ein valides DICOM mit Bildinhalt ist
def validate_dicom(file_path: str) -> bool:
    try:
        ds = pydicom.dcmread(file_path)
        _ = ds.pixel_array  # Versuche, Pixel-Daten zu extrahieren
        logging.info(f"[Validator] Gültige DICOM-Datei mit Bilddaten: {file_path}")
        return True
    except InvalidDicomError:
        logging.warning(f"[Validator] Ungültige DICOM-Datei: {file_path}")
        return False
    except AttributeError:
        logging.warning(f"[Validator] Keine Pixel-Daten gefunden in Datei: {file_path}")
        return False
    except FileNotFoundError:
        logging.error(f"[Validator] Datei nicht gefunden: {file_path}")
        return False
    except Exception as e:
        logging.error(f"[Validator] Fehler beim Validieren der Datei {file_path}: {str(e)}")
        return False

