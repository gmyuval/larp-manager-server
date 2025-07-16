#!/usr/bin/env python3
"""
Development server runner for LARP Manager Server.

This script provides a convenient way to run the development server with
proper environment setup and configuration.
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.larp_manager_server.config import get_settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def check_environment():
    """Check if the environment is properly set up."""
    logger.info("Checking environment setup...")
    
    # Check if virtual environment is active
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        logger.warning("⚠️  Virtual environment not detected. Consider using a virtual environment.")
    
    # Check if required packages are installed
    required_packages = ["fastapi", "uvicorn", "sqlalchemy", "asyncpg", "alembic"]
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        logger.error(f"❌ Missing required packages: {', '.join(missing_packages)}")
        logger.error("Please install dependencies with: pip install -r requirements-dev.txt")
        return False
    
    logger.info("✅ Environment check passed")
    return True


def setup_environment_variables():
    """Set up environment variables for development."""
    logger.info("Setting up development environment variables...")
    
    # Set default environment variables if not already set
    default_env_vars = {
        "ENVIRONMENT": "development",
        "DEBUG": "true",
        "LOG_LEVEL": "DEBUG",
        "DATABASE_URL": "postgresql+asyncpg://postgres:postgres@localhost:5432/larp_manager_db",
    }
    
    for key, value in default_env_vars.items():
        if key not in os.environ:
            os.environ[key] = value
            logger.info(f"Set {key}={value}")
    
    # Load .env file if it exists
    env_file = project_root / ".env"
    if env_file.exists():
        logger.info("Loading environment variables from .env file")
        try:
            from dotenv import load_dotenv
            load_dotenv(env_file)
        except ImportError:
            logger.warning("python-dotenv not installed. Skipping .env file loading.")


def run_server(host="0.0.0.0", port=8000, reload=True, log_level="info"):
    """Run the development server."""
    logger.info(f"Starting development server on {host}:{port}")
    
    try:
        import uvicorn
        
        # Configure uvicorn
        uvicorn.run(
            "src.larp_manager_server.main:app",
            host=host,
            port=port,
            reload=reload,
            log_level=log_level,
            reload_dirs=[str(project_root / "src")],
            access_log=True,
        )
    except ImportError:
        logger.error("❌ uvicorn not installed. Please install it with: pip install uvicorn")
        return 1
    except Exception as e:
        logger.error(f"❌ Failed to start server: {e}")
        return 1


def main():
    """Main function to run the development server."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run LARP Manager Server development server")
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host to bind to (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind to (default: 8000)"
    )
    parser.add_argument(
        "--no-reload",
        action="store_true",
        help="Disable auto-reload"
    )
    parser.add_argument(
        "--log-level",
        default="info",
        choices=["critical", "error", "warning", "info", "debug", "trace"],
        help="Log level (default: info)"
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Only check environment, don't start server"
    )
    
    args = parser.parse_args()
    
    logger.info("🚀 Starting LARP Manager Server development environment...")
    
    # Check environment
    if not check_environment():
        return 1
    
    # Setup environment variables
    setup_environment_variables()
    
    if args.check_only:
        logger.info("✅ Environment check completed")
        return 0
    
    # Print configuration information
    try:
        settings = get_settings()
        logger.info(f"Environment: {settings.environment}")
        logger.info(f"Debug mode: {settings.debug}")
        logger.info(f"Database URL: {settings.database.url}")
        logger.info(f"API prefix: {settings.api_v1_prefix}")
    except Exception as e:
        logger.error(f"❌ Configuration error: {e}")
        return 1
    
    # Print helpful URLs
    logger.info("Server will be available at:")
    logger.info(f"  - Main API: http://{args.host}:{args.port}")
    logger.info(f"  - Health check: http://{args.host}:{args.port}/health")
    logger.info(f"  - Database health: http://{args.host}:{args.port}/health/db")
    logger.info(f"  - API docs: http://{args.host}:{args.port}/docs")
    logger.info(f"  - ReDoc: http://{args.host}:{args.port}/redoc")
    
    # Start the server
    return run_server(
        host=args.host,
        port=args.port,
        reload=not args.no_reload,
        log_level=args.log_level
    )


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.info("❌ Server stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        sys.exit(1)