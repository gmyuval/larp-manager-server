"""
Tests for configuration management.
"""

import pytest
from pydantic import ValidationError

from src.larp_manager_server.config import Settings, DatabaseSettings, SecuritySettings, LoggingSettings


class TestDatabaseSettings:
    """Test database configuration settings."""
    
    def test_default_values(self):
        """Test default database settings."""
        db_settings = DatabaseSettings()
        
        assert db_settings.url == "postgresql+asyncpg://postgres:postgres@localhost:5432/larp_manager_db"
        assert db_settings.pool_size == 20
        assert db_settings.max_overflow == 0
        assert db_settings.pool_timeout == 30
        assert db_settings.pool_recycle == 1800
    
    def test_custom_values(self):
        """Test custom database settings."""
        db_settings = DatabaseSettings(
            url="postgresql+asyncpg://user:pass@host:5432/db",
            pool_size=10,
            max_overflow=5,
        )
        
        assert db_settings.url == "postgresql+asyncpg://user:pass@host:5432/db"
        assert db_settings.pool_size == 10
        assert db_settings.max_overflow == 5


class TestSecuritySettings:
    """Test security configuration settings."""
    
    def test_default_values(self):
        """Test default security settings."""
        security_settings = SecuritySettings()
        
        assert security_settings.secret_key == "your-secret-key-here-change-in-production"
        assert security_settings.algorithm == "HS256"
        assert security_settings.access_token_expire_minutes == 30
        assert security_settings.refresh_token_expire_days == 30
    
    def test_custom_values(self):
        """Test custom security settings."""
        security_settings = SecuritySettings(
            secret_key="custom-secret-key",
            algorithm="RS256",
            access_token_expire_minutes=60,
        )
        
        assert security_settings.secret_key == "custom-secret-key"
        assert security_settings.algorithm == "RS256"
        assert security_settings.access_token_expire_minutes == 60


class TestLoggingSettings:
    """Test logging configuration settings."""
    
    def test_default_values(self):
        """Test default logging settings."""
        logging_settings = LoggingSettings()
        
        assert logging_settings.level == "INFO"
        assert logging_settings.format == "json"
    
    def test_level_validation(self):
        """Test log level validation."""
        # Valid levels
        for level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            settings = LoggingSettings(level=level)
            assert settings.level == level
        
        # Case insensitive
        settings = LoggingSettings(level="debug")
        assert settings.level == "DEBUG"
        
        # Invalid level
        with pytest.raises(ValidationError):
            LoggingSettings(level="INVALID")
    
    def test_format_validation(self):
        """Test log format validation."""
        # Valid formats
        for fmt in ["json", "text"]:
            settings = LoggingSettings(format=fmt)
            assert settings.format == fmt
        
        # Case insensitive
        settings = LoggingSettings(format="JSON")
        assert settings.format == "json"
        
        # Invalid format
        with pytest.raises(ValidationError):
            LoggingSettings(format="invalid")


class TestSettings:
    """Test main application settings."""
    
    def test_default_values(self):
        """Test default application settings."""
        settings = Settings()
        
        assert settings.project_name == "LARP Manager Server"
        assert settings.debug is False
        assert settings.api_v1_prefix == "/api/v1"
        assert settings.environment == "development"
        assert settings.cors_origins == ["http://localhost:3000", "http://localhost:8080"]
        assert settings.cors_allow_credentials is True
        assert settings.cors_allow_methods == ["*"]
        assert settings.cors_allow_headers == ["*"]
    
    def test_environment_validation(self):
        """Test environment validation."""
        # Valid environments
        for env in ["development", "staging", "production", "testing"]:
            settings = Settings(environment=env)
            assert settings.environment == env
        
        # Case insensitive
        settings = Settings(environment="PRODUCTION")
        assert settings.environment == "production"
        
        # Invalid environment
        with pytest.raises(ValidationError):
            Settings(environment="invalid")
    
    def test_environment_properties(self):
        """Test environment property methods."""
        # Development
        settings = Settings(environment="development")
        assert settings.is_development is True
        assert settings.is_production is False
        assert settings.is_testing is False
        
        # Production
        settings = Settings(environment="production")
        assert settings.is_development is False
        assert settings.is_production is True
        assert settings.is_testing is False
        
        # Testing
        settings = Settings(environment="testing")
        assert settings.is_development is False
        assert settings.is_production is False
        assert settings.is_testing is True
    
    def test_nested_settings(self):
        """Test nested settings configuration."""
        settings = Settings()
        
        # Check nested settings are properly initialized
        assert isinstance(settings.database, DatabaseSettings)
        assert isinstance(settings.security, SecuritySettings)
        assert isinstance(settings.logging, LoggingSettings)
        
        # Check that nested settings have default values
        assert settings.database.pool_size == 20
        assert settings.security.algorithm == "HS256"
        assert settings.logging.level == "INFO"
    
    def test_custom_nested_settings(self):
        """Test custom nested settings configuration."""
        settings = Settings(
            database=DatabaseSettings(pool_size=50),
            security=SecuritySettings(algorithm="RS256"),
            logging=LoggingSettings(level="DEBUG"),
        )
        
        assert settings.database.pool_size == 50
        assert settings.security.algorithm == "RS256"
        assert settings.logging.level == "DEBUG"