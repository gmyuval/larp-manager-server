"""
Tests for database connectivity and session management.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.larp_manager_server.database import DatabaseManager, db_manager
from src.larp_manager_server.config import Settings


class TestDatabaseManager:
    """Test DatabaseManager class functionality."""
    
    @pytest.mark.asyncio
    async def test_database_manager_lifecycle(self):
        """Test database manager initialization and cleanup."""
        manager = DatabaseManager()
        
        # Initially not initialized
        assert manager.engine is None
        assert manager.session_factory is None
        assert not manager.is_initialized
        
        # Initialize
        await manager.initialize()
        assert manager.engine is not None
        assert manager.session_factory is not None
        assert manager.is_initialized
        
        # Clean up
        await manager.close()
        assert manager.engine is None
        assert manager.session_factory is None
        assert not manager.is_initialized
    
    @pytest.mark.asyncio
    async def test_database_manager_double_initialize(self):
        """Test that double initialization is handled gracefully."""
        manager = DatabaseManager()
        
        await manager.initialize()
        # Should not raise an exception
        await manager.initialize()
        
        assert manager.is_initialized
        await manager.close()
    
    @pytest.mark.asyncio
    async def test_database_manager_close_without_init(self):
        """Test closing without initialization."""
        manager = DatabaseManager()
        
        # Should not raise an exception
        await manager.close()
        assert not manager.is_initialized
    
    @pytest.mark.asyncio
    async def test_database_manager_health_check(self):
        """Test database manager health check."""
        manager = DatabaseManager()
        
        # Health check without initialization
        health = await manager.health_check()
        assert health["status"] == "unhealthy"
        assert health["error"] == "Database not initialized"
        
        # Initialize and check again
        await manager.initialize()
        try:
            health = await manager.health_check()
            # Should be healthy if database is available
            assert health["status"] in ["healthy", "unhealthy"]
            if health["status"] == "healthy":
                assert health["test_query"] is True
                assert "pool_stats" in health
        finally:
            await manager.close()
    
    @pytest.mark.asyncio
    async def test_database_manager_create_schema(self):
        """Test database manager schema creation."""
        manager = DatabaseManager()
        
        # Schema creation without initialization
        with pytest.raises(RuntimeError, match="Database not initialized"):
            await manager.create_schema()
        
        # Initialize and create schema
        await manager.initialize()
        try:
            await manager.create_schema()
            # Should not raise an exception
        finally:
            await manager.close()
    
    @pytest.mark.asyncio
    async def test_database_manager_get_session(self):
        """Test database manager session retrieval."""
        manager = DatabaseManager()
        
        # Session retrieval without initialization
        with pytest.raises(RuntimeError, match="Database not initialized"):
            async for session in manager.get_session():
                break
        
        await manager.initialize()
        try:
            async for session in manager.get_session():
                assert isinstance(session, AsyncSession)
                break
        finally:
            await manager.close()
    
    @pytest.mark.asyncio
    async def test_database_manager_get_engine(self):
        """Test database manager engine retrieval."""
        manager = DatabaseManager()
        
        # Engine retrieval without initialization
        with pytest.raises(RuntimeError, match="Database not initialized"):
            await manager.get_engine()
        
        await manager.initialize()
        try:
            engine = await manager.get_engine()
            assert engine is not None
            assert hasattr(engine, 'dispose')
        finally:
            await manager.close()
    
    @pytest.mark.asyncio
    async def test_database_manager_with_custom_settings(self):
        """Test database manager with custom settings."""
        # Create custom settings
        settings = Settings(
            database={
                "url": "sqlite+aiosqlite:///:memory:",
                "pool_size": 5,
                "max_overflow": 2,
            }
        )
        
        manager = DatabaseManager(settings=settings)
        
        await manager.initialize()
        try:
            assert manager.settings.database.pool_size == 5
            assert manager.settings.database.max_overflow == 2
            
            # Test that it can create an engine
            engine = await manager.get_engine()
            assert engine is not None
        finally:
            await manager.close()
    
    @pytest.mark.asyncio
    async def test_database_manager_execute_raw_sql(self):
        """Test raw SQL execution."""
        manager = DatabaseManager()
        
        # Raw SQL without initialization
        with pytest.raises(RuntimeError, match="Database not initialized"):
            await manager.execute_raw_sql("SELECT 1")
        
        await manager.initialize()
        try:
            result = await manager.execute_raw_sql("SELECT 1")
            assert result["success"] is True
            assert "result" in result
        finally:
            await manager.close()
    
    @pytest.mark.asyncio
    async def test_database_manager_execute_raw_sql_error(self):
        """Test raw SQL execution with error."""
        manager = DatabaseManager()
        
        await manager.initialize()
        try:
            # Execute invalid SQL
            result = await manager.execute_raw_sql("SELECT * FROM non_existent_table")
            assert result["success"] is False
            assert "error" in result
        finally:
            await manager.close()


class TestGlobalDatabaseManager:
    """Test global database manager instance."""
    
    @pytest.mark.asyncio
    async def test_global_db_manager_exists(self):
        """Test that global db_manager exists."""
        assert db_manager is not None
        assert isinstance(db_manager, DatabaseManager)
    
    @pytest.mark.asyncio
    async def test_global_db_manager_session(self):
        """Test global db_manager session functionality."""
        # Reset global manager
        await db_manager.close()
        
        # Test without initialization
        with pytest.raises(RuntimeError, match="Database not initialized"):
            async for session in db_manager.get_session():
                break
        
        # Initialize and test
        await db_manager.initialize()
        try:
            async for session in db_manager.get_session():
                assert isinstance(session, AsyncSession)
                break
        finally:
            await db_manager.close()