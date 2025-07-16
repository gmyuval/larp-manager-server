"""
Main FastAPI application for LARP Manager Server.

This module provides the application entry point and basic configuration.
Most functionality has been moved to specialized modules for better organization.
"""

from larp_manager_server.app_factory import create_app
from larp_manager_server.logging_config import setup_logging

# Set up logging
setup_logging()

# Create the FastAPI app instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    
    from larp_manager_server.config import get_settings
    
    settings = get_settings()
    
    uvicorn.run(
        "src.larp_manager_server.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.logging.level.lower(),
    )