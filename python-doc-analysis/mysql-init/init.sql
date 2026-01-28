-- Initialize database schema for document analysis project

-- Create database if not exists
CREATE DATABASE IF NOT EXISTS doc_analysis CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Use the database
USE doc_analysis;

-- Create documents table
CREATE TABLE IF NOT EXISTS documents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    filename VARCHAR(255) NOT NULL COMMENT 'Stored filename',
    original_filename VARCHAR(255) NOT NULL COMMENT 'Original filename',
    file_hash VARCHAR(64) UNIQUE COMMENT 'File SHA256 hash for deduplication',
    file_size BIGINT COMMENT 'File size in bytes',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    parsed_at TIMESTAMP NULL,
    INDEX idx_filename (filename),
    INDEX idx_hash (file_hash)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Document table';

-- Create numbered_sections table
CREATE TABLE IF NOT EXISTS numbered_sections (
    id INT AUTO_INCREMENT PRIMARY KEY,
    document_id INT NOT NULL COMMENT 'Document ID',
    number_path VARCHAR(64) NOT NULL COMMENT 'Number path like 1, 1.1, 1.1.1',
    level INT NOT NULL COMMENT 'Hierarchy level, 0 is top',
    parent_id INT NULL COMMENT 'Parent section ID',
    title VARCHAR(512) COMMENT 'Section title',
    content_html LONGTEXT COMMENT 'HTML format content',
    content_json LONGTEXT COMMENT 'JSON format content for rich text editor',
    sort_order INT NOT NULL COMMENT 'Sort order',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE,
    FOREIGN KEY (parent_id) REFERENCES numbered_sections(id) ON DELETE CASCADE,
    INDEX idx_document (document_id),
    INDEX idx_parent (parent_id),
    INDEX idx_sort (sort_order),
    UNIQUE KEY unique_doc_number (document_id, number_path)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Numbered section table';

-- Create section_tables table
CREATE TABLE IF NOT EXISTS section_tables (
    id INT AUTO_INCREMENT PRIMARY KEY,
    section_id INT NOT NULL COMMENT 'Section ID',
    table_index INT NOT NULL COMMENT 'Table order in section',
    row_count INT NOT NULL COMMENT 'Number of rows',
    col_count INT NOT NULL COMMENT 'Number of columns',
    html TEXT COMMENT 'Table HTML',
    json_data LONGTEXT COMMENT 'Table JSON data',
    sort_order INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (section_id) REFERENCES numbered_sections(id) ON DELETE CASCADE,
    INDEX idx_section (section_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Section table table';

-- Create section_images table
CREATE TABLE IF NOT EXISTS section_images (
    id INT AUTO_INCREMENT PRIMARY KEY,
    section_id INT NOT NULL COMMENT 'Section ID',
    image_index INT NOT NULL COMMENT 'Image order in section',
    filename VARCHAR(255) NOT NULL COMMENT 'Original filename',
    mime_type VARCHAR(64) NOT NULL COMMENT 'MIME type',
    base64_data LONGTEXT NOT NULL COMMENT 'Base64 encoded image data',
    width INT COMMENT 'Width in pixels',
    height INT COMMENT 'Height in pixels',
    sort_order INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (section_id) REFERENCES numbered_sections(id) ON DELETE CASCADE,
    INDEX idx_section (section_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Section image table';

-- Grant privileges to doc_user
GRANT ALL PRIVILEGES ON doc_analysis.* TO 'doc_user'@'%';
FLUSH PRIVILEGES;
