# exceptions.py
# ---------------------------------------------
# Enthält eigene benutzerdefinierte Exceptions für die KI-Image-Logik

class NoKIImagesInTheList(Exception):
    """Wird geworfen, wenn keine KI-Bilder in der Liste vorhanden sind."""
    pass

class KIImageNotFound(Exception):
    """Wird geworfen, wenn ein bestimmtes KI-Bild nicht existiert."""
    pass

class DatabaseError(Exception):
    """Wird geworfen bei allgemeinen Datenbankfehlern."""
    pass

#TODO: final entscheiden welche Exceptions geworfen werden
class DICOMNotFound(Exception):
    pass

class NoDICOMInTheList(Exception):
    pass

class DICOMProcessingError(Exception):
    """Basisklasse für alle Fehler bei der Verarbeitung von DICOM-Dateien."""
    pass

class DICOMValidationError(DICOMProcessingError):
    """Basisklasse für Fehler, die bei der Prüfung von DICOM-Dateien auftreten."""
    pass

class InvalidDICOMFileType(DICOMValidationError):
    """Die hochgeladene Datei ist weder .dcm noch .zip."""
    pass

class InvalidDICOMFormat(DICOMValidationError):
    """Die Datei konnte nicht als gültiges DICOM-Format erkannt werden (z. B. durch pydicom)."""
    pass

class MissingRequiredTagError(DICOMValidationError):
    """Im DICOM-Header fehlen Pflicht-Tags wie SOPInstanceUID, PatientID etc."""
    pass

class MissingPixelData(DICOMValidationError):
    """Die DICOM-Datei enthält kein PixelData-Tag (kein Bild vorhanden)."""
    pass

class DICOMExtractionError(DICOMProcessingError):
    """Fehler beim Extrahieren von Bild- oder Metadaten aus der DICOM-Datei."""
    pass

# class FailedPixelDataExtraction(DICOMExtractionError):
#     """Fehler beim Zugriff auf oder Umwandlung der Pixeldaten."""
#     pass

class UnexpectedDICOMError(DICOMProcessingError):
    """Allgemeiner, unerwarteter Fehler bei der DICOM-Verarbeitung (z. B. I/O, Bugs)."""
    pass

# class InvalidDICOMFileType(Exception):
#     """Wird geworfen wenn DICOM-File weder .dcm oder .zip ist"""
#     pass

# #TODO: Beschreibung besser schreibe
# class InvalidDicomFormat(Exception):
#     """Wird geworfen wenn das DICOM-File nicht DICOM konform ist"""
#     pass

# #TODO: Beschreibung besser schreiben
# class MissingRequiredTagError(Exception):
#     """Wird geworfen wenn Tags im DICOM-File fhelen"""
#     pass

# #TODO: Beschreibung besser schreiben
# class MissingPixelData(Exception):
#     """Wird geworfen, wenn DICOM-File kein Pixeldata hat"""
#     pass

# class FailedPixelDataExtraction(Exception):
#     """Wird geworfen, wenn Extraktion der DICOM-Pixeldaten fehlschlägt"""
#     pass