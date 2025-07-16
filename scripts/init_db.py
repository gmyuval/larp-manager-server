#!/usr/bin/env python3
"""
Database initialization script for LARP Manager Server.

This script initializes the database with schema creation, migration application,
and optional development data setup.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from alembic import command
from alembic.config import Config
from sqlalchemy import text

from src.larp_manager_server.config import get_settings
from src.larp_manager_server.database import db_manager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def check_database_connection():
    """Check if database connection is working."""
    logger.info("Checking database connection...")
    
    try:
        await db_manager.initialize()
        health_check = await db_manager.health_check()
        
        if health_check["status"] == "healthy":
            logger.info("✅ Database connection successful")
            return True
        else:
            logger.error(f"❌ Database connection failed: {health_check['error']}")
            return False
    except Exception as e:
        logger.error(f"❌ Database connection error: {e}")
        return False


async def create_schema():
    """Create the larp_manager schema and required extensions."""
    logger.info("Creating database schema...")
    
    try:
        await db_manager.create_schema()
        logger.info("✅ Database schema created successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Schema creation failed: {e}")
        return False


def run_migrations():
    """Run Alembic migrations."""
    logger.info("Running database migrations...")
    
    try:
        # Configure Alembic
        alembic_cfg = Config("alembic.ini")
        
        # Run migrations
        command.upgrade(alembic_cfg, "head")
        
        logger.info("✅ Database migrations completed successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        return False


async def setup_development_data():
    """Set up development data (optional)."""
    logger.info("Setting up development data...")
    
    try:
        # This is a placeholder for development data setup
        # In future phases, this would create sample users, games, etc.
        
        # For now, just verify we can connect and run a simple query
        engine = await db_manager.get_engine()
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT 1"))
            test_value = result.scalar()
            
            if test_value == 1:
                logger.info("✅ Development data setup placeholder completed")
                return True
            else:
                logger.error("❌ Development data setup failed")
                return False
    except Exception as e:
        logger.error(f"❌ Development data setup error: {e}")
        return False


async def reset_database():
    """Reset the database by dropping and recreating schema."""
    logger.warning("⚠️  Resetting database - this will destroy all data!")
    
    try:
        engine = await db_manager.get_engine()
        async with engine.begin() as conn:
            # Drop the schema and recreate it
            await conn.execute(text("DROP SCHEMA IF EXISTS larp_manager CASCADE"))
            await conn.execute(text("CREATE SCHEMA larp_manager"))
            
            # Recreate extensions
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\""))
            
        logger.info("✅ Database reset completed")
        return True
    except Exception as e:
        logger.error(f"❌ Database reset failed: {e}")
        return False


async def main():
    """Main function to initialize the database."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Initialize LARP Manager Server database")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Reset the database (WARNING: destroys all data)"
    )
    parser.add_argument(
        "--skip-migrations",
        action="store_true",
        help="Skip running migrations"
    )
    parser.add_argument(
        "--skip-dev-data",
        action="store_true",
        help="Skip setting up development data"
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Only check database connection, don't initialize"
    )
    
    args = parser.parse_args()
    
    logger.info("🚀 Starting database initialization...")
    
    # Check database connection
    if not await check_database_connection():
        logger.error("❌ Database connection failed. Please check your configuration.")
        return 1
    
    if args.check_only:
        logger.info("✅ Database connection check completed")
        return 0
    
    # Reset database if requested
    if args.reset:
        if not await reset_database():
            return 1
    
    # Create schema
    if not await create_schema():
        return 1
    
    # Run migrations
    if not args.skip_migrations:
        if not run_migrations():
            return 1
    
    # Setup development data
    if not args.skip_dev_data:
        if not await setup_development_data():
            return 1
    
    logger.info("✅ Database initialization completed successfully!")
    
    # Print helpful information
    settings = get_settings()
    logger.info(f"Database URL: {settings.database.url}")
    logger.info("Next steps:")
    logger.info("  1. Start the development server: python scripts/run_dev.py")
    logger.info("  2. Check health endpoint: curl http://localhost:8000/health")
    logger.info("  3. Check database health: curl http://localhost:8000/health/db")
    
    return 0


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.info("❌ Interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        sys.exit(1)
    finally:
        # Clean up database connections
        try:
            asyncio.run(db_manager.close())
        except Exception:
            pass