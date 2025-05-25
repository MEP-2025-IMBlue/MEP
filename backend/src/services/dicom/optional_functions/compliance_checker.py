# import logging
# from datetime import datetime
# from fastapi import HTTPException
# from pydicom.dataset import Dataset

# # DSGVO-relevante Felder in DICOM-Dateien
# DSGVO_FIELDS = [
#     "PatientName", "PatientID", "InstitutionName", "ReferringPhysicianName",
#     "AccessionNumber", "InstitutionAddress"
# ]

# # Typische Werte, die auf eine Anonymisierung hindeuten
# ANONYMIZED_VALUES = {"ANONYMIZED", "ANONYMOUS", "XXXX", "****", "REMOVED", "N/A", "DEIDENTIFIED"}

# def check_compliance(ds: Dataset, filename: str) -> None:
#     logging.info(f"[Compliance] Starte DSGVO/HIPAA-Prüfung für Datei: {filename}")

#     anonymization_log = []
#     for field in DSGVO_FIELDS:
#         value = getattr(ds, field, None)
#         if value and str(value).strip().upper() in ANONYMIZED_VALUES:
#             anonymization_log.append({
#                 "field": field,
#                 "status": "anonymized",
#                 "value": str(value),
#                 "timestamp": datetime.utcnow().isoformat()
#             })

#     if anonymization_log:
#         logging.info(f"[Audit] Anonymisierungsprotokoll für Datei {filename}: {anonymization_log}")
#     else:
#         logging.warning(f"[Compliance] Keine Anonymisierung nachweisbar in Datei {filename}.")

#     compliance_issues = []

#     # Prüfung 1: Anonymisierung erfolgt?
#     if not anonymization_log:
#         compliance_issues.append("Keine Anonymisierung der sensiblen Felder nachweisbar.")

#     # Prüfung 2: Nutzer über Verarbeitung informiert? (Platzhalter für UI-Session)
#     user_informed = True  # TODO: Aus Session oder UI übernehmen
#     if not user_informed:
#         compliance_issues.append("Nutzer wurde nicht über die Datenverarbeitung informiert.")

#     # Prüfung 3: Einwilligung vorhanden? (z. B. Checkbox im Upload-Dialog)
#     consent_given = True  # TODO: Implementierung via Frontend notwendig
#     if not consent_given:
#         compliance_issues.append("Einwilligung zur Datenverarbeitung fehlt.")

#     if compliance_issues:
#         logging.error(f"[Compliance] Konformitätsprobleme in Datei {filename}: {compliance_issues}")
#         raise HTTPException(
#             status_code=422,
#             detail=f"DSGVO/HIPAA compliance issues: {compliance_issues}"
#         )
#     else:
#         logging.info(f"[Compliance] DSGVO/HIPAA-Grundanforderungen erfüllt für Datei: {filename}")

