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
    image_provider_id INTEGER NOT NULL,
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