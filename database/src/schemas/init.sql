CREATE TABLE IF NOT EXISTS ki_image_metadata (
    image_id VARCHAR PRIMARY KEY,
    image_name VARCHAR(255) NOT NULL,
    tag VARCHAR(128) NOT NULL,
    repository VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    size INTEGER NOT NULL,
    architecture VARCHAR(32),
    os VARCHAR(32)
);