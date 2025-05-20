import logging
import pydicom

# Diese Funktion anonymisiert sensible DICOM-Felder gemäß DSGVO / HIPAA
def anonymize_dicom_fields(ds: pydicom.Dataset) -> pydicom.Dataset:
    """
    Entfernt oder ersetzt personenbezogene Informationen aus dem DICOM-Dataset.
    Alle ersetzten Felder werden mit dem Wert "ANONYMIZED" befüllt und protokolliert.
    """
    tags_to_anonymize = [
        "PatientName",              # Name des Patienten
        "PatientID",                # Interne ID
        "PatientBirthDate",         # Geburtsdatum
        "InstitutionName",          # Name der Klinik
        "ReferringPhysicianName",   # Überweisender Arzt
        "OtherPatientIDs",          # Weitere IDs
        "AccessionNumber",          # Zugriffsnummer
        "OperatorsName",            # Bedienername
        "PatientAddress",           # Adresse
        "IssuerOfPatientID",        # ID-Aussteller
        "StudyID"                   # Studiennummer
    ]

    for tag in tags_to_anonymize:
        if tag in ds:
            original_value = str(ds.get(tag, ""))
            ds.data_element(tag).value = "ANONYMIZED"
            logging.info(f"[Anonymizer] Feld '{tag}' anonymisiert (alt: {original_value})")

    return ds
