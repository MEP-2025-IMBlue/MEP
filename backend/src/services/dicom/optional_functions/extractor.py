# # extractor.py
# import os
# import logging
# import numpy as np
# import pydicom

# # Diese Funktion extrahiert das Pixel-Array und speichert es als .npy-Datei im angegebenen oder konfigurierten Verzeichnis
# def extract_pixel_array(ds: pydicom.Dataset, hash_name: str, output_dir: str = None) -> str:
#     """
#     Wandelt das DICOM-Bild in ein NumPy-Array um und speichert es im .npy-Format.
#     Der Speicherort wird über Umgebungsvariable 'PROCESSED_DIR' oder optionalen Parameter gesteuert.
#     """
#     if output_dir is None:
#         output_dir = os.getenv("PROCESSED_DIR", "/tmp/processed")
#         logging.info(f"[Extractor] Verwende Standardverzeichnis: {output_dir}")

#     os.makedirs(output_dir, exist_ok=True)

#     try:
#         array = ds.pixel_array.astype(np.float32)
#         logging.info(f"[Extractor] Pixel-Array erfolgreich extrahiert")
#     except Exception as e:
#         logging.error(f"[Extractor] Fehler beim Extrahieren des Pixel-Arrays: {str(e)}")
#         raise ValueError("Pixel array extraction failed") from e

#     out_path = os.path.join(output_dir, f"{hash_name}_anon.npy")
#     np.save(out_path, array)
#     logging.info(f"[Extractor] Pixel-Array gespeichert unter: {out_path}")
#     return out_path


