-- init.sql

-- =========================
-- Tabelle: ki_image_metadata
-- =========================
CREATE TABLE IF NOT EXISTS ki_image_metadata (
    image_id SERIAL PRIMARY KEY,
    image_name VARCHAR(255) NOT NULL,
    image_tag VARCHAR(128) NOT NULL,
    image_description VARCHAR(500),
    image_path VARCHAR(500),
    image_local_name VARCHAR(255),
    image_provider_id INTEGER NOT NULL
);

-- =========================
-- Tabelle: dicom_metadata
-- =========================
CREATE TABLE IF NOT EXISTS dicom_metadata (
    dicom_id SERIAL PRIMARY KEY,
    dicom_uuid VARCHAR(64) NOT NULL UNIQUE,
    dicom_modality VARCHAR(50),
    dicom_body_part_examined VARCHAR(100),
    dicom_study_description VARCHAR(255),
    dicom_model VARCHAR(128)
);
