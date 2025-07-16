"""
Application factory for LARP Manager Server.

This module provides the main application factory function that creates
and configures the FastAPI application instance.
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from larp_manager_server.config import get_settings
from larp_manager_server.database import db_manager
from larp_manager_server.middleware.exception_handlers import setup_exception_handlers
from larp_manager_server.routes.health import setup_health_routes

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan manager.
    
    Handles startup and shutdown events for the FastAPI application.
    """
    # Startup
    logger.info("Starting LARP Manager Server...")
    
    try:
        # Initialize database
        await db_manager.initialize()
        
        # Create larp_manager schema if it doesn't exist
        await db_manager.create_schema()
        
        logger.info("Database initialized successfully")
        
        # Additional startup tasks can be added here
        
        logger.info("LARP Manager Server started successfully")
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down LARP Manager Server...")
    
    try:
        # Close database connections
        await db_manager.close()
        logger.info("Database connections closed")
        
        # Additional shutdown tasks can be added here
        
        logger.info("LARP Manager Server shut down successfully")
        
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()
    
    # Create FastAPI app
    app = FastAPI(
        title=settings.project_name,
        description="A comprehensive LARP (Live Action Role Playing) management system",
        version="1.0.0",
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        openapi_url="/openapi.json" if settings.debug else None,
        lifespan=lifespan,
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=settings.cors_allow_methods,
        allow_headers=settings.cors_allow_headers,
    )
    
    # Set up exception handlers
    setup_exception_handlers(app)
    
    # Add health check routes
    setup_health_routes(app)
    
    # Add API routes (placeholder for future phases)
    # app.include_router(api_router, prefix=settings.api_v1_prefix)
    
    return app