
class NoKIImagesInTheList(Exception):
    """Wird geworfen, wenn keine KI-Bilder in der DB vorhanden sind."""
    pass

class DatabaseError(Exception):
    """Wird geworfen bei allgemeinen DB-Fehlern."""
    pass
