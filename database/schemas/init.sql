CREATE TABLE IF NOT EXISTS ki_image_metadata (
    image_id int PRIMARY KEY,
    image_name VARCHAR(255) NOT NULL,
    image_tag VARCHAR NOT NULL,
    description VARCHAR(255),
    image_path VARCHAR(255),
    local_image_name VARCHAR(255), 
    provider_id int 
);

    