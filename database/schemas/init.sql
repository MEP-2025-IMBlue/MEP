-- init.sql

-- =========================
-- Tabelle: ki_image_metadata
-- =========================
CREATE TABLE IF NOT EXISTS ki_image_metadata (
    image_id SERIAL PRIMARY KEY,
    image_name VARCHAR(255) NOT NULL,
    image_tag VARCHAR(128) NOT NULL,
    image_description VARCHAR(500),
    image_reference VARCHAR(255),
    image_provider_id VARCHAR(36) NOT NULL,  -- speichert die UUID des Providers als String (Keycloak user_id)
    image_created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =========================
-- Tabelle: dicom_metadata
-- =========================
CREATE TABLE IF NOT EXISTS dicom_metadata (
    dicom_id SERIAL PRIMARY KEY,
    dicom_modality VARCHAR(10),
    dicom_sop_class_uid VARCHAR(64),
    dicom_manufacturer VARCHAR(100),
    dicom_rows INTEGER,
    dicom_columns INTEGER,
    dicom_bits_allocated INTEGER,
    dicom_photometric_interpretation VARCHAR(20),
    dicom_transfer_syntax_uid VARCHAR(64),
    dicom_file_path VARCHAR(255),
    dicom_created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Hinweis:
-- Das Feld image_provider_id speichert NICHT einen Integer,
-- sondern die vom Auth-System (Keycloak) generierte UUID des Providers.
-- Owner-Prüfung und Berechtigung im Backend erfolgen stets mit diesem Wert.