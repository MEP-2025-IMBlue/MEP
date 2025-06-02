import pydicom
import numpy as np
from pydicom.errors import InvalidDicomError
from typing import Dict

# ===========================================
# DICOM Datei lesen (Metadaten und Bildinfo)
# ===========================================
def read_dicom(file_path: str) -> Dict:
    """
    Liest eine DICOM-Datei und extrahiert DSGVO-konforme Metadaten und Bildinformationen.
    """
    try:
        # DICOM-Datei einlesen
        dicom = pydicom.dcmread(file_path)
        
        # DSGVO-konforme Metadaten extrahieren (keine personenbezogenen Daten)
        metadata = {
            "dicom_modality": getattr(dicom, "Modality", "N/A"),
            "dicom_sop_class_uid": getattr(dicom, "SOPClassUID", "N/A"),
            "dicom_manufacturer": getattr(dicom, "Manufacturer", "N/A"),
            "dicom_rows": getattr(dicom, "Rows", None),
            "dicom_columns": getattr(dicom, "Columns", None),
            "dicom_bits_allocated": getattr(dicom, "BitsAllocated", None),
            "dicom_photometric_interpretation": getattr(dicom, "PhotometricInterpretation", "N/A"),
            "dicom_transfer_syntax_uid": getattr(dicom.file_meta, "TransferSyntaxUID", "N/A"),
            "dicom_file_path": file_path
        }
        
        # Bilddaten extrahieren
        pixel_array = dicom.pixel_array
        image_info = {
            "shape": pixel_array.shape,
            "data_type": str(pixel_array.dtype),
            "min_pixel_value": np.min(pixel_array),
            "max_pixel_value": np.max(pixel_array)
        }
        
        return {
            "status": "success",
            "metadata": metadata,
            "image_info": image_info
        }
    
    except InvalidDicomError:
        return {"status": "error", "message": "Ungültige DICOM-Datei."}
    except Exception as e:
        return {"status": "error", "message": f"Fehler beim Einlesen: {str(e)}"}

# Beispiel: Teste eine Datei
#file_path = "/Users/maimuna/Desktop/DICOM-Files/series-00000/image-00000.dcm"  # Ersetze mit deinem Dateipfad
#file_path = "/Users/maimuna/Desktop/DICOM-Files/Siemens-MRI-Magnetom-Vida-3T_Large-FOV_1800000004364898/Vida_Abdomen_T1_VIBE_Dixon_W_Vi001_SL95.dcm"  # Ersetze mit deinem Dateipfad
#file_path = "/Users/maimuna/Desktop/DICOM-Files/0002.dcm"
#file_path = "/Users/maimuna/Desktop/DICOM-Files/0003.dcm"
#result = read_dicom(file_path)
#print(result)
