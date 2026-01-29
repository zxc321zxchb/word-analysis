"""Application configuration."""
import os
from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # Database
    database_url: str = "mysql+pymysql://doc_user:doc_password@localhost:3306/doc_analysis"

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_prefix: str = "/api/v1"

    # CORS
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:8080"]

    # File Upload
    max_file_size_mb: int = 50  # Maximum file size in MB
    max_upload_size_mb: int = 100  # Maximum total upload size in MB
    allowed_mime_types: List[str] = [
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/octet-stream",
    ]

    # Pagination
    max_page_size: int = 100
    default_page_size: int = 10

    # Document Parser
    max_heading_level: int = 9  # Maximum heading level supported (1-9)

    # Content Format
    content_format: str = "both"  # "html", "json", or "both"

    # Gzip Compression
    enable_gzip: bool = True
    gzip_min_size: int = 1000  # Minimum response size in bytes to trigger gzip
    gzip_level: int = 6  # Compression level 1-9 (9 = max compression)

    # Logging
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
