#TO DO: wir nehmen statt ein Hashwert eine DICOM interne ID
# -> diese wird in der Datenbank gespeichert
# -> und auch in den temporär gespeicherten Dateien ans Name hinzugefügt: /storage/processed
# und /storage/uploads

# # hasher.py
# import hashlib
# import logging
# import pydicom

# # Erstellt einen SHA-256-Hash basierend auf UIDs und (optional) Pixel-Daten
# def generate_dicom_hash(ds: pydicom.Dataset) -> str:
#     """
#     Erzeugt einen eindeutigen SHA-256-Hash für ein DICOM-Objekt.
#     Die Hash-Eingabe besteht aus den UIDs und optional den Bilddaten (PixelArray).
#     """
#     uid_part = (
#         str(ds.get("StudyInstanceUID", "")) +
#         str(ds.get("SeriesInstanceUID", "")) +
#         str(ds.get("SOPInstanceUID", ""))
#     )

#     try:
#         pixel_data = ds.pixel_array.tobytes().hex()
#         logging.info("[Hasher] Pixel-Daten erfolgreich in Hash integriert.")
#     except Exception as e:
#         logging.warning(f"[Hasher] Pixel-Daten konnten nicht gelesen werden: {str(e)}")
#         pixel_data = ""

#     hash_input = uid_part + pixel_data
#     result = hashlib.sha256(hash_input.encode()).hexdigest()
#     logging.info(f"[Hasher] SHA-256-Hash erzeugt: {result}")
#     return result

