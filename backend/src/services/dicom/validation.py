import re
import logging
from datetime import datetime
from fastapi import HTTPException
from pydicom.dataset import Dataset
from services.dicom.compliance_checker import check_compliance

# Logging-Konfiguration
logging.basicConfig(level=logging.INFO)


# Pflichtfelder mit Typen: 1 = erforderlich mit Inhalt, 2 = erforderlich aber darf leer sein
REQUIRED_TAGS = {
    "PatientID": 2,
    "PatientName": 2,
    "PatientBirthDate": 2,
    "PatientSex": 2,
    "StudyInstanceUID": 2,
    "StudyDate": 2,
    "StudyDescription": 2,
    "AccessionNumber": 2,
    "SeriesInstanceUID": 1,
    "SeriesNumber": 2,
    "SeriesDescription": 2,
    "SOPInstanceUID": 1,
    "SOPClassUID": 1,
    "InstanceNumber": 2
}

# Gültige Modalitäten gemäß DICOM-Standard
VALID_MODALITIES = {"CT", "MR", "XR", "US", "NM", "PT", "DX", "MG", "CR"}

# Bekannte TransferSyntaxUIDs
TRANSFER_SYNTAX_UIDS = {
    "1.2.840.10008.1.2": "Implicit VR Little Endian",
    "1.2.840.10008.1.2.1": "Explicit VR Little Endian",
    "1.2.840.10008.1.2.2": "Explicit VR Big Endian",
    "1.2.840.10008.1.2.4.50": "JPEG Baseline (Lossy)",
    "1.2.840.10008.1.2.4.70": "JPEG Lossless",
    "1.2.840.10008.1.2.4.80": "JPEG-LS Lossless",
    "1.2.840.10008.1.2.4.90": "JPEG 2000 Lossless",
    "1.2.840.10008.1.2.5": "RLE Lossless"
}


def run_full_validation(ds: Dataset, filename: str) -> None:
    logging.info(f"[Validation] Starte Validierung der DICOM-Metadaten für Datei: {filename}")
    check_compliance(ds, filename)

    # Dynamische Pflichtfelder basierend auf Modalität
    required_tags = {
        "PatientID": 2,
        "PatientName": 2,
        "StudyInstanceUID": 2,
        "SeriesInstanceUID": 2,
        "SOPInstanceUID": 1,
        "SOPClassUID": 1,
        "Modality": 1,
        "InstanceNumber": 2,
        "StudyDate": 2,
        "FrameOfReferenceUID": 2,
        "SamplesPerPixel": 2,
        "PhotometricInterpretation": 2,
    }

    if ds.Modality in {"CT", "MR", "PT"}:
        required_tags["ImagePositionPatient"] = 2
        required_tags["ImageOrientationPatient"] = 2
        required_tags["PixelSpacing"] = 2

    check_required_tags(ds, required_tags)
    check_date_fields(ds)
    check_uid_formats(ds)
    check_modality(ds)
    check_pixeldata_presence(ds, filename)
    check_transfer_syntax(ds)
    log_private_tags(ds, filename)
    logging.info(f"[Validation] DICOM-Metadaten erfolgreich validiert für Datei: {filename}")


def check_required_tags(ds: Dataset, required_tags: dict) -> None:
    fehlende_typ1 = []

    for tag, tag_typ in required_tags.items():
        if not hasattr(ds, tag):
            if tag_typ == 1:
                fehlende_typ1.append(tag)
            elif tag_typ == 2:
                logging.warning(f"[Validation] Optionaler Pflichtwert (Type 2) fehlt: {tag}")
            continue

        value = getattr(ds, tag)
        if tag_typ == 1 and (value is None or str(value).strip() == ""):
            fehlende_typ1.append(tag)
        elif tag_typ == 2 and (value is None or str(value).strip() == ""):
            logging.warning(f"[Validation] {tag} ist leer – erlaubt, aber protokolliert.")

    if fehlende_typ1:
        logging.error(f"[Validation] Fehlende Pflichtfelder (Type 1): {fehlende_typ1}")
        raise ValueError(f"Fehlende Pflichtfelder: {', '.join(fehlende_typ1)}")


def check_date_fields(ds: Dataset) -> None:
    for field in ["PatientBirthDate", "StudyDate"]:
        value = getattr(ds, field, "")
        if value and not re.fullmatch(r"\d{8}", value):
            logging.error(f"[Validation] Ungültiges Datumsformat in {field}: {value}")
            raise HTTPException(status_code=422, detail=f"Ungültiges Datumsformat in {field}. Erwartet: YYYYMMDD.")
        if field == "PatientBirthDate" and value:
            try:
                if datetime.strptime(value, "%Y%m%d") > datetime.now():
                    logging.error("[Validation] Geburtsdatum liegt in der Zukunft.")
                    raise HTTPException(status_code=422, detail="Geburtsdatum liegt in der Zukunft.")
            except Exception as e:
                logging.error(f"[Validation] Fehler beim Parsen des Geburtsdatums: {str(e)}")
                raise HTTPException(status_code=422, detail="Ungültiges Geburtsdatum.")

    if hasattr(ds, "StudyTime"):
        value = str(ds.StudyTime)
        if value and not re.fullmatch(r"\d{6}(\.\d+)?", value):
            logging.error(f"[Validation] Ungültiges Zeitformat in StudyTime: {value}")
            raise HTTPException(status_code=422, detail="Ungültiges Zeitformat in StudyTime. Erwartet: HHMMSS.")


def check_uid_formats(ds: Dataset) -> None:
    for field in ["StudyInstanceUID", "SeriesInstanceUID", "SOPInstanceUID", "SOPClassUID"]:
        uid = getattr(ds, field, "")
        if uid and not re.fullmatch(r"^\d+(\.\d+)+$", uid):
            logging.error(f"[Validation] Ungültige UID in {field}: {uid}")
            raise HTTPException(status_code=422, detail=f"Ungültiges UID-Format in {field}.")


def check_modality(ds: Dataset) -> None:
    modality = getattr(ds, "Modality", "").upper()
    if modality and modality not in VALID_MODALITIES:
        logging.error(f"[Validation] Unbekannte oder ungültige Modalität: {modality}")
        raise HTTPException(status_code=422, detail=f"Unbekannte oder ungültige Modalität: {modality}.")


def check_pixeldata_presence(ds: Dataset, filename: str) -> None:
    if not hasattr(ds, "PixelData"):
        logging.error(f"[Validation] Fehlender 'PixelData' in Datei: {filename}")
        raise HTTPException(status_code=422, detail="Fehlender 'Pixel Data' (7FE0,0010) Tag.")
    verify_pixeldata_consistency(ds, filename)


def verify_pixeldata_consistency(ds: Dataset, filename: str) -> None:
    try:
        actual_length = len(ds.PixelData)
        rows = int(ds.get("Rows", 0))
        cols = int(ds.get("Columns", 0))
        samples = int(ds.get("SamplesPerPixel", 1))
        bits = int(ds.get("BitsAllocated", 16))
        expected_length = rows * cols * samples * (bits // 8)
        if actual_length != expected_length:
            logging.error(f"[Validation] PixelData-Länge inkonsistent: erwartet {expected_length}, gefunden {actual_length}")
            raise HTTPException(
                status_code=422,
                detail=f"PixelData-Länge inkonsistent: erwartet {expected_length} Byte, gefunden {actual_length} Byte."
            )
    except Exception as e:
        logging.error(f"[Validation] Fehler bei der Konsistenzprüfung der PixelData: {str(e)}")
        raise HTTPException(
            status_code=422,
            detail=f"Fehler bei der Konsistenzprüfung der PixelData: {str(e)}"
        )


def check_transfer_syntax(ds: Dataset) -> None:
    try:
        ts = str(ds.file_meta.TransferSyntaxUID)
        if ts not in TRANSFER_SYNTAX_UIDS:
            logging.warning(f"[TransferSyntax] Unbekannte Transfer Syntax UID: {ts}")
    except Exception as e:
        logging.warning(f"[TransferSyntax] Fehler bei TransferSyntax-Prüfung: {e}")


def log_private_tags(ds: Dataset, filename: str) -> None:
    for elem in ds.iterall():
        if elem.tag.is_private:
            logging.warning(f"[PrivateTag] {filename}: {elem.tag} = {elem.value}")

