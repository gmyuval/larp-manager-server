-- PostgreSQL initialization script for LARP Manager Server
-- This script sets up the database with required extensions and schemas

-- Create the uuid-ossp extension for UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create the larp_manager schema
CREATE SCHEMA IF NOT EXISTS larp_manager;

-- Set default search path to include larp_manager schema
-- This allows tables to be accessed without schema prefix
ALTER DATABASE larp_manager_db SET search_path TO larp_manager, public;

-- Create a role for the application (optional but recommended)
-- This is commented out as it's handled by the main user
-- CREATE ROLE larp_manager_user WITH LOGIN PASSWORD 'larp_password';
-- GRANT ALL PRIVILEGES ON SCHEMA larp_manager TO larp_manager_user;
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA larp_manager TO larp_manager_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA larp_manager TO larp_manager_user;

-- Grant necessary permissions to the postgres user for development
GRANT ALL PRIVILEGES ON SCHEMA larp_manager TO postgres;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA larp_manager TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA larp_manager TO postgres;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA larp_manager TO postgres;

-- Set default permissions for future objects
ALTER DEFAULT PRIVILEGES IN SCHEMA larp_manager GRANT ALL ON TABLES TO postgres;
ALTER DEFAULT PRIVILEGES IN SCHEMA larp_manager GRANT ALL ON SEQUENCES TO postgres;
ALTER DEFAULT PRIVILEGES IN SCHEMA larp_manager GRANT ALL ON FUNCTIONS TO postgres;