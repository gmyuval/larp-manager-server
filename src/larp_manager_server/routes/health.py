"""
Health check routes for LARP Manager Server.

This module provides health check endpoints for monitoring and
deployment readiness verification.
"""

import logging

from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

from larp_manager_server.database import db_manager

logger = logging.getLogger(__name__)


def setup_health_routes(app: FastAPI) -> None:
    """Set up health check routes."""
    
    @app.get("/health", tags=["health"])
    async def health_check():
        """Basic health check endpoint."""
        return {
            "status": "healthy",
            "service": "larp-manager-server",
            "version": "1.0.0"
        }
    
    @app.get("/health/db", tags=["health"])
    async def database_health_check():
        """Database health check endpoint."""
        try:
            health_result = await db_manager.health_check()
            
            if health_result["status"] == "healthy":
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={
                        "status": "healthy",
                        "database": health_result
                    }
                )
            else:
                return JSONResponse(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    content={
                        "status": "unhealthy",
                        "database": health_result
                    }
                )
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content={
                    "status": "unhealthy",
                    "database": {
                        "status": "unhealthy",
                        "error": str(e)
                    }
                }
            )
    
    @app.get("/health/ready", tags=["health"])
    async def readiness_check():
        """Readiness check endpoint for deployment."""
        try:
            # Check database connectivity
            db_health = await db_manager.health_check()
            
            if db_health["status"] != "healthy":
                return JSONResponse(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    content={
                        "status": "not_ready",
                        "reason": "Database not healthy",
                        "database": db_health
                    }
                )
            
            # Additional readiness checks can be added here
            
            return {
                "status": "ready",
                "service": "larp-manager-server",
                "database": db_health
            }
            
        except Exception as e:
            logger.error(f"Readiness check failed: {e}")
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content={
                    "status": "not_ready",
                    "reason": str(e)
                }
            )
    
    @app.get("/health/live", tags=["health"])
    async def liveness_check():
        """Liveness check endpoint for deployment."""
        # This should be a simple check that the application is running
        # and can handle requests
        return {
            "status": "alive",
            "service": "larp-manager-server"
        }