"""
Logging configuration for LARP Manager Server.

This module provides centralized logging configuration that can be
used across the application.
"""

import logging
from typing import Dict, Any

from larp_manager_server.config import get_settings


def setup_logging() -> None:
    """Set up logging configuration for the application."""
    settings = get_settings()
    
    # Configure logging based on settings
    logging.basicConfig(
        level=getattr(logging, settings.logging.level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Set up specific logger levels if needed
    if settings.debug:
        # In debug mode, show more detailed logging
        logging.getLogger("uvicorn").setLevel(logging.DEBUG)
        logging.getLogger("fastapi").setLevel(logging.DEBUG)
    else:
        # In production, reduce noise from external libraries
        logging.getLogger("uvicorn.access").setLevel(logging.WARNING)


def get_logger_config() -> Dict[str, Any]:
    """Get logging configuration dictionary for external tools."""
    settings = get_settings()
    
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            },
            "json": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                # JSON formatter would be implemented here if needed
            },
        },
        "handlers": {
            "default": {
                "formatter": "default",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
            },
        },
        "root": {
            "level": settings.logging.level,
            "handlers": ["default"],
        },
        "loggers": {
            "larp_manager_server": {
                "level": settings.logging.level,
                "handlers": ["default"],
                "propagate": False,
            },
        },
    }