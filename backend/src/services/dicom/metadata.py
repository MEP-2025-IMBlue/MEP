#TO DO: diese py-Datei ist nur relevant für die Speicherung von Daten in der Datenbank, 
# also für die Statistik. Diese wird noch nicht angegangen, erst später

# import logging
# import pydicom

# # Extrahiert minimale Metadaten aus einem DICOM-Datensatz für die Speicherung
# def extract_metadata(ds: pydicom.Dataset) -> dict:
#     """
#     Gibt ein Dictionary mit den minimal erforderlichen DICOM-Metadaten zurück.
#     Nur Felder, die in der Datenbank persistiert werden, sind enthalten.
#     """

#     metadata = {
#         "dicom_uuid": str(ds.get("SOPInstanceUID", "")),
#         "dicom_modality": ds.get("Modality", "")
#     }

#     logging.info(f"[Metadata] Extrahierte reduzierte Metadaten: {metadata}")
#     return metadata

