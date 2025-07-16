"""
Database connection and session management for LARP Manager Server.

This module provides async database connectivity using SQLAlchemy 2.0 with AsyncPG.
It includes connection pooling, session management, and health check functionality.
"""

import logging
from typing import AsyncGenerator, Optional

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from larp_manager_server.config import Settings, get_settings

logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    Database manager for handling lifecycle and operations.
    
    This class encapsulates all database-related functionality including
    connection management, session handling, and health checks.
    """
    
    def __init__(self, settings: Optional[Settings] = None):
        """
        Initialize the database manager.
        
        Args:
            settings: Optional settings object. If None, will use get_settings()
        """
        self.settings = settings or get_settings()
        self.engine: Optional[AsyncEngine] = None
        self.session_factory: Optional[async_sessionmaker[AsyncSession]] = None
        self._initialized = False
    
    async def initialize(self) -> None:
        """Initialize the database connection and session factory."""
        if self._initialized:
            logger.warning("Database manager already initialized")
            return
        
        self.engine = await self._create_engine()
        self.session_factory = self._create_session_factory()
        self._initialized = True
        
        logger.info("Database manager initialized successfully")
    
    async def close(self) -> None:
        """Close the database connection and cleanup resources."""
        if not self._initialized:
            logger.warning("Database manager not initialized")
            return
        
        if self.engine:
            await self.engine.dispose()
            logger.info("Database engine disposed")
        
        self.engine = None
        self.session_factory = None
        self._initialized = False
        
        logger.info("Database manager closed")
    
    async def _create_engine(self) -> AsyncEngine:
        """Create and configure the database engine."""
        engine = create_async_engine(
            self.settings.database.url,
            pool_size=self.settings.database.pool_size,
            max_overflow=self.settings.database.max_overflow,
            pool_timeout=self.settings.database.pool_timeout,
            pool_recycle=self.settings.database.pool_recycle,
            echo=self.settings.debug,
            future=True,
        )
        
        logger.info(f"Database engine created with pool_size={self.settings.database.pool_size}")
        return engine
    
    def _create_session_factory(self) -> async_sessionmaker[AsyncSession]:
        """Create the session factory."""
        if self.engine is None:
            raise RuntimeError("Engine not initialized")
        
        return async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
    
    def _ensure_initialized(self) -> None:
        """Ensure the database manager is initialized."""
        if not self._initialized:
            raise RuntimeError("Database not initialized. Call initialize() first.")
    
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Get a database session with proper lifecycle management.
        
        This method provides a database session for each request
        and ensures proper cleanup and error handling.
        
        Yields:
            AsyncSession: A database session
        """
        self._ensure_initialized()
        
        if self.session_factory is None:
            raise RuntimeError("Session factory not initialized")
        
        async with self.session_factory() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    
    async def health_check(self) -> dict:
        """
        Check database connectivity and health.
        
        Returns:
            dict: Health check results with status and details
        """
        if not self._initialized or self.engine is None:
            return {
                "status": "unhealthy",
                "error": "Database not initialized",
                "details": None
            }
        
        try:
            async with self.engine.begin() as conn:
                # Test basic connectivity
                result = await conn.execute(text("SELECT 1"))
                test_value = result.scalar()
                
                # Check if we can access the larp_manager schema
                schema_check = await conn.execute(
                    text("SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'larp_manager'")
                )
                schema_exists = schema_check.scalar() is not None
                
                # Get connection pool stats
                pool = self.engine.pool
                pool_stats = {
                    "pool_size": pool.size(),
                    "checked_in": pool.checkedin(),
                    "checked_out": pool.checkedout(),
                    "overflow": pool.overflow(),
                    "invalid": pool.invalid(),
                }
                
                return {
                    "status": "healthy",
                    "test_query": test_value == 1,
                    "schema_exists": schema_exists,
                    "pool_stats": pool_stats,
                    "error": None
                }
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "details": None
            }
    
    async def create_schema(self) -> None:
        """Create the larp_manager schema if it doesn't exist."""
        self._ensure_initialized()
        
        if self.engine is None:
            raise RuntimeError("Engine not initialized")
        
        try:
            async with self.engine.begin() as conn:
                # Create schema if it doesn't exist
                await conn.execute(text("CREATE SCHEMA IF NOT EXISTS larp_manager"))
                
                # Install UUID extension if needed
                await conn.execute(text("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\""))
                
                logger.info("larp_manager schema created successfully")
        except Exception as e:
            logger.error(f"Failed to create larp_manager schema: {e}")
            raise
    
    async def get_engine(self) -> AsyncEngine:
        """
        Get the database engine.
        
        Returns:
            AsyncEngine: The database engine
        """
        self._ensure_initialized()
        
        if self.engine is None:
            raise RuntimeError("Engine not initialized")
        
        return self.engine
    
    @property
    def is_initialized(self) -> bool:
        """Check if the database manager is initialized."""
        return self._initialized
    
    async def execute_raw_sql(self, sql: str) -> dict:
        """
        Execute raw SQL and return results.
        
        Args:
            sql: The SQL query to execute
            
        Returns:
            dict: Query results
        """
        self._ensure_initialized()
        
        if self.engine is None:
            raise RuntimeError("Engine not initialized")
        
        try:
            async with self.engine.begin() as conn:
                result = await conn.execute(text(sql))
                return {"success": True, "result": result.fetchall()}
        except Exception as e:
            logger.error(f"Raw SQL execution failed: {e}")
            return {"success": False, "error": str(e)}


# Global database manager instance
db_manager = DatabaseManager()