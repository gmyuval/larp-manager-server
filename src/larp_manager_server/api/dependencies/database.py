"""
Database-related dependencies for LARP Manager Server.

This module provides FastAPI dependencies for database operations.
"""

import logging
from typing import AsyncGenerator

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from larp_manager_server.database import db_manager

logger = logging.getLogger(__name__)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Get database session dependency.
    
    This dependency provides a database session for each request
    and ensures proper cleanup and error handling.
    """
    async for session in db_manager.get_session():
        yield session


async def get_db_session_with_error_handling() -> AsyncGenerator[AsyncSession, None]:
    """
    Get database session with comprehensive error handling.
    
    This dependency provides a database session with automatic error handling
    and transaction management for endpoints that need extra protection.
    """
    async for session in db_manager.get_session():
        try:
            yield session
        except Exception as e:
            await session.rollback()
            logger.error(f"Database error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database operation failed"
            )
        finally:
            await session.close()