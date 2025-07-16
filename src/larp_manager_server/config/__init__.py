"""
Configuration package for LARP Manager Server.

This package provides configuration management organized into specialized modules:

- config.database: Database configuration settings
- config.security: Security configuration settings
- config.logging: Logging configuration settings
- config.settings: Main application settings that combines all other settings

This __init__.py provides convenient imports for the most commonly used configuration.
For specific functionality, import from the specialized modules directly.
"""

# Import all settings classes
from larp_manager_server.config.database import DatabaseSettings
from larp_manager_server.config.security import SecuritySettings
from larp_manager_server.config.logging import LoggingSettings
from larp_manager_server.config.settings import Settings

# Create global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings."""
    return settings


# Export commonly used items
__all__ = [
    "DatabaseSettings",
    "SecuritySettings", 
    "LoggingSettings",
    "Settings",
    "settings",
    "get_settings",
]