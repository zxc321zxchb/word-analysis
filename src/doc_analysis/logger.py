"""Logging configuration for the application."""

import logging
import sys
from typing import Any

from src.doc_analysis.config import settings


def setup_logging() -> None:
    """Configure application logging with structured format."""
    logging.basicConfig(
        level=settings.log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the given name.

    Args:
        name: Logger name, typically __name__ of the module

    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)
