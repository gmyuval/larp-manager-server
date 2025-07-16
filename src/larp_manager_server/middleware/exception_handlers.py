"""
Global exception handlers for LARP Manager Server.

This module provides centralized exception handling for the FastAPI application.
"""

import logging

from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

from larp_manager_server.config import get_settings

logger = logging.getLogger(__name__)


def setup_exception_handlers(app: FastAPI) -> None:
    """Set up global exception handlers for the application."""
    
    @app.exception_handler(Exception)
    async def global_exception_handler(request, exc):
        """Global exception handler for unhandled exceptions."""
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        
        settings = get_settings()
        
        if settings.debug:
            # In debug mode, return detailed error information
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "error": "Internal server error",
                    "detail": str(exc),
                    "type": type(exc).__name__
                }
            )
        else:
            # In production, return generic error message
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "error": "Internal server error",
                    "detail": "An unexpected error occurred"
                }
            )