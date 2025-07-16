"""
Database configuration settings for LARP Manager Server.

This module provides database-specific configuration using Pydantic Settings.
"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    """Database configuration settings."""
    
    url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/larp_manager_db",
        description="Database connection URL"
    )
    pool_size: int = Field(default=20, description="Database connection pool size")
    max_overflow: int = Field(default=0, description="Maximum overflow connections")
    pool_timeout: int = Field(default=30, description="Pool timeout in seconds")
    pool_recycle: int = Field(default=1800, description="Pool recycle time in seconds")
    
    model_config = SettingsConfigDict(env_prefix="DATABASE_")