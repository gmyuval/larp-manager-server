"""
Main application settings for LARP Manager Server.

This module provides the main application configuration that combines
all other configuration modules.
"""

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from larp_manager_server.config.database import DatabaseSettings
from larp_manager_server.config.security import SecuritySettings
from larp_manager_server.config.logging import LoggingSettings


class Settings(BaseSettings):
    """Main application settings."""
    
    # Application settings
    project_name: str = Field(default="LARP Manager Server", description="Project name")
    debug: bool = Field(default=False, description="Debug mode")
    api_v1_prefix: str = Field(default="/api/v1", description="API v1 prefix")
    
    # Environment
    environment: str = Field(default="development", description="Environment")
    
    # CORS settings
    cors_origins: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080"],
        description="CORS allowed origins"
    )
    cors_allow_credentials: bool = Field(
        default=True,
        description="Allow credentials in CORS"
    )
    cors_allow_methods: list[str] = Field(
        default=["*"],
        description="CORS allowed methods"
    )
    cors_allow_headers: list[str] = Field(
        default=["*"],
        description="CORS allowed headers"
    )
    
    # Nested settings
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    security: SecuritySettings = Field(default_factory=SecuritySettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    
    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v):
        """Validate environment."""
        valid_environments = ["development", "staging", "production", "testing"]
        if v.lower() not in valid_environments:
            raise ValueError(f"Invalid environment: {v}. Must be one of {valid_environments}")
        return v.lower()
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment == "development"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == "production"
    
    @property
    def is_testing(self) -> bool:
        """Check if running in testing environment."""
        return self.environment == "testing"