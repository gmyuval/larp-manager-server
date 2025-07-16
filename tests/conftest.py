"""
Test configuration and fixtures for LARP Manager Server tests.
"""

import asyncio
import pytest
from typing import AsyncGenerator
from unittest.mock import MagicMock

from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.larp_manager_server.config import Settings
from src.larp_manager_server.api.dependencies import get_db_session
from src.larp_manager_server.models.base import Base
from src.larp_manager_server.main import app


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_settings():
    """Provide test settings."""
    return Settings(
        project_name="LARP Manager Server Test",
        environment="testing",
        debug=True,
        database={
            "url": "sqlite+aiosqlite:///:memory:",
            "pool_size": 1,
            "max_overflow": 0,
        },
        security={
            "secret_key": "test-secret-key",
            "algorithm": "HS256",
        },
        logging={
            "level": "DEBUG",
            "format": "text",
        }
    )


@pytest.fixture
async def test_engine(test_settings):
    """Create test database engine."""
    engine = create_async_engine(
        test_settings.database.url,
        echo=test_settings.debug,
        future=True,
    )
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Clean up
    await engine.dispose()


@pytest.fixture
async def test_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create test database session."""
    async_session = sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    async with async_session() as session:
        yield session


@pytest.fixture
def mock_db_session():
    """Create mock database session for unit tests."""
    session = MagicMock(spec=AsyncSession)
    session.begin = MagicMock()
    session.commit = MagicMock()
    session.rollback = MagicMock()
    session.close = MagicMock()
    return session


@pytest.fixture
def client(test_session):
    """Create test client with dependency overrides."""
    async def override_get_db():
        yield test_session
    
    app.dependency_overrides[get_db_session] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    # Clean up
    app.dependency_overrides.clear()


@pytest.fixture
def mock_client():
    """Create test client without database dependencies."""
    with TestClient(app) as test_client:
        yield test_client


# Test data fixtures
@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "full_name": "Test User",
        "password": "testpassword123",
    }


@pytest.fixture
def sample_game_data():
    """Sample game data for testing."""
    return {
        "name": "Test LARP Game",
        "description": "A test LARP game for testing purposes",
        "start_date": "2024-06-01T10:00:00Z",
        "end_date": "2024-06-01T18:00:00Z",
        "max_players": 20,
        "cost": 50.00,
    }


# Async test utilities
@pytest.fixture
def async_mock():
    """Create async mock function."""
    async def _async_mock(*args, **kwargs):
        return MagicMock()
    return _async_mock


# Test markers
pytest.mark.unit = pytest.mark.unit
pytest.mark.integration = pytest.mark.integration
pytest.mark.slow = pytest.mark.slow