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

class InvalidDICOMFileType(Exception):
    """Wird geworfen wenn DICOM-File weder .dcm oder .zip ist"""
    pass

#TODO: Beschreibung besser schreiben
class MissingRequiredTagError(Exception):
    """Wird geworfen wenn Tags im DICOM-File fhelen"""

#TODO: Beschreibung besser schreiben
class MissingPixelData(Exception):
    """Wird geworfen, wenn DICOM-File kein Pixeldata hat"""

class FailedPixelDataExtraction(Exception):
    """Wird geworfen, wenn Extraktion der DICOM-Pixeldaten fehlschlägt"""